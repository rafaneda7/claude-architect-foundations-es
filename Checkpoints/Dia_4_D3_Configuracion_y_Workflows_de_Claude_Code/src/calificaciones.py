"""Funciones didácticas para comprobar validaciones y cálculo de notas."""
from math import isfinite


def validar_notas(notas: list[float]) -> list[float]:
    """Valida una lista no vacía de notas numéricas finitas en [0, 10]."""
    if not isinstance(notas, list) or not notas:
        raise ValueError("Se esperaba una lista no vacía")
    for nota in notas:
        if isinstance(nota, bool) or not isinstance(nota, (int, float)):
            raise ValueError("Cada nota debe ser numérica y no booleana")
        if not isfinite(nota) or not (0 <= nota <= 10):
            raise ValueError("La nota debe ser finita y estar entre 0 y 10")
    return notas


def calcular_media(notas: list[float]) -> float:
    """Devuelve la media redondeada a dos decimales."""
    notas = validar_notas(notas)
    return round(sum(notas) / len(notas), 2)


def clasificar_aprobado(nota: float) -> bool:
    """Devuelve True cuando la nota es al menos 5 (escala 0-10)."""
    validar_notas([nota])
    return nota >= 5
