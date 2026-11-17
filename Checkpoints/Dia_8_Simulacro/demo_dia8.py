from motor_dia8 import Identidad, consultar_pedido, construir_resultados, decidir_reembolso, validar_factura, estado_tarea


def main():
    usuario = Identidad('cliente_a', True)
    print('Pedido autorizado:', consultar_pedido('O-100', usuario))
    print('Decisión de reembolso:', decidir_reembolso(usuario, 'O-100', '47.90'))
    solicitudes = [
        {'type':'tool_use','id':'toolu_01','name':'consultar_pedido','input':{'pedido_id':'O-100'}},
        {'type':'tool_use','id':'toolu_02','name':'consultar_pedido','input':{'pedido_id':'O-200'}},
    ]
    print('Herramientas múltiples:', construir_resultados(solicitudes, usuario))
    print('Validación de factura:', validar_factura({'items':[{'cantidad':2,'precio_unitario':'3.50'}], 'total_declarado':'7.00'}))
    print('Turno con error:', estado_tarea('end_turn', hubo_error_herramienta=True))


if __name__ == '__main__':
    main()
