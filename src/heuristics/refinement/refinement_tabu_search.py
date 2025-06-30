from collections import deque
from src.heuristics.penalty_rules import (
    load_offered_components, load_requirements,
    load_student_status, has_schedule_conflict,
    has_prerequisite_issues
)
from src.metaheuristics.vns import load_equivalences

def tabu_search(initial_solution, weighted_csv, load_weighted_disciplines,
                course, period, processed_csv, max_iterations=1000,
                tabu_size=20):
    weights      = dict(load_weighted_disciplines(weighted_csv))
    requirements = load_requirements()
    status       = load_student_status(processed_csv)
    offered      = load_offered_components(course, period)
    equivs       = load_equivalences(course)
    offered_set  = set(offered.keys())

    def score(sol):
        return sum(weights.get(c, 0) for c in sol)

    def is_valid(sol):
        conflict, _ = has_schedule_conflict(sol, offered)
        return not conflict and not has_prerequisite_issues(sol, requirements, status)

    def fix_conflicts(sol):
        sol = sol[:]
        for disc in has_schedule_conflict(sol, offered)[1]:
            # tenta equivalências
            for eq in equivs.get(disc, []):
                if eq in offered_set and eq not in sol:
                    tmp = sol[:]; tmp[tmp.index(disc)] = eq
                    if is_valid(tmp):
                        sol = tmp
                        break
            else:
                # tenta qualquer outra disciplina
                for alt in weights:
                    if alt not in sol:
                        tmp = sol[:]; tmp[tmp.index(disc)] = alt
                        if is_valid(tmp):
                            sol = tmp
                            break
                else:
                    sol.remove(disc)
        return sol

    def neighbors(sol):
        for i in range(len(sol)):
            for cand in weights:
                if cand not in sol:
                    tmp = sol[:]; tmp[i] = cand
                    if is_valid(tmp):
                        yield tmp

    # corrige conflitos iniciais
    current    = fix_conflicts(initial_solution[:])
    best       = current[:]
    best_score = score(best)
    tabu       = deque([current], maxlen=tabu_size)

    for _ in range(max_iterations):
        # vizinhos válidos e não tabu
        opts = [n for n in neighbors(current) if n not in tabu]
        if not opts:
            break
        current = max(opts, key=score)
        tabu.append(current)
        sc = score(current)
        if sc > best_score:
            best, best_score = current[:], sc

    return best, best_score