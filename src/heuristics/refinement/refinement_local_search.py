import random
from itertools import product
from src.heuristics.penalty_rules import (
    load_offered_components, load_requirements, load_student_status,
    has_schedule_conflict, has_prerequisite_issues
)
from src.metaheuristics.vns import load_equivalences


def local_search(initial_solution, weighted_csv, course, period,
                 load_weighted_disciplines, processed_csv, max_jumps=1000):
    # Load data
    disciplines = {code: w for code, w in load_weighted_disciplines(weighted_csv)}
    requirements = load_requirements()
    student_status = load_student_status(processed_csv)
    offered = load_offered_components(course, period)
    equivalents = load_equivalences(course)

    def fix_conflicts(solution):
        for disc in has_schedule_conflict(solution, offered)[1]:
            for eq in equivalents.get(disc, []):
                if eq not in solution and is_valid_swap(solution, disc, eq):
                    solution[solution.index(disc)] = eq
                    break
            else:
                for alt in disciplines:
                    if alt not in solution and is_valid_swap(solution, disc, alt):
                        solution[solution.index(disc)] = alt
                        break
                else:
                    solution.remove(disc)
        return solution

    def is_valid_swap(solution, old, new):
        temp = solution[:]
        temp[temp.index(old)] = new
        return not has_schedule_conflict(temp, offered)[0] and \
               not has_prerequisite_issues(temp, requirements, student_status)

    def calculate_score(solution):
        return sum(disciplines.get(c, 0) for c in solution)

    # Initialize
    best = fix_conflicts(initial_solution[:])
    best_score = calculate_score(best)
    jumps = 0

    while jumps < max_jumps:
        improved = False

        # Try single replacements
        for disc in has_schedule_conflict(best, offered)[1]:
            for eq in equivalents.get(disc, []):
                if eq not in best and is_valid_swap(best, disc, eq):
                    best[best.index(disc)] = eq
                    best_score = calculate_score(best)
                    improved = True
                    break
            if improved:
                break

        # Try batch replacements
        if not improved:
            for combo in product(*[equivalents.get(d, []) for d in has_schedule_conflict(best, offered)[1]]):
                temp = best[:]
                for d, e in zip(has_schedule_conflict(best, offered)[1], combo):
                    if e and e not in temp:
                        temp[temp.index(d)] = e
                if not has_schedule_conflict(temp, offered)[0] and \
                   not has_prerequisite_issues(temp, requirements, student_status):
                    score = calculate_score(temp)
                    if score > best_score:
                        best, best_score = temp, score
                        improved = True
                        break

        # Try random swaps
        if not improved:
            for _ in range(len(has_schedule_conflict(best, offered)[1])):
                disc = random.choice(has_schedule_conflict(best, offered)[1])
                alt = random.choice([x for x in disciplines if x not in best])
                if is_valid_swap(best, disc, alt):
                    best[best.index(disc)] = alt
                    best_score = calculate_score(best)
                    improved = True
                    break

        # Remove conflicts
        if not improved:
            for disc in has_schedule_conflict(best, offered)[1]:
                temp = best[:]
                temp.remove(disc)
                if not has_schedule_conflict(temp, offered)[0] and \
                   not has_prerequisite_issues(temp, requirements, student_status):
                    best, best_score = temp, calculate_score(temp)
                    improved = True
                    break

        # Update jumps
        if not improved:
            jumps += 1
        else:
            jumps = 0

    return best, best_score