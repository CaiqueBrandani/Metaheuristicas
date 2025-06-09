import random
import itertools
from src.heuristics.utils.utils import split_blocos
from src.heuristics.penalty_rules import (
    load_offered_components,
    load_requirements,
    load_student_status,
    has_prerequisite_issues
)


def decode_chromosome(
    chromosome,
    all_disciplines,
    offered_components,
    requirements,
    student_status,
    max_subjects=5,
    threshold=0.5
):
    sorted_disc_genes = sorted(zip(all_disciplines, chromosome), key=lambda x: x[1], reverse=True)
    candidates = [code for code, gene in sorted_disc_genes if gene >= threshold][:max_subjects]
    if not candidates:
        return [], [], {}

    schedule_options = []

    for code in candidates:
        turmas = offered_components.get(code, [])
        turmas_filtradas = []
        for turma in turmas:
            if isinstance(turma, list):
                turmas_filtradas.append(turma)
            elif isinstance(turma, str):
                turmas_filtradas.append([turma])
        if not turmas_filtradas:
            print(f"[!] Sem turmas válidas para {code}")
            return [], [], {}
        schedule_options.append(turmas_filtradas)

    total_combinations = 1
    for opts in schedule_options:
        total_combinations *= len(opts)

    print(f"[DEBUG] schedule_options: {[len(opts) for opts in schedule_options]}")

    for offer_indices in itertools.product(*[range(len(opts)) for opts in schedule_options]):
        blocos = []
        for i, idx in enumerate(offer_indices):
            entry = schedule_options[i][idx]
            for s in entry:
                if not isinstance(s, str) or s.strip() == '--':
                    continue
                for part in s.split(" + "):
                    blocos += split_blocos(part.strip())

        schedule_map = {}
        has_conflict = False
        for bloco in blocos:
            if len(bloco) < 3:
                continue
            dia, turno, slots = bloco[0], bloco[1], bloco[2:]
            if dia not in {'2','3','4','5','6'} or turno not in 'MTN':
                continue
            for slot in slots:
                key = f"{dia}-{turno}{slot}"
                if key in schedule_map:
                    has_conflict = True
                    break
                schedule_map[key] = True
            if has_conflict:
                break

        if not has_conflict and not has_prerequisite_issues(candidates, requirements, student_status):
            offer_map = {
                candidates[i]: schedule_options[i][offer_indices[i]]
                for i in range(len(candidates))
            }
            return candidates, offer_indices, offer_map

    print(f"[!] Nenhuma combinação viável para: {candidates} ({total_combinations} tentativas)")
    return [], [], {}

