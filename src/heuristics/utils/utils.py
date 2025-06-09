def split_blocos(bloco_str):
    """
    Divide blocos colados como '25N12' em ['2N1', '2N2', '5N1', '5N2'].
    """
    i = 0
    blocos = []
    while i < len(bloco_str):
        # Se for dois dias colados (ex: "25N12")
        if i+3 < len(bloco_str) and bloco_str[i].isdigit() and bloco_str[i+1].isdigit() and bloco_str[i+2] in "MTN":
            dias = [bloco_str[i], bloco_str[i+1]]
            turno = bloco_str[i+2]
            slots = ""
            j = i+3
            while j < len(bloco_str) and bloco_str[j].isdigit():
                slots += bloco_str[j]
                j += 1
            for dia in dias:
                for slot in slots:
                    blocos.append(f"{dia}{turno}{slot}")
            i = j
        # Se for padrão normal (ex: "2N12")
        elif i+2 < len(bloco_str) and bloco_str[i].isdigit() and bloco_str[i+1] in "MTN":
            dia = bloco_str[i]
            turno = bloco_str[i+1]
            slots = ""
            j = i+2
            while j < len(bloco_str) and bloco_str[j].isdigit():
                slots += bloco_str[j]
                j += 1
            for slot in slots:
                blocos.append(f"{dia}{turno}{slot}")
            i = j
        else:
            i += 1
    return blocos