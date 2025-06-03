import random

from src.heuristics.penalty_rules import load_offered_components, load_requirements, load_student_status, has_schedule_conflict, has_prerequisite_issues


def random_heuristic(csv_path, course, period, load_weighted_disciplines, processed_input_path, max_subjects=5, max_no_improve=10000):
    random.seed(None)
    disciplines = load_weighted_disciplines(csv_path)
    requirements = load_requirements()
    student_status = load_student_status(processed_input_path)

    best_combination = ([], 0)

    for subjects_to_try in range(max_subjects, 0, -1):
        no_improve_count = 0
        while no_improve_count < max_no_improve:
            selected_disciplines = random.sample(disciplines, min(subjects_to_try, len(disciplines)))
            selected_codes = [code for code, _ in selected_disciplines]

            if has_prerequisite_issues(selected_codes, requirements, student_status):
                total_weight = sum(weight for _, weight in selected_disciplines)
                if total_weight > best_combination[1]:
                    best_combination = (selected_codes, total_weight)
                    no_improve_count = 0
                else:
                    no_improve_count += 1
            else:
                no_improve_count += 1

    return best_combination