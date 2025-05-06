import csv

# Pesos para solução inicial
PESOS = {
    "status_2": 2,
    "status_1": 4,
    "status_0": -50, # Penalizando as matérias ja cumpridas
    "reprovado": 2,
    "pre_req": 5,
    "dist_periodo": 1
}

def calculate_score(status, reprovado, pre_requisitos, distancia):
    if status == 2:
        base = PESOS["status_2"]
    elif status == 1:
        base = PESOS["status_1"]
    else:
        base = PESOS["status_0"]

    return (
        base
        - PESOS["reprovado"] * reprovado
        - PESOS["pre_req"] * pre_requisitos
        - PESOS["dist_periodo"] * abs(distancia)
    )

def load_disciplines(caminho_csv):
    disciplinas = []
    with open(caminho_csv, newline='') as csvfile:
        leitor = csv.reader(csvfile)
        for linha in leitor:
            codigo = linha[0]
            dados = list(map(int, linha[1:]))  # aprovado, reprovado, pré-req, distância
            disciplinas.append((codigo, dados))
    return disciplinas


def constructive_heuristic(caminho_csv, top_n=5):
    #Lista (Código, pontuação)
    disciplinas = load_disciplines(caminho_csv)

    # Retorna as top_n disciplinas com base no calculo da FO
    disciplinas.sort(key=lambda x: x[1], reverse=True)
    return [codigo for codigo, _ in disciplinas[:top_n]]
