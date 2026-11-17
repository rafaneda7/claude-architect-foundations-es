"""Servidor MCP v2 de práctica. No utiliza la API de Claude ni datos reales.
Ejecuta: python -m mcp dev servidor_mcp_dia3.py (necesita Node/npx para Inspector).
"""
from mcp.server import MCPServer
from herramientas_dia3 import (PROYECTOS, buscar_proyectos as buscar,
                                obtener_proyecto as obtener, calcular_media as media)

mcp = MCPServer("BootcampDemoD3")


@mcp.tool()
def buscar_proyectos(consulta: str, limite: int = 5) -> dict:
    """Busca por fragmento de título o código entre proyectos ficticios. 
    Úsala para descubrir códigos desconocidos, no para consultar un código exacto.
    Devuelve total y resultados; una búsqueda sin coincidencias es válida y devuelve [].
    """
    return buscar(consulta, limite)


@mcp.tool()
def obtener_proyecto(codigo: str) -> dict:
    """Recupera un proyecto ficticio por código exacto (ej. 'G1').
    Úsala solo cuando ya se conoce el código. No realiza búsquedas por palabras.
    Si el código no existe, devuelve error de herramienta.
    """
    return obtener(codigo)


@mcp.tool()
def calcular_media(notas: list[float]) -> dict:
    """Calcula la media de una lista no vacía de notas numéricas de 0 a 10.
    Úsala para cálculos, no para consultar proyectos. Devuelve media y cantidad.
    Rechaza booleanos, NaN y valores fuera del rango.
    """
    return media(notas)


@mcp.resource("bootcamp://catalogo")
def catalogo() -> str:
    """Catálogo público ficticio con códigos de proyectos disponibles."""
    return "Proyectos ficticios: " + ", ".join(
        f"{p['codigo']} ({p['titulo']})" for p in PROYECTOS.values()
    )


@mcp.prompt()
def analizar_proyecto(codigo: str) -> str:
    """Plantilla para analizar un proyecto del catálogo de ejemplo."""
    return (
        f"Consulta el proyecto {codigo} usando la herramienta de código exacto. "
        "Resume título, estado y nota. No inventes datos."
    )
