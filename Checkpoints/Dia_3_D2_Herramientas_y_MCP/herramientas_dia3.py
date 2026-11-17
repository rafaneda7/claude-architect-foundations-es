"""Lógica local reutilizable por MCP y por pruebas. Datos inventados."""
from __future__ import annotations

import math

PROYECTOS = {
    "G1": {"codigo": "G1", "titulo": "EDA de videojuegos", "estado": "revision", "nota": 8.5},
    "G2": {"codigo": "G2", "titulo": "Prediccion de ventas", "estado": "completado", "nota": 9.0},
    "G3": {"codigo": "G3", "titulo": "Analisis de clientes", "estado": "pendiente", "nota": None},
}


def buscar_proyectos(consulta: str, limite: int = 5) -> dict:
    """Busca proyectos por texto del título o código. Sin coincidencias devuelve éxito vacío."""
    if not isinstance(consulta, str) or not consulta.strip():
        raise ValueError("La consulta debe ser texto no vacío.")
    if isinstance(limite, bool) or not isinstance(limite, int) or not 1 <= limite <= 10:
        raise ValueError("El límite debe ser un entero entre 1 y 10.")
    patron = consulta.strip().casefold()
    encontrados = [dict(x) for x in PROYECTOS.values()
                   if patron in x["titulo"].casefold() or patron in x["codigo"].casefold()]
    return {"total": len(encontrados), "resultados": encontrados[:limite]}


def obtener_proyecto(codigo: str) -> dict:
    """Consulta por identificador exacto; no sirve para búsqueda textual."""
    if not isinstance(codigo, str) or not codigo.strip():
        raise ValueError("El código debe ser una cadena no vacía.")
    code = codigo.strip().upper()
    if code not in PROYECTOS:
        raise LookupError(f"El proyecto {code} no existe.")
    return dict(PROYECTOS[code])


def calcular_media(notas: list[float]) -> dict:
    """Media aritmética de notas 0..10 (booleanos y no finitos prohibidos)."""
    if not isinstance(notas, list) or not notas:
        raise ValueError("Debes proporcionar una lista no vacía.")
    for nota in notas:
        if (isinstance(nota, bool) or not isinstance(nota, (int, float))
                or not math.isfinite(nota) or not 0 <= nota <= 10):
            raise ValueError("Cada nota debe ser un número finito entre 0 y 10.")
    return {"media": round(sum(notas)/len(notas), 2), "cantidad": len(notas)}


def error_estructurado(error: Exception) -> dict:
    """Metadatos propios de la app: NO son automáticamente el isError de MCP."""
    if isinstance(error, PermissionError):
        categoria, reintentar, codigo = "permission", False, "ACCESS_DENIED"
    elif isinstance(error, (ValueError, TypeError, LookupError)):
        categoria, reintentar, codigo = "validation", False, "INVALID_INPUT_OR_NOT_FOUND"
    elif isinstance(error, (TimeoutError, ConnectionError)):
        categoria, reintentar, codigo = "transient", True, "TEMPORARY_UNAVAILABLE"
    else:
        categoria, reintentar, codigo = "internal", False, "INTERNAL_ERROR"
    return {"ok": False, "errorCategory": categoria, "isRetryable": reintentar,
            "code": codigo, "message": str(error) if categoria != "internal" else "Error interno."}
