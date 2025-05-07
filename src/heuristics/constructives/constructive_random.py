import random

from src.heuristics.penalty_rules import load_offered_components, load_requirements, load_student_status, has_schedule_conflict, has_prerequisite_issues


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