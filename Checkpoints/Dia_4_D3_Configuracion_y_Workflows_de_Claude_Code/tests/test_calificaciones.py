import unittest
from src.calificaciones import validar_notas, calcular_media, clasificar_aprobado


class TestCalificaciones(unittest.TestCase):
    def test_media(self):
        self.assertEqual(calcular_media([7, 8, 9]), 8.0)

    def test_decimales(self):
        self.assertEqual(calcular_media([8, 9, 9]), 8.67)

    def test_lista_vacia(self):
        with self.assertRaises(ValueError):
            calcular_media([])

    def test_bool(self):
        with self.assertRaises(ValueError):
            calcular_media([True, 7])

    def test_nan(self):
        with self.assertRaises(ValueError):
            calcular_media([float("nan")])

    def test_infinito(self):
        with self.assertRaises(ValueError):
            calcular_media([float("inf")])

    def test_fuera_rango(self):
        with self.assertRaises(ValueError):
            validar_notas([10.5])

    def test_tipo_no_lista(self):
        with self.assertRaises(ValueError):
            validar_notas((7, 8))

    def test_aprobado(self):
        self.assertTrue(clasificar_aprobado(5))

    def test_suspenso(self):
        self.assertFalse(clasificar_aprobado(4.99))
