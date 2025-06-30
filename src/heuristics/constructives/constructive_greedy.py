from src.heuristics.penalty_rules import load_requirements, load_student_status, load_offered_components, has_prerequisite_issues

def greedy_heuristic(csv_path, course, period, load_weighted_disciplines, processed_input_path, max_subjects=5):
    disciplines = load_weighted_disciplines(csv_path)
    disciplines.sort(key=lambda x: x[1], reverse=True)  # Ordena por peso

    requirements = load_requirements()
    student_status = load_student_status(processed_input_path)

    selected_disciplines = []
    for code, weight in disciplines:
        if len(selected_disciplines) >= max_subjects:
            break

        selected_codes = [d[0] for d in selected_disciplines] + [code]
        if not has_prerequisite_issues(selected_codes, requirements, student_status):
            selected_disciplines.append((code, weight))

    total_weight = sum(weight for _, weight in selected_disciplines)
    selected_codes = [code for code, _ in selected_disciplines]
    return selected_codes, total_weight