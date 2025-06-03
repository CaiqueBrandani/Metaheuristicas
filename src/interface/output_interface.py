OPTIONS_DICT = {
    "h": {
        "desc": "Heurística utilizada para seleção das disciplinas.",
        "options": {
            "greedy": "Heurística gulosa.",
            "random": "Heurística aleatória."
        }
    },
    "r": {
        "desc": "Tipo de refinamento aplicado após a heurística.",
        "options": {
            "none": "Sem refinamento.",
            "local": "Refinamento local.",
            "tabu": "Busca tabu."
        }
    },
    "c": {
        "desc": "Curso do histórico a ser processado (ex: CCO, SIN).",
        "options": {}
    },
    "i": {
        "desc": "Índice do histórico do aluno (ex: 1, 2, 3...).",
        "options": {}
    }
}

def print_result(title, selected, total_weight, exec_time):
    print(f"\n{title}:")
    print(f"Matérias escolhidas: {selected}")
    print(f"Peso total: {total_weight}")
    print(f"Tempo de execução: {exec_time:.4f} segundos")

def print_options_dict():
    print("\nParâmetros disponíveis:")
    for param, info in OPTIONS_DICT.items():
        print(f"\n--{param}: {info['desc']}")
        if info["options"]:
            print("  Opções:")
            for key, desc in info["options"].items():
                print(f"    {key}: {desc}")

def print_error(msg):
    print(f"\n[ERRO] {msg}")