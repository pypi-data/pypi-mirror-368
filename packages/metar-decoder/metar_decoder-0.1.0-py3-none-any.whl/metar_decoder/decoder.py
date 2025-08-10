import re
import math
from datetime import datetime, UTC
from collections import OrderedDict
from typing import Any, Dict, List, Optional

from metar_decoder.regex_patterns import METAR_REGEX
from metar_decoder.weather_utils import *
from metar_decoder.datatypes import Temperature, Precipitation, Pressure, Wind
from metar_decoder.utils import (
    clean_metar_string, corregir_partes_metar, extraer_temperaturas_extremas
)

class MetarDecoder:
    def __init__(self, metar_string: str):
        self.metar = metar_string
        self.fields = OrderedDict()
        self._init_schema()
        self.parse()
    
    # inicialización del esquema
    def _init_schema(self):
        self.fields["metar"] = {"raw": None}
        self.fields["station"] = {"icao": None}
        self.fields["time"] = {"datetime_utc": None}
        self.fields["wind"] = {
            "raw": None,
            "direction_deg": None,
            "speed": None,
            "gust": None,
            "units": None,
            "variable": False,
            "varying_from_deg": None,
            "varying_to_deg": None,
            "description": None,
        }
        self.fields["visibility"] = {
            "raw": None,
            "meters": None,
            "miles": None,
            "direction": None,
            "cavok": False,
            "description": None,
        }
        self.fields["temperature"] = {
            "air": None,
            "dew_point": None,
            "max_24h_c": None,
            "min_24h_c": None,
            "extremos": {},
        }
        self.fields["pressure"] = {
            "raw": None,
            "qnh_hpa": None,
            "altimeter_inhg": None,
        }
        self.fields["precipitation"] = {
            "raw": None,
            "std": None,
            "mm_custom": None,
            "traza": False,
            "noche": False,
            "description": None,
        }
        self.fields["clouds"] = {
            "condition": None,
            "layers": [],
            "ceiling_ft": None,
            "summary": None,
        }
        self.fields["weather"] = {
            "present": [],
            "present_desc": [],
            "summary": None,
        }
        self.fields["derived"] = {"humidity_rel_percent": None}

    def parse(self):
        # Limpiar y corregir entrada antes de procesar
        self.metar = clean_metar_string(self.metar)
        self.metar = corregir_partes_metar(self.metar)
        self.fields["metar"]["raw"] = self.metar

        # Estación
        if match := METAR_REGEX["station"].search(self.metar):
            self.fields["station"]["icao"] = match.group("station")

        # Fecha y hora UTC
        if match := METAR_REGEX["datetime"].search(self.metar):
            dt_raw = match.group("datetime")
            day, hour, minute = int(dt_raw[:2]), int(dt_raw[2:4]), int(dt_raw[4:6])
            today = datetime.now(UTC)
            try:
                obs_time = today.replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
            except ValueError:
                obs_time = None
            self.fields["time"]["datetime_utc"] = obs_time

        # Viento (usando clase Wind)
        if match := re.search(r"\b(?P<wind>(\d{3}|VRB)\d{2,3}(G\d{2,3})?(KT|MPS))\b", self.metar):
            wind_str = match.group("wind")
            wind = Wind(wind_str)
            self.fields["wind"].update({
                "raw": wind_str,
                "direction_deg": wind.direction_degrees,
                "speed": wind.speed,
                "gust": wind.gust,
                "units": wind.units,
                "variable": wind.variable,
                "description": str(wind),
            })

        # Dirección variable (ej: 320V040)
        if match := re.search(r"\b(?P<from>\d{3})V(?P<to>\d{3})\b", self.metar):
            self.fields["wind"]["varying_from_deg"] = int(match.group("from"))
            self.fields["wind"]["varying_to_deg"] = int(match.group("to"))

        # Visibilidad
        if "CAVOK" in self.metar:
            self.fields["visibility"].update({
                "raw": "CAVOK",
                "meters": 10000,
                "cavok": True,
                "description": "10 km o más (CAVOK)",
            })
        elif match := re.search(r"\b(?P<vis_m>\d{4})(?P<dir>[NSEW]{1,2})?\b", self.metar):
            vis_m = int(match.group("vis_m"))
            dir_ = match.group("dir")
            desc = "10 km o más" if vis_m >= 9999 else ("menos de 50 m" if vis_m == 0 else f"{vis_m} m")
            if dir_:
                desc += f" hacia {dir_}"
            self.fields["visibility"].update({
                "raw": match.group(0),
                "meters": vis_m,
                "direction": dir_,
                "description": desc,
            })
        elif match := re.search(r"\b(?P<whole>\d{1,2})(?: (?P<num>\d)/(?P<den>\d))?SM\b", self.metar):
            whole = int(match.group("whole"))
            num = int(match.group("num")) if match.group("num") else 0
            den = int(match.group("den")) if match.group("den") else 1
            miles = whole + (num / den if den else 0)
            meters = round(miles * 1609.344)
            self.fields["visibility"].update({
                "raw": match.group(0),
                "meters": meters,
                "miles": miles,
                "description": f"{miles:.2f} millas (≈ {meters} m)",
            })

        # Temperatura y punto de rocío
        if match := METAR_REGEX["temp_dew"].search(self.metar):
            t = Temperature(match.group("temp"))
            d = Temperature(match.group("dew"))
            self.fields["temperature"].update({"air": t, "dew_point": d})

        # Presión (Q y A)
        if match := METAR_REGEX["altimeter_q"].search(self.metar):
            p = Pressure(value=match.group("alt_q"), unit="Q")
            self.fields["pressure"].update({
                "raw": match.group(0),
                "qnh_hpa": p.hPa,
                "altimeter_inhg": p.inHg,
            })
        elif match := METAR_REGEX["altimeter_a"].search(self.metar):
            p = Pressure(value=match.group("alt_a"), unit="A")
            self.fields["pressure"].update({
                "raw": match.group(0),
                "qnh_hpa": p.hPa,
                "altimeter_inhg": p.inHg,
            })

        # Precipitación estándar
        if match := METAR_REGEX["precip"].search(self.metar):
            self.fields["precipitation"]["raw"] = match.group(0)
            self.fields["precipitation"]["std"] = Precipitation(match.group("precip"))

        # Temperatura extrema Tnnnnnnnn
        if match := METAR_REGEX["extreme_temps"].search(self.metar):
            tmax = int(match.group("tmax")) / 10
            tmin = int(match.group("tmin")) / 10
            if match.group("tmax_sign") == "1":
                tmax = -tmax
            if match.group("tmin_sign") == "1":
                tmin = -tmin
            self.fields["temperature"]["max_24h_c"] = round(tmax, 1)
            self.fields["temperature"]["min_24h_c"] = round(tmin, 1)

        # --- Extras personalizados ---

        # Precipitación PP
        if match := METAR_REGEX["pp_custom"].search(self.metar):
            val = match.group(1).upper()
            if val == "TRZ":
                self.fields["precipitation"]["mm_custom"] = 0.0
                self.fields["precipitation"]["traza"] = True
                self.fields["precipitation"]["description"] = "traza (<0.1 mm)"
            else:
                self.fields["precipitation"]["mm_custom"] = float(val) if "." in val else int(val) / 10
        if "NOCHE" in self.metar.upper():
            self.fields["precipitation"]["noche"] = True

        # Temperatura máxima TX
        extremos_extra = extraer_temperaturas_extremas(self.metar)
        if extremos_extra:
            self.fields["temperature"]["extremos"] = extremos_extra
            # Mantener si vienen como 'tx_c'/'tn_c' u otros
            if "tx_c" in extremos_extra:
                self.fields["temperature"]["max_24h_c"] = extremos_extra.get("tx_c")
            if "tn_c" in extremos_extra:
                self.fields["temperature"]["min_24h_c"] = extremos_extra.get("tn_c")

        # Humedad relativa
        t = self.fields["temperature"].get("air")
        d = self.fields["temperature"].get("dew_point")
        if t and d:
            self.fields["derived"]["humidity_rel_percent"] = self._calc_rh(t.celsius, d.celsius)

        # Nubes
        upper_metar = self.metar.upper()

        special_cloud_conditions = {
            "NSC": "No hay nubes significativas",
            "NCD": "No se detectaron nubes",
            "SKC": "Cielo despejado (manual)",
            "CLR": "Cielo despejado (automático)",
        }

        # Si es CAVOK, reflejarlo también en clouds y saltar capas
        if "CAVOK" in upper_metar:
            self.fields["clouds"].update({
                "condition": "CAVOK (visibilidad y cielo OK)",
                "layers": [],
                "ceiling_ft": None,
                "summary": None,
            })
            cloud_matches = []  # fuerza a NO procesar capas
        else:
            found_special = False
            for token, label in special_cloud_conditions.items():
                if re.search(rf"\b{token}\b", upper_metar):
                    self.fields["clouds"].update({
                        "condition": label,
                        "layers": [],
                        "ceiling_ft": None,
                        "summary": None,
                    })
                    found_special = True
                    break
            if found_special:
                cloud_matches = []  # fuerza a NO procesar capas
            else:
                cloud_matches = METAR_REGEX["cloud"].findall(self.metar)

        # Procesar capas si hay
        layers: List[Dict[str, Any]] = []
        for cover, height, cloud_type in cloud_matches:
            height_ft: Optional[int]
            if height and height.isdigit():
                height_ft = int(height) * 100
            elif height == "///":
                height_ft = None
            else:
                height_ft = None

            cov_desc_map = {
                "FEW": "pocas nubes",
                "SCT": "nubes dispersas",
                "BKN": "nubes fragmentadas",
                "OVC": "cubierto",
                "VV": "visibilidad vertical",
            }
            cov_desc = cov_desc_map.get(cover, cover)
            desc = f"{cov_desc} a {height_ft} ft" if height_ft else f"{cov_desc} (altura desconocida)"
            if cloud_type == "CB":
                desc += " con cumulonimbos"
            elif cloud_type == "TCU":
                desc += " con cúmulos en torre"

            layers.append({
                "cover": cover,
                "height_ft": height_ft,
                "type": cloud_type or None,
                "description": desc,
            })

        if layers:
            self.fields["clouds"]["layers"] = layers
            ceiling_layer = next((l for l in layers if l["cover"] in ("BKN", "OVC") and l["height_ft"]), None)
            if ceiling_layer:
                self.fields["clouds"]["ceiling_ft"] = ceiling_layer["height_ft"]
            self.fields["clouds"]["summary"] = "; ".join(l["description"] for l in layers)
        
        # Tiempo presente (múltiples fenómenos)
        weather_groups = METAR_REGEX["weather_multi"].findall(self.metar)
        if weather_groups:
            for group in weather_groups:
                grp = group.strip()
                match = METAR_REGEX["weather"].match(grp)
                if not match:
                    continue
                code = {
                    "intensity": (match.group("intensity") or ""),
                    "descriptor": (match.group("descriptor") or ""),
                    "phenomena": (match.group("phenomena") or ""),
                }
                readable_parts: List[str] = []
                if code["descriptor"] in WEATHER_DESCRIPTOR:
                    readable_parts.append(WEATHER_DESCRIPTOR[code["descriptor"]])
                if code["phenomena"] in WEATHER_TYPES:
                    readable_parts.append(WEATHER_TYPES[code["phenomena"]])
                if code["intensity"] in WEATHER_INTENSITY:
                    readable_parts.append(WEATHER_INTENSITY[code["intensity"]])

                self.fields["weather"]["present"].append(code)
                self.fields["weather"]["present_desc"].append(" ".join(readable_parts))
            self.fields["weather"]["summary"] = ", ".join(self.fields["weather"]["present_desc"]) or None

    def _calc_rh(self, t_c: float, td_c: float) -> float:
        es_td = 6.11 * math.exp(17.625 * td_c / (243.04 + td_c))
        es_t = 6.11 * math.exp(17.625 * t_c / (243.04 + t_c))
        return round((es_td / es_t) * 100, 1)

    def to_dict(self) -> Dict[str, Any]:
        """Retorna el diccionario *ordenado* (agrupado por secciones)."""
        return self.fields

    def to_flat_dict(self) -> Dict[str, Any]:
        """
        Retorna un diccionario plano para retrocompatibilidad con código existente.
        Las claves nuevas mantienen nomenclatura consistente.
        """
        flat: Dict[str, Any] = {
            # Meta
            "raw_metar": self.fields["metar"]["raw"],
            # Station & time
            "station": self.fields["station"]["icao"],
            "datetime_utc": self.fields["time"]["datetime_utc"],
        }
        # Wind
        w = self.fields["wind"]
        flat.update({
            "wind": w["raw"],
            "wind_dir_degrees": w["direction_deg"],
            "wind_speed": w["speed"],
            "wind_units": w["units"],
            "wind_gust": w["gust"],
            "wind_is_variable": w["variable"],
            "wind_var_from": w["varying_from_deg"],
            "wind_var_to": w["varying_to_deg"],
            "wind_desc": w["description"],
        })
        # Visibility
        v = self.fields["visibility"]
        flat.update({
            "visibility_m": v["meters"],
            "visibility_sm": v["miles"],
            "visibility_direction": v["direction"],
            "visibility_cavok": v["cavok"],
            "visibility_desc": v["description"],
        })
        # Temps
        temp = self.fields["temperature"]
        flat.update({
            "temperature": temp["air"],
            "dew_point": temp["dew_point"],
            "temp_max_24h_c": temp["max_24h_c"],
            "temp_min_24h_c": temp["min_24h_c"],
        })
        # Pressure
        pr = self.fields["pressure"]
        flat.update({
            "pressure_hpa": pr["qnh_hpa"],
            "pressure_inHg": pr["altimeter_inhg"],
        })
        # Precip
        pp = self.fields["precipitation"]
        flat.update({
            "precipitation": pp["std"],
            "precip_mm_custom": pp["mm_custom"],
            "precip_traza": pp["traza"],
            "precip_noche": pp["noche"],
            "precip_desc": pp["description"],
        })
        # Clouds
        cl = self.fields["clouds"]
        flat.update({
            "cloud_layers": cl["layers"],
            "cloud_summary": cl["summary"],
            "cloud_condition": cl["condition"],
            "ceiling_ft": cl["ceiling_ft"],
        })
        # Weather present
        wx = self.fields["weather"]
        flat.update({
            "present_weather": wx["present"],
            "present_weather_desc": wx["present_desc"],
            "present_weather_summary": wx["summary"],
        })
        # Derived
        flat.update(self.fields["derived"])  # humidity_rel_percent
        return flat

    def __repr__(self):
        st = self.fields["station"]["icao"]
        dt = self.fields["time"]["datetime_utc"]
        return f"<MetarDecoder {st} at {dt}>"