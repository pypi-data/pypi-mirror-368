# 🌦️ METAR Decoder

Decodificador de mensajes **METAR** (Meteorological Aerodrome Report) para
procesar, validar y estructurar observaciones meteorológicas aeronáutica

> Proyecto desarrollado para SENAMHI. Compatible con variantes comunes del
formato METAR y con elementos no estándar frecuentes en Latinoamérica.

## 📋 Características

- **Decodificación completa** de los campos principales (estación, fecha/hora,
  viento, visibilidad, nubes, temperatura/rocío, presión, fenómenos, tendencias, etc.).
- **Tolerante a errores**: intenta corregir inconsistencias comunes.
- **Salida estructurada** mediante tipos de datos (`Temperature`, `Wind`,
  `Pressure`, etc.).
- **Salida plana** mediante `to_flat_dict()` con valores simples y listas/diccionarios.
- **CLI incluida** para decodificar desde la terminal.
- **Ejemplos y pruebas** incluidos.

## 🚀 Instalación

### Opción 1: Instalación en modo desarrollo 
```bash
# Clonar o descargar el proyecto
git clone https://github.com/CADV92/metar_decoder.git
cd metar_decoder

# Instalar en modo desarrollo (cambios se reflejan automáticamente)
pip install -e .
```

### Opción 2: Instalación estándar
```bash
cd metar_decoder
pip install .
```

### Verificar instalación
```bash
python -c "from metar_decoder import MetarDecoder; print('✅ Instalación exitosa')"
```

## 💡 Uso Básico

```python
from metar_decoder.decoder import MetarDecoder

# Ejemplo básico
metar = "METAR SPIM 061800Z 26008KT 9999 FEW020 SCT100 25/21 Q1013 RMK"
decoder = MetarDecoder(metar)

# Diccionario estructurado
data = decoder.to_dict()

# Diccionario plano (valores simples)
flat = decoder.to_flat_dict()

# Acceder a los datos decodificados
print(flat["station"])                      # 'SPIM'
print(flat["wind_speed"])                   # 8
print(flat["temperature"].celsius)          # 25
print(flat["visibility_desc"])              # "10 km o más"
```

## 🧰 CLI (línea de comandos)
```bash
# Decodificar un METAR directamente
python -m metar_decoder.cli "SPIM 061800Z 26008KT 9999 25/21 Q1013"

# Decodificar desde un archivo con un METAR por línea
python -m metar_decoder.cli --file metars.txt

# Ejecución directa
metar_decode "SPAY 241200Z 15005KT 2400 BR SCT008 BKN025 19/18 Q1016"
```

## 📊 Elementos Soportados

### Elementos Básicos
- ✅ **Identificador de estación** (ICAO de 4 letras)
- ✅ **Fecha y hora** (formato DDHHMMZ)
- ✅ **Viento** (dirección, velocidad, ráfagas, variable)
- ✅ **Visibilidad** (metros, millas estatutas, CAVOK)
- ✅ **Tiempo presente** (precipitación, obscuración, etc.)
- ✅ **Nubes** (cobertura, altura, tipo)
- ✅ **Temperatura y punto de rocío**
- ✅ **Presión atmosférica** (QNH/altímetro)

### Elementos Adicionales
- ✅ **Precipitación** (cantidad en las últimas horas)
- ✅ **Temperaturas extremas** (máxima/mínima 24h)
- ✅ **Dirección variable del viento**
- ✅ **Elementos personalizados** (PP, TX, TN)
- ✅ **Breve correción de errores en mensajes metar**

## 🔧 Estructura del Proyecto

```
metar_decoder/
├── metar_decoder/           # Paquete principal
│   ├── __init__.py          # Inicialización del paquete
│   ├── cli.py               # Modulo CLI
│   ├── decoder.py           # Clase principal MetarDecoder
│   ├── datatypes.py         # Clases para tipos de datos específicos
│   ├── regex_patterns.py    # Patrones de expresiones regulares
│   ├── weather_utils.py     # Utilidades para fenómenos meteorológicos
│   └── utils.py             # Funciones utilitarias y corrección de errores
├── tests/                   # Tests del paquete
│   ├── __init__.py
│   └── test_decoder.py      # Tests principales
├── examples/                # Ejemplos de uso
│   ├── __init__.py
│   └── example.py           # Ejemplos demostrativos
├── setup.py                 # Configuración de instalación
├── README.md                # Este archivo
└── LICENSE                  # Licencia del proyecto
```

## 📖 Ejemplos Detallados

