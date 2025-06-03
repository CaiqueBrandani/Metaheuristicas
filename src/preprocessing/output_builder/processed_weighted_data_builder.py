import csv

WEIGHTS = {
    "prerequisite": 5,
    "status": 4,
    "type": 3,
    "distance": 2,
    "recent_failure": 1,
}

def build_processed_weighted_data(weighted_matrix_file, output_file):
    weighted_matrix = []

    # Carregar matriz de pesos
    with open(weighted_matrix_file, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            code = row[0]
            values = {
                "prerequisite": float(row[3]),
                "status": float(row[1]),
                "type": float(row[2]),
                "distance": float(row[4]),
                "recent_failure": float(row[5]),
            }
            weighted_matrix.append((code, values))

    results = []
    for code, values in weighted_matrix:
        # Calcular média ponderada
        weighted_sum = sum(values[key] * WEIGHTS[key] for key in WEIGHTS)
        total_weight = sum(WEIGHTS.values())
        weighted_average = weighted_sum / total_weight
        results.append([code, round(weighted_average, 4)])

    # Escrever os resultados no arquivo de saída
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(results)