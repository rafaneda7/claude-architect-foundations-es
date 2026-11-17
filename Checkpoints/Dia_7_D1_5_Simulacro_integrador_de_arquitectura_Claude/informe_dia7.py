"""Informe JSON posterior a una consulta autorizada. No publica aprobaciones."""
from __future__ import annotations
import json
from typing import Any

SCHEMA = {
    "type": "object",
    "properties": {
        "codigo": {"type": "string"},
        "estado": {"type": "string", "enum": ["apto_para_revision_humana", "requiere_revision"]},
        "hallazgos": {"type": "array", "items": {"type": "string"}},
        "evidencias": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["codigo", "estado", "hallazgos", "evidencias"],
    "additionalProperties": False,
}


def validar_informe(informe: dict[str, Any], proyecto: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(informe, dict):
        raise ValueError("Se esperaba objeto JSON")
    if set(informe) != {"codigo", "estado", "hallazgos", "evidencias"}:
        raise ValueError("Campos inesperados o ausentes")
    if informe["codigo"] != proyecto["codigo"]:
        raise ValueError("Código distinto del proyecto autorizado")
    if informe["estado"] not in ("apto_para_revision_humana", "requiere_revision"):
        raise ValueError("Estado inválido")
    if not isinstance(informe["hallazgos"], list) or any(not isinstance(x,str) for x in informe["hallazgos"]):
        raise ValueError("Hallazgos inválidos")
    if not isinstance(informe["evidencias"], list) or not informe["evidencias"]:
        raise ValueError("Evidencias insuficientes")
    if any(e not in proyecto["evidencias"] for e in informe["evidencias"]):
        raise ValueError("Evidencia inventada")
    if informe["estado"] == "apto_para_revision_humana":
        if proyecto["tests_superados"] is not True or proyecto["posible_leakage"] is True:
            raise ValueError("No se puede presentar como apto")
    return informe


def obtener_informe_json(client, proyecto: dict[str, Any], modelo="claude-haiku-5-5") -> dict:
    """Una llamada facturable si se invoca con cliente Anthropic real."""
    response = client.messages.create(
        model=modelo, max_tokens=450,
        system="Elabora un informe preliminar usando solo el JSON proporcionado. No inventes evidencias ni apruebes notas.",
        messages=[{"role": "user", "content": json.dumps(proyecto, ensure_ascii=False)}],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
    )
    if response.stop_reason != "end_turn":
        raise ValueError(f"Respuesta no completada: {response.stop_reason}")
    texto="".join(b.text for b in response.content if getattr(b, "type", None)=="text")
    if not texto.strip():
        raise ValueError("Respuesta vacía")
    try:
        informe=json.loads(texto)
    except json.JSONDecodeError as e:
        raise ValueError("JSON inválido") from e
    return validar_informe(informe, proyecto)
