# Diccionario de fenómenos meteorológicos
WEATHER_INTENSITY = {
    "+": "fuerte",
    "-": "ligero",
    "VC": "en cercanías"
}

WEATHER_DESCRIPTOR = {
    "MI": "poco profundo", "PR": "parcial", "BC": "bancos", "DR": "baja deriva",
    "BL": "levantado", "SH": "chubascos", "TS": "tormenta", "FZ": "congelante"
}

WEATHER_TYPES = {
    "DZ": "llovizna", "RA": "lluvia", "SN": "nieve", "SG": "gránulos de nieve",
    "IC": "cristales de hielo", "PL": "granizo pequeño", "GR": "granizo",
    "GS": "granizo pequeño o nieve granulada", "UP": "precipitación desconocida",
    "BR": "neblina", "FG": "niebla", "FU": "humo", "VA": "ceniza volcánica",
    "DU": "polvo", "SA": "arena", "HZ": "calina", "PY": "rocío",
    "PO": "remolinos", "SQ": "ráfagas", "FC": "torbellino / tornado",
    "SS": "tormenta de arena", "DS": "tormenta de polvo"
}

WEATHER_PHENOMENA = {
    # Precipitación
    "DZ": "llovizna",
    "RA": "lluvia",
    "SN": "nieve",
    "SG": "gránulos de nieve",
    "IC": "cristales de hielo (diamond dust)",
    "PL": "granizo pequeño (pellets de hielo)",
    "GR": "granizo grande",
    "GS": "granizo pequeño o nieve granulada",
    "UP": "precipitación desconocida",  # solo estaciones automáticas

    # Obscuración (hidrometeoros)
    "FG": "niebla",                     # vis < 1000 m
    "BR": "neblina",                    # vis 1000–5000 m
    "BCFG": "bancos de niebla",         # codificado como BC + FG

    # Obscuración (litometeoros)
    "FU": "humo",
    "VA": "ceniza volcánica",
    "DU": "polvo",
    "SA": "arena",
    "HZ": "calina",
    "PY": "rocío",                      # spray

    # Otros fenómenos
    "PO": "remolinos de polvo (dust devil)",
    "SQ": "ráfaga de viento (squall)",
    "FC": "torbellino / tornado / tromba marina",
    "SS": "tormenta de arena",
    "DS": "tormenta de polvo"
}

def describe_weather(code_dict):
    desc = []
    if code_dict["intensity"] == "+":
        desc.append("fuerte")
    elif code_dict["intensity"] == "-":
        desc.append("ligero")
    elif code_dict["intensity"] == "VC":
        desc.append("cercano")

    if code_dict["descriptor"]:
        desc.append(code_dict["descriptor"])

    if code_dict["phenomena"]:
        phenomena = code_dict["phenomena"]
        readable = WEATHER_PHENOMENA.get(phenomena, phenomena)
        desc.append(readable)

    return " ".join(desc)