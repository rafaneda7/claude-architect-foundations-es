"""Ejemplo didáctico: bucle de herramientas de cliente con Claude.

No ejecuta llamadas a la API al importarse. Ejecutar directamente para la práctica real.
"""
import json
import math
import os

from pathlib import Path
from dotenv import load_dotenv

# Obtener la raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Cargar las variables del archivo .env
load_dotenv(PROJECT_ROOT / ".env")

MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-5-5")
MAX_LLAMADAS = 4
MAX_TOKENS_RESPUESTA = 512

PROYECTOS = {
    "G1": {"nombre": "EDA de videojuegos", "estado": "En revisión", "nota": 8.5},
    "G2": {"nombre": "Predicción de ventas", "estado": "Completado", "nota": 9.0},
    "G3": {"nombre": "Clasificación de imágenes", "estado": "Pendiente", "nota": None},
}
PERMISOS = {
    "ta_demo": {"G1", "G2"},
    "mentor_demo": {"G1", "G2", "G3"},
}

HERRAMIENTAS = [
    {
        "name": "consultar_proyecto",
        "description": "Consulta un proyecto ficticio por su código de grupo. Solo lectura.",
        "input_schema": {
            "type": "object",
            "properties": {"grupo": {"type": "string", "description": "Código como G1 o G2"}},
            "required": ["grupo"],
            "additionalProperties": False,
        },
    },
    {
        "name": "calcular_media",
        "description": "Calcula la media aritmética de una lista de notas de 0 a 10.",
        "input_schema": {
            "type": "object",
            "properties": {"notas": {"type": "array", "items": {"type": "number"}}},
            "required": ["notas"],
            "additionalProperties": False,
        },
    },
]


def ejecutar_herramienta(nombre: str, argumentos: dict, usuario_id: str) -> dict:
    """Valida nombre, parámetros y permisos antes de operar."""
    if not isinstance(argumentos, dict):
        raise ValueError("Los argumentos deben ser un objeto JSON.")

    if nombre == "consultar_proyecto":
        grupo = argumentos.get("grupo")
        if not isinstance(grupo, str):
            raise ValueError("El campo grupo debe ser texto.")
        if grupo not in PERMISOS.get(usuario_id, set()):
            raise PermissionError("No tienes permiso para consultar ese grupo.")
        if grupo not in PROYECTOS:
            raise ValueError("Proyecto inexistente.")
        return PROYECTOS[grupo]

    if nombre == "calcular_media":
        notas = argumentos.get("notas")
        if not isinstance(notas, list) or not notas:
            raise ValueError("notas debe ser una lista no vacía.")
        if any(
            isinstance(n, bool)
            or not isinstance(n, (int, float))
            or not math.isfinite(n)
            or not 0 <= n <= 10
            for n in notas
        ):
            raise ValueError("Todas las notas deben ser números finitos entre 0 y 10.")
        return {"media": round(sum(notas) / len(notas), 2), "cantidad": len(notas)}

    raise ValueError("Herramienta desconocida o no autorizada.")


def extraer_texto(response) -> str:
    return "\n".join(
        block.text for block in response.content if block.type == "text"
    )


def crear_resultados(response, usuario_id: str) -> list[dict]:
    resultados = []
    for block in response.content:
        if block.type != "tool_use":
            continue
        print(f"Herramienta solicitada: {block.name}")
        try:
            salida = ejecutar_herramienta(block.name, block.input, usuario_id)
            resultados.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(salida, ensure_ascii=False),
            })
        except (ValueError, TypeError, PermissionError) as exc:
            resultados.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": str(exc),
                "is_error": True,
            })
    return resultados


def ejecutar_agente(pregunta: str, usuario_id: str = "ta_demo") -> dict:
    """Controla el bucle; nunca declara éxito solo por agotar iteraciones."""
    try:
        from anthropic import Anthropic, APIError
    except ImportError as exc:
        raise RuntimeError("Instala el SDK: python -m pip install anthropic") from exc

    client = Anthropic(max_retries=0, timeout=30.0)
    mensajes = [{"role": "user", "content": pregunta}]
    total_entrada = 0
    total_salida = 0

    for numero in range(1, MAX_LLAMADAS + 1):
        try:
            respuesta = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS_RESPUESTA,
                system=(
                    "Eres un asistente de revisión de proyectos ficticios. "
                    "Responde en español y utiliza herramientas para consultar o calcular. "
                    "No inventes resultados de herramientas ni afirmes tener acceso si falla."
                ),
                tools=HERRAMIENTAS,
                messages=mensajes,
            )
        except APIError as exc:
            return {"estado": "error_api", "detalle": type(exc).__name__}

        total_entrada += respuesta.usage.input_tokens
        total_salida += respuesta.usage.output_tokens
        print(f"Llamada {numero} | stop_reason={respuesta.stop_reason} "
              f"| tokens entrada={respuesta.usage.input_tokens} "
              f"salida={respuesta.usage.output_tokens}")

        if respuesta.stop_reason == "tool_use":
            resultados = crear_resultados(respuesta, usuario_id)
            if not resultados:
                return {"estado": "error_protocolo", "detalle": "Sin bloques tool_use"}
            mensajes.append({"role": "assistant", "content": respuesta.content})
            mensajes.append({"role": "user", "content": resultados})
            continue
        if respuesta.stop_reason == "end_turn":
            return {
                "estado": "completado",
                "texto": extraer_texto(respuesta),
                "tokens_entrada": total_entrada,
                "tokens_salida": total_salida,
            }
        return {"estado": "interrumpido", "motivo": respuesta.stop_reason,
                "tokens_entrada": total_entrada, "tokens_salida": total_salida}

    return {"estado": "incompleto", "motivo": "limite_de_llamadas",
            "tokens_entrada": total_entrada, "tokens_salida": total_salida}


if __name__ == "__main__":
    resultado = ejecutar_agente(
        "Consulta el proyecto G1 y calcula la media de 7, 8 y 9.",
        usuario_id="ta_demo",  # Identidad simulada. En producción: sesión verificada.
    )
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

# Si quieres ejecutarlo en VSC para que se vea renderizado el resultado, descomenta la siguiente sección y comenta la anterior.
# if __name__ == "__main__":
#     resultado = ejecutar_agente(
#         "Consulta el proyecto G1 y calcula la media de 7, 8 y 9.",
#         usuario_id="ta_demo",
#     )

#     if resultado["estado"] == "completado":
#         display(Markdown(resultado["texto"]))
#     else:
#         print(json.dumps(resultado, indent=2, ensure_ascii=False))