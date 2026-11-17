"""Laboratorio determinista Día 8: seguridad, herramientas, facturas y estados.

No usa Anthropic ni requiere una API Key. Todo se realiza con datos ficticios.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json


class AccesoDenegado(PermissionError):
    pass


class ValidacionFallida(ValueError):
    pass


@dataclass(frozen=True)
class Identidad:
    usuario_id: str
    verificada: bool


PEDIDOS = {
    'O-100': {'usuario_id': 'cliente_a', 'importe': '47.90', 'estado': 'entregado'},
    'O-200': {'usuario_id': 'cliente_b', 'importe': '650.00', 'estado': 'entregado'},
}


def consultar_pedido(pedido_id: str, identidad: Identidad) -> dict:
    if not identidad.verificada:
        raise AccesoDenegado('IDENTITY_NOT_VERIFIED')
    pedido = PEDIDOS.get(pedido_id)
    if pedido is None:
        raise ValidacionFallida('ORDER_NOT_FOUND')
    if pedido['usuario_id'] != identidad.usuario_id:
        raise AccesoDenegado('PERMISSION_DENIED')
    return {'pedido_id': pedido_id, **pedido}


def decidir_reembolso(
    identidad: Identidad, pedido_id: str, importe: str,
    *, aprobado_humano: bool = False, transaccion_previa: bool = False
) -> dict:
    """Solo decide; no mueve dinero. Requiere aprobación para >500 EUR."""
    pedido = consultar_pedido(pedido_id, identidad)
    try:
        monto = Decimal(importe)
        maximo = Decimal(pedido['importe'])
    except (InvalidOperation, TypeError):
        raise ValidacionFallida('INVALID_AMOUNT') from None
    if not monto.is_finite() or monto <= 0 or monto > maximo:
        raise ValidacionFallida('INVALID_AMOUNT')
    if transaccion_previa:
        return {'estado': 'verificar_estado_previo', 'pedido_id': pedido_id}
    if monto > Decimal('500') and not aprobado_humano:
        return {'estado': 'requiere_aprobacion', 'pedido_id': pedido_id, 'importe': str(monto)}
    return {'estado': 'autorizable', 'pedido_id': pedido_id, 'importe': str(monto)}


def construir_resultados(tools: list[dict], identidad: Identidad) -> list[dict]:
    """Produce un tool_result por cada tool_use incluso si la ejecución falla."""
    salidas = []
    vistos = set()
    for block in tools:
        if block.get('type') != 'tool_use':
            continue
        tool_id = block.get('id')
        if not isinstance(tool_id, str) or not tool_id or tool_id in vistos:
            raise ValidacionFallida('INVALID_TOOL_ID')
        vistos.add(tool_id)
        try:
            nombre = block.get('name')
            datos = block.get('input')
            if not isinstance(datos, dict):
                raise ValidacionFallida('INVALID_INPUT')
            if nombre == 'consultar_pedido':
                resultado = consultar_pedido(datos['pedido_id'], identidad)
            elif nombre == 'decidir_reembolso':
                resultado = decidir_reembolso(identidad, datos['pedido_id'], datos['importe'], aprobado_humano=datos.get('aprobado_humano', False))
            else:
                raise ValidacionFallida('UNKNOWN_TOOL')
            salidas.append({'type':'tool_result','tool_use_id':tool_id,'content':json.dumps(resultado,ensure_ascii=False)})
        except (AccesoDenegado, ValidacionFallida, KeyError) as e:
            codigo = str(e).strip("'") if not isinstance(e,KeyError) else 'MISSING_ARGUMENT'
            salidas.append({'type':'tool_result','tool_use_id':tool_id,'is_error':True,'content':json.dumps({'ok': False, 'error_code': codigo})})
    return salidas


def validar_factura(doc: dict) -> dict:
    """Factura simplificada sin impuestos ni descuentos (ejercicio)."""
    if not isinstance(doc, dict):
        raise ValidacionFallida('DOCUMENT_NOT_OBJECT')
    items=doc.get('items')
    if not isinstance(items,list) or not items:
        raise ValidacionFallida('EMPTY_ITEMS')
    total = Decimal('0')
    for it in items:
        try:
            cantidad=Decimal(str(it['cantidad']))
            precio=Decimal(str(it['precio_unitario']))
        except (KeyError,InvalidOperation,TypeError):
            raise ValidacionFallida('INVALID_ITEM') from None
        if not cantidad.is_finite() or not precio.is_finite() or cantidad<=0 or precio<0:
            raise ValidacionFallida('INVALID_ITEM')
        total+=cantidad*precio
    declarado=doc.get('total_declarado')
    if declarado is not None:
        try:
            declarado=Decimal(str(declarado))
        except (InvalidOperation, TypeError):
            raise ValidacionFallida('INVALID_DECLARED_TOTAL') from None
        if not declarado.is_finite() or abs(declarado-total)>Decimal('0.01'):
            raise ValidacionFallida('SEMANTIC_TOTAL_MISMATCH')
    return {'ok': True, 'calculado': str(total), 'declarado': str(declarado) if declarado is not None else None}


def estado_tarea(stop_reason: str, *, hubo_error_herramienta: bool = False) -> str:
    if stop_reason == 'end_turn' and not hubo_error_herramienta:
        return 'turno_terminado_sin_errores_reportados'
    if stop_reason == 'end_turn' and hubo_error_herramienta:
        return 'turno_terminado_operacion_fallida'
    if stop_reason == 'tool_use':
        return 'requiere_herramientas'
    return 'interrumpido'
