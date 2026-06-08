from typing import Tuple

def calcular_requerimientos(peso_kg, altura_cm, edad_anios, objetivo) -> Tuple[int,int,int,int]:
    try:
        peso = float(peso_kg)
        altura = float(altura_cm)
        if altura < 3.0:
            altura = altura * 100
        edad = int(edad_anios)
    except:
        return 2000, 130, 220, 65 

    tmb = (10 * peso) + (6.25 * altura) - (5 * edad) + 5
    calorias_mantenimiento = tmb * 1.375

    if objetivo and ("ganar" in objetivo.lower() or "muscular" in objetivo.lower()):
        calorias_objetivo = calorias_mantenimiento + 400
    elif objetivo and ("perder" in objetivo.lower() or "peso" in objetivo.lower()):
        calorias_objetivo = calorias_mantenimiento - 400
    else:
        calorias_objetivo = calorias_mantenimiento

    proteinas = int(peso * 2)
    grasas = int(peso * 1)
    calorias_restantes = calorias_objetivo - (proteinas * 4) - (grasas * 9)
    carbohidratos = int(calorias_restantes / 4)

    return int(calorias_objetivo), proteinas, carbohidratos, grasas
