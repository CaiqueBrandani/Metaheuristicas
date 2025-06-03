import csv
import json
from collections import Counter

from src.preprocessing.utils.status_enums import ApprovedStatus, FailedStatus

def build_processed_input_data(history_components, pending_components, output_csv, course, current_period, period):
    equivalences_file = f"data/raw/equivalences/{course}/{course}_Equiv_Subjects.csv"
    requirements_file = f"data/raw/requirements/requirements.json"
    offered_components_file = f"data/raw/offers/{course}/{course}_Offered_Components_{period}.csv"

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

    def flatten_prereqs(prereq):
        result = set()
        if isinstance(prereq, list):
            for item in prereq:
                if isinstance(item, list):
                    result.update(flatten_prereqs(item))
                else:
                    result.add(item)
        elif isinstance(prereq, str):
            result.add(prereq)
        return result

    prerequisite_count = Counter()
    with open(requirements_file, mode="r", encoding="utf-8") as file:
        requirements = json.load(file)
        for subject, prereq_list in requirements.items():
            prereqs_in_line = flatten_prereqs(prereq_list)
            for prereq in prereqs_in_line:
                prerequisite_count[prereq] += 1

    offered_components = {}
    with open(offered_components_file, mode="r", encoding="utf-8") as file:
        for row in csv.reader(file):
            code, column_value = row[1], row[2]
            offered_components[code] = int(column_value)

    final_records = []
    for component in history_components:
        period = component["period"]
        if period not in period_map:
            period_counter += 1
            period_map[period] = period_counter
        component["period_counter"] = period_map[period]

        final_records.append([
            component["code"],
            0 if component["status"] in {status.value for status in ApprovedStatus} else 2,
            1 if (component["status"] in {status.value for status in FailedStatus} and (current_period - component["period_counter"] <= 1)) else 0,
            prerequisite_count.get(component["code"], 0),
            2 if offered_components.get(component["code"], 0) == 2 else 1,
            (current_period - int(subject_period_map.get(component["code"], 0))) if component["status"] in {status.value for status in FailedStatus} else 0
        ])

    final_records += [
        [
            component["code"],
            1,
            0,
            prerequisite_count.get(component["code"], 0),
            2 if offered_components.get(component["code"], 0) == 2 else 1,
            current_period - int(subject_period_map.get(component["code"], 0))
        ]
        for component in pending_components
    ]

    final_records = [list(filter(lambda x: x is not None, record)) for record in final_records]

    final_records.sort(key=lambda x: x[1])

    with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(final_records)