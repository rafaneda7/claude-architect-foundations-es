import json
import unittest
from types import SimpleNamespace as S
from unittest.mock import Mock

from motor_dia7 import (
    Identidad, autorizar_proyecto, validar_notas, ejecutar_herramienta,
    construir_tool_results, extraer_texto, agent_loop, dictamen_determinista,
)

A = Identidad('alumno_a', 'alumno')
B = Identidad('alumno_b', 'alumno')
P = Identidad('profesor_1', 'profesor', frozenset({'G1'}))

def respuesta(stop, *bloques):
    return S(stop_reason=stop, content=list(bloques))

def tool(i='t1', name='consultar_proyecto', args=None):
    return S(type='tool_use', id=i, name=name, input=args if args is not None else {'codigo':'G1'})

def txt(t='respuesta'):
    return S(type='text', text=t)

class DomainTests(unittest.TestCase):
    def test_alumno_own(self): self.assertEqual(autorizar_proyecto('G1', A)['codigo'], 'G1')
    def test_alumno_other(self):
        with self.assertRaises(PermissionError): autorizar_proyecto('G2', A)
    def test_professor_assigned(self): self.assertEqual(autorizar_proyecto('G1', P)['codigo'], 'G1')
    def test_professor_other(self):
        with self.assertRaises(PermissionError): autorizar_proyecto('G2', P)
    def test_no_admin_by_default(self):
        with self.assertRaises(PermissionError): autorizar_proyecto('G1', Identidad('evil','admin'))
    def test_unknown_project(self):
        with self.assertRaises(ValueError): autorizar_proyecto('G10', A)
    def test_bad_code(self):
        with self.assertRaises(ValueError): autorizar_proyecto(None, A)
    def test_media(self): self.assertEqual(ejecutar_herramienta('calcular_media', {'notas':[7,8,9]}, A)['media'], 8.0)
    def test_empty(self):
        with self.assertRaises(ValueError): validar_notas([])
    def test_boolean(self):
        with self.assertRaises(ValueError): validar_notas([True])
    def test_nan(self):
        with self.assertRaises(ValueError): validar_notas([float('nan')])
    def test_inf(self):
        with self.assertRaises(ValueError): validar_notas([float('inf')])
    def test_outside(self):
        with self.assertRaises(ValueError): validar_notas([15])
    def test_string(self):
        with self.assertRaises(ValueError): validar_notas('7,8,9')
    def test_unknown_tool(self):
        with self.assertRaises(ValueError): ejecutar_herramienta('borrar_proyecto', {}, A)
    def test_non_dict(self):
        with self.assertRaises(ValueError): ejecutar_herramienta('calcular_media', None, A)
    def test_project_fields(self): self.assertNotIn('propietario', ejecutar_herramienta('consultar_proyecto', {'codigo':'G1'}, A))
    def test_text_only(self): self.assertEqual(extraer_texto(respuesta('end_turn', txt('Hola'), tool(), txt('mundo'))), 'Hola\nmundo')
    def test_no_text(self): self.assertEqual(extraer_texto(respuesta('end_turn', tool())), '')
    def test_multi_tools(self):
        r = respuesta('tool_use', tool('t1'), tool('t2','calcular_media', {'notas':[8,10]}))
        resultados, errors=construir_tool_results(r, A)
        self.assertEqual([x['tool_use_id'] for x in resultados],['t1','t2'])
        self.assertFalse(errors)
    def test_denied_tool_result(self):
        resultados, errors=construir_tool_results(respuesta('tool_use',tool(args={'codigo':'G2'})),A)
        self.assertTrue(resultados[0]['is_error'])
        self.assertEqual(errors,['PERMISSION_DENIED'])
        self.assertEqual(json.loads(resultados[0]['content'])['error_code'],'PERMISSION_DENIED')
    def test_invalid_tool_result(self):
        resultados, errors=construir_tool_results(respuesta('tool_use',tool(name='calcular_media',args={'notas':[]})),A)
        self.assertTrue(resultados[0]['is_error'])
        self.assertEqual(errors,['INVALID_REQUEST'])
    def test_tool_text_ignored(self): self.assertEqual(construir_tool_results(respuesta('tool_use',txt()),A),([],[]))
    def test_dictamen_good(self): self.assertEqual(dictamen_determinista(autorizar_proyecto('G1', A))['estado'],'apto_para_revision_humana')
    def test_dictamen_bad(self):
        x = dictamen_determinista(autorizar_proyecto('G2', B))
        self.assertIn('RIESGO_LEAKAGE',x['motivos'])
        self.assertIn('TESTS_INCOMPLETOS',x['motivos'])
    def test_missing_evidence(self): self.assertEqual(dictamen_determinista({'evidencias':[]})['estado'],'requiere_revision')

class LoopTests(unittest.TestCase):
    def fake(self,*responses):
        m=Mock()
        m.messages.create.side_effect=responses
        return m
    def test_completed(self):
        m=self.fake(respuesta('end_turn',txt('Final')))
        self.assertEqual(agent_loop(m,'Pregunta',A)['estado'],'completado_turno')
    def test_empty_end_turn(self): self.assertEqual(agent_loop(self.fake(respuesta('end_turn')),'Pregunta',A)['motivo'],'respuesta_vacia')
    def test_max_tokens(self): self.assertEqual(agent_loop(self.fake(respuesta('max_tokens',txt('Cortado'))),'Pregunta',A)['estado'],'interrumpido')
    def test_refusal(self): self.assertEqual(agent_loop(self.fake(respuesta('refusal',txt('No'))),'Pregunta',A)['motivo'],'refusal')
    def test_pause(self): self.assertEqual(agent_loop(self.fake(respuesta('pause_turn')),'Pregunta',A)['motivo'],'pause_turn')
    def test_tool_no_blocks(self): self.assertEqual(agent_loop(self.fake(respuesta('tool_use',txt())),'Pregunta',A)['motivo'],'tool_use_sin_bloques')
    def test_boundary_one_call(self):
        m=self.fake(respuesta('tool_use',tool()))
        self.assertEqual(agent_loop(m,'Pregunta',A,max_llamadas=1)['estado'],'incompleto')
        self.assertEqual(m.messages.create.call_count,1)
    def test_history_link(self):
        m=self.fake(respuesta('tool_use',tool('t5')),respuesta('end_turn',txt('Fin')))
        out=agent_loop(m,'Pregunta',A)
        self.assertEqual(out['llamadas'],2)
        last_messages=m.messages.create.call_args.kwargs['messages']
        self.assertEqual(last_messages[-1]['content'][0]['tool_use_id'],'t5')
    def test_denied_not_success(self):
        m=self.fake(respuesta('tool_use',tool(args={'codigo':'G2'})),respuesta('end_turn',txt('No permitido')))
        self.assertEqual(agent_loop(m,'Pregunta',A)['estado'],'acceso_denegado')
    def test_validation_not_success(self):
        m=self.fake(respuesta('tool_use',tool(name='calcular_media',args={'notas':[]})),respuesta('end_turn',txt('Falló')))
        self.assertEqual(agent_loop(m,'Pregunta',A)['estado'],'requiere_revision')
    def test_bad_query(self):
        with self.assertRaises(ValueError): agent_loop(self.fake(),' ',A)
    def test_bad_limit(self):
        with self.assertRaises(ValueError): agent_loop(self.fake(),'Pregunta',A,max_llamadas=0)

if __name__=='__main__': unittest.main()
