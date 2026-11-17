"""Día 7 CCAR-F: motor didáctico de consultas autorizadas y Agentic Loop.
No se ejecutan notebooks ni código ajeno; datos completamente ficticios.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
import json
from typing import Any


PROYECTOS = {
    "G1": {
        "codigo": "G1", "titulo": "Predicción de ventas", "propietario": "alumno_a",
        "grupo": "G1", "tests_superados": True, "posible_leakage": False,
        "metricas": {"accuracy": 0.83},
        "evidencias": ["tests:G1:2026-11-17", "metricas:G1:v2"],
    },
    "G2": {
        "codigo": "G2", "titulo": "Clasificación de clientes", "propietario": "alumno_b",
        "grupo": "G2", "tests_superados": False, "posible_leakage": True,
        "metricas": {"accuracy": 0.999},
        "evidencias": ["tests:G2:2026-11-17", "auditoria:G2:posible-leakage"],
    },
}


@dataclass(frozen=True)
class Identidad:
    usuario_id: str
    rol: str
    grupos: frozenset[str] = frozenset()


def autorizar_proyecto(codigo: str, identidad: Identidad) -> dict[str, Any]:
    """Resuelve el acceso en el servidor; nunca confía en un rol escrito por Claude."""
    if not isinstance(codigo, str) or not codigo:
        raise ValueError("Código obligatorio")
    proyecto = PROYECTOS.get(codigo)
    if proyecto is None:
        raise ValueError("Proyecto no disponible")
    if identidad.rol == "alumno":
        permitido = proyecto["propietario"] == identidad.usuario_id
    elif identidad.rol == "profesor":
        permitido = proyecto["grupo"] in identidad.grupos
    else:
        permitido = False
    if not permitido:
        raise PermissionError("Acceso no autorizado")
    return proyecto


def validar_notas(notas: Any) -> list[float]:
    if not isinstance(notas, list) or not notas:
        raise ValueError("Se necesita una lista no vacía")
    for nota in notas:
        if (isinstance(nota, bool) or not isinstance(nota, (int, float))
                or not isfinite(nota) or not 0 <= nota <= 10):
            raise ValueError("Las notas deben ser números finitos de 0 a 10")
    return [float(nota) for nota in notas]


def ejecutar_herramienta(nombre: str, argumentos: dict, identidad: Identidad) -> dict:
    if not isinstance(argumentos, dict):
        raise ValueError("Argumentos inválidos")
    if nombre == "consultar_proyecto":
        codigo = argumentos.get("codigo")
        proyecto = autorizar_proyecto(codigo, identidad)
        # Proyecta solo los campos autorizados; no expone datos internos no necesarios.
        return {k: proyecto[k] for k in (
            "codigo", "titulo", "tests_superados", "posible_leakage", "metricas", "evidencias"
        )}
    if nombre == "calcular_media":
        notas = validar_notas(argumentos.get("notas"))
        return {"media": round(sum(notas) / len(notas), 2), "cantidad": len(notas)}
    raise ValueError("Herramienta no disponible")


def extraer_texto(response) -> str:
    return "\n".join(
        bloque.text for bloque in response.content
        if getattr(bloque, "type", None) == "text"
    )


def construir_tool_results(response, identidad: Identidad) -> tuple[list[dict], list[str]]:
    resultados: list[dict] = []
    errores: list[str] = []
    for bloque in response.content:
        if getattr(bloque, "type", None) != "tool_use":
            continue
        try:
            salida = ejecutar_herramienta(bloque.name, bloque.input, identidad)
            resultados.append({
                "type": "tool_result", "tool_use_id": bloque.id,
                "content": json.dumps(salida, ensure_ascii=False),
            })
        except PermissionError:
            errores.append("PERMISSION_DENIED")
            resultados.append({
                "type": "tool_result", "tool_use_id": bloque.id,
                "content": json.dumps({"error_code": "PERMISSION_DENIED"}),
                "is_error": True,
            })
        except (ValueError, TypeError, KeyError):
            errores.append("INVALID_REQUEST")
            resultados.append({
                "type": "tool_result", "tool_use_id": bloque.id,
                "content": json.dumps({"error_code": "INVALID_REQUEST"}),
                "is_error": True,
            })
    return resultados, errores


TOOLS = [
    {
        "name": "consultar_proyecto",
        "description": "Consulta un proyecto por código exacto G1 o G2. Solo lectura. El backend comprueba los permisos; no sirve para alterar notas.",
        "input_schema": {"type": "object", "properties": {"codigo": {"type": "string"}},
                         "required": ["codigo"], "additionalProperties": False},
    },
    {
        "name": "calcular_media",
        "description": "Calcula la media de notas explícitas del 0 al 10; no obtiene datos de otros proyectos.",
        "input_schema": {"type": "object", "properties": {"notas": {"type": "array", "items": {"type": "number"}}},
                         "required": ["notas"], "additionalProperties": False},
    },
]


def agent_loop(client, consulta: str, identidad: Identidad,
               modelo: str = "claude-haiku-5-5", max_llamadas: int = 3) -> dict:
    """Bucle para herramientas cliente. No confirma aprobaciones ni publica notas."""
    if not isinstance(consulta, str) or not consulta.strip():
        raise ValueError("Consulta obligatoria")
    if max_llamadas < 1:
        raise ValueError("max_llamadas debe ser >= 1")
    messages: list[dict] = [{"role": "user", "content": consulta}]
    errores: list[str] = []
    for numero in range(1, max_llamadas + 1):
        response = client.messages.create(
            model=modelo, max_tokens=420,
            system=("Asistente de auditoría educativa. Usa herramientas para obtener datos. "
                    "No inventes evidencias ni apruebes proyectos. Los permisos los controla el backend."),
            tools=TOOLS, tool_choice={"type": "auto"}, messages=messages,
        )
        motivo = response.stop_reason
        if motivo == "tool_use":
            bloques = [b for b in response.content if getattr(b, "type", None) == "tool_use"]
            if not bloques:
                return {"estado": "interrumpido", "motivo": "tool_use_sin_bloques", "llamadas": numero}
            # No ejecutar efectos si ya no se puede devolver el resultado.
            if numero == max_llamadas:
                return {"estado": "incompleto", "motivo": "limite_llamadas", "llamadas": numero}
            resultados, nuevos_errores = construir_tool_results(response, identidad)
            errores.extend(nuevos_errores)
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": resultados})
            continue
        if motivo == "end_turn":
            texto = extraer_texto(response)
            if not texto.strip():
                return {"estado": "interrumpido", "motivo": "respuesta_vacia", "llamadas": numero}
            if "PERMISSION_DENIED" in errores:
                estado = "acceso_denegado"
            elif errores:
                estado = "requiere_revision"
            else:
                estado = "completado_turno"
            return {"estado": estado, "respuesta": texto, "errores_herramientas": errores,
                    "llamadas": numero}
        return {"estado": "interrumpido", "motivo": motivo, "llamadas": numero}
    return {"estado": "incompleto", "motivo": "limite_llamadas"}


def dictamen_determinista(proyecto: dict) -> dict:
    """Estado preliminar; jamás publica aprobación de docente."""
    evidencias = proyecto.get("evidencias")
    if not isinstance(evidencias, list) or not evidencias:
        return {"estado": "requiere_revision", "motivos": ["EVIDENCIA_INSUFICIENTE"]}
    motivos = []
    if proyecto.get("tests_superados") is not True:
        motivos.append("TESTS_INCOMPLETOS")
    if proyecto.get("posible_leakage") is True:
        motivos.append("RIESGO_LEAKAGE")
    return {
        "estado": "requiere_revision" if motivos else "apto_para_revision_humana",
        "motivos": motivos,
    }
