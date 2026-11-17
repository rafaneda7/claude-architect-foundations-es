# DÍA 2 — Arquitectura agéntica y orquestación con Claude

**Curso:** Preparación intensiva CCAR-F · **Dominio principal:** D1 — Agentic Architecture & Orchestration · **Duración:** 4 horas · **Nivel:** Python intermedio, agentes desde cero.

> Este Día 2 profundiza en un subconjunto de D1. No equivale a tener aprobado o completado todo el dominio. Las preguntas de práctica no son oficiales.

## Objetivos de aprendizaje

Al terminar deberías poder explicar por qué un agente es distinto de un workflow, implementar un ciclo `tool_use → tool_result`, conservar el historial, distinguir finalización e interrupción, validar argumentos y permisos, identificar patrones de orquestación y justificar cuándo NO conviene usar varios agentes.

## Plan de 4 horas

| Bloque | Duración | Qué se aprende |
|---|---:|---|
| 1 · Fundamentos | 35 min | LLM, workflow, agente, decisión frente a ejecución |
| 2 · Protocolo | 45 min | `tool_use`, `tool_result`, `stop_reason`, historial |
| 3 · Laboratorio | 80 min | SDK, agente real, pruebas y fallos seguros |
| 4 · Orquestación | 30 min | Chaining, routing, parallelization, coordinator-workers, evaluator-optimizer |
| 5 · Arquitectura | 20 min | Seguridad, contexto, observabilidad, costes |
| 6 · Repaso y test | 30 min | Preguntas y diseño razonado |

## 1. Del LLM al agente

### LLM simple

Entrada: “Explica qué es overfitting”. Backend → Claude → texto. El modelo genera una respuesta; no necesita ejecutar herramientas ni coordinar pasos externos.

### Workflow

Un workflow sigue pasos predeterminados: subir CSV → validar columnas → ejecutar tests → producir informe. El orden lo establece el programa, aunque uno o más pasos puedan consultar un modelo.

### Agente

Un agente utiliza el modelo para seleccionar dinámicamente pasos o herramientas a partir del objetivo y sus resultados. Ejemplo: “Investiga por qué mi pipeline de ML obtiene 99,9 % de accuracy”. Podría inspeccionar particiones, métricas y transformaciones, según lo que encuentre.

**Pregunta arquitectónica:** ¿el siguiente paso está predefinido por el código o se elige basándose en el resultado anterior?

| Rasgo | LLM simple | Workflow | Agente |
|---|---|---|---|
| Próximos pasos | No hacen falta | Programados | Elegidos dinámicamente dentro de límites |
| Herramientas externas | Opcionales | Opcionales | A menudo centrales |
| Control de operaciones | Backend | Backend | Backend siempre autoriza y ejecuta las herramientas de cliente |
| Coste/complejidad | Habitualmente menor | Más predecible | Potencialmente mayor |

**Ejercicio A:** clasifica y justifica: (1) resumir una FAQ, (2) procesar 100 CSV iguales, (3) diagnosticar fallo de origen desconocido, (4) separar tickets entre departamentos.

## 2. Contrato de las herramientas

La herramienta no es una función que Claude “ejecuta mágicamente”. Tu aplicación ofrece un contrato; Claude produce una petición estructurada; tu backend valida y ejecuta; el resultado regresa al contexto del modelo.

Ejemplo de declaración de herramienta:

```python
{
    "name": "calcular_media",
    "description": "Calcula la media aritmética de notas entre 0 y 10",
    "input_schema": {
        "type": "object",
        "properties": {
            "notas": {"type": "array", "items": {"type": "number"}}
        },
        "required": ["notas"]
    }
}
```

- `name` identifica la herramienta.
- `description` le indica al modelo cuándo usarla.
- `input_schema` describe argumentos; **NO** sustituye la validación del backend.
- `tool_use.id` identifica **una solicitud concreta**, no una herramienta en general.

### Ciclo manual completo

1. Mensaje inicial del usuario.
2. `client.messages.create(..., tools=HERRAMIENTAS, messages=mensajes)`.
3. Claude devuelve `stop_reason="tool_use"` y un bloque con `id`, `name`, `input`.
4. Guardas **toda la respuesta** de Claude en el historial como `role="assistant"`.
5. Ejecutas cada herramienta con validación y permisos.
6. Devuelves sus resultados con `role="user"` y bloques `tool_result` que coinciden en `tool_use_id`.
7. Solicitas el siguiente turno con el historial actualizado.
8. Si devuelve `end_turn`, el turno terminó normalmente; si retorna otra razón, manejas esa condición.

