import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from motor_dia8 import Identidad, consultar_pedido, AccesoDenegado, ValidacionFallida, decidir_reembolso, construir_resultados, validar_factura, estado_tarea
from corrector_dia8 import cargar_banco, corregir

class TestDay8(unittest.TestCase):
    def setUp(self):
        self.a=Identidad('cliente_a',True)
        self.b=Identidad('cliente_b',True)
    def test_authorized_order(self):
        self.assertEqual(consultar_pedido('O-100',self.a)['importe'],'47.90')
    def test_other_user(self):
        with self.assertRaises(AccesoDenegado): consultar_pedido('O-200',self.a)
    def test_not_verified(self):
        with self.assertRaises(AccesoDenegado): consultar_pedido('O-100',Identidad('cliente_a',False))
    def test_missing_order(self):
        with self.assertRaises(ValidacionFallida): consultar_pedido('O-000',self.a)
    def test_refund_success(self):
        self.assertEqual(decidir_reembolso(self.a,'O-100','30.00')['estado'],'autorizable')
    def test_refund_approval(self):
        self.assertEqual(decidir_reembolso(self.b,'O-200','600')['estado'],'requiere_aprobacion')
    def test_refund_with_approval(self):
        self.assertEqual(decidir_reembolso(self.b,'O-200','600',aprobado_humano=True)['estado'],'autorizable')
    def test_refund_over_value(self):
        with self.assertRaises(ValidacionFallida): decidir_reembolso(self.a,'O-100','49.00')
    def test_refund_nan(self):
        with self.assertRaises(ValidacionFallida): decidir_reembolso(self.a,'O-100','NaN')
    def test_refund_idempotence(self):
        self.assertEqual(decidir_reembolso(self.a,'O-100','10',transaccion_previa=True)['estado'],'verificar_estado_previo')
    def test_multiple_results(self):
        data=[{'type':'text','text':'Hola'}, {'type':'tool_use','id':'x1','name':'consultar_pedido','input':{'pedido_id':'O-100'}}, {'type':'tool_use','id':'x2','name':'consultar_pedido','input':{'pedido_id':'O-200'}}]
        r=construir_resultados(data,self.a)
        self.assertEqual(len(r),2)
        self.assertEqual([x['tool_use_id'] for x in r], ['x1','x2'])
        self.assertNotIn('is_error',r[0]); self.assertTrue(r[1]['is_error'])
    def test_unknown_tool(self):
        r=construir_resultados([{'type':'tool_use','id':'x3','name':'borrar_db','input':{}}],self.a)
        self.assertTrue(r[0]['is_error'])
    def test_duplicate_id(self):
        data=[{'type':'tool_use','id':'x','name':'consultar_pedido','input':{}}, {'type':'tool_use','id':'x','name':'consultar_pedido','input':{}}]
        with self.assertRaises(ValidacionFallida): construir_resultados(data,self.a)
    def test_invoice_valid(self):
        self.assertTrue(validar_factura({'items':[{'cantidad':2,'precio_unitario':'3.50'}], 'total_declarado':'7.00'})['ok'])
    def test_invoice_nullable(self):
        self.assertIsNone(validar_factura({'items':[{'cantidad':2,'precio_unitario':'3.50'}], 'total_declarado':None})['declarado'])
    def test_invoice_mismatch(self):
        with self.assertRaises(ValidacionFallida): validar_factura({'items':[{'cantidad':2,'precio_unitario':'3.50'}], 'total_declarado':'8.00'})
    def test_invoice_nan(self):
        with self.assertRaises(ValidacionFallida): validar_factura({'items':[{'cantidad':1,'precio_unitario':'NaN'}], 'total_declarado':None})
    def test_stop_reason_error(self):
        self.assertEqual(estado_tarea('end_turn',hubo_error_herramienta=True),'turno_terminado_operacion_fallida')
    def test_stop_reason_tool(self):
        self.assertEqual(estado_tarea('tool_use'),'requiere_herramientas')
    def test_bank_counts(self):
        qs=cargar_banco()
        self.assertEqual(len(qs),60)
        from collections import Counter
        self.assertEqual(dict(Counter(q['domain'] for q in qs)),{'D1':16,'D2':11,'D5':9,'D3':12,'D4':12})
    def test_grade_all_correct(self):
        qs=cargar_banco();answers={str(q['number']):q['answer'] for q in qs};r=corregir(answers,qs)
        self.assertEqual(r['aciertos'],60)
        self.assertEqual(r['pendientes'],[])
    def test_grade_wrong(self):
        qs=cargar_banco();answers={str(q['number']):'' for q in qs};answers['1']='D' if qs[0]['answer']!='D' else 'A';r=corregir(answers,qs)
        self.assertEqual(r['aciertos'],0);self.assertEqual(len(r['errores']),1);self.assertEqual(len(r['pendientes']),59)

if __name__=='__main__':
    unittest.main()
