#!/usr/bin/env python3
"""
Pruebas para el METAR Decoder
Se validan los campos expuestos por `to_flat_dict()`.
"""

import unittest
from metar_decoder import MetarDecoder
from metar_decoder.datatypes import Temperature, Pressure, Wind  # Wind/Pressure/Temperature smoke tests

class TestMetarDecoderFlat(unittest.TestCase):
    def test_basic_metar(self):
        metar = "METAR SPJC 061800Z 26008KT 9999 25/21 Q1013"
        dec = MetarDecoder(metar).to_flat_dict()
        self.assertEqual(dec["station"], "SPJC")
        self.assertEqual(dec["temperature"].celsius, 25)
        self.assertEqual(dec["dew_point"].celsius, 21)
        self.assertEqual(dec["wind_speed"], 8)
        self.assertEqual(dec["wind_dir_degrees"], 260)
        self.assertEqual(dec["pressure_hpa"], 1013)

    def test_wind_variable(self):
        metar = "SPJC 061800Z VRB05KT CAVOK 28/20 Q1018"
        dec = MetarDecoder(metar).to_flat_dict()
        self.assertTrue(dec["wind_is_variable"])
        self.assertEqual(dec["wind_speed"], 5)
        self.assertIsNone(dec["wind_dir_degrees"])

    def test_wind_gusts(self):
        metar = "SPJC 061800Z 26012G18KT 9999 25/21 Q1013"
        dec = MetarDecoder(metar).to_flat_dict()
        self.assertEqual(dec["wind_speed"], 12)
        self.assertEqual(dec["wind_gust"], 18)
        self.assertEqual(dec["wind_dir_degrees"], 260)

    def test_cavok_conditions(self):
        metar = "SPJC 061800Z 26008KT CAVOK 25/21 Q1013"
        dec = MetarDecoder(metar).to_flat_dict()
        self.assertTrue(dec.get("visibility_cavok", False))
        # El paquete marca CAVOK y puede dejar visibility_m None; validamos el flag y la descripción
        self.assertIn("CAVOK", dec.get("visibility_desc", ""))

    def test_negative_temperature(self):
        metar = "SPJC 061800Z 26008KT 9999 M05/M10 Q1013"
        dec = MetarDecoder(metar).to_flat_dict()
        self.assertEqual(dec["temperature"].celsius, -5)
        self.assertEqual(dec["dew_point"].celsius, -10)

    def test_cloud_layers(self):
        metar = "SPJC 061800Z 26008KT 9999 FEW020 BKN080 OVC120 25/21 Q1013"
        dec = MetarDecoder(metar).to_flat_dict()
        self.assertIn("cloud_layers", dec)
        self.assertEqual(len(dec["cloud_layers"]), 3)
        self.assertEqual(dec["cloud_layers"][0]["cover"], "FEW")
        self.assertEqual(dec["cloud_layers"][0]["height_ft"], 2000)
        self.assertEqual(dec["ceiling_ft"], 8000)  # primera BKN/OVC

    def test_present_weather(self):
        metar = "SPJC 061800Z 26008KT 2000 -RA FG BKN008 18/17 Q1015"
        dec = MetarDecoder(metar).to_flat_dict()
        self.assertIn("present_weather", dec)
        self.assertIn("present_weather_desc", dec)

    def test_humidity_calculation(self):
        metar = "SPJC 061800Z 26008KT 9999 25/21 Q1013"
        dec = MetarDecoder(metar).to_flat_dict()
        self.assertIn("humidity_rel_percent", dec)
        self.assertTrue(0 <= dec["humidity_rel_percent"] <= 100)

    def test_visibility_meters(self):
        metar = "SPJC 061800Z 26008KT 4000 25/21 Q1013"
        dec = MetarDecoder(metar).to_flat_dict()
        self.assertEqual(dec["visibility_m"], 4000)
        self.assertEqual(dec["visibility_desc"], "4000 m")

    def test_visibility_miles(self):
        metar = "KORD 061800Z 26008KT 10SM FEW250 25/21 A2992"
        dec = MetarDecoder(metar).to_flat_dict()
        self.assertIn("visibility_sm", dec)
        self.assertEqual(dec["visibility_sm"], 10.0)

class TestDataTypes(unittest.TestCase):
    def test_temperature_positive(self):
        temp = Temperature("25")
        self.assertEqual(temp.celsius, 25)
        self.assertEqual(str(temp), "25 °C")

    def test_temperature_negative(self):
        temp = Temperature("M05")
        self.assertEqual(temp.celsius, -5)
        self.assertEqual(str(temp), "-5 °C")

    def test_pressure_hpa(self):
        p = Pressure("1013", "Q")
        self.assertEqual(p.hPa, 1013)
        self.assertAlmostEqual(p.inHg, 29.9, places=1)

    def test_pressure_inhg(self):
        p = Pressure("2992", "A")
        self.assertEqual(p.inHg, 29.92)
        self.assertAlmostEqual(p.hPa, 1013.0, places=0)

# Nota: La clase Wind se usa indirectamente a través de to_flat_dict,
# y se valida en los casos de viento arriba.

if __name__ == "__main__":
    unittest.main(verbosity=2)
