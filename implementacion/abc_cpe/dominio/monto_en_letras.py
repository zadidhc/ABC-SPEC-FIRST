"""Conversión de importes monetarios a su representación textual para la Leyenda 1000 de SUNAT."""

from decimal import Decimal, ROUND_HALF_UP
from abc_cpe.dominio.catalogos import Moneda


UNIDADES = {
    0: "",
    1: "UN",
    2: "DOS",
    3: "TRES",
    4: "CUATRO",
    5: "CINCO",
    6: "SEIS",
    7: "SIETE",
    8: "OCHO",
    9: "NUEVE",
    10: "DIEZ",
    11: "ONCE",
    12: "DOCE",
    13: "TRECE",
    14: "CATORCE",
    15: "QUINCE",
    16: "DIECISEIS",
    17: "DIECISIETE",
    18: "DIECIOCHO",
    19: "DIECINUEVE",
    20: "VEINTE",
    21: "VEINTIUN",
    22: "VEINTIDOS",
    23: "VEINTITRES",
    24: "VEINTICUATRO",
    25: "VEINTICINCO",
    26: "VEINTISEIS",
    27: "VEINTISIETE",
    28: "VEINTIOCHO",
    29: "VEINTINUEVE",
}

DECENAS = {
    30: "TREINTA",
    40: "CUARENTA",
    50: "CINCUENTA",
    60: "SESENTA",
    70: "SETENTA",
    80: "OCHENTA",
    90: "NOVENTA",
}

CENTENAS = {
    100: "CIENTO",
    200: "DOSCIENTOS",
    300: "TRESCIENTOS",
    400: "CUATROCIENTOS",
    500: "QUINIENTOS",
    600: "SEISCIENTOS",
    700: "SETECIENTOS",
    800: "OCHOCIENTOS",
    900: "NOVECIENTOS",
}


def _centenas_a_letras(n: int) -> str:
    """Convierte un entero entre 0 y 999 a texto en español."""
    if n == 0:
        return ""
    if n == 100:
        return "CIEN"
    
    partes = []
    c = (n // 100) * 100
    r = n % 100

    if c > 0:
        partes.append(CENTENAS[c])

    if r > 0:
        if r in UNIDADES:
            partes.append(UNIDADES[r])
        else:
            d = (r // 10) * 10
            u = r % 10
            if u == 0:
                partes.append(DECENAS[d])
            else:
                partes.append(f"{DECENAS[d]} Y {UNIDADES[u]}")

    return " ".join(partes)


def numero_a_palabras(n: int) -> str:
    """Convierte un número entero positivo hasta millones a palabras en mayúsculas."""
    if n == 0:
        return "CERO"

    partes = []

    millones = n // 1_000_000
    resto_millones = n % 1_000_000

    if millones == 1:
        partes.append("UN MILLON")
    elif millones > 1:
        partes.append(f"{_centenas_a_letras(millones)} MILLONES")

    miles = resto_millones // 1_000
    unidades = resto_millones % 1_000

    if miles == 1:
        partes.append("MIL")
    elif miles > 1:
        partes.append(f"{_centenas_a_letras(miles)} MIL")

    if unidades > 0:
        partes.append(_centenas_a_letras(unidades))

    return " ".join(p for p in partes if p)


def monto_en_letras(monto: Decimal, moneda: Moneda = Moneda.PEN) -> str:
    """
    Genera el texto legal de la Leyenda 1000 (Monto en palabras).
    Ejemplo: 'SON: CIENTO DIECIOCHO CON 00/100 SOLES'
    """
    monto_redondeado = monto.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    entero = int(monto_redondeado)
    centavos = int((monto_redondeado - Decimal(entero)) * 100)

    texto_entero = numero_a_palabras(entero)
    nombre_moneda = "SOLES" if moneda == Moneda.PEN else "DOLARES AMERICANOS"

    return f"SON: {texto_entero} CON {centavos:02d}/100 {nombre_moneda}"

