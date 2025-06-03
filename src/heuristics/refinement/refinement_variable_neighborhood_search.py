import random
import csv
import os
from src.heuristics.penalty_rules import (load_offered_components, load_requirements, load_student_status, has_schedule_conflict, has_prerequisite_issues)

def load_equivalences(course):
    path = f"data/raw/equivalences/{course}/{course}_Equiv_Subjects.csv"
    equivalences = {}
    if not os.path.exists(path):
        return equivalences
    with open(path, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            code = row[1]
            equivs = set()
            for col in row[3:]:
                if col and col != "--":
                    for eq in col.split(","):
                        eq = eq.strip()
                        if eq:
                            equivs.add(eq)
            if equivs:
                equivalences[code] = equivs
    return equivalences

def variable_neighborhood_search(constructive_heuristic, weighted_csv, course, period, load_weighted_disciplines, processed_csv, max_k=2, max_no_improve=1000):
    all_disciplines = load_weighted_disciplines(weighted_csv)
    disciplines_dict = {code: weight for code, weight in all_disciplines}
    requirements = load_requirements()
    student_status = load_student_status(processed_csv)
    offered_components = load_offered_components(course, period)
    equivalences = load_equivalences(course)
    offered_set = set(offered_components.keys())

    best_solution = []
    best_score = 0

    def solution_to_tuple(solution):
        return tuple(sorted(solution))

    visited_solutions = set()

    def get_neighbors(solution, k):
        neighbors = []
        available = [code for code in disciplines_dict if code not in solution]
        if len(available) < k or len(solution) < k:
            return neighbors
        for _ in range(20):
            indices = random.sample(range(len(solution)), k)
            new_codes = random.sample(available, k)
            neighbor = solution[:]
            for idx, new_code in zip(indices, new_codes):
                neighbor[idx] = new_code
            if solution_to_tuple(neighbor) in visited_solutions:
                continue
            if not has_schedule_conflict(neighbor, offered_components) and \
               not has_prerequisite_issues(neighbor, requirements, student_status):
                neighbors.append(neighbor)
        return neighbors

    def fix_penalty_issues(solution):
        fixed_solution = solution[:]
        total_weight_adjustment = 0  # Soma dos pesos das matérias originais
        for i, code in enumerate(solution):
            if has_schedule_conflict([code], offered_components) or \
                    has_prerequisite_issues([code], requirements, student_status):
                replaced = False
                for eq in equivalences.get(code, []):
                    if eq in offered_set and eq not in fixed_solution and \
                        not has_schedule_conflict([eq], offered_components) and \
                        not has_prerequisite_issues([eq], requirements, student_status):
                        fixed_solution[i] = eq
                        total_weight_adjustment += disciplines_dict.get(code, 0)  # Soma o peso da matéria original
                        replaced = True
                        break
                if not replaced:
                    for replacement in disciplines_dict:
                        if replacement not in fixed_solution and \
                                not has_schedule_conflict([replacement], offered_components) and \
                                not has_prerequisite_issues([replacement], requirements, student_status):
                            fixed_solution[i] = replacement
                            replaced = True
                            break
                if not replaced:
                    fixed_solution[i] = None
        fixed_solution = [code for code in fixed_solution if code is not None]
        return fixed_solution, total_weight_adjustment

    max_subjects = 5
    for subjects_to_try in range(max_subjects, 0, -1):
        current_solution, _ = constructive_heuristic(weighted_csv, course, period, load_weighted_disciplines, processed_csv, max_subjects=subjects_to_try)
        current_solution, weight_adjustment = fix_penalty_issues(current_solution)
        if len(current_solution) != subjects_to_try:
            continue
        visited_solutions.clear()
        visited_solutions.add(solution_to_tuple(current_solution))
        current_score = sum(disciplines_dict[code] for code in current_solution if code in disciplines_dict) + weight_adjustment
        if current_score > best_score:
            best_solution = current_solution[:]
            best_score = current_score
        no_improve = 0
        while no_improve < max_no_improve:
            k = 1
            improved = False
            while k <= max_k:
                neighbors = get_neighbors(current_solution, k)
                neighbors = [n for n in neighbors if solution_to_tuple(n) not in visited_solutions]
                if not neighbors:
                    k += 1
                    continue
                neighbor = random.choice(neighbors)
                local_best, weight_adjustment = fix_penalty_issues(neighbor)
                if len(local_best) != subjects_to_try:
                    k += 1
                    continue
                local_best_tuple = solution_to_tuple(local_best)
                if local_best_tuple in visited_solutions:
                    k += 1
                    continue
                visited_solutions.add(local_best_tuple)
                local_best_score = sum(disciplines_dict[code] for code in local_best if code in disciplines_dict) + weight_adjustment
                if local_best_score > best_score:
                    best_solution = local_best
                    best_score = local_best_score
                    current_solution = local_best
                    improved = True
                    no_improve = 0
                    k = 1  # Reinicia k ao encontrar uma melhoria
                    break
                else:
                    k += 1
            if not improved:
                no_improve += 1
    return best_solution, best_score