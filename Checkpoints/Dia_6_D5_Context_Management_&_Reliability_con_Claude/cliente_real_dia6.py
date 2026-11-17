"""Una llamada opcional a Claude; por defecto no consume tokens."""
from __future__ import annotations

import argparse
import os
from contexto_dia6 import Conversacion, Documento, Incidencia, agregar_incidencia, crear_contexto


def preparar_ejemplo() -> list[dict]:
    conversacion = Conversacion(
        conversacion_id="conv_demo_1",
        propietario_id="alumno_demo",
        resumen="El usuario preguntó por dos incidencias de una compra ficticia.",
        mensajes_recientes=[
            {"role": "user", "content": "¿Qué ocurre con mi devolución?"},
            {"role": "assistant", "content": "Revisaré el estado registrado."},
        ],
    )
    agregar_incidencia(conversacion, "alumno_demo", Incidencia(
        incidencia_id="INC-001", usuario_id="alumno_demo",
        descripcion="Devolución de cuaderno", estado="abierto",
        importe="12.50", fecha="2026-11-10", fuente="sistema_demo",
        siguiente_paso="Verificar recepción del paquete"))
    docs = [Documento("DOC-1", "alumno_demo",
                      "La devolución INC-001 sigue pendiente de recepción.",
                      ("devolución", "recepción"), "2026-11-11"),
            Documento("DOC-2", "otra_persona", "Dato privado de otro usuario", ("devolución",))]
    return crear_contexto(conversacion, "alumno_demo",
                         "¿Qué se sabe de la devolución INC-001 y cuál es el siguiente paso?", docs)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--real", action="store_true", help="Hacer una llamada de pago a Claude")
    args = parser.parse_args()
    messages = preparar_ejemplo()

    if not args.real:
        print("MODO DEMO: no se ha llamado a Claude.")
        print("Mensajes de contexto preparados:", len(messages))
        print("Para llamar a Claude: python cliente_real_dia6.py --real")
        return

    if not os.getenv("ANTHROPIC_API_KEY"):
        raise SystemExit("Falta ANTHROPIC_API_KEY")

    import anthropic
    client = anthropic.Anthropic(max_retries=0, timeout=30.0)
    modelo = os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5")

    try:
        cuenta = client.messages.count_tokens(
            model=modelo,
            system=("Eres un asistente de soporte con acceso solo a datos ficticios. "
                    "No inventes hechos; indica la fuente y las limitaciones."),
            messages=messages,
        )
        print("Tokens estimados de entrada:", cuenta.input_tokens)
        if cuenta.input_tokens > 2500:
            raise SystemExit("Contexto excesivo para esta práctica (>2500 tokens)")

        response = client.messages.create(
            model=modelo, max_tokens=300,
            system=("Eres un asistente de soporte con acceso solo a datos ficticios. "
                    "No inventes hechos; indica la fuente y las limitaciones."),
            messages=messages,
        )
        print("stop_reason:", response.stop_reason)
        if response.stop_reason != "end_turn":
            print("No completado; no publicar como resolución confirmada.")
            return
        texto = "\n".join(b.text for b in response.content if b.type == "text")
        if not texto.strip():
            print("Sin respuesta textual utilizable.")
            return
        print("\nRESPUESTA:\n", texto)
        print("Tokens de entrada/salida:", response.usage.input_tokens, response.usage.output_tokens)
    except anthropic.AuthenticationError:
        print("No autenticado: verifica credenciales sin mostrarlas")
    except anthropic.RateLimitError:
        print("Límite de uso o de gasto: consulta detalles en la consola; no reintentar a ciegas")
    except anthropic.APIError as err:
        print("Error de API:", type(err).__name__)


if __name__ == "__main__":
    main()
