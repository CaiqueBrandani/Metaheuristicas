import random
from src.heuristics.penalty_rules import (
    load_offered_components,
    load_requirements,
    load_student_status,
    has_schedule_conflict,
    has_prerequisite_issues
)

def decode_chromosome(chromosome, all_disciplines, offered_components, requirements, student_status, max_subjects=5, threshold=0.25):
    selected = []
    for code, gene_val in sorted(zip(all_disciplines, chromosome), key=lambda x: x[1], reverse=True):
        if len(selected) >= max_subjects:
            break
        if code in selected:
            continue
        if gene_val < threshold:
            continue
        temp_selection = selected + [code]
        conflict, _ = has_schedule_conflict(temp_selection, offered_components)  # <-- ATUALIZA AQUI
        if not conflict and \
           not has_prerequisite_issues(temp_selection, requirements, student_status):
            selected.append(code)
    return selected




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

    #print("Disciplinas analisadas:", all_disciplines)

    offered_components = load_offered_components(course, period)
    requirements = load_requirements()
    student_status = load_student_status(processed_csv)

    n_genes = len(all_disciplines)
    elite_size = int(population_size * elite_fraction)
    mutant_size = int(population_size * mutant_fraction)
    offspring_size = population_size - elite_size - mutant_size

    def fitness(chromosome):
        selected = decode_chromosome(chromosome, all_disciplines, offered_components, requirements, student_status, max_subjects)
        code_to_weight = dict(disciplines_with_weights)
        return sum(code_to_weight.get(code, 0) for code in selected), selected

    # Inicializa população
    population = []
    for _ in range(population_size):
        genes = [random.random() for _ in range(n_genes)]
        population.append(genes)
    # discipline_sets = set()
    #
    # max_attempts = 10 * population_size
    # attempts = 0
    #
    # while len(population) < population_size and attempts < max_attempts:
    #     attempts += 1
    #     genes = [random.random() for _ in range(n_genes)]
    #     selected_disciplines = decode_chromosome(genes, all_disciplines, offered_components, requirements,
    #                                              student_status, max_subjects)
    #     key = frozenset(selected_disciplines)
    #
    #     if key not in discipline_sets:
    #         discipline_sets.add(key)
    #         population.append(genes)

    # Aviso se não conseguiu uma população completamente distinta
    # if len(population) < population_size:
    #     print(f"Atenção: população inicial incompleta. Gerados {len(population)} de {population_size}.")
    #     while len(population) < population_size:
    #         genes = [random.random() for _ in range(n_genes)]
    #         population.append(genes)

    for _ in range(generations):
        seen = set()
        scored_population = []
        for ind in population:
            score, selected = fitness(ind)
            key = tuple(sorted(selected))  # Ignora a ordem
            if key not in seen:
                seen.add(key)
                scored_population.append(((score, selected), ind))

        scored_population.sort(reverse=True, key=lambda x: x[0][0])

        # top_50pct = scored_population[:len(scored_population) // 2]
        # print(f"\n=== Debug: Top 50% da geração {_} ===")
        # for idx, ((score, selected), ind) in enumerate(top_50pct):
        #     print(f"{idx + 1:2d}: Valor: {score:8.2f} | Matérias: {selected}")
        # print("==============================\n")
        #
        # print(f"\n=== Debug: População Completa ===")
        # for idx, ((score, selected), ind) in enumerate(scored_population):
        #     print(f"{idx + 1:2d}: Valor: {score:8.2f} | Matérias: {selected}")
        # print("==============================\n")

        # Para contar quantos são únicos:
        # unicos = set(tuple(sorted(selected)) for (score, selected), ind in scored_population)
        # print(f"Indivíduos únicos na geração {_ + 1}: {len(unicos)}\n")

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
            other_parent = random.choice(population)  # escolher em toda população para mais diversidade
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
    best_score, best_selected = final_scored[0][0]
    return best_selected, best_score
