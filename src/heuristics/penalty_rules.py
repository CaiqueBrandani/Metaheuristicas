import csv
import json
import re

def load_requirements():
    file_path = f"data/raw/requirements/requirements.json"
    with open(file_path, mode="r", encoding="utf-8") as file:
        return json.load(file)

def load_student_status(processed_input_path):
    student_status = {}
    with open(processed_input_path, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            subject = row[0]
            status = int(row[1])
            student_status[subject] = status
    return student_status

def load_offered_components(course, period):
    file_path = f"data/raw/offers/{course}/{course}_Offered_Components_{period}.csv"
    offered_components = {}
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            code = row[1]
            times = row[3:]
            offered_components[code] = times
    return offered_components

def has_prerequisite_issues(selected_disciplines, requirements, student_status):
    for disc in selected_disciplines:
        if disc not in requirements:
            continue  # sem pré-requisito
        ok_in_or = False
        for req_list in requirements[disc]:
            if all(student_status.get(req, 1) == 0 for req in req_list):
                ok_in_or = True
                break
        if not ok_in_or:
            return True  # encontrou problema
    return False

def has_schedule_conflict(selected_disciplines, offered_components):
    def parse_slots(schedule_str):
        slots = []
        for part in schedule_str.split(" + "):
            m = re.match(r"(\d+)([TMN])(\d+)", part)
            if not m:
                continue
            days, period, hours = m.groups()
            for d in days:
                for h in hours:
                    slots.append((d, period, h))
        return slots

    occupied = set()
    conflicts = []

    for disc in selected_disciplines:
        options = offered_components.get(disc, [])
        encaixou = False

        for sched in options:
            if sched == "--":
                continue
            slots = parse_slots(sched)
            # testa conflito
            if all(slot not in occupied for slot in slots):
                # reserva estes slots
                occupied.update(slots)
                encaixou = True
                break

        if not encaixou:
            conflicts.append(disc)

    return len(conflicts) > 0, conflicts

def fix_conflicts(disciplines, offered_comps, equivalences, offered_set,
                  weight_map, requirements, student_status):
    from copy import deepcopy
    new_sol = deepcopy(disciplines)
    conflict, conflicted = has_schedule_conflict(new_sol, offered_comps)
    for disc in conflicted:
        replaced = False
        for eq in equivalences.get(disc, []):
            if eq in offered_set and eq not in new_sol:
                temp = new_sol[:]
                temp[temp.index(disc)] = eq
                c, _ = has_schedule_conflict(temp, offered_comps)
                if not c and not has_prerequisite_issues(temp, requirements, student_status):
                    new_sol = temp
                    replaced = True
                    break
        if not replaced:
            for alt in weight_map:
                if alt not in new_sol:
                    temp = new_sol[:]
                    temp[temp.index(disc)] = alt
                    c, _ = has_schedule_conflict(temp, offered_comps)
                    if not c and not has_prerequisite_issues(temp, requirements, student_status):
                        new_sol = temp
                        replaced = True
                        break
        if not replaced:
            new_sol.remove(disc)
    return new_sol