```text
Usuario: "Consulta G1 y calcula la media de 7, 8, 9"
               |
               v
Claude: tool_use(id=toolu_A, name=consultar_proyecto, input={grupo:G1})
        tool_use(id=toolu_B, name=calcular_media, input={notas:[7,8,9]})
               |
               v
Backend: valida y ejecuta AMBAS herramientas
               |
               v
Usuario (mensaje de protocolo, no humano):
    tool_result(tool_use_id=toolu_A, content=...)
    tool_result(tool_use_id=toolu_B, content=...)
               |
               v
Claude: "G1 está en revisión; la media es 8.0" (end_turn)
```

El `role="user"` del `tool_result` viene del contrato de Messages API. **No significa que un humano haya escrito el resultado**.

### `stop_reason` en la práctica

| Valor | Interpretación | Comportamiento |
|---|---|---|
| `tool_use` | Herramienta de cliente pendiente | Ejecutar las peticiones y devolver resultados |
| `end_turn` | Finalizó normalmente | Mostrar resultado, aun si el texto está vacío |
| `max_tokens` | Salida truncada por límite de tokens | No declarar éxito; revisar truncamiento/continuación |
| `pause_turn` | Pausa en ciclo de herramientas del servidor | Continuación según documentación; no confundir con `tool_use` |
| `stop_sequence` | Se activó secuencia programada | Aplicar contrato de tu app |
| `refusal` | Rechazo | Gestionar rechazo |
| `model_context_window_exceeded` | Límite de contexto | Tratar respuesta como truncada |

**Error habitual:** declarar éxito cuando la variable `iteracion` llega al máximo. Eso solo significa que el backend dejó de llamar al modelo.

### Bloques no textuales

`response.content` puede tener bloques `text` y `tool_use`. Tu extracción de texto debe filtrar por `block.type == "text"`. Cuando no haya ningún bloque textual, devolver `""` es válido para la función de extracción, pero la aplicación debe mirar también `stop_reason`.

**Ejercicio B:** Claude responde con texto «Voy a consultar» y `tool_use(id="toolu_47")`. ¿Se ha completado? ¿Por qué no se debe mostrar solo el texto? ¿Qué ID debe acompañar el `tool_result`?

## 3. Laboratorio en VS Code usando tu API

### Estructura sugerida en tu repositorio

```text
claude_architect/
├── .venv/
└── Ckeckpoints/
    ├── Dia1/
    └── Dia2/
        ├── agente_dia2.py
        ├── test_agente_dia2.py
        └── CHECKPOINT_02.md
```

Reutiliza tu `.venv` de la raíz si ya funciona. En **Git Bash** desde `claude_architect`:

```bash
source .venv/Scripts/activate
python -m pip install --upgrade anthropic
mkdir -p Ckeckpoints/Dia2
```

Configura la variable de entorno sin escribir la clave en el archivo ni pegarla en el chat:

```bash
read -rs -p "API Key de Claude: " ANTHROPIC_API_KEY; echo
export ANTHROPIC_API_KEY
```

La clave estará disponible durante esa sesión del terminal. Confirma sin imprimir su valor:

```bash
python -c 'import os; print(bool(os.getenv("ANTHROPIC_API_KEY")))'
```

**Nota sobre los 5 USD de saldo:** emplearemos inicialmente Haiku 5.5, límites conservadores (`MAX_LLAMADAS=4` y `max_tokens=512`) y registro de tokens. Eso **no es un tope duro de facturación**. Revisa el panel de uso de Anthropic. Los precios dependen del modelo, longitud del prompt, caching y otras funciones. La API real no se ha ejecutado al elaborar este material.

### Archivo 1 — `agente_dia2.py`

Código didáctico ejecutable:

```python
"""Ejemplo didáctico: bucle de herramientas de cliente con Claude.

No ejecuta llamadas a la API al importarse. Ejecutar directamente para la práctica real.
"""
import json
import math
import os

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

```

### Archivo 2 — `test_agente_dia2.py`

Estos tests **no utilizan la API** y comprueban que el backend no confíe en argumentos de Claude sin validarlos.

