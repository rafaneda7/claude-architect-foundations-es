import unittest
from types import SimpleNamespace
from agente_dia2 import ejecutar_herramienta, extraer_texto, crear_resultados


class TestDia2(unittest.TestCase):
    def test_media(self):
        self.assertEqual(ejecutar_herramienta("calcular_media", {"notas": [7, 8, 9]}, "ta_demo")["media"], 8)

    def test_media_vacia(self):
        with self.assertRaises(ValueError):
            ejecutar_herramienta("calcular_media", {"notas": []}, "ta_demo")

    def test_bool_no_es_nota(self):
        with self.assertRaises(ValueError):
            ejecutar_herramienta("calcular_media", {"notas": [True, 7]}, "ta_demo")

    def test_permiso_valido(self):
        self.assertEqual(ejecutar_herramienta("consultar_proyecto", {"grupo": "G1"}, "ta_demo")["nota"], 8.5)

    def test_permiso_denegado(self):
        with self.assertRaises(PermissionError):
            ejecutar_herramienta("consultar_proyecto", {"grupo": "G3"}, "ta_demo")

    def test_nombre_desconocido(self):
        with self.assertRaises(ValueError):
            ejecutar_herramienta("borrar_todo", {}, "ta_demo")

    def test_extraer_texto(self):
        response = SimpleNamespace(content=[SimpleNamespace(type="text", text="hola"), SimpleNamespace(type="tool_use")])
        self.assertEqual(extraer_texto(response), "hola")

    def test_texto_vacio(self):
        response = SimpleNamespace(content=[SimpleNamespace(type="tool_use")])
        self.assertEqual(extraer_texto(response), "")

    def test_error_tool_result(self):
        response = SimpleNamespace(content=[SimpleNamespace(type="tool_use", name="consultar_proyecto", id="toolu_fake", input={"grupo": "G3"})])
        results = crear_resultados(response, "ta_demo")
        self.assertEqual(results[0]["tool_use_id"], "toolu_fake")
        self.assertTrue(results[0]["is_error"])

    def test_multiples_tool_results(self):
        response = SimpleNamespace(content=[
            SimpleNamespace(type="tool_use", name="consultar_proyecto", id="toolu_1", input={"grupo": "G1"}),
            SimpleNamespace(type="tool_use", name="calcular_media", id="toolu_2", input={"notas": [7, 9]})
        ])
        results = crear_resultados(response, "ta_demo")
        self.assertEqual([r["tool_use_id"] for r in results], ["toolu_1", "toolu_2"])

if __name__ == "__main__":
    unittest.main()


# Como ejecutar
# bash
# python -m unittest -v
# ```

# **Resultado esperado:** 10 pruebas locales correctas. El código de estas pruebas sí se ha ejecutado y verificado localmente al preparar este material.

# Para hacer la llamada **real** a Claude:

# ```bash
# python agente_dia2.py
# ```

# **Salida orientativa** (el modelo podría escoger otros pasos):

# ```text
# Llamada 1 | stop_reason=tool_use | ...
# Herramienta solicitada: consultar_proyecto
# Herramienta solicitada: calcular_media
# Llamada 2 | stop_reason=end_turn | ...
# {
#   "estado": "completado",
#   "texto": "El proyecto G1 está en revisión y la media es 8.0.",
#   "tokens_entrada": ...,
#   "tokens_salida": ...
# }
