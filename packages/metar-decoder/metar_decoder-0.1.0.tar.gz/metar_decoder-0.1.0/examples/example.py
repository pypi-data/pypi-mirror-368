#!/usr/bin/env python3
"""
Ejemplos de uso del METAR Decoder

Este archivo demuestra diferentes formas de usar el decodificador
con varios tipos de mensajes METAR.
"""

from metar_decoder import MetarDecoder
import json

def _to_celsius(x):
    """Devuelve °C si es un objeto Temperature, o el valor si ya es numérico/str."""
    try:
        # objetos con atributo celsius
        return getattr(x, "celsius", x)
    except Exception:
        return x

def _print_header(title):
    print("=" * 72)
    print(title)
    print("=" * 72)

def _mostrar_resumen(flat):
    """Muestra un pequeño resumen a partir del diccionario plano."""
    campos = [
        ("Estación", "station"),
        ("Hora UTC", "datetime_utc"),
        ("Viento (desc)", "wind_desc"),
        ("Dir°", "wind_dir_degrees"),
        ("Vel (kt)", "wind_speed"),
        ("Ráfaga (kt)", "wind_gust"),
        ("Visibilidad (m)", "visibility_m"),
        ("Visibilidad", "visibility_desc"),
        ("CAVOK", "visibility_cavok"),
        ("Fenómenos", "present_weather_summary"),
        ("Nubes", "cloud_summary"),
        ("Techo (ft)", "ceiling_ft"),
        ("Temperatura (°C)", "temperature"),
        ("Punto de rocío (°C)", "dew_point"),
        ("QNH (hPa)", "pressure_hpa"),
        ("Humedad (%)", "humidity_rel_percent"),
    ]
    for etiqueta, clave in campos:
        if clave in flat and flat[clave] is not None:
            val = flat[clave]
            if clave in ("temperature", "dew_point"):
                val = _to_celsius(val)
            print(f"  {etiqueta}: {val}")

def ejemplo_basico():
    """Ejemplo básico de decodificación de METAR"""
    _print_header("EJEMPLO 1: METAR Básico")
    metar = "METAR SPJC 061800Z 26008KT 9999 FEW020 25/21 Q1013"
    print(f"METAR original: {metar}\n")
    decoder = MetarDecoder(metar)
    flat = decoder.to_flat_dict()
    print("Datos extraídos:")
    _mostrar_resumen(flat)
    print()

def ejemplo_tiempo_presente():
    """Ejemplo con fenómenos meteorológicos"""
    _print_header("EJEMPLO 2: METAR con Fenómenos Meteorológicos")
    metar = "METAR SPJC 121300Z 08012G18KT 2000 -RA BKN008 OVC015 18/17 Q1015"
    print(f"METAR original: {metar}\n")
    decoder = MetarDecoder(metar)
    flat = decoder.to_flat_dict()
    print("Datos extraídos:")
    _mostrar_resumen(flat)
    print()

def ejemplo_cavok():
    """Ejemplo con condiciones CAVOK"""
    _print_header("EJEMPLO 3: METAR con CAVOK")
    metar = "SPJC 061800Z VRB05KT CAVOK 28/20 Q1018"
    print(f"METAR original: {metar}\n")
    decoder = MetarDecoder(metar)
    flat = decoder.to_flat_dict()
    print("Datos extraídos:")
    _mostrar_resumen(flat)
    print()

def ejemplo_elementos_personalizados():
    """Ejemplo con elementos personalizados (TX, TN, PP)"""
    _print_header("EJEMPLO 4: METAR con Elementos Personalizados")
    metar = "SPJC 061800Z 26008KT 9999 25/21 Q1013 TX285 TN198 PP015"
    print(f"METAR original: {metar}\n")
    decoder = MetarDecoder(metar)
    flat = decoder.to_flat_dict()
    print("Datos extraídos:")
    _mostrar_resumen(flat)
    print()

def ejemplo_json_export():
    """Ejemplo exportando todos los datos a JSON"""
    _print_header("EJEMPLO 5: Exportar Datos a JSON")
    metar = "METAR SPJC 061800Z 26008G15KT 8000 FEW020 BKN080 25/21 Q1013"
    print(f"METAR original: {metar}\n")
    decoder = MetarDecoder(metar)
    flat = decoder.to_flat_dict()

    # Serializar a JSON manejando objetos no serializables (datetime, Temperature, etc.)
    def default(o):
        if hasattr(o, "isoformat"):
            return o.isoformat()
        if hasattr(o, "celsius"):
            return o.celsius
        return str(o)

    print("Datos en formato JSON:")
    print(json.dumps(flat, ensure_ascii=False, indent=2, default=default))
    print()

def main():
    """Ejecuta todos los ejemplos"""
    print("> EJEMPLOS DE USO - METAR DECODER\nDesarrollado para SENAMHI\n")
    ejemplo_basico()
    ejemplo_tiempo_presente()
    ejemplo_cavok()
    ejemplo_elementos_personalizados()
    ejemplo_json_export()
    print("=" * 72)
    print("> Ejemplos completados")
    print("=" * 72)

if __name__ == "__main__":
    main()
