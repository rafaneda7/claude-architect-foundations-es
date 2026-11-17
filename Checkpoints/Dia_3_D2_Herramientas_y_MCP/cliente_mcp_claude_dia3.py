"""Bridge real MCP v2 -> Claude Messages API. Consume saldo SOLO al ejecutar este archivo.
Requisitos: pip install 'mcp[cli]' anthropic
La conexión MCP es local, en proceso. La API sí utiliza red.
"""
from __future__ import annotations
import asyncio
import json
import os
import anthropic
from mcp import Client
from mcp.types import TextContent
from servidor_mcp_dia3 import mcp

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5")
MAX_LLAMADAS = 4


def convertir_herramientas(mcp_tools) -> list[dict]:
    """Convierte definiciones MCP a herramientas de cliente de Claude."""
    return [{"name": t.name, "description": t.description or f"Herramienta {t.name}",
             "input_schema": t.input_schema} for t in mcp_tools]


def contenido_resultado(result) -> str:
    """Toma structured_content si existe; en otro caso toma bloques de texto."""
    if result.structured_content is not None and not result.is_error:
        return json.dumps(result.structured_content, ensure_ascii=False)
    textos = [c.text for c in result.content if isinstance(c, TextContent)]
    return "\n".join(textos) or ("Error de herramienta sin detalle" if result.is_error else "")


async def ejecutar(pregunta: str) -> dict:
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("Falta ANTHROPIC_API_KEY en el entorno.")
    async with Client(mcp) as conexion:
        herramientas = await conexion.list_tools()
        tools = convertir_herramientas(herramientas.tools)
        nombres_permitidos = {t["name"] for t in tools}
        api = anthropic.AsyncAnthropic(max_retries=0, timeout=30)
        mensajes = [{"role": "user", "content": pregunta}]
        input_total = 0
        output_total = 0
        for n in range(1, MAX_LLAMADAS + 1):
            response = await api.messages.create(
                model=MODEL, max_tokens=512, tool_choice={"type": "auto"},
                tools=tools,
                system=("Eres un asistente de un catálogo ficticio. Responde en español. "
                        "Para datos de proyectos consulta las herramientas; jamás inventes resultados."),
                messages=mensajes,
            )
            input_total += response.usage.input_tokens
            output_total += response.usage.output_tokens
            print(f"Llamada {n} | stop_reason={response.stop_reason}")
            if response.stop_reason == "end_turn":
                texto = "\n".join(b.text for b in response.content if b.type == "text")
                return {"estado": "completado", "respuesta": texto, "llamadas": n,
                        "tokens_entrada": input_total, "tokens_salida": output_total}
            if response.stop_reason != "tool_use":
                return {"estado": "interrumpido", "motivo": response.stop_reason}
            if n == MAX_LLAMADAS:
                return {"estado": "incompleto", "motivo": "limite_de_llamadas"}
            mensajes.append({"role": "assistant", "content": response.content})
            resultados = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                if block.name not in nombres_permitidos:
                    resultados.append({"type": "tool_result", "tool_use_id": block.id,
                                       "content": "Herramienta no autorizada.", "is_error": True})
                    continue
                try:
                    r = await conexion.call_tool(block.name, block.input)
                    resultados.append({"type": "tool_result", "tool_use_id": block.id,
                                       "content": contenido_resultado(r),
                                       "is_error": bool(r.is_error)})
                except Exception:
                    resultados.append({"type": "tool_result", "tool_use_id": block.id,
                                       "content": "Error de conexión con la herramienta.", "is_error": True})
            if not resultados:
                return {"estado": "interrumpido", "motivo": "sin_herramientas"}
            mensajes.append({"role": "user", "content": resultados})
        return {"estado": "incompleto", "motivo": "limite_de_llamadas"}


if __name__ == "__main__":
    try:
        print(json.dumps(asyncio.run(ejecutar(
            "Busca el proyecto de videojuegos, consulta su código exacto y dime su nota."
        )), ensure_ascii=False, indent=2))
    except (anthropic.APIError, RuntimeError) as exc:
        print(f"No completado: {type(exc).__name__}. Revisa credenciales, cuota o conectividad.")
