import re

METAR_REGEX = {
    "station": re.compile(r"^(?P<station>[A-Z]{4})"),
    "datetime": re.compile(r"(?P<datetime>\d{6}Z)"),
    "wind": re.compile(
        r"\b(?P<dir>\d{3}|VRB)(?P<speed>\d{2,3})(G(?P<gust>\d{2,3}))?(?P<units>KT|MPS)\b"
    ),
    "wind_var": re.compile(
        r"\b(?P<from>\d{3})V(?P<to>\d{3})\b"
    ),
    # Visibilidad en metros
    "visibility_m": re.compile(r"\b(?P<vis_m>\d{4})(?P<dir>[A-Z]{1,2})?\b"),

    # Visibilidad en millas (SM) con fracción opcional
    "visibility_sm": re.compile(
        r"\b(?P<whole>\d{1,2})(?: (?P<num>\d)/(?P<den>\d))?SM\b"
    ),
    "temp_dew": re.compile(r"(?P<temp>M?\d{2})/(?P<dew>M?\d{2})"),
    "altimeter_q": re.compile(r"\bQ(?P<alt_q>\d{4})\b"),     # presión en hPa
    "altimeter_a": re.compile(r"\bA(?P<alt_a>\d{4})\b"),     # presión en inHg
    "precip": re.compile(r"\bP(?P<precip>\d{4})\b"),
    "extreme_temps": re.compile(r"T(?P<tmax_sign>[01])(?P<tmax>\d{3})(?P<tmin_sign>[01])(?P<tmin>\d{3})"),
    
    # Extras personalizados
    "pp_custom": re.compile(r'PP(\d+\.\d+|\d{3}|TRZ)', re.IGNORECASE),
    "tmax_custom": re.compile(r'TX\s*(\d{1,2}\.\d)'),
    "tmin_custom": re.compile(r'TN\s*(M)?\s*(\d{1,2}\.\d)'),
    "cloud": re.compile(
        r"\b(?P<cover>FEW|SCT|BKN|OVC|NSC|NCD|SKC|CLR|VV)"
        r"(?P<height>\d{3}|///)?"
        r"(?P<type>CB|TCU)?\b"
    ),
    # Captura un grupo individual de fenómeno con intensidad y descriptor
    "weather": re.compile(
        r"^(?P<intensity>\+|-|VC)?"
        r"(?P<descriptor>MI|PR|BC|DR|BL|SH|TS|FZ)?"
        r"(?P<phenomena>DZ|RA|SN|SG|IC|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|SS|DS)$"
    ),

    # Captura múltiples grupos meteorológicos del METAR
    "weather_multi": re.compile(
        r"(?:(?:\+|-|VC)?(?:MI|PR|BC|DR|BL|SH|TS|FZ)?"
        r"(?:DZ|RA|SN|SG|IC|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|SS|DS))"
    )
}
