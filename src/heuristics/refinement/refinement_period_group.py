from src.heuristics.constructives.constructive_greedy import load_disciplines


def refine_group_period(solucao_inicial, caminho_csv):
    todas_disciplinas = load_disciplines(caminho_csv)
    disciplinas_dict = {codigo: dados for codigo, dados in todas_disciplinas}

    nova_solucao = solucao_inicial[:]

    distancias = [disciplinas_dict[cod][3] for cod in nova_solucao]
    media = sum(distancias) / len(distancias)


    fora_da_solucao = [
        cod for cod in disciplinas_dict if cod not in nova_solucao
    ]
    fora_ordenado = sorted(fora_da_solucao, key=lambda cod: abs(disciplinas_dict[cod][3] - media))


    nova_solucao.sort(key=lambda cod: abs(disciplinas_dict[cod][3] - media), reverse=True)

    for i in range(len(nova_solucao)):
        substituto = fora_ordenado[i] if i < len(fora_ordenado) else None
        if substituto:
            nova_solucao[i] = substituto

    return nova_solucao
