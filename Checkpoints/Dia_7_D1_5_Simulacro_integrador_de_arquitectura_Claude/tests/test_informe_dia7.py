import unittest
from unittest.mock import Mock
from types import SimpleNamespace as S
import json
from motor_dia7 import Identidad, autorizar_proyecto
from informe_dia7 import validar_informe, obtener_informe_json

A = Identidad('alumno_a','alumno')
P = autorizar_proyecto('G1',A)

class InformeTests(unittest.TestCase):
    def ok(self): return {'codigo':'G1','estado':'apto_para_revision_humana','hallazgos':[],'evidencias':['tests:G1:2026-11-17']}
    def test_valid(self): self.assertEqual(validar_informe(self.ok(),P)['codigo'],'G1')
    def test_wrong_code(self):
        x=self.ok();x['codigo']='G2'
        with self.assertRaises(ValueError): validar_informe(x,P)
    def test_fake_evidence(self):
        x=self.ok();x['evidencias']=['archivo inventado']
        with self.assertRaises(ValueError): validar_informe(x,P)
    def test_missing_evidence(self):
        x=self.ok();x['evidencias']=[]
        with self.assertRaises(ValueError): validar_informe(x,P)
    def test_wrong_fields(self):
        x=self.ok();x['extra']='x'
        with self.assertRaises(ValueError): validar_informe(x,P)
    def test_bad_hallazgos(self):
        x=self.ok();x['hallazgos']=[3]
        with self.assertRaises(ValueError): validar_informe(x,P)
    def test_bad_status(self):
        x=self.ok();x['estado']='aprobado'
        with self.assertRaises(ValueError): validar_informe(x,P)
    def test_leakage_prevents_apt(self):
        proyecto=dict(P);proyecto['posible_leakage']=True
        with self.assertRaises(ValueError): validar_informe(self.ok(),proyecto)
    def test_bad_tests_prevents_apt(self):
        proyecto=dict(P);proyecto['tests_superados']=False
        with self.assertRaises(ValueError): validar_informe(self.ok(),proyecto)
    def test_wrong_type(self):
        with self.assertRaises(ValueError): validar_informe([],P)
    def test_real_mock_completed(self):
        cliente=Mock()
        cliente.messages.create.return_value = S(stop_reason='end_turn',content=[S(type='text',text=json.dumps(self.ok()))])
        self.assertEqual(obtener_informe_json(cliente,P)['estado'],'apto_para_revision_humana')
        self.assertIn('output_config',cliente.messages.create.call_args.kwargs)
    def test_max_tokens(self):
        cliente=Mock();cliente.messages.create.return_value = S(stop_reason='max_tokens',content=[])
        with self.assertRaises(ValueError): obtener_informe_json(cliente,P)
    def test_invalid_json(self):
        cliente=Mock();cliente.messages.create.return_value = S(stop_reason='end_turn',content=[S(type='text',text='{bad')])
        with self.assertRaises(ValueError): obtener_informe_json(cliente,P)

if __name__=='__main__': unittest.main()
