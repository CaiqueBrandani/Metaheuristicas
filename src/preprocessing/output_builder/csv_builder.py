import csv
from collections import Counter

from src.preprocessing.utils.status_enums import ApprovedStatus, FailedStatus

def build_csv(history_components, pending_components, output_csv, course, current_period):
    equivalences_file = f"../data/raw/equivalences/{course}/{course}_Equiv_Subjects_2013_2022.csv"
    requirements_file = f"../data/raw/requirements/{course}/{course}_requirements.csv"
    offered_components_file = "../data/raw/offers/Offered_Components.csv"

    subject_period_map = {}
    period_map = {}
    period_counter = 0

    with open(equivalences_file, mode="r", encoding="utf-8") as file:
        for row in csv.reader(file):
            period, *subjects = row
            for subject in subjects:
                if subject and subject != "--":
                    for sub in subject.split(" + "):
                        subject_period_map[sub.strip()] = period

    prerequisite_count = Counter()
    with open(requirements_file, mode="r", encoding="utf-8") as file:
        for row in csv.reader(file):
            prerequisites = row[1:]
            for prerequisite in prerequisites:
                prerequisite_count[prerequisite.strip()] += 1

    offered_components = {}
    with open(offered_components_file, mode="r", encoding="utf-8") as file:
        for row in csv.reader(file):
            code, column_value = row[0], row[1]
            offered_components[code] = int(column_value)

    final_records = []
    for component in history_components:
        period = component["period"]
        if period not in period_map:
            period_counter += 1
            period_map[period] = period_counter
        component["period_counter"] = period_map[period]

        offered_value = offered_components.get(component["code"], 0)
        new_column_value = 2 if offered_value == 1 else 1 if offered_value == 3 else 0

        final_records.append([
            component["code"],
            0 if component["status"] in {status.value for status in ApprovedStatus} else 2,
            1 if (component["status"] in {status.value for status in FailedStatus} and (current_period - component["period_counter"] <= 1)) else 0,
            prerequisite_count.get(component["code"], 0),
            2 if offered_components.get(component["code"], 0) == 1 else 1 if offered_components.get(component["code"], 0) == 3 else 0,
            (current_period - int(subject_period_map.get(component["code"], 0))) if component["status"] in {status.value for status in FailedStatus} else 0
        ])

    final_records += [
        [
            component["code"],
            1,
            0,
            prerequisite_count.get(component["code"], 0),
            2 if offered_components.get(component["code"], 0) == 1 else 1 if offered_components.get(component["code"], 0) == 3 else 0,
            current_period - int(subject_period_map.get(component["code"], 0))
        ]
        for component in pending_components
    ]

    final_records = [list(filter(lambda x: x is not None, record)) for record in final_records]

    final_records.sort(key=lambda x: x[1])

    with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(final_records)