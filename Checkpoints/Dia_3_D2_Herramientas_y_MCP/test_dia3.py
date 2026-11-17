import unittest
from types import SimpleNamespace
from herramientas_dia3 import buscar_proyectos, obtener_proyecto, calcular_media, error_estructurado


class TestDia3(unittest.TestCase):
    def test_busqueda_por_titulo(self):
        self.assertEqual(buscar_proyectos("videojuegos")["resultados"][0]["codigo"], "G1")
    def test_busqueda_por_codigo(self):
        self.assertEqual(buscar_proyectos("g2")["resultados"][0]["codigo"], "G2")
    def test_busqueda_vacia_valida(self):
        self.assertEqual(buscar_proyectos("noexiste"), {"total": 0, "resultados": []})
    def test_limite(self):
        self.assertEqual(len(buscar_proyectos("G", 1)["resultados"]), 1)
    def test_consulta_vacia_rechazada(self):
        with self.assertRaises(ValueError): buscar_proyectos(" ")
    def test_limite_booleano_rechazado(self):
        with self.assertRaises(ValueError): buscar_proyectos("G", True)
    def test_exacta(self):
        self.assertEqual(obtener_proyecto(" g1 ")["nota"], 8.5)
    def test_codigo_inexistente(self):
        with self.assertRaises(LookupError): obtener_proyecto("G999")
    def test_media(self):
        self.assertEqual(calcular_media([7,8,9])["media"], 8)
    def test_media_vacia(self):
        with self.assertRaises(ValueError): calcular_media([])
    def test_media_booleano(self):
        with self.assertRaises(ValueError): calcular_media([True, 7])
    def test_media_nan(self):
        with self.assertRaises(ValueError): calcular_media([float("nan")])
    def test_media_inf(self):
        with self.assertRaises(ValueError): calcular_media([float("inf")])
    def test_media_fuera_rango(self):
        with self.assertRaises(ValueError): calcular_media([11])
    def test_error_permiso(self):
        e = error_estructurado(PermissionError("No autorizado"))
        self.assertEqual((e["errorCategory"],e["isRetryable"]), ("permission",False))
    def test_error_transitorio(self):
        e=error_estructurado(TimeoutError("Time out"))
        self.assertEqual((e["errorCategory"],e["isRetryable"]),("transient",True))
    def test_error_validacion(self):
        self.assertFalse(error_estructurado(ValueError("No válido"))["isRetryable"])
    def test_error_interno_oculta_detalle(self):
        self.assertNotIn("secreto",error_estructurado(RuntimeError("secreto"))["message"])

if __name__ == '__main__': unittest.main()
