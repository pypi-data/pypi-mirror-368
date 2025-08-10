"""
METAR Decoder Package

Un decodificador completo de mensajes METAR (Meteorological Aerodrome Report) 
desarrollado para SENAMHI.

Uso básico:
    from metar_decoder import MetarDecoder

    flat = MetarDecoder("SPIM 061800Z 26008KT 9999 25/21 Q1013").to_flat_dict()
    print(flat["station"])                 # SPIM
    print(flat["temperature"].celsius)     # 25

Clases principales disponibles:
    - MetarDecoder: Clase principal para decodificar mensajes METAR
    - Temperature: Clase para manejar datos de temperatura
    - Wind: Clase para manejar datos de viento
    - Pressure: Clase para manejar datos de presión
    - Precipitation: Clase para manejar datos de precipitación
"""

from importlib.metadata import PackageNotFoundError, version, metadata

# Versión desde setuptools-scm (tags git). Fallback útil en editable installs.
try:
    __version__ = version("metar_decoder")
    _meta = metadata("metar_decoder")
except PackageNotFoundError:
    __version__ = "0.0.0"
    _meta = {}

__author__ = _meta.get("Author", "Christian Dávila")
__description__ = _meta.get("Summary", "Decodificador de mensajes METAR")

# Importaciones principales para facilitar el uso
from .decoder import MetarDecoder
from .datatypes import Temperature, Wind, Pressure, Precipitation

# Exportar también las clases de tipos de datos
__all__ = [
    'MetarDecoder',
    'Temperature',
    'Wind',
    'Pressure',
    'Precipitation',
    '__version__',
    '__author__',
    '__description__'
]
