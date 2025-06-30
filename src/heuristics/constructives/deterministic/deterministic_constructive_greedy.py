from src.heuristics.penalty_rules import load_requirements, load_student_status, load_offered_components, \
    has_prerequisite_issues, has_schedule_conflict, fix_conflicts
from src.metaheuristics.vns import load_equivalences


def deterministic_greedy_heuristic(csv_path, course, period,
                                   load_weighted_disciplines, processed_input_path,max_subjects=5):
    disciplines = load_weighted_disciplines(csv_path)
    weight_map = {c: w for c, w in disciplines}
    equivalences = load_equivalences(course)
    offered_comps = load_offered_components(course, period)
    offered_set = set(offered_comps.keys())
    requirements = load_requirements()
    student_status = load_student_status(processed_input_path)
    disciplines.sort(key=lambda x: x[1], reverse=True)

    best_solution = ([], 0)
    for limit in range(max_subjects, 0, -1):
        selected_temp = []
        for code, weight in disciplines:
            test_codes = [c[0] for c in selected_temp] + [code]
            conflict, _ = has_schedule_conflict(test_codes, offered_comps)
            if not conflict and not has_prerequisite_issues(test_codes, requirements, student_status):
                selected_temp.append((code, weight))
            if len(selected_temp) == limit:
                break
        fixed = fix_conflicts([c[0] for c in selected_temp], offered_comps,
                              equivalences, offered_set, weight_map, requirements, student_status)
        total_temp = sum(weight_map.get(c, 0) for c in fixed)
        if total_temp > best_solution[1]:
            best_solution = (fixed, total_temp)
    return best_solution[0], best_solution[1]