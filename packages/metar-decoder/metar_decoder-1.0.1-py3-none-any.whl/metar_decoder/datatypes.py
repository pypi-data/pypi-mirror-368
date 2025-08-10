class Temperature:
    def __init__(self, value: str):
        self.raw = value
        self.celsius = -int(value[1:]) if value.startswith('M') else int(value)
    
    @property
    def fahrenheit(self) -> float:
        return (self.celsius * 9/5) + 32

    def __repr__(self):
        return f"{self.celsius} °C"


class Precipitation:
    def __init__(self, value: str):
        self.raw = value
        self.inches = int(value) / 100
        self.mm = round(self.inches * 25.4, 2)

    def __repr__(self):
        return f"{self.mm} mm"


class Wind:
    def __init__(self, raw_string: str):
        import re
        match = re.match(r"(?P<dir>\d{3}|VRB)(?P<speed>\d{2,3})(G(?P<gust>\d{2,3}))?(KT|MPS)", raw_string)
        if not match:
            raise ValueError(f"Formato de viento inválido: {raw_string}")
        
        self.raw = raw_string
        self.dir = match.group("dir")
        self.speed = int(match.group("speed"))
        self.gust = int(match.group("gust")) if match.group("gust") else None
        self.units = "KT" if "KT" in raw_string else "MPS"
        self.variable = self.dir == "VRB"

    @property
    def direction_degrees(self):
        return None if self.variable else int(self.dir)

    def __repr__(self):
        gust_str = f" con ráfagas de {self.gust} {self.units.lower()}" if self.gust else ""
        return f"{'variable' if self.variable else self.dir + '°'} a {self.speed} {self.units.lower()}{gust_str}"


class Pressure:
    def __init__(self, value: str, unit: str):
        self.raw = value
        if unit == "Q":
            self.hPa = int(value)
            self.inHg = round(self.hPa / 33.8639, 2)
        elif unit == "A":
            self.inHg = int(value) / 100
            self.hPa = round(self.inHg * 33.8639, 1)
        else:
            raise ValueError("Unidad de presión desconocida")

    def __repr__(self):
        return f"{self.hPa} hPa / {self.inHg:.2f} inHg"