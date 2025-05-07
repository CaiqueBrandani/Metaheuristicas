import csv

def normalize_preprocessed_input(input_file, output_file):
    data = []
    max_distancia = 0
    max_pre_requisito = 0

    with open(input_file, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            status = int(row[1])
            if status == 0:  # Ignorar matérias com status = 0
                continue

            distancia = int(row[5])
            pre_requisito = int(row[3])
            max_distancia = max(max_distancia, abs(distancia))
            max_pre_requisito = max(max_pre_requisito, pre_requisito)
            data.append(row)

    normalized_data = []
    for row in data:
        status = int(row[1])
        pre_requisito = int(row[3])
        tipo = int(row[4])
        distancia = int(row[5])

        status_normalizado = status / 2
        pre_requisito_normalizado = pre_requisito / max_pre_requisito if max_pre_requisito > 0 else 0
        tipo_normalizado = tipo / 2
        distancia_normalizada = distancia / max_distancia if max_distancia > 0 else 0

        normalized_data.append([
            row[0],
            status_normalizado,
            pre_requisito_normalizado,
            tipo_normalizado,
            distancia_normalizada
        ])

    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(normalized_data)