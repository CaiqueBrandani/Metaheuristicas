import random

from src.heuristics.penalty_rules import load_requirements, load_student_status, has_prerequisite_issues, \
    has_schedule_conflict, load_offered_components, fix_conflicts
from src.metaheuristics.vns import load_equivalences


def deterministic_random_heuristic(csv_path, course, period, load_weighted_disciplines,
                                   processed_input_path,max_subjects=5, max_no_improve=1000, seed=None):
    if seed is not None:
        random.seed(seed)
    disciplines = load_weighted_disciplines(csv_path)
    weight_map = {c: w for c, w in disciplines}
    equivalences = load_equivalences(course)
    offered_comps = load_offered_components(course, period)
    offered_set = set(offered_comps.keys())
    requirements = load_requirements()
    student_status = load_student_status(processed_input_path)

    best_combination = ([], 0)
    for subjects_to_try in range(max_subjects, 0, -1):
        no_improve_count = 0
        while no_improve_count < max_no_improve:
            attempt = min(subjects_to_try, len(disciplines))
            selected = random.sample(disciplines, attempt)
            selected_codes = [c for c, _ in selected]
            conflict, _ = has_schedule_conflict(selected_codes, offered_comps)
            if not conflict and not has_prerequisite_issues(selected_codes, requirements, student_status):
                fixed = fix_conflicts(selected_codes, offered_comps, equivalences,
                                      offered_set, weight_map, requirements, student_status)
                score = sum(weight_map.get(c, 0) for c in fixed)
                if score > best_combination[1]:
                    best_combination = (fixed, score)
                    no_improve_count = 0
                else:
                    no_improve_count += 1
            else:
                no_improve_count += 1
    return best_combination[0], best_combination[1]