### Ejemplo 1: METAR Básico
```python
from metar_decoder import MetarDecoder

metar = "METAR SPIM 061800Z 26008KT 9999 FEW020 25/21 Q1013"
flat = MetarDecoder(metar).to_flat_dict()

print(flat["station"])                 # SPIM
print(flat["datetime_utc"])            # 2023-12-06T18:00:00+00:00
print(flat["wind_desc"])               # 260° a 8 kt
print(flat["temperature"].celsius)     # 25
print(flat["dew_point"].celsius)       # 21
print(flat["pressure_hpa"])            # 1013
```

### Ejemplo 2: METAR con Fenómenos Meteorológicos
```python
metar = "METAR SPJC 121300Z 08012G18KT 2000 -RA BKN008 OVC015 18/17 Q1015"
flat = MetarDecoder(metar).to_flat_dict()

print(flat["wind_desc"])
print(flat["present_weather_desc"])
print(flat["cloud_summary"])
print(f"{flat['humidity_rel_percent']}%")
```

### Ejemplo 3: Acceso a Datos Específicos
```python
flat = MetarDecoder("SPIM 061800Z VRB05KT CAVOK 28/20 Q1018").to_flat_dict()

if flat.get("wind_is_variable"):
    print("Viento variable")
    print(f"{flat['wind_speed']} {flat['wind_units']}")

if flat.get("visibility_cavok"):
    print("Condiciones CAVOK")

spread = flat["temperature"].celsius - flat["dew_point"].celsius
print(f"Spread T-Td: {spread}°C")
```

## 🏗️ Clases de Datos

### Temperature
```python
temp = Temperature("25")     # Temperatura positiva
temp_neg = Temperature("M05") # Temperatura negativa (-5°C)
print(temp.celsius)          # 25
```

### Wind
```python
wind = Wind("26015G25KT")
print(wind.direction_degrees)  # 260
print(wind.speed)             # 15
print(wind.gust)              # 25
print(wind.units)             # KT
```

### Pressure
```python
pressure_hpa = Pressure("1013", "Q")  # hPa
pressure_inhg = Pressure("2992", "A") # inHg
print(pressure_hpa.hPa)               # 1013
print(pressure_hpa.inHg)              # 29.91
```

## 🔍 Corrección Automática de Errores

El sistema incluye corrección automática para errores comunes:

```python
# Corrige errores de tipeo comunes
metar_erroneo = "SPIM 061800Z VBR08KT CAVOK 25/21 Q1013"  # VBR -> VRB
decoder = MetarDecoder(metar_erroneo)
# Automáticamente corregido durante el procesamiento
```

## 🧪 Testing

Ejecutar las pruebas incluidas:

```bash
# Ejecutar todos los tests
cd metar_decoder
python tests/test_decoder.py

# O usando pytest (si está instalado)
pytest tests/

# Con cobertura (si tienes pytest-cov)
pytest tests/ --cov=metar_decoder
```

### Ejecutar ejemplos
```bash
# Ver ejemplos de uso completos
cd metar_decoder
python examples/example.py
```

### Tests disponibles
- **TestMetarDecoder**: Pruebas de decodificación completa de METAR
- **TestDataTypes**: Pruebas de clases de tipos de datos (Temperature, Wind, Pressure)
- **TestErrorCorrection**: Pruebas de corrección automática de errores
- **TestExtremeCases**: Pruebas de casos límite y extremos

## 📝 Formato de Salida

El método `to_dict()` retorna un diccionario con todos los campos decodificados:

```python
{
    'raw_metar': 'SPIM 061800Z 26008KT 9999 25/21 Q1013',
    'station': 'SPIM',
    'datetime_utc': datetime.datetime(2023, 12, 6, 18, 0),
    'wind': <Wind object>,
    'wind_desc': '260° a 8 kt',
    'wind_dir_degrees': 260,
    'wind_speed': 8,
    'wind_units': 'KT',
    'visibility_m': 9999,
    'visibility_desc': '10 km o más',
    'temperature': <Temperature object>,
    'dew_point': <Temperature object>,
    'pressure': <Pressure object>,
    'humidity_rel_percent': 84.0,
    # ... más campos según contenido del METAR
}
```

## 🐛 Debugging y Logs

Para debugging, examina el METAR procesado:
```python
decoder = MetarDecoder(metar_string)
print(f"METAR original: {metar_string}")
print(f"METAR procesado: {decoder.fields['raw_metar']}")
print(f"Campos extraídos: {list(decoder.fields.keys())}")
```

## 🤝 Contribuciones

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Agrega nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crea un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🏢 Desarrollado para SENAMHI

Proyecto desarrollado para el Servicio Nacional de Meteorología e Hidrología del Perú (SENAMHI) para el procesamiento automatizado de datos meteorológicos aeronáuticos.

---

**Nota**: Este decodificador está diseñado para manejar variaciones específicas de METAR utilizadas en la región, incluyendo elementos no estándar y formatos personalizados.
