#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI para METAR Decoder (versión sin emoji)
"""

import argparse
import sys
import json
import re
from datetime import datetime
from typing import Any, List, Optional, Dict

from metar_decoder import MetarDecoder
try:
    from metar_decoder.datatypes import Temperature, Wind, Pressure, Precipitation
except Exception:
    Temperature = Wind = Pressure = Precipitation = tuple()

from . import __version__

# ------------------------ Utilidades JSON ------------------------ #

def serialize_for_json(obj: Any) -> Any:
    if isinstance(obj, datetime) or getattr(obj, "isoformat", None) and not isinstance(obj, (str, bytes, bytearray)):
        try:
            return obj.isoformat()
        except Exception:
            pass
    if isinstance(obj, Temperature):
        return {"raw": getattr(obj, "raw", None),
                "celsius": getattr(obj, "celsius", None),
                "fahrenheit": getattr(obj, "fahrenheit", None)}
    if isinstance(obj, Pressure):
        return {"raw": getattr(obj, "raw", None),
                "hPa": getattr(obj, "hPa", getattr(obj, "qnh_hpa", None)),
                "inHg": getattr(obj, "inHg", getattr(obj, "altimeter_inhg", None))}
    if isinstance(obj, Wind):
        return {"raw": getattr(obj, "raw", None),
                "direction_deg": getattr(obj, "direction_degrees", getattr(obj, "direction_deg", None)),
                "speed": getattr(obj, "speed", None),
                "gust": getattr(obj, "gust", None),
                "units": getattr(obj, "units", None),
                "variable": getattr(obj, "variable", None),
                "description": str(obj)}
    if isinstance(obj, Precipitation):
        return {"raw": getattr(obj, "raw", None),
                "mm": getattr(obj, "mm", getattr(obj, "mm_custom", None)),
                "inches": getattr(obj, "inches", None)}
    if isinstance(obj, (list, tuple)):
        return [serialize_for_json(item) for item in obj]
    if isinstance(obj, dict):
        return {key: serialize_for_json(value) for key, value in obj.items()}
    if hasattr(obj, "__dict__"):
        return {k: serialize_for_json(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
    if obj is None or isinstance(obj, (int, float, str, bool)):
        return obj
    return str(obj)


def pick_json_payload(decoder: MetarDecoder, flat: bool) -> dict:
    if flat and hasattr(decoder, "to_flat_dict"):
        data = decoder.to_flat_dict()
    else:
        if hasattr(decoder, "to_dict"):
            data = decoder.to_dict()
        else:
            data = getattr(decoder, "fields", {})
    return serialize_for_json(data)


# ------------------------ Utilidades de formato texto ------------------------ #

def _get(d: Dict, path: str, default=None):
    cur = d
    for p in path.split("."):
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return default
    return cur

def _fmt_temp(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return f"{v:.0f} °C"
    # v es string u otro imprimible
    s = str(v).strip()
    # Si ya tiene °C, respeta
    if "°C" in s:
        return s
    # Normaliza casos tipo "22 C" -> "22 °C"
    if s.endswith(" C"):
        return s[:-2].strip() + " °C"
    # Extrae número si viene mezclado (e.g. "T=22")
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if m:
        return f"{m.group(0)} °C"
    # Fallback: deja el texto y añade °C una vez
    return s + " °C"


def format_text_output(decoder: MetarDecoder) -> str:
    if hasattr(decoder, "to_dict"):
        f = decoder.to_dict()
    else:
        f = getattr(decoder, "fields", {})

    out = []
    out.append(">>> DECODIFICACIÓN METAR")
    out.append("-" * 50)
    raw_metar = _get(f, "metar.raw", _get(f, "raw_metar", "N/A"))
    out.append(f"METAR: {raw_metar}")
    out.append("-" * 50)

    icao = _get(f, "station.icao")
    if icao:
        out.append(f"Estación: {icao}")

    dt = _get(f, "time.datetime_utc") or _get(f, "datetime_utc")
    if dt:
        out.append(f"Hora UTC: {dt}")

    wind_desc = _get(f, "wind.description") or _get(f, "wind_desc")
    if wind_desc:
        out.append(f"Viento: {wind_desc}")

    vis_desc = _get(f, "visibility.description") or _get(f, "visibility_desc")
    if vis_desc:
        out.append(f"Visibilidad: {vis_desc}")

    wx_summary = _get(f, "weather.summary") or _get(f, "present_weather_summary")
    if wx_summary:
        out.append(f"Tiempo presente: {wx_summary}")

    # Nubes
    print(_get(f, "clouds"))
    clouds_summary = _get(f, "clouds.summary") or _get(f, "cloud_summary")
    cloud_condition = _get(f, "clouds.condition") or _get(f, "cloud_condition")
    if clouds_summary:
        out.append(f"> Nubes: {clouds_summary}")
    elif cloud_condition:
        out.append(f"> Cielo: {cloud_condition}")

    # Temperaturas 
    t_air = _get(f, "temperature.air.celsius")
    if t_air is None:
        # Puede que venga como string o como dict plano
        t_air = _get(f, "temperature.air") or _get(f, "air")

    t_dew = _get(f, "temperature.dew_point.celsius")
    if t_dew is None:
        t_dew = _get(f, "temperature.dew_point") or _get(f, "dew_point")

    if t_air is not None:
        out.append(f"> Temperatura: {_fmt_temp(t_air)}")
    if t_dew is not None:
        out.append(f"> Punto de rocío: {_fmt_temp(t_dew)}")

    # Humedad Relativa
    rh = _get(f, "derived.humidity_rel_percent") or _get(f, "humidity_rel_percent")
    if rh is not None:
        try:
            out.append(f"> Humedad: {float(rh):.0f}%")
        except Exception:
            out.append(f"> Humedad: {rh}%")

    qnh = _get(f, "pressure.qnh_hpa") or _get(f, "pressure.hPa") or _get(f, "pressure")
    if isinstance(qnh, (int, float)):
        out.append(f"> Presión: {qnh} hPa")

    precip_desc = _get(f, "precipitation.description")
    precip_mm = _get(f, "precipitation.mm_custom") or _get(f, "precip_mm_custom")
    precip_traza = _get(f, "precipitation.traza") or _get(f, "precip_traza")
    if precip_desc:
        out.append(f"> Precipitación: {precip_desc}")
    elif precip_mm is not None:
        out.append(f"> Precipitación: {precip_mm} mm")

    tmax = (
        _get(f, "temperature.max_24h_c")
        or _get(f, "temperature.extremos.tmax_c_custom")
        or _get(f, "tmax_c_custom")
        or _get(f, "temp_max_24h_c")
    )
    tmin = (
        _get(f, "temperature.min_24h_c")
        or _get(f, "temperature.extremos.tmin_c_custom")
        or _get(f, "tmin_c_custom")
        or _get(f, "temp_min_24h_c")
    )
    if tmax is not None or tmin is not None:
        partes = []
        if tmax is not None:
            partes.append(f"Máx {tmax:.1f} °C" if isinstance(tmax, (int, float)) else f"Máx {tmax} °C")
        if tmin is not None:
            partes.append(f"Mín {tmin:.1f} °C" if isinstance(tmin, (int, float)) else f"Mín {tmin} °C")
        out.append("> Temp. Extremas: " + " / ".join(partes))

    return "\n".join(out)

def format_output(decoder: MetarDecoder, format_type: str = "text") -> str:
    if format_type == "json":
        data = pick_json_payload(decoder, flat=False)
        return json.dumps(serialize_for_json(data), indent=2, ensure_ascii=False)
    return format_text_output(decoder)

# Programa Principal
def main():
    print(f"metar_decoder {__version__}")
    parser = argparse.ArgumentParser(
        description="Decodificador de mensajes METAR (sin emoji)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ejemplos de uso:
  metar_decode "SPIM 061800Z 26008KT 9999 25/21 Q1013"
  metar_decode --file metars.txt --format json
  echo "SPIM 061800Z VRB05KT CAVOK 28/20 Q1018" | metar_decode --stdin
        '''
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("metar", nargs="?", help="Mensaje METAR a decodificar")
    input_group.add_argument("--file", "-f", help="Archivo con mensajes METAR (uno por línea)")
    input_group.add_argument("--stdin", action="store_true", help="Leer METAR desde stdin")

    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Formato de salida (default: text)",
    )
    parser.add_argument(
        "--flat",
        action="store_true",
        help="Con --format json, exporta el JSON plano (to_flat_dict) si está disponible",
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="Solo mostrar errores")
    parser.add_argument("--version", action="version", version="metar_decoder 0.1.0")

    args = parser.parse_args()

    try:
        metars: List[str] = []

        if args.metar:
            metars = [args.metar]
        elif args.file:
            try:
                with open(args.file, "r", encoding="utf-8") as f:
                    metars = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                print(f"Error: Archivo '{args.file}' no encontrado", file=sys.stderr)
                return 1
        elif args.stdin:
            metars = [line.strip() for line in sys.stdin if line.strip()]

        results = []
        errors = []

        for i, metar in enumerate(metars):
            try:
                decoder = MetarDecoder(metar)

                if args.format == "json":
                    payload = pick_json_payload(decoder, flat=args.flat and hasattr(decoder, "to_flat_dict"))
                    results.append(payload)
                else:
                    if not args.quiet and len(metars) > 1:
                        print(f"\n--- METAR {i+1} ---")
                    print(format_output(decoder, format_type="text"))

            except Exception as e:
                msg = f"Error procesando METAR '{metar}': {e}"
                errors.append(msg)
                if not args.quiet:
                    print(msg, file=sys.stderr)
                if len(metars) == 1:
                    return 1

        if args.format == "json":
            if len(results) == 1:
                print(json.dumps(serialize_for_json(results[0]), indent=2, ensure_ascii=False))
            else:
                print(json.dumps(serialize_for_json(results), indent=2, ensure_ascii=False))

        if errors and len(metars) > 1 and not args.quiet:
            print(
                f"\n  Procesados: {len(metars) - len(errors)}/{len(metars)}, Errores: {len(errors)}",
                file=sys.stderr,
            )

        return 0 if (len(metars) - len(errors)) > 0 else 1

    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error inesperado: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
