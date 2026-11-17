import os

from dotenv import load_dotenv
from decimal import Decimal



# Cargar las variables de entorno del archivo .env.
load_dotenv()


ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

CLAUDE_MODEL = "claude-haiku-5-5"

MAX_OUTPUT_TOKENS = 400


if not ANTHROPIC_API_KEY:
    raise RuntimeError(
        "No se encontró ANTHROPIC_API_KEY. "
        "Comprueba el archivo .env."
    )


# Prompts de hasta 100.000 tokens
CLAUDE_INPUT_USD_PER_M = Decimal("0.10")
CLAUDE_OUTPUT_USD_PER_M = Decimal("0.50")

# Prompts superiores a 100.000 tokens
CLAUDE_LONG_INPUT_USD_PER_M = Decimal("0.50")
CLAUDE_LONG_OUTPUT_USD_PER_M = Decimal("2.50")

# Umbral de precios
LONG_CONTEXT_THRESHOLD = 100_000

# Tarifas de caché (contexto normal)
CACHE_WRITE_5M_USD_PER_M = Decimal("0.125")
CACHE_WRITE_1H_USD_PER_M = Decimal("0.20")
CACHE_READ_USD_PER_M = Decimal("0.01")

MAX_COST_PER_CALL = Decimal("0.03")
COST_SAFETY_MARGIN = Decimal("1.20")

API_TIMEOUT = 30.0
API_MAX_RETRIES = 0
