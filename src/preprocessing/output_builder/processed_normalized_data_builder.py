import csv

def load_offered_components(offer_file):
    offered_components = set()
    with open(offer_file, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if row[2] != "--":
                offered_components.add(row[1])
    return offered_components

def build_processed_normalized_data(input_file, output_file, offer_file):
    offered_components = load_offered_components(offer_file)
    data = []
    with open(input_file, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if int(row[1]) != 0 and row[0] in offered_components:
                data.append(row)

    num_indices = [3, 5]

    max_values = {}
    min_values = {}
    for idx in num_indices:
        vals = [float(row[idx]) for row in data]
        max_values[idx] = max(vals)
        min_values[idx] = min(vals)

    def normalize_value(value, idx):
        range_ = max_values[idx] - min_values[idx]
        if range_ == 0:
            return value
        return (value - min_values[idx]) / range_ if value >= 0 else (value - max_values[idx]) / range_

    normalized_data = []
    for row in data:
        normalized_row = row[:]
        for idx in num_indices:
            normalized_row[idx] = normalize_value(float(row[idx]), idx)
        normalized_data.append(normalized_row)

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(normalized_data)