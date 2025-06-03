import csv
import json

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
            times = row[3:]
            offered_components[code] = times
    return offered_components

def has_schedule_conflict(selected_disciplines, offered_components):
    from itertools import product

    all_schedules = [
        offered_components.get(code, []) for code in selected_disciplines
    ]

    for schedule_combination in product(*all_schedules):
        schedule_map = {}
        conflict_found = False

        for time in schedule_combination:
            if time == "--":
                continue

            time_slots = time.split(" + ")

            for slot in time_slots:
                period, slots = slot[:-2], slot[-2:]
                if period not in schedule_map:
                    schedule_map[period] = set()
                if any(slot in schedule_map[period] for slot in slots):
                    conflict_found = True
                    break
                schedule_map[period].update(slots)

            if conflict_found:
                break

        if not conflict_found:
            return False

    return True