#!/usr/bin/env python3
"""
Pruebas para el METAR Decoder (ajustadas a la API actual).
Se validan los campos expuestos por `to_flat_dict()`.
"""

import unittest
from metar_decoder import MetarDecoder
from metar_decoder.datatypes import Temperature, Pressure, Wind  # Wind/Pressure/Temperature smoke tests

class TestMetarDecoderFlat(unittest.TestCase):
    def test_basic_metar(self):
        metar = "METAR SPJC 061800Z 26008KT 9999 25/21 Q1013"
        dec = MetarDecoder(metar).to_flat_dict()
        self.assertEqual(dec["station"], "SPJC")
        self.assertEqual(dec["temperature"].celsius, 25)
        self.assertEqual(dec["dew_point"].celsius, 21)
        self.assertEqual(dec["wind_speed"], 8)
        self.assertEqual(dec["wind_dir_degrees"], 260)
        self.assertEqual(dec["pressure_hpa"], 1013)

    def test_wind_variable(self):
        metar = "SPJC 061800Z VRB05KT CAVOK 28/20 Q1018"
        dec = MetarDecoder(metar).to_flat_dict()
        self.assertTrue(dec["wind_is_variable"])
        self.assertEqual(dec["wind_speed"], 5)
        self.assertIsNone(dec["wind_dir_degrees"])

    def test_wind_gusts(self):
        metar = "SPJC 061800Z 26012G18KT 9999 25/21 Q1013"
        dec = MetarDecoder(metar).to_flat_dict()
        self.assertEqual(dec["wind_speed"], 12)
        self.assertEqual(dec["wind_gust"], 18)
        self.assertEqual(dec["wind_dir_degrees"], 260)

    def test_cavok_conditions(self):
        metar = "SPJC 061800Z 26008KT CAVOK 25/21 Q1013"
        dec = MetarDecoder(metar).to_flat_dict()
        self.assertTrue(dec.get("visibility_cavok", False))
        # El paquete marca CAVOK y puede dejar visibility_m None; validamos el flag y la descripción
        self.assertIn("CAVOK", dec.get("visibility_desc", ""))

    def test_negative_temperature(self):
        metar = "SPJC 061800Z 26008KT 9999 M05/M10 Q1013"
        dec = MetarDecoder(metar).to_flat_dict()
        self.assertEqual(dec["temperature"].celsius, -5)
        self.assertEqual(dec["dew_point"].celsius, -10)

    def test_cloud_layers(self):
        metar = "SPJC 061800Z 26008KT 9999 FEW020 BKN080 OVC120 25/21 Q1013"
        dec = MetarDecoder(metar).to_flat_dict()
        self.assertIn("cloud_layers", dec)
        self.assertEqual(len(dec["cloud_layers"]), 3)
        self.assertEqual(dec["cloud_layers"][0]["cover"], "FEW")
        self.assertEqual(dec["cloud_layers"][0]["height_ft"], 2000)
        self.assertEqual(dec["ceiling_ft"], 8000)  # primera BKN/OVC

    def test_present_weather(self):
        metar = "SPJC 061800Z 26008KT 2000 -RA FG BKN008 18/17 Q1015"
        dec = MetarDecoder(metar).to_flat_dict()
        self.assertIn("present_weather", dec)
        self.assertIn("present_weather_desc", dec)

    def test_humidity_calculation(self):
        metar = "SPJC 061800Z 26008KT 9999 25/21 Q1013"
        dec = MetarDecoder(metar).to_flat_dict()
        self.assertIn("humidity_rel_percent", dec)
        self.assertTrue(0 <= dec["humidity_rel_percent"] <= 100)

    def test_visibility_meters(self):
        metar = "SPJC 061800Z 26008KT 4000 25/21 Q1013"
        dec = MetarDecoder(metar).to_flat_dict()
        self.assertEqual(dec["visibility_m"], 4000)
        self.assertEqual(dec["visibility_desc"], "4000 m")

    def test_visibility_miles(self):
        metar = "KORD 061800Z 26008KT 10SM FEW250 25/21 A2992"
        dec = MetarDecoder(metar).to_flat_dict()
        self.assertIn("visibility_sm", dec)
        self.assertEqual(dec["visibility_sm"], 10.0)

class TestDataTypes(unittest.TestCase):
    def test_temperature_positive(self):
        temp = Temperature("25")
        self.assertEqual(temp.celsius, 25)
        self.assertEqual(str(temp), "25 °C")

    def test_temperature_negative(self):
        temp = Temperature("M05")
        self.assertEqual(temp.celsius, -5)
        self.assertEqual(str(temp), "-5 °C")

    def test_pressure_hpa(self):
        p = Pressure("1013", "Q")
        self.assertEqual(p.hPa, 1013)
        self.assertAlmostEqual(p.inHg, 29.9, places=1)

    def test_pressure_inhg(self):
        p = Pressure("2992", "A")
        self.assertEqual(p.inHg, 29.92)
        self.assertAlmostEqual(p.hPa, 1013.0, places=0)

# Nota: La clase Wind se usa indirectamente a través de to_flat_dict,
# y se valida en los casos de viento arriba.

if __name__ == "__main__":
    unittest.main(verbosity=2)
