import csv
import random

def load_requirements(course):
    file_path = f"../data/raw/requirements/{course}/{course}_requirements.csv"
    requirements = {}
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            subject = row[0]
            prerequisites = row[1:]
            requirements[subject] = [prereq for prereq in prerequisites if prereq]
    return requirements

def load_student_status(processed_input_path):
    student_status = {}
    with open(processed_input_path, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            subject = row[0]
            status = int(row[1])  # 0 = aprovado, outros valores = pendente/reprovado
            student_status[subject] = status
    return student_status

def has_prerequisite_issues(selected_disciplines, requirements, student_status):
    for discipline in selected_disciplines:
        prerequisites = requirements.get(discipline, [])
        for prereq in prerequisites:
            if student_status.get(prereq, 1) != 0:  # 1 = pendente/reprovado
                return True  # Pré-requisito não cumprido
    return False

def load_offered_components(course):
    file_path = f"../data/raw/offers/{course}/{course}_Offered_Components.csv"
    offered_components = {}
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            code = row[1]
            times = row[3:]
            offered_components[code] = times
    return offered_components

def has_schedule_conflict(selected_disciplines, offered_components):
    from itertools import product

    # Obter todas as combinações possíveis de horários para as disciplinas
    all_schedules = [
        offered_components.get(code, []) for code in selected_disciplines
    ]

    # Gerar o produto cartesiano para testar todas as combinações de horários
    for schedule_combination in product(*all_schedules):
        schedule_map = {}
        conflict_found = False

        for time in schedule_combination:
            if time == "--":
                continue

            # Divide horários fracionados (ex.: "2T34 + 4T12")
            time_slots = time.split(" + ")

            for slot in time_slots:
                period, slots = slot[:-2], slot[-2:]
                if period not in schedule_map:
                    schedule_map[period] = set()
                if any(slot in schedule_map[period] for slot in slots):
                    conflict_found = True
                    break
                schedule_map[period].update(slots)

            if conflict_found:
                break

        if not conflict_found:
            return False  # Pelo menos uma combinação de horários é válida

    return True  # Todas as combinações têm conflito

def random_heuristic(csv_path, course, load_weighted_disciplines, processed_input_path, max_subjects=5, max_attempts=100000):
    disciplines = load_weighted_disciplines(csv_path)
    offered_components = load_offered_components(course)

    requirements = load_requirements(course)
    student_status = load_student_status(processed_input_path)

    best_combination = ([], 0)  # Armazena a melhor combinação parcial (códigos, peso)

    for subjects_to_try in range(max_subjects, 0, -1):  # Tenta de `max_subjects` até 1 matéria
        for attempt in range(max_attempts):
            selected_disciplines = random.sample(disciplines, min(subjects_to_try, len(disciplines)))
            selected_codes = [code for code, _ in selected_disciplines]

            if not has_schedule_conflict(selected_codes, offered_components) and \
               not has_prerequisite_issues(selected_codes, requirements, student_status):
                total_weight = sum(weight for _, weight in selected_disciplines)
                return selected_codes, total_weight

            # Atualiza a melhor combinação parcial encontrada
            total_weight = sum(weight for _, weight in selected_disciplines)
            if total_weight > best_combination[1]:
                best_combination = (selected_codes, total_weight)

    return best_combination