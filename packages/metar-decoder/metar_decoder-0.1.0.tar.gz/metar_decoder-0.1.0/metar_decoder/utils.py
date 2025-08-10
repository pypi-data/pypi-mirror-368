import re
import difflib

def clean_metar_string(metar: str) -> str:
    """
    Limpia un METAR compuesto, devolviendo solo la parte principal.
    """
    parts = metar.strip().split()

    # Detecta inicio válido de METAR
    for i in range(len(parts)):
        if re.match(r"^[A-Z]{4}$", parts[i]) and i + 2 < len(parts):
            if re.match(r"^\d{6}Z$", parts[i + 1]) and re.match(r"^(VRB|\d{3})\d{2,3}(G\d{2,3})?(KT|MPS)$", parts[i + 2]):
                # Ahora busca dónde termina este METAR (antes del siguiente identificador de estación)
                for j in range(i + 3, len(parts)):
                    if re.match(r"^(METAR)?\s*[A-Z]{4}$", parts[j]):
                        return " ".join(parts[i:j])
                return " ".join(parts[i:])  # No se encontró otro METAR, usar hasta el final

    return metar

def corregir_cavok(part):
    part = part.strip()
    if len(part) in (4, 5):
        if difflib.SequenceMatcher(None, part.upper(), 'CAVOK').ratio() > 0.7:
            return 'CAVOK'
    return part

def corregir_nube(part):
    part = part.strip()
    nube_tipos = ['FEW', 'SCT', 'BKN', 'OVC', 'VV']
    if len(part) >= 6 and part[-3:].isdigit():
        base = part[:-3].upper()
        similitudes = {tipo: difflib.SequenceMatcher(None, base, tipo).ratio() for tipo in nube_tipos}
        mejor = max(similitudes, key=similitudes.get)
        if similitudes[mejor] > 0.7:
            return mejor + part[-3:]
    return part

def corregir_rmk(part):
    part = part.strip()
    if len(part) >= 3:
        if difflib.SequenceMatcher(None, part.upper(), 'RMK').ratio() > 0.6:
            return 'RMK'
    return part

def corregir_vrb(part):
    part = part.strip()
    variantes = ['VRB', 'VBR', 'VRRB', 'VVBR', 'VAR', 'VR']
    for variante in variantes:
        if difflib.SequenceMatcher(None, part.upper(), variante).ratio() > 0.7:
            return 'VRB'
    return part

def corregir_partes_metar(parts):
    """Corrige errores comunes en partes del METAR."""
    if isinstance(parts, str):
        parts = parts.strip().split()
    corregidos = []
    for part in parts:
        part = corregir_cavok(part)
        part = corregir_nube(part)
        part = corregir_rmk(part)
        part = corregir_vrb(part)
        corregidos.append(part)
    return " ".join(corregidos)

def extraer_temperaturas_extremas(metar: str):
    """Extrae temperaturas máximas/mínimas a partir de etiquetas comunes."""
    result = {}
    patrones = [
        (r'\b(?:TX|TMAX|T\.MAX|T\.X|TMX|MX)\s*[:=]?\s*(M?-?\d{1,2}(?:[.,]\d)?)\b', 'tmax_c_custom'),
        (r'\b(?:TN|TMIN|T\.MIN|T\.N|TMN|MN)\s*[:=]?\s*(M?-?\d{1,2}(?:[.,]\d)?)\b', 'tmin_c_custom')
    ]

    for pattern, key in patrones:
        match = re.search(pattern, metar, re.IGNORECASE)
        if match:
            raw = match.group(1).replace("M", "-").replace(",", ".")
            try:
                result[key] = float(raw)
            except ValueError:
                continue

    return result
