import csv
import json
from src.heuristics.utils.utils import *

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

def has_prerequisite_issues(selected_disciplines, requirements, student_status):
    def is_satisfied(prerequisite):
        if isinstance(prerequisite, list):
            if prerequisite and all(isinstance(item, list) for item in prerequisite):
                return any(is_satisfied(group) for group in prerequisite)

            else:
                return all(is_satisfied(item) for item in prerequisite)
        elif isinstance(prerequisite, str):
            return student_status.get(prerequisite, 1) == 0
        return False

    for discipline in selected_disciplines:
        prereq = requirements.get(discipline, [])
        if prereq:
            if not is_satisfied(prereq):
                return True
    return False


def load_offered_components(course, period):
    file_path = f"data/raw/offers/{course}/{course}_Offered_Components_{period}.csv"
    offered_components = {}

    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            code = row[1]
            times = row[3:]  # ['25N12', '--'] ou ['3T34 + 6N12', '--']
            if code not in offered_components:
                offered_components[code] = []
            offered_components[code].append(times)

    return offered_components




def has_schedule_conflict(selected_disciplines, offered_components, return_combination=False):
    from itertools import product

    all_schedules = [
        offered_components.get(code, []) for code in selected_disciplines
    ]

    for schedule_combination in product(*all_schedules):
        schedule_map = {}
        conflict_found = False
        blocos = []
        for entry in schedule_combination:
            if not isinstance(entry, (list, tuple)):
                entry = [entry]
            for s in entry:
                if not isinstance(s, str) or s.strip() == '--':
                    continue
                for part in s.split(' + '):
                    blocos += split_blocos(part.strip())

        chaves = blocos_para_chaves(blocos)
        for key in chaves:
            if key in schedule_map:
                conflict_found = True
                break
            schedule_map[key] = True
        if not conflict_found:
            if return_combination:
                print("COMBINAÇÃO VÁLIDA:", schedule_combination)
                return False, schedule_combination
            else:
                return False
    if return_combination:
        print("NENHUMA COMBINAÇÃO VÁLIDA")
        return True, None
    else:
        return True