```python
import unittest
from types import SimpleNamespace
from agente_dia2 import ejecutar_herramienta, extraer_texto, crear_resultados


class TestDia2(unittest.TestCase):
    def test_media(self):
        self.assertEqual(ejecutar_herramienta("calcular_media", {"notas": [7, 8, 9]}, "ta_demo")["media"], 8)

    def test_media_vacia(self):
        with self.assertRaises(ValueError):
            ejecutar_herramienta("calcular_media", {"notas": []}, "ta_demo")

    def test_bool_no_es_nota(self):
        with self.assertRaises(ValueError):
            ejecutar_herramienta("calcular_media", {"notas": [True, 7]}, "ta_demo")

    def test_permiso_valido(self):
        self.assertEqual(ejecutar_herramienta("consultar_proyecto", {"grupo": "G1"}, "ta_demo")["nota"], 8.5)

    def test_permiso_denegado(self):
        with self.assertRaises(PermissionError):
            ejecutar_herramienta("consultar_proyecto", {"grupo": "G3"}, "ta_demo")

    def test_nombre_desconocido(self):
        with self.assertRaises(ValueError):
            ejecutar_herramienta("borrar_todo", {}, "ta_demo")

    def test_extraer_texto(self):
        response = SimpleNamespace(content=[SimpleNamespace(type="text", text="hola"), SimpleNamespace(type="tool_use")])
        self.assertEqual(extraer_texto(response), "hola")

    def test_texto_vacio(self):
        response = SimpleNamespace(content=[SimpleNamespace(type="tool_use")])
        self.assertEqual(extraer_texto(response), "")

    def test_error_tool_result(self):
        response = SimpleNamespace(content=[SimpleNamespace(type="tool_use", name="consultar_proyecto", id="toolu_fake", input={"grupo": "G3"})])
        results = crear_resultados(response, "ta_demo")
        self.assertEqual(results[0]["tool_use_id"], "toolu_fake")
        self.assertTrue(results[0]["is_error"])

    def test_multiples_tool_results(self):
        response = SimpleNamespace(content=[
            SimpleNamespace(type="tool_use", name="consultar_proyecto", id="toolu_1", input={"grupo": "G1"}),
            SimpleNamespace(type="tool_use", name="calcular_media", id="toolu_2", input={"notas": [7, 9]})
        ])
        results = crear_resultados(response, "ta_demo")
        self.assertEqual([r["tool_use_id"] for r in results], ["toolu_1", "toolu_2"])

if __name__ == "__main__":
    unittest.main()

```

### Cómo ejecutar

Sitúate en la carpeta del Día 2, con el entorno activo:

```bash
python -m unittest -v
```

**Resultado esperado:** 10 pruebas locales correctas. El código de estas pruebas sí se ha ejecutado y verificado localmente al preparar este material.

Para hacer la llamada **real** a Claude:

```bash
python agente_dia2.py
```

**Salida orientativa** (el modelo podría escoger otros pasos):

```text
Llamada 1 | stop_reason=tool_use | ...
Herramienta solicitada: consultar_proyecto
Herramienta solicitada: calcular_media
Llamada 2 | stop_reason=end_turn | ...
{
  "estado": "completado",
  "texto": "El proyecto G1 está en revisión y la media es 8.0.",
  "tokens_entrada": ...,
  "tokens_salida": ...
}
```

La salida exacta, el número de llamadas y el consumo varían. Si el modelo responde sin llamar a herramientas, eso también es una señal para investigar: ¿la pregunta realmente requería consulta? ¿Conviene `tool_choice` en una prueba controlada?

### Qué revisar en el código

1. `PERMISOS`: G3 no está autorizado para `ta_demo`.
2. `ejecutar_herramienta`: sólo ejecuta las dos herramientas de una lista blanca.
3. `math.isfinite`: evita `NaN` e infinitos en notas.
4. `isinstance(n, bool)`: excluye booleanos (en Python, `bool` es subclase de `int`).
5. `crear_resultados`: procesa **todos** los bloques `tool_use` y conserva cada ID.
6. `mensajes.append({"role": "assistant", ...})`: conserva el turno de solicitud.
7. `mensajes.append({"role": "user", ...})`: devuelve los resultados.
8. `MAX_LLAMADAS`: controla duración, pero no garantiza finalización.
9. `usage`: registra tokens, no implica cálculo automático de costes.
10. `APIError`: se devuelve un estado de error sin proclamar éxito ni exponer credenciales.

### Prácticas adicionales

**Práctica 1:** pide acceso a G3 como `ta_demo` y documenta el resultado; después prueba como `mentor_demo`.

**Práctica 2:** añade `calcular_maximo` con `notas` no vacías y valores 0–10, más tres tests (normal, lista vacía, booleano).

**Práctica 3:** añade `G4`, pero no concedas acceso a `ta_demo`. Prueba que Claude no pueda eludir el permiso con una instrucción en lenguaje natural.

**Práctica 4:** cambia `MAX_LLAMADAS` a 1. Documenta por qué el estado `incompleto` no equivale a un resultado correcto.

