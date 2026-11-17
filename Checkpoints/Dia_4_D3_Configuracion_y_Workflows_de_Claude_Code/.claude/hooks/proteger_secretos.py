"""Hook didáctico de PreToolUse para impedir Edit/Write de archivos sensibles.

Lee el evento JSON completo por stdin; imprime permiso deny si corresponde.
No reemplaza un sandbox, permisos administrados ni protección en el SO.
"""
from pathlib import PurePosixPath
import json
import sys


def nombre_archivo(ruta: str) -> str:
    """Normaliza separadores POSIX/Windows para examinar el nombre final."""
    return PurePosixPath(ruta.replace("\\", "/")).name.casefold()


def decidir(evento: dict) -> dict | None:
    """Devuelve decisión de denegación o None si aplica la política normal."""
    if evento.get("tool_name") not in {"Write", "Edit"}:
        return None
    entrada = evento.get("tool_input") or {}
    ruta = entrada.get("file_path")
    if not isinstance(ruta, str):
        return {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Falta la ruta del archivo"
        }}
    nombre = nombre_archivo(ruta)
    if nombre == ".env" or nombre.startswith(".env.") or nombre in {"credentials.json", "secrets.json"}:
        return {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "No modificar archivos de secretos con Write o Edit"
        }}
    return None


def main() -> int:
    try:
        evento = json.load(sys.stdin)
        if not isinstance(evento, dict):
            raise ValueError("Evento no es objeto JSON")
    except (ValueError, json.JSONDecodeError):
        # Fallar cerrado dentro del alcance Write/Edit de este hook.
        evento = {"tool_name": "Write", "tool_input": {}}
    decision = decidir(evento)
    if decision:
        print(json.dumps(decision, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
