from src.heuristics.constructives.constructive_greedy import calculate_score, load_disciplines

def refine_local(solucao_inicial, caminho_csv, max_saltos=5):
    todas_disciplinas = load_disciplines(caminho_csv)


    disciplinas_dict = {codigo: dados for codigo, dados in todas_disciplinas}

    melhor_solucao = solucao_inicial[:]
    melhor_pontuacao = sum(calculate_score(*disciplinas_dict[cod]) for cod in melhor_solucao)

    saltos = 0

    while saltos < max_saltos:
        melhorou = False
        for cod_fora in disciplinas_dict:
            if cod_fora in melhor_solucao:
                continue
            for i in range(len(melhor_solucao)):
                nova_solucao = melhor_solucao[:]
                nova_solucao[i] = cod_fora
                nova_pontuacao = sum(calculate_score(*disciplinas_dict[cod]) for cod in nova_solucao)
                if nova_pontuacao > melhor_pontuacao:
                    melhor_solucao = nova_solucao
                    melhor_pontuacao = nova_pontuacao
                    melhorou = True
                    break  # sai do loop interno
            if melhorou:
                break  # sai do loop externo
        if melhorou:
            saltos = 0  # reinicia os saltos se houve melhora
        else:
            saltos += 1  # incrementa os saltos sem melhora

    return melhor_solucao
