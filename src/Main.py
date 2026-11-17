from anthropic import Anthropic

from config import API_KEY, MODEL, MAX_OUTPUT_TOKENS


client = Anthropic(
    api_key=API_KEY
)

SYSTEM_PROMPT = """
Eres un asistente especializado en Data Science
y arquitectura de aplicaciones con inteligencia artificial.

Tus responsabilidades son:

1. Explicar conceptos técnicos.
2. Utilizar ejemplos de Python.
3. Responder en español.
4. Diferenciar hechos de suposiciones.
5. No inventar información.
6. Reconocer cuando no dispones de datos suficientes.

Utiliza un lenguaje técnico y pedagógico.
"""

response = client.messages.create(
    model=MODEL,
    max_tokens=MAX_OUTPUT_TOKENS,
    system=SYSTEM_PROMPT,
    messages=[
        {
            "role": "user",
            "content": "Explícame qué es un LLM."
        }
    ]
)

for block in response.content:

    if block.type == "text":

        print(block.text)