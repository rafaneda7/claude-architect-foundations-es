"""Mock sin coste; --real hace como máximo 3 llamadas a tu API Anthropic."""
from __future__ import annotations
import argparse
import json
import os
from types import SimpleNamespace

from motor_dia7 import Identidad, agent_loop


def bloque(**campos):
    return SimpleNamespace(**campos)


class RespuestasSimuladas:
    def __init__(self, respuestas):
        self.respuestas = iter(respuestas)
        self.llamadas = 0
        self.historiales = []

    def create(self, **kwargs):
        self.llamadas += 1
        self.historiales.append(kwargs["messages"])
        return next(self.respuestas)


class ClienteSimulado:
    def __init__(self):
        self.messages = RespuestasSimuladas([
            bloque(stop_reason="tool_use", content=[
                bloque(type="text", text="Voy a consultar G1."),
                bloque(type="tool_use", id="toolu_demo", name="consultar_proyecto",
                       input={"codigo": "G1"}),
            ]),
            bloque(stop_reason="end_turn", content=[
                bloque(type="text", text="G1: pruebas superadas; la revisión humana sigue siendo necesaria.")
            ]),
        ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--real", action="store_true", help="Hace llamadas facturables a Claude")
    args = parser.parse_args()
    identidad = Identidad(usuario_id="alumno_a", rol="alumno")
    if args.real:
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise SystemExit("Falta ANTHROPIC_API_KEY")
        from anthropic import Anthropic
        client = Anthropic(timeout=30, max_retries=0)
    else:
        client = ClienteSimulado()
    resultado = agent_loop(
        client, "Consulta G1. Explica los hallazgos sin aprobar ni modificar notas.",
        identidad=identidad, max_llamadas=3,
    )
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
