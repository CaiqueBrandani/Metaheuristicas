import csv

class ProcessedWeightedDataBuilder:
    WEIGHTS = {
        "prerequisite": 5,
        "status": 4,
        "type": 3,
        "distance": 2,
        "recent_failure": 1,
    }

    def __init__(self, offer_file):
        self.offer_file = offer_file

    def calculate_subject_weight(self, status, prerequisite, recent_failure, distance, subject_type):
        return (
            self.WEIGHTS["prerequisite"] * prerequisite +
            self.WEIGHTS["status"] * status +
            self.WEIGHTS["type"] * subject_type +
            self.WEIGHTS["distance"] * distance +
            self.WEIGHTS["recent_failure"] * recent_failure
        )

    @staticmethod
    def round_to_one_decimal_place(value):
        return round(value, 1)

    def load_offered_components(self):
        offered_components = set()
        with open(self.offer_file, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[2] != "--":
                    offered_components.add(row[1])
        return offered_components

    def process_subjects(self, input_file, output_file):
        offered_components = self.load_offered_components()
        results = []

        with open(input_file, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                code = row[0]
                if code not in offered_components:
                    continue

                status = float(row[1])
                prerequisite = float(row[2])
                subject_type = float(row[3])
                distance = float(row[4])
                recent_failure = 1.0 if distance >= -0.5 else 0.0

                weight = self.calculate_subject_weight(status, prerequisite, recent_failure, distance, subject_type)
                rounded_weight = self.round_to_one_decimal_place(weight)
                results.append([code, rounded_weight])

        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(results)