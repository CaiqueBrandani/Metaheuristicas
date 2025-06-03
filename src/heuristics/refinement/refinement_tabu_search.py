from collections import deque
from src.heuristics.penalty_rules import load_offered_components, load_requirements, load_student_status, has_schedule_conflict, has_prerequisite_issues

def tabu_search(initial_solution, weighted_csv, load_weighted_disciplines, course, period, processed_csv, max_iterations=10000, tabu_size=10):
    all_disciplines = load_weighted_disciplines(weighted_csv)
    disciplines_dict = {code: weight for code, weight in all_disciplines}

    requirements = load_requirements()
    student_status = load_student_status(processed_csv)
    offered_components = load_offered_components(course, period)

    current_solution = initial_solution[:]
    best_solution = current_solution[:]
    best_score = sum(disciplines_dict[code] for code in best_solution)

    tabu_list = deque(maxlen=tabu_size)

    for _ in range(max_iterations):
        neighbors = []

        for i in range(len(current_solution)):
            for code_out in disciplines_dict:
                if code_out not in current_solution:
                    neighbor = current_solution[:]
                    neighbor[i] = code_out

                    if has_schedule_conflict(neighbor, offered_components) or \
                       has_prerequisite_issues(neighbor, requirements, student_status):
                        continue

                    neighbors.append(neighbor)

        best_neighbor = None
        best_neighbor_score = -float('inf')
        for neighbor in neighbors:
            if neighbor in tabu_list:
                continue
            score = sum(disciplines_dict[code] for code in neighbor)
            if score > best_neighbor_score:
                best_neighbor = neighbor
                best_neighbor_score = score

        if best_neighbor:
            current_solution = best_neighbor
            tabu_list.append(best_neighbor)

            if best_neighbor_score > best_score:
                best_solution = best_neighbor
                best_score = best_neighbor_score

    return best_solution, best_score