**Práctica 5:** registra eventos en `logging`, incluyendo nombre de herramienta y resultado operativo, sin almacenar claves ni datos privados innecesarios.

## 4. Patrones de orquestación

### Prompt chaining

Secuencia definida: extraer contenido → estructurar datos → validar → informar. Útil cuando los pasos dependen unos de otros y su orden se conoce.

### Routing

Clasificar una petición y enviarla al flujo adecuado: preguntas Python al flujo Python, dudas SQL al flujo SQL. La ruta se elige, pero el flujo posterior puede ser determinista.

### Parallelization

Procesar subtareas independientes al mismo tiempo: revisar documentación, tests y estilo. Puede mejorar latencia, pero no debe paralelizar pasos con dependencias o efectos secundarios incompatibles.

### Orchestrator–workers

Un coordinador descompone dinámicamente una tarea y delega a especialistas según los hallazgos. Ejemplo: inspeccionar un repositorio desconocido, donde no sabes de antemano qué módulos serán problemáticos.

### Evaluator–optimizer

Un generador propone una solución; otro componente la evalúa según una rúbrica; se corrige hasta cumplir criterios o alcanzar un presupuesto/límite de iteraciones.

| Patrón | Pregunta de diseño |
|---|---|
| Prompt chaining | ¿Conozco de antemano la secuencia? |
| Routing | ¿Necesito seleccionar entre flujos? |
| Parallelization | ¿Son realmente independientes las tareas? |
| Orchestrator–workers | ¿La descomposición depende de los hallazgos? |
| Evaluator–optimizer | ¿Tengo una rúbrica verificable para iterar? |

### Subagentes y contexto

No supongas que los subagentes tienen automáticamente el contexto del coordinador. Un contrato de delegación debería incluir:

```python
tarea = {
    "objetivo": "Revisar el modelo de clasificación",
    "archivos_autorizados": ["src/modelo.py", "tests/test_modelo.py"],
    "criterios": ["métricas", "data leakage", "reproducibilidad"],
    "restricciones": ["solo lectura", "sin acceso a otros alumnos"],
    "salida": ["hallazgo", "evidencia", "severidad", "recomendacion"]
}
```

**Ejercicio C:** diseña un sistema de dos subagentes y un coordinador para evaluar un proyecto final. Describe inputs/outputs, permisos, cómo combinar resultados y cuándo declarar la evaluación incompleta.

## 5. Arquitectura fiable y segura

```text
Usuario autenticado
       |
       v
Frontend (solicitud, nunca clave privada)
       |
       v
Backend (sesión, autorización, validación)
       |
       +----> PostgreSQL (datos autorizados / persistencia)
       |
       +----> Claude Messages API (decisión y generación)
                      |
                      v
               tool_use solicitado
                      |
                      v
         Backend ejecuta herramienta permitida
                      |
                      v
            tool_result a Claude
                      |
                      v
             end_turn / interrupción
                      |
                      v
           Validar, registrar, responder
```

- **Aislamiento:** el usuario autenticado sólo puede acceder a sus recursos permitidos; un ID en un prompt no concede permisos.
- **Validación:** parámetros de la herramienta se tratan como datos no confiables.
- **Persistencia:** el backend guarda los mensajes y puede recuperar el contexto adecuado. Claude no conserva por sí solo una base de datos de sesiones.
- **Observabilidad:** registra etapa, estado, duración, tokens, errores y herramientas utilizadas; no reveles secretos.
- **Fiabilidad:** diferencia `completado`, `incompleto`, `interrumpido` y `error_api`.
- **Costes:** limita las llamadas y la salida; un límite de iteraciones no es un límite financiero garantizado. Las llamadas repetidas pueden volver a incluir el historial acumulado.
- **Tool results:** considera que el contenido de una herramienta externa también puede ser malicioso; no conviertas instrucciones de los resultados en permisos del sistema.

**Ejercicio D:** ¿qué falla si `usuario_id` se toma de un parámetro enviado libremente por el frontend? ¿Cómo lo corregirías?

## 6. Evaluación del Día 2 (100 puntos; sin respuestas)

### Parte A · 10 preguntas tipo test (40 puntos)

**A1.** Claude devuelve `stop_reason="tool_use"` y un bloque `text`. El backend debe: (A) finalizar; (B) procesar herramientas y continuar; (C) borrar historial; (D) mostrar el texto como único resultado.

**A2.** El campo que permite relacionar el resultado de una herramienta con su solicitud concreta es: (A) `model`; (B) `usage`; (C) `tool_use_id`; (D) `max_tokens`.

