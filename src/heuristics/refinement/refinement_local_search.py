from src.heuristics.penalty_rules import load_offered_components, load_requirements, load_student_status, has_schedule_conflict, has_prerequisite_issues

def load_disciplines(csv_path):
    import csv
    disciplines = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            code = row[0]
            weight = float(row[1])
            disciplines.append((code, weight))
    return disciplines

def calculate_score(weight):
    return weight

def refine_local(constructive_heuristic, weighted_csv, course, load_weighted_disciplines, processed_csv, *args, max_jumps=5):
    initial_solution, _ = constructive_heuristic(weighted_csv, course, load_weighted_disciplines, processed_csv, *args)

    all_disciplines = load_weighted_disciplines(weighted_csv)
    disciplines_dict = {code: weight for code, weight in all_disciplines}

    requirements = load_requirements(course)
    student_status = load_student_status(processed_csv)
    offered_components = load_offered_components(course)

    best_solution = initial_solution[:]
    best_score = sum(calculate_score(disciplines_dict[code]) for code in best_solution)

    jumps = 0

    while jumps < max_jumps:
        improved = False
        for code_out in disciplines_dict:
            if code_out in best_solution:
                continue
            for i in range(len(best_solution)):
                new_solution = best_solution[:]
                new_solution[i] = code_out

                if has_schedule_conflict(new_solution, offered_components) or \
                   has_prerequisite_issues(new_solution, requirements, student_status):
                    continue

                new_score = sum(calculate_score(disciplines_dict[code]) for code in new_solution)
                if new_score > best_score:
                    best_solution = new_solution
                    best_score = new_score
                    improved = True
                    break
            if improved:
                break
        if improved:
            jumps = 0
        else:
            jumps += 1

    total_weight = sum(disciplines_dict[code] for code in best_solution)

    return best_solution, total_weight