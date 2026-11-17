import unittest
from contexto_dia6 import (AccesoDenegado, ContextoInvalido, Incidencia,
    Documento, Conversacion, agregar_incidencia, buscar_documentos,
    reducir_resultado_herramienta, crear_contexto, clasificar_error_http, decidir_escalado)


class TestDia6(unittest.TestCase):
    def setUp(self):
        self.c = Conversacion("C1", "u1", resumen="Información general antigua")
        self.i = Incidencia("I1", "u1", "Devolución", "abierto", "10.00", "2026-11-01", "Esperar", "DB")

    def test_acceso_ajeno(self):
        with self.assertRaises(AccesoDenegado): crear_contexto(self.c,"u2","hola")

    def test_usuario_vacio(self):
        with self.assertRaises(AccesoDenegado): crear_contexto(self.c,"","hola")

    def test_añadir_incidencia(self):
        agregar_incidencia(self.c,"u1",self.i)
        self.assertIn("I1",self.c.incidencias)

    def test_incidencia_ajena(self):
        with self.assertRaises(AccesoDenegado): agregar_incidencia(self.c,"u1",Incidencia("I2","u2","x","abierto"))

    def test_incidencia_duplicada(self):
        agregar_incidencia(self.c,"u1",self.i)
        with self.assertRaises(ValueError): agregar_incidencia(self.c,"u1",self.i)

    def test_importe_invalido(self):
        with self.assertRaises(ValueError): Incidencia("I2","u1","x","abierto", "NaN")

    def test_estado_invalido(self):
        with self.assertRaises(ValueError): Incidencia("I2","u1","x","pendiente")

    def test_retrieval_autorizado(self):
        docs=[Documento("D1","u1","devolución pendiente"),Documento("D2","u2","devolución privada")]
        result=buscar_documentos(docs,"u1","devolución")
        self.assertEqual([d.documento_id for d in result],["D1"])

    def test_retrieval_sin_terminos(self):
        self.assertEqual(buscar_documentos([],"u1","  "),[])

    def test_retrieval_limite(self):
        with self.assertRaises(ValueError): buscar_documentos([],"u1","x",0)

    def test_retrieval_ranking(self):
        docs=[Documento("D1","u1","devolución"),Documento("D2","u1","devolución urgente")]
        self.assertEqual(buscar_documentos(docs,"u1","devolución urgente")[0].documento_id,"D2")

    def test_contexto_con_hechos(self):
        agregar_incidencia(self.c,"u1",self.i)
        ms=crear_contexto(self.c,"u1","¿Importe?")
        self.assertIn('"importe": "10.00"',ms[0]["content"])
        self.assertIn('"incidencia_id": "I1"',ms[0]["content"])

    def test_contexto_recientes(self):
        self.c.mensajes_recientes=[{"role":"user","content":str(i)} for i in range(6)]
        ms=crear_contexto(self.c,"u1","pregunta",max_recientes=2)
        self.assertEqual([m["content"] for m in ms[1:-1]],["4","5"])

    def test_contexto_sin_recientes(self):
        self.c.mensajes_recientes=[{"role":"user","content":"x"}]
        self.assertEqual(len(crear_contexto(self.c,"u1","pregunta",max_recientes=0)),2)

    def test_herramienta_pendiente(self):
        self.c.tiene_herramienta_pendiente=True
        with self.assertRaises(ContextoInvalido): crear_contexto(self.c,"u1","pregunta")

    def test_mensaje_invalido(self):
        self.c.mensajes_recientes=[{"role":"system","content":"x"}]
        with self.assertRaises(ContextoInvalido): crear_contexto(self.c,"u1","pregunta")

    def test_resultado_reducido(self):
        raw={"tool_use_id":"toolu-1","estado":"fallo","error_code":"timeout","fuente":"API", "debug_dump":"100MB"}
        red=reducir_resultado_herramienta(raw)
        self.assertNotIn("debug_dump",red)
        self.assertEqual(red["tool_use_id"],"toolu-1")
        self.assertEqual(red["error_code"],"timeout")

    def test_resultado_datos(self):
        raw={"datos":{"id":"I1","importe":"8.25","fecha":"2026-01-01","imagen_blob":"huge"}}
        self.assertNotIn("imagen_blob",reducir_resultado_herramienta(raw)["datos"])

    def test_resultado_tipo(self):
        with self.assertRaises(TypeError): reducir_resultado_herramienta("hola")

    def test_401_no_reintento(self):
        self.assertFalse(clasificar_error_http(401)["reintentar"])

    def test_429_retry_after(self):
        self.assertEqual(clasificar_error_http(429,True)["accion"],"esperar_retry_after")

    def test_429_tope_gasto(self):
        self.assertFalse(clasificar_error_http(429,False,True)["reintentar"])

    def test_529_transitorio(self):
        self.assertTrue(clasificar_error_http(529)["reintentar"])

    def test_400_no_reintento(self):
        self.assertFalse(clasificar_error_http(400)["reintentar"])

    def test_escalar_aprobacion(self):
        self.assertTrue(decidir_escalado(self.i,requiere_aprobacion=True)["escalar"])

    def test_escalar_repetidos(self):
        self.assertTrue(decidir_escalado(self.i,intentos_fallidos=2)["escalar"])

    def test_no_escalar_por_sentimiento(self):
        self.assertFalse(decidir_escalado(self.i)["escalar"])

    def test_escalar_no_negativo(self):
        with self.assertRaises(ValueError): decidir_escalado(self.i,intentos_fallidos=-1)

    def test_estado_escalado(self):
        i=Incidencia("I2","u1","x","escalado")
        self.assertIn("ya_escalado",decidir_escalado(i)["motivos"])

    def test_pregunta_vacia(self):
        with self.assertRaises(ValueError): crear_contexto(self.c,"u1"," ")


if __name__ == "__main__": unittest.main()