**A3.** Si la herramienta consulta datos académicos, el permiso debe comprobarse: (A) solo en prompt; (B) en frontend; (C) en backend antes del acceso; (D) después de publicar resultados.

**A4.** `end_turn` indica: (A) turno terminado normalmente; (B) herramienta pendiente; (C) contexto perdido; (D) solicitud siempre facturada al máximo.

**A5.** Se alcanza el límite de iteraciones sin `end_turn`: (A) tarea completada; (B) estado incompleto; (C) no ocurrió ninguna llamada; (D) permiso autorizado.

**A6.** ¿Cuándo conviene un workflow fijo? (A) pasos conocidos y previsibles; (B) investigación cuyo siguiente paso es desconocido; (C) nunca; (D) solo para tareas sin Python.

**A7.** ¿Cuál es el patrón de revisión iterativa según rúbrica? (A) routing; (B) evaluator–optimizer; (C) parallelization; (D) una sola llamada sin herramientas.

**A8.** Claude devuelve dos bloques `tool_use`: (A) ejecutar uno solamente; (B) devolver ambos sin ejecutar; (C) procesar cada uno y devolver resultados con IDs; (D) convertirlos automáticamente en texto.

**A9.** ¿Qué debe enviarse a un subagente con contexto aislado? (A) solo su nombre; (B) objetivo, contexto autorizado, restricciones y contrato de salida; (C) clave privada; (D) acceso ilimitado.

**A10.** La presencia de un bloque `tool_use` significa: (A) que la herramienta ya se ejecutó en tu backend; (B) que Claude ha solicitado la acción, no que tu backend la haya ejecutado; (C) que la tarea finalizó; (D) que no hace falta validar parámetros.

### Parte B · Razonamiento técnico (30 puntos)

**B1 — 10 puntos:** explica el ciclo completo de `tool_use → tool_result → end_turn`, incluyendo roles, contenido del historial y varios resultados de herramienta.

**B2 — 10 puntos:** una aplicación termina tras cuatro llamadas y siempre devuelve `estado="completado"`. Explica el error y propón una corrección.

**B3 — 10 puntos:** compara un workflow fijo con un sistema coordinator–workers. Da un ejemplo donde cada uno resulte apropiado y analiza el coste de sobreingeniería.

### Parte C · Diseño arquitectónico (20 puntos)

Un bootcamp quiere corregir proyectos de Data Science usando Claude. Debe comprobar permisos por alumno, leer archivos autorizados, ejecutar tests, revisar métricas, detectar riesgos de fuga de datos, registrar uso y no publicar notas cuando la ejecución sea incompleta. Propón arquitectura, herramientas, patrón, flujo de mensajes, estados de finalización y controles de seguridad.

### Parte D · Python (10 puntos)

Sin consultar el ejemplo del laboratorio, implementa:

```python
def construir_resultados(response, usuario_id) -> list[dict]:
    """Procesa todos los tool_use; valida permisos; devuelve tool_result con id y errores."""
    # Tu código aquí
    pass
```

**Rúbrica:** A=40, B=30, C=20, D=10. Objetivo didáctico: 85/100 (no es nota oficial). Resuelve primero, corrige después.

## CHECKPOINT 02 — Para pegar en VS Code

```markdown
# CHECKPOINT 02 — Agentic Architecture (D1)

- [ ] Distingo LLM, workflow y agente.
- [ ] Entiendo la diferencia entre decidir y ejecutar.
- [ ] Explico tool_use, tool_result e IDs.
- [ ] Mantengo correctamente el historial.
- [ ] Manejo varios tool_use por respuesta.
- [ ] Distingo end_turn, max_tokens y límites de iteraciones.
- [ ] Ejecuto 10 pruebas locales correctamente.
- [ ] Pruebo una petición real con Claude (si la cuenta lo permite).
- [ ] Compruebo autorización y validación.
- [ ] Comparo patrones de orquestación.
- [ ] Diseño subagentes con contexto explícito.
- [ ] Registro tokens sin exponer credenciales.

Nota de evaluación: ___ / 100
Errores pendientes:
1.
2.
3.
Próxima acción:
```

## Documentación oficial

- [Cómo funciona Tool Use](https://platform.claude.com/docs/es/agents-and-tools/tool-use/how-tool-use-works)
- [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls)
- [Stop reasons](https://platform.claude.com/docs/es/build-with-claude/handling-stop-reasons)
- [Modelos y precios](https://platform.claude.com/docs/es/models/overview)
- [Tarifas de la API](https://platform.claude.com/docs/en/about-claude/pricing)