def run_brkga(
    weighted_csv,
    course,
    load_weights_fn,
    processed_csv,
    period,
    population_size,
    elite_fraction,
    mutant_fraction,
    generations,
    max_subjects,
    seed
):
    if seed is not None:
        random.seed(seed)
    else:
        random.seed(42)

    disciplines_with_weights = load_weights_fn(weighted_csv)
    all_disciplines = [code for code, _ in disciplines_with_weights]

    offered_components = load_offered_components(course, period)
    requirements = load_requirements()
    student_status = load_student_status(processed_csv)

    n_genes = len(all_disciplines)
    elite_size = int(population_size * elite_fraction)
    mutant_size = int(population_size * mutant_fraction)
    offspring_size = population_size - elite_size - mutant_size

    def fitness(chromosome):
        selected, _, _ = decode_chromosome(
            chromosome,
            all_disciplines,
            offered_components,
            requirements,
            student_status,
            max_subjects
        )
        code_to_weight = dict(disciplines_with_weights)
        return sum(code_to_weight.get(code, 0) for code in selected), selected

    # Inicializa população
    population = []
    discipline_sets = set()

    max_attempts = 10 * population_size
    attempts = 0

    while len(population) < population_size and attempts < max_attempts:
        attempts += 1
        genes = [random.random() for _ in range(n_genes)]

        selected = []
        for num_subjs in range(max_subjects, 0, -1):
            for threshold in [0.5, 0.4, 0.3, 0.2, 0.0]:
                selected_try, _, _ = decode_chromosome(
                    genes,
                    all_disciplines,
                    offered_components,
                    requirements,
                    student_status,
                    max_subjects=num_subjs,
                    threshold=threshold
                )
                if selected_try:
                    selected = selected_try
                    break
            if selected:
                break

        if not selected:
            continue  # Ainda assim, pula inválido

        key = frozenset(selected)
        if key not in discipline_sets:
            discipline_sets.add(key)
            population.append(genes)

    # Aviso se não conseguiu uma população completamente distinta
    if len(population) < population_size:
        print(f"Atenção: população inicial incompleta. Gerados {len(population)} de {population_size}.")
        while len(population) < population_size:
            genes = [random.random() for _ in range(n_genes)]
            population.append(genes)

    for _ in range(generations):
        seen = set()
        scored_population = []
        for ind in population:
            score, selected = fitness(ind)
            key = tuple(sorted(selected))
            if key not in seen:
                seen.add(key)
                scored_population.append(((score, selected), ind))

        scored_population.sort(reverse=True, key=lambda x: x[0][0])
        elites = [ind for (_, ind) in scored_population[:elite_size]]
        next_population = elites[:]

        # Mutantes aleatórios
        for _ in range(mutant_size):
            mutant = [random.random() for _ in range(n_genes)]
            next_population.append(mutant)

        # Offspring cruzando elite com não-elite
        mutation_rate = 0.1  # 10% chance de mutar um gene

        for _ in range(offspring_size):
            elite_parent = random.choice(elites)
            other_parent = random.choice(population)  # mais diversidade
            child = [
                elite_gene if random.random() < 0.7 else other_gene
                for elite_gene, other_gene in zip(elite_parent, other_parent)
            ]
            # mutação leve
            child = [gene if random.random() > mutation_rate else random.random() for gene in child]
            next_population.append(child)

        population = next_population

    # Melhor indivíduo
    final_scored = [ (fitness(ind), ind) for ind in population ]
    final_scored.sort(reverse=True, key=lambda x: x[0][0])
    best_fitness, best_ind = final_scored[0]
    (best_score, best_selected), _ = best_fitness, best_ind

    # Pegue também o offer_map correto e o índice das turmas:
    best_selected, best_offer_indices, offer_map = decode_chromosome(
        best_ind,
        all_disciplines,
        offered_components,
        requirements,
        student_status,
        max_subjects
    )

    # Construção da grade horária
    dias = ['2', '3', '4', '5', '6']
    rotulo_dia = {'2': 'SEG', '3': 'TER', '4': 'QUA', '5': 'QUI', '6': 'SEX'}
    horas = ['M1', 'M2', 'M3', 'M4', 'M5', 'T1', 'T2', 'T3', 'T4', 'N1', 'N2', 'N3', 'N4']
    grade = {f'{rotulo_dia[d]}-{h}': '0' for d in dias for h in horas}

    for code in best_selected:
        turma_escolhida = offer_map.get(code)
        blocos = []
        if isinstance(turma_escolhida, str):
            if turma_escolhida.strip() == '--':
                continue
            for part in turma_escolhida.split(" + "):
                blocos += split_blocos(part.strip())
        elif isinstance(turma_escolhida, (list, tuple)):
            for s in turma_escolhida:
                if not isinstance(s, str) or s.strip() == '--':
                    continue
                for part in s.split(" + "):
                    blocos += split_blocos(part.strip())
        else:
            continue

        for bloco in blocos:
            if len(bloco) < 3:
                continue
            dia = bloco[0]
            turno = bloco[1]
            slots = bloco[2:]
            if dia not in rotulo_dia or turno not in 'MTN':
                continue
            for slot in slots:
                key = f"{rotulo_dia[dia]}-{turno}{slot}"
                if key in grade:
                    grade[key] = code

    print("\nGrade Horária:")
    cabecalho = "Hora | " + " ".join([f"{rotulo_dia[d]:^8}" for d in dias])
    print(cabecalho)
    print("-" * len(cabecalho))

    for hora in horas:
        linha = [f"{grade.get(f'{rotulo_dia[d]}-{hora}', '0'):^8}" for d in dias]
        print(f"{hora} | " + " ".join(linha))


    return best_selected, best_score