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

def variable_neighborhood_search(initial_solution, weighted_csv, course, period,
                                 load_weighted_disciplines, processed_csv,
                                 max_k=3, max_no_improve=1000):
    all_disc = load_weighted_disciplines(weighted_csv)
    weight_map = {c: w for c, w in all_disc}
    requirements = load_requirements()
    student_status = load_student_status(processed_csv)
    offered = load_offered_components(course, period)
    equivalences = load_equivalences(course)
    offered_set = set(offered.keys())

    def fix_conflicts(sol):
        new_sol = sol[:]
        conflicts = []
        has_conf, conflicted = has_schedule_conflict(new_sol, offered)
        for disc in conflicted:
            replaced = False
            for eq in equivalences.get(disc, []):
                if eq in offered_set and eq not in new_sol:
                    tmp = new_sol[:]
                    tmp[tmp.index(disc)] = eq
                    if not has_schedule_conflict(tmp, offered)[0] \
                       and not has_prerequisite_issues(tmp, requirements, student_status):
                        new_sol = tmp
                        replaced = True
                        break
            if not replaced:
                # tenta swap por qualquer outra matéria disponível
                for alt in weight_map:
                    if alt not in new_sol:
                        tmp = new_sol[:]
                        tmp[tmp.index(disc)] = alt
                        if not has_schedule_conflict(tmp, offered)[0] \
                           and not has_prerequisite_issues(tmp, requirements, student_status):
                            new_sol = tmp
                            replaced = True
                            break
            if not replaced:
                # se não der, remove
                new_sol.remove(disc)
            conflicts.append(disc)
        return new_sol

    def neighborhood(sol, k):
        neighs = []
        size = len(sol)
        if size < k:
            return neighs
        for _ in range(10 * k):
            idxs = random.sample(range(size), k)
            choices = random.sample([c for c in weight_map if c not in sol], k)
            cand = sol[:]
            for i, c_new in zip(idxs, choices):
                cand[i] = c_new
            # resolve conflitos localmente
            cand = fix_conflicts(cand)
            tup = tuple(sorted(cand))
            neighs.append((cand, tup))
        return neighs

    # initial fix
    current = fix_conflicts(initial_solution)
    best = current[:]
    best_score = sum(weight_map.get(c, 0) for c in best)
    visited = {tuple(sorted(best))}

    no_improve = 0
    while no_improve < max_no_improve:
        k = random.randint(1, max_k)
        neighs = neighborhood(current, k)
        improved = False

        random.shuffle(neighs)
        for cand, key in neighs:
            if key in visited:
                continue
            visited.add(key)
            if has_prerequisite_issues(cand, requirements, student_status):
                continue
            score = sum(weight_map.get(c, 0) for c in cand)
            if score > best_score:
                best, best_score, current = cand, score, cand
                improved = True
                break

        if improved:
            no_improve = 0
        else:
            no_improve += 1

    return best, best_score