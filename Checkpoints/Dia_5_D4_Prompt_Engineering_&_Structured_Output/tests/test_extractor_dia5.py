import copy
import json
import math
import unittest
from types import SimpleNamespace

from extractor_dia5 import (
    SCHEMA, ValidacionSemanticaError, crear_prompt, es_numero_finito,
    extraer_json_respuesta, validar_extraccion, extraer_con_claude,
)

DOC = "Ticket: 2 cuadernos a 3.50 EUR. TOTAL 7.00 EUR"
BUENO = {
    "tipo": "ticket", "moneda": "EUR",
    "items": [{"descripcion":"cuadernos", "cantidad":2, "precio_unitario":3.5,
               "evidencia":"2 cuadernos a 3.50 EUR"}],
    "total_declarado": 7.0, "observaciones":""
}

class TestsDia5(unittest.TestCase):
    def test_valido(self):
        self.assertEqual(validar_extraccion(BUENO,DOC)["total_calculado"], 7)
    def test_total_incorrecto(self):
        d=copy.deepcopy(BUENO); d['total_declarado']=8
        with self.assertRaisesRegex(ValidacionSemanticaError,'Total inconsistente'):
            validar_extraccion(d,DOC)
    def test_total_ausente_es_valido(self):
        d=copy.deepcopy(BUENO); d['total_declarado']=None
        self.assertEqual(validar_extraccion(d,DOC)['total_calculado'],7)
    def test_evidencia_inventada(self):
        d=copy.deepcopy(BUENO); d['items'][0]['evidencia']='10 plátanos'
        with self.assertRaisesRegex(ValidacionSemanticaError,'evidencia no encontrada'):
            validar_extraccion(d,DOC)
    def test_booleano_rechazado(self):
        d=copy.deepcopy(BUENO); d['items'][0]['cantidad']=True
        with self.assertRaisesRegex(ValidacionSemanticaError,'cantidad inválida'):
            validar_extraccion(d,DOC)
    def test_precio_negativo(self):
        d=copy.deepcopy(BUENO); d['items'][0]['precio_unitario']=-1
        with self.assertRaises(ValidacionSemanticaError): validar_extraccion(d,DOC)
    def test_inf_rechazado(self):
        d=copy.deepcopy(BUENO); d['items'][0]['precio_unitario']=math.inf
        with self.assertRaises(ValidacionSemanticaError): validar_extraccion(d,DOC)
    def test_enum_invalido(self):
        d=copy.deepcopy(BUENO); d['moneda']='GBP'
        with self.assertRaises(ValidacionSemanticaError): validar_extraccion(d,DOC)
    def test_campo_sobrante(self):
        d=copy.deepcopy(BUENO); d['invento']=123
        with self.assertRaises(ValidacionSemanticaError): validar_extraccion(d,DOC)
    def test_lista_vacia_con_total(self):
        d=copy.deepcopy(BUENO); d['items']=[]
        with self.assertRaises(ValidacionSemanticaError): validar_extraccion(d,DOC)
    def test_json_correcto(self):
        resp=SimpleNamespace(stop_reason='end_turn', content=[SimpleNamespace(type='text', text=json.dumps(BUENO))])
        self.assertEqual(extraer_json_respuesta(resp)['tipo'],'ticket')
    def test_max_tokens(self):
        resp=SimpleNamespace(stop_reason='max_tokens', content=[SimpleNamespace(type='text', text=json.dumps(BUENO))])
        with self.assertRaisesRegex(ValueError,'no finalizada'): extraer_json_respuesta(resp)
    def test_refusal(self):
        resp=SimpleNamespace(stop_reason='refusal', content=[SimpleNamespace(type='text', text='No')])
        with self.assertRaises(ValueError): extraer_json_respuesta(resp)
    def test_bloque_no_textual(self):
        resp=SimpleNamespace(stop_reason='end_turn', content=[SimpleNamespace(type='tool_use')])
        with self.assertRaisesRegex(ValueError,'no contiene texto'): extraer_json_respuesta(resp)
    def test_json_malformado(self):
        resp=SimpleNamespace(stop_reason='end_turn', content=[SimpleNamespace(type='text', text='{mal')])
        with self.assertRaisesRegex(ValueError,'JSON válido'): extraer_json_respuesta(resp)
    def test_prompt_aisla_fuente(self):
        self.assertIn('<documento>',crear_prompt('hola'))
    def test_validador_numerico(self):
        self.assertTrue(es_numero_finito(0));self.assertFalse(es_numero_finito(True));self.assertFalse(es_numero_finito(math.nan))
    def test_esquema_no_minimum(self):
        self.assertNotIn('minimum',json.dumps(SCHEMA))

class FakeMessages:
    def __init__(self, responses): self.responses=responses;self.calls=[]
    def create(self,**kwargs):
        self.calls.append(kwargs)
        return self.responses.pop(0)

class FakeClient:
    def __init__(self, responses): self.messages=FakeMessages(responses)

class TestsSimulados(unittest.TestCase):
    def response(self, datos):
        return SimpleNamespace(stop_reason='end_turn',content=[SimpleNamespace(type='text',text=json.dumps(datos))])
    def test_extraccion_mock_una_llamada(self):
        c=FakeClient([self.response(BUENO)])
        res=extraer_con_claude(DOC,c)
        self.assertEqual(res['total_calculado'],7)
        self.assertEqual(len(c.messages.calls),1)
        self.assertEqual(c.messages.calls[0]['output_config']['format']['type'],'json_schema')
    def test_extraccion_mock_retry_semantico(self):
        malo=copy.deepcopy(BUENO);malo['total_declarado']=8
        c=FakeClient([self.response(malo),self.response(BUENO)])
        res=extraer_con_claude(DOC,c)
        self.assertEqual(res['total_calculado'],7)
        self.assertEqual(len(c.messages.calls),2)
        self.assertIn('Total inconsistente',str(c.messages.calls[1]['messages']))
    def test_no_reintentar_refusal(self):
        c=FakeClient([SimpleNamespace(stop_reason='refusal',content=[])])
        with self.assertRaises(ValueError): extraer_con_claude(DOC,c)
        self.assertEqual(len(c.messages.calls),1)
    def test_no_reintentar_documento_vacio(self):
        c=FakeClient([])
        with self.assertRaises(ValueError): extraer_con_claude('  ',c)
        self.assertEqual(len(c.messages.calls),0)

if __name__ == '__main__': unittest.main()
