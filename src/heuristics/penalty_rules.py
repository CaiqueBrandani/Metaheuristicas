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