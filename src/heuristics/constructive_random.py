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
    schedule_map = {}
    for code in selected_disciplines:
        times = offered_components.get(code, [])
        conflict_found = True  # Assume que há conflito até verificar todos os horários

        for time in times:
            if time == "--":
                continue

            # Divide horários fracionados (ex.: "3N12 + 6N34")
            time_slots = time.split(" + ")
            temp_schedule_map = schedule_map.copy()
            local_conflict = False

            for slot in time_slots:
                period, slots = slot[:-2], slot[-2:]
                if period not in temp_schedule_map:
                    temp_schedule_map[period] = set()
                if any(slot in temp_schedule_map[period] for slot in slots):
                    local_conflict = True
                    break
                temp_schedule_map[period].update(slots)

            if not local_conflict:
                # Atualiza o mapa de horários apenas se não houver conflito
                schedule_map = temp_schedule_map
                conflict_found = False
                break

        if conflict_found:
            return True  # Conflito encontrado para todos os horários disponíveis

    return False

def random_heuristic(csv_path, course, load_weighted_disciplines, processed_input_path, max_subjects=5, max_attempts=1000000):
    disciplines = load_weighted_disciplines(csv_path)
    offered_components = load_offered_components(course)

    requirements = load_requirements(course)
    student_status = load_student_status(processed_input_path)

    for _ in range(max_attempts):
        selected_disciplines = random.sample(disciplines, min(max_subjects, len(disciplines)))
        selected_codes = [code for code, _ in selected_disciplines]

        if not has_schedule_conflict(selected_codes, offered_components) and \
           not has_prerequisite_issues(selected_codes, requirements, student_status):
            total_weight = sum(weight for _, weight in selected_disciplines)
            return selected_codes, total_weight

    return [], 0