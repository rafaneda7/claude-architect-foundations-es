# DÍA 7 — Simulacro integrador de arquitectura Claude (D1–D5)

> **CCAR-F · Claude Certified Architect – Foundations**  
> **Tipo:** jornada integradora y resolución de escenarios  
> **Duración prevista:** 4 horas  
> **Tecnología:** Python 3.12, VS Code, Git Bash, SDK Anthropic  
> **Prácticas:** simulador local sin coste; API real opcional  
> **Evaluación:** 100 puntos (40 + 30 + 20 + 10) con solucionario

## Qué cambia respecto a los seis primeros días

En los Días 1–6 se estudiaron los fundamentos y dominios por separado. Hoy importa conectarlos. Una arquitectura puede utilizar bien `tool_use`, pero seguir siendo incorrecta si expone datos de otro usuario, interpreta un `max_tokens` como éxito, inventa evidencias o acepta una respuesta JSON válida con información falsa.

**Regla de la jornada:** distinguir la finalización del turno del modelo, el resultado de las herramientas y el estado real de la tarea. No son lo mismo.

Esta práctica está inspirada en los dominios del temario, **no contiene preguntas oficiales ni reproduce escenarios de examen**.

| Dominio | Peso de referencia del temario | Aplicación en Día 7 |
|---|---:|---|
| D1 · Agentic Architecture & Orchestration | 27 % | Decidir entre workflow, agente y coordinador |
| D2 · Tool Design & MCP Integration | 18 % | Contratos, herramientas y permisos |
| D3 · Claude Code Configuration & Workflows | 20 % | CLAUDE.md, pruebas, hooks y CI |
| D4 · Prompt Engineering & Structured Output | 20 % | JSON Schema, evidencia, validación |
| D5 · Context Management & Reliability | 15 % | Contexto, aislamiento, límites y escalamiento |

## Plan de 4 horas

| Módulo | Tiempo | Contenido |
|---|---:|---|
| 1 | 35 min | Decisiones arquitectónicas con escenarios |
| 2 | 40 min | Diseñar un sistema de evaluación fiable |
| 3 | 75 min | Laboratorio Python integrador y API opcional |
| 4 | 35 min | Depuración, fiabilidad y salida JSON |
| 5 | 35 min | Ejercicios integradores y soluciones |
| 6 | 20 min | Evaluación de 100 puntos y criterios de corrección |

## Objetivos

- [ ] Elegir el diseño más sencillo que cumpla los requisitos.
- [ ] Diferenciar decisión del modelo y ejecución del backend.
- [ ] Mantener identidad y autorización fuera del control de Claude.
- [ ] Conservar los IDs de `tool_use` y `tool_result`.
- [ ] Distinguir `end_turn` de éxito de negocio.
- [ ] Procesar errores sin transformarlos en resultados vacíos.
- [ ] Garantizar que JSON válido tenga respaldo en fuentes autorizadas.
- [ ] Mantener hechos críticos y resultados de herramientas en contexto.
- [ ] Implementar tests locales que no consuman saldo.
- [ ] Justificar decisiones D1–D5 en escenarios escritos.

---

# MÓDULO 1 — Decisiones arquitectónicas

## 1.1. Seleccionar la arquitectura por requisitos

**LLM sencillo:** responde a una petición estable basada en contexto suficiente.  
**Workflow:** secuencia conocida, verificable y mayoritariamente determinista.  
**Agente:** el modelo decide algunos pasos posteriores a partir de observaciones.  
**Coordinador con trabajadores:** distribuye tareas especializadas, valida sus resultados y sintetiza hallazgos. Solo se justifica si ofrece una mejora medible.

| Problema | Diseño preferente | Motivo |
|---|---|---|
| Calcular la media de una lista conocida | Python directo | No necesita LLM |
| Validar 40 CSV idénticos | Workflow | Pasos estables |
| Investigar una causa desconocida de data leakage | Agente con herramientas de lectura | El próximo paso depende de lo encontrado |
| Auditar un repositorio grande y heterogéneo | Coordinador y subagentes, si aporta valor | Especialización y trabajo independiente |
| Publicar notas finales | Backend y autorización humana | Operación de alto impacto que no debe depender de una decisión textual del modelo |

### 1.2. ¿Quién hace qué?

```text
Alumno o profesor
      │
      ▼
Frontend
      │
      ▼
Backend ─────── autenticación + autorización
      │
      ├──────── PostgreSQL / archivos autorizados
      │
      ├──────── Claude Messages API ───→ tool_use
      │                              │
      └─ ejecutor de herramientas ←──┘
                  │
                  └────── tool_result → Claude
                                    │
                                    ▼
                        propuesta de respuesta
                                    │
                                    ▼
                  validación, registro y estado
```

- **Inferencia:** Claude genera texto o solicitudes estructuradas.
- **Ejecución:** el backend ejecuta herramientas permitidas y aplica reglas.
- **Persistencia:** el backend conserva datos en una base de datos.
- **Autorización:** el backend impide acceso a datos de terceros.
- **Estado de negocio:** se obtiene de operaciones verificadas, no de frases del LLM.

### 1.3. Tres estados que no deben mezclarse

1. **Turno finalizado:** `stop_reason == "end_turn"`.
2. **Herramienta ejecutada con éxito:** hay un `tool_result` sin `is_error` y el sistema verificó su resultado.
3. **Tarea de negocio completada:** el backend verificó que todos los requisitos se cumplen y puede publicar o confirmar la operación.

Un `end_turn` puede terminar con un mensaje de denegación, un resumen de error o una respuesta sin información suficiente. Por tanto, **`end_turn` no equivale a una aprobación ni a una operación completada**.

## Ejercicio 1 — Elegir arquitectura

Clasifica y justifica:

1. Corregir sintaxis de una docena de CSV con columnas conocidas.
2. Inspeccionar un modelo con `accuracy=0.999` cuya causa se desconoce.
3. Determinar si un alumno puede leer el proyecto G2.
4. Generar feedback del proyecto a partir de tests y métricas previamente verificadas.
5. Auditar 50 proyectos independientes durante la noche.

**No mires el solucionario del Módulo 5 hasta responder.**

---

# MÓDULO 2 — Caso integrador: evaluación de proyectos de Data Science

## 2.1. El encargo

La escuela dispone de proyectos con notas, métricas, pruebas unitarias y evidencias. Los alumnos solo deben ver los suyos; cada profesor ve los grupos asignados. Claude puede consultar proyectos y explicar hallazgos, pero **no puede modificar notas ni aprobar entregas por su cuenta**.

Los resultados deben ser auditables y no se pueden inventar evidencias. La interfaz debe informar si una revisión está completa, incompleta o denegada.

### Datos de práctica

```json
{
  "G1": {
    "titulo": "Predicción de ventas",
    "propietario": "alumno_a",
    "tests_superados": true,
    "posible_leakage": false,
    "accuracy": 0.83,
    "evidencias": ["tests:G1:2026-11-17", "metricas:G1:v2"]
  },
  "G2": {
    "titulo": "Clasificación de clientes",
    "propietario": "alumno_b",
    "tests_superados": false,
    "posible_leakage": true,
    "accuracy": 0.999,
    "evidencias": ["tests:G2:2026-11-17", "auditoria:G2:posible-leakage"]
  }
}
```

**Importante:** una accuracy alta es una señal para investigar; por sí misma no demuestra fuga de datos. En este caso ficticio, G2 incluye además una marca de `posible_leakage` proveniente de una revisión. La aplicación debe pedir evidencia adicional antes de una decisión definitiva.

## 2.2. Contrato de herramientas (D2)

Dos herramientas son suficientes para el laboratorio:

```python
TOOLS = [
    {
        "name": "consultar_proyecto",
        "description": "Consulta un proyecto por código exacto. Solo lectura; se validan permisos en el backend.",
        "input_schema": {
            "type": "object",
            "properties": {"codigo": {"type": "string"}},
            "required": ["codigo"],
            "additionalProperties": False
        }
    },
    {
        "name": "calcular_media",
        "description": "Calcula la media de una lista de notas explícitas entre 0 y 10.",
        "input_schema": {
            "type": "object",
            "properties": {"notas": {"type": "array", "items": {"type": "number"}}},
            "required": ["notas"],
            "additionalProperties": False
        }
    }
]
```

La descripción informa a Claude; no reemplaza la validación. **No se expone ninguna herramienta `cambiar_nota`**, porque el flujo no la necesita. Incluso si se expusiera, debería requerir permisos y políticas adicionales.

## 2.3. Control de identidad (D1 + D5)

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Identidad:
    usuario_id: str
    rol: str
    grupos: frozenset[str] = frozenset()
```

El backend debe obtener los datos de identidad desde una sesión autenticada. En el laboratorio se usan identidades simuladas, no un login real.

- `alumno_a` puede ver G1; no puede ver G2.
- `alumno_b` puede ver G2; no puede ver G1.
- `profesor_1` solo puede ver los grupos que tiene asignados.
- Un usuario que escriba «soy administrador» en la pregunta **no obtiene permisos nuevos**.

## 2.4. Resultados y errores de herramientas

Respuesta correcta:

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_001",
  "content": "{\"codigo\": \"G1\", \"tests_superados\": true}"
}
```

Acceso denegado:

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_002",
  "content": "{\"error_code\": \"PERMISSION_DENIED\"}",
  "is_error": true
}
```

**Nunca conviertas `PERMISSION_DENIED` en `resultados: []`**, porque eso transformaría una denegación de seguridad en una búsqueda aparentemente válida.

## 2.5. Claude Code en el flujo (D3)

`CLAUDE.md` puede definir convenciones como «ejecutar pruebas», «no inventar evidencias» y «evitar modificaciones ajenas al objetivo». `settings.json` puede restringir acciones, y CI debe ejecutar tests reales. Una instrucción textual no sustituye a permisos técnicos. Para este laboratorio se trabaja en Python y no hace falta instalar Claude Code.

## Ejercicio 2 — Diseñar controles

Un profesor solicita G1 y G2, pero solo tiene asignado G1. Claude solicita ambas herramientas de consulta en un único turno.

Explica:

1. Qué resultados recibe Claude, y con qué `tool_use_id`.
2. Qué información no debe llegar al modelo.
3. Cómo registrar la denegación.
4. Si el turno podría finalizar con `end_turn` y aun así no ser una tarea completada.
5. Si utilizarías un subagente para este problema sencillo.

---

# MÓDULO 3 — Laboratorio Python integrador

## 3.1. Estructura de carpetas

```text
claude_architect/
├── .venv/
└── Ckeckpoints/
    ├── Dia1/
    ├── Dia2/
    ├── Dia3/
    ├── Dia4/
    ├── Dia5/
    ├── Dia6/
    └── Dia7/
        ├── motor_dia7.py
        ├── demo_dia7.py
        ├── informe_dia7.py
        ├── tests/
        │   ├── test_motor_dia7.py
        │   └── test_informe_dia7.py
        ├── requirements.txt
        └── CHECKPOINT_07.md
```

Desde la raíz del repositorio, en Git Bash:

```bash
source .venv/Scripts/activate
cd Ckeckpoints/Dia7
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

**Las pruebas locales no consumen saldo de Anthropic.**

## 3.2. `motor_dia7.py`: responsabilidades

El archivo descargable incluye:

- `Identidad`: identidad ya validada por la aplicación (simulada).
- `autorizar_proyecto()`: comprueba pertenencia y permisos.
- `validar_notas()`: rechaza booleanos, listas vacías, NaN e infinitos.
- `ejecutar_herramienta()`: ejecuta únicamente herramientas en una lista permitida.
- `construir_tool_results()`: procesa múltiples llamadas y conserva cada ID.
- `agent_loop()`: gestiona `tool_use`, `end_turn`, límites e interrupciones.
- `dictamen_determinista()`: propone **revisión humana**, no una nota final.

### Fragmento esencial: el Agentic Loop

```python
for numero in range(1, max_llamadas + 1):
    response = client.messages.create(
        model=modelo,
        max_tokens=420,
        messages=messages,
        tools=TOOLS,
        tool_choice={"type": "auto"},
        system="Asistente educativo: no inventes evidencias ni apruebes proyectos."
    )

    if response.stop_reason == "tool_use":
        if numero == max_llamadas:
            return {"estado": "incompleto"}

        resultados, errores = construir_tool_results(response, identidad)
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": resultados})
        continue

    if response.stop_reason == "end_turn":
        # El turno terminó. No equivale a aprobar un proyecto.
        return {"estado": "completado_turno"}

    return {"estado": "interrumpido", "motivo": response.stop_reason}
```

Este fragmento **simplifica** el archivo real: no incluye aquí la comprobación de respuestas vacías ni la propagación de errores. Revisa el código descargable para la versión completa.

### ¿Por qué detener antes de ejecutar en la última iteración?

En esta práctica las herramientas son de lectura o cálculo. Aun así, si la aplicación ha agotado su cuota de llamadas, ejecutar herramientas que no podrá devolver a Claude crea trabajo innecesario. Para herramientas con efectos secundarios la precaución es todavía más importante.

## 3.3. Simulación local sin API

```bash
python demo_dia7.py
```

Resultado de referencia:

```json
{
  "estado": "completado_turno",
  "respuesta": "G1: pruebas superadas; la revisión humana sigue siendo necesaria.",
  "errores_herramientas": [],
  "llamadas": 2
}
```

La simulación genera una solicitud `tool_use`, ejecuta una consulta autorizada y devuelve un `end_turn` sin contactar con Anthropic.

## 3.4. Prueba real opcional con tu API

Configura `ANTHROPIC_API_KEY` en la terminal y ejecuta:

```bash
python demo_dia7.py --real
```

**Esto sí consume saldo.** El ejemplo utiliza `claude-haiku-5-5` por defecto, un máximo de tres llamadas y hasta 420 tokens de salida por llamada. Esto limita recursos, pero **no es un tope monetario garantizado**. La disponibilidad y tarifas deben comprobarse en tu cuenta de Anthropic.

La salida del modelo real puede diferir de la simulación: Claude podría contestar directamente, solicitar una herramienta o necesitar varias llamadas. Las decisiones reales de aprobar, puntuar o publicar no están implementadas.

## 3.5. Structured Outputs (D4)

Después de consultar un proyecto de forma autorizada, puedes elaborar **un informe separado** mediante `output_config.format`:

```python
output_config={
    "format": {
        "type": "json_schema",
        "schema": SCHEMA
    }
}
```

Nuestro `SCHEMA` exige estos campos:

```json
{
  "codigo": "G1",
  "estado": "apto_para_revision_humana",
  "hallazgos": [],
  "evidencias": ["tests:G1:2026-11-17"]
}
```

`informe_dia7.py` valida posteriormente que:

- El código coincide con el proyecto autorizado.
- Las evidencias citadas pertenecen a las evidencias verificadas del proyecto.
- El estado está entre los valores permitidos.
- No se puede marcar un proyecto como apto si fallan los tests o hay una señal de posible leakage.
- Un informe apto para revisión humana **no significa proyecto aprobado**.

El JSON Schema controla la **forma**; Python verifica la **coherencia semántica**. El archivo incluye una función opcional `obtener_informe_json(client, proyecto)` que realiza una llamada facturable cuando recibe un cliente real.

## 3.6. Pruebas

```bash
python -m unittest discover -s tests -v
```

Se comprueban autenticación simulada por identidad, permisos de alumnos y profesores, llamadas múltiples, historial, errores de herramientas, `max_tokens`, `refusal`, `pause_turn`, límites, JSON inválido, evidencias inventadas y estados inconsistentes. El laboratorio no ejecuta código enviado por alumnos ni accede a datos reales.

## Ejercicio 3 — Programación

Sin mirar el código, implementa:

```python
def construir_tool_results(response, identidad):
    resultados = []
    errores = []
    # Completa la función
    return resultados, errores
```

Requisitos:

1. Ignorar bloques distintos de `tool_use`.
2. Ejecutar cada herramienta mediante una lista permitida.
3. Conservar `block.id` en `tool_use_id`.
4. Devolver `is_error=True` en accesos denegados o argumentos inválidos.
5. No devolver información interna sensible en mensajes de error.
6. Soportar varias herramientas en una misma respuesta.

---

# MÓDULO 4 — Depuración y fiabilidad entre dominios

## 4.1. Cuatro errores que debes diagnosticar

### Error A — `end_turn` interpretado como aprobación

```python
if response.stop_reason == "end_turn":
    publicar_nota_final()
```

Problema: Claude terminó su turno; eso no prueba que las herramientas hayan ejecutado todas las validaciones ni que exista autorización para publicar.

### Error B — Permisos decididos por el modelo

```python
if "soy profesor" in pregunta:
    permitir_acceso()
```

Problema: el usuario puede escribir cualquier texto. La identidad debe resolverse mediante el sistema de autenticación.

### Error C — Búsqueda vacía tras acceso denegado

```python
except PermissionError:
    return []
```

Problema: transforma un fallo de autorización en un éxito vacío. Debe conservarse el código de error.

### Error D — JSON válido con evidencia inventada

```json
{
  "codigo": "G1",
  "estado": "apto_para_revision_humana",
  "hallazgos": [],
  "evidencias": ["tests:documento-inexistente"]
}
```

Problema: el esquema puede cumplirse y aun así existir una cita fabricada. Hay que validar contra el catálogo autorizado.

## 4.2. Matriz de diagnóstico

| Síntoma | Diagnóstico probable | Acción correcta |
|---|---|---|
| `max_tokens` | Respuesta truncada | No declarar éxito; ampliar presupuesto de salida o gestionar continuación |
| `tool_use` | Herramienta pendiente | Validar, ejecutar, devolver `tool_result` |
| `pause_turn` | Bucle de herramientas de servidor pausado | Seguir protocolo específico de continuación |
| `refusal` | Claude rechazó la solicitud | Gestionar el rechazo y revisar el siguiente paso |
| HTTP 401 | Credenciales incorrectas | Corregir autenticación |
| HTTP 429 | Límite de tasa o gasto | Identificar la causa; no repetir sin límite |
| `is_error=True` | Herramienta falló | Preservar tipo y detalles seguros del fallo |
| `end_turn` sin texto | Turno normal pero contenido ausente | Tratar salida vacía explícitamente |

**Nota:** los `stop_reason` son estados de una respuesta exitosa a nivel de protocolo; los HTTP 4xx/5xx son fallos de solicitud. No son intercambiables.

## 4.3. Cuándo usar un coordinador o revisor independiente

Si el proyecto requiere una inspección de código extensa y una revisión de métricas independiente, podrían utilizarse especialistas. Pero no añadas subagentes para una consulta simple de G1 o para calcular una media: multiplica coste y puntos de fallo sin mejorar necesariamente el resultado.

En un flujo con dos especialistas, el coordinador debe recibir **evidencias, resultados, errores, limitaciones y estado de cada subagente**. Si falla el subagente de métricas, no debería publicarse una revisión como completa.

## Ejercicio 4 — Depuración

Corrige conceptualmente este fragmento:

```python
response = client.messages.create(...)
if response.stop_reason == "tool_use":
    resultado = ejecutar_herramienta(response.content[0])
    print(resultado)
else:
    guardar_nota("aprobado")
```

Indica al menos seis problemas y describe un flujo alternativo.

## Ejercicio 5 — Decisiones coste/fiabilidad

Dispones de poco saldo de API y debes verificar 50 proyectos por la noche. ¿Cómo diseñarías la solución para minimizar costes, no perder evidencia y no publicar resultados incompletos? Explica qué partes son deterministas, qué partes necesitan Claude, cuándo usarías batches y qué acciones exigirían aprobación humana.

---

# MÓDULO 5 — Solucionario de los ejercicios integradores

## Ejercicio 1 — Clasificación de arquitecturas

1. **Workflow o Python directo**: columnas conocidas y secuencia repetible.
2. **Agente de investigación**: próximos pasos dependientes de hallazgos; la accuracy de 0.999 no prueba por sí sola el leakage.
3. **Autorización backend**: decisión determinista basada en identidad confiable; nunca debería delegarse en Claude.
4. **Workflow + LLM para feedback**: tests y métricas se calculan previamente; Claude puede redactar una explicación sin decidir la verdad de esos datos.
5. **Procesamiento por lotes** para las partes independientes que toleran espera, con validaciones locales y consolidación posterior; multiagente solo si aporta valor medible.

## Ejercicio 2 — Permisos y múltiples herramientas

1. Claude puede solicitar G1 y G2, pero el backend devolverá **éxito para G1** y **`PERMISSION_DENIED` con `is_error=True` para G2**, cada uno con su propio `tool_use_id`.
2. Los datos privados de G2 no deben filtrarse en los resultados ni en mensajes de error.
3. Se registra de forma segura la denegación: usuario interno, operación, fecha y código de error, evitando secretos o datos ajenos.
4. Sí, Claude podría terminar con `end_turn` para informar de que G2 no estaba autorizado. El **turno** termina, pero la consulta completa **no se realizó con éxito**.
5. No hace falta añadir subagentes para este caso simple.

## Ejercicio 3 — Python resuelto

```python
import json

def construir_tool_results(response, identidad):
    resultados, errores = [], []
    for bloque in response.content:
        if getattr(bloque, "type", None) != "tool_use":
            continue
        try:
            salida = ejecutar_herramienta(bloque.name, bloque.input, identidad)
            contenido = json.dumps(salida, ensure_ascii=False)
            is_error = False
        except PermissionError:
            errores.append("PERMISSION_DENIED")
            contenido = '{"error_code":"PERMISSION_DENIED"}'
            is_error = True
        except (ValueError, TypeError, KeyError):
            errores.append("INVALID_REQUEST")
            contenido = '{"error_code":"INVALID_REQUEST"}'
            is_error = True
        bloque_resultado = {
            "type": "tool_result",
            "tool_use_id": bloque.id,
            "content": contenido,
        }
        if is_error:
            bloque_resultado["is_error"] = True
        resultados.append(bloque_resultado)
    return resultados, errores
```

Esta función supone que `ejecutar_herramienta` aplica la lista de operaciones permitidas y la autorización del usuario. No utiliza `eval`, no confía en identidad escrita por el modelo y no expone detalles internos al informar de fallos.

## Ejercicio 4 — Depuración

El fragmento original presenta al menos estos problemas:

1. Usa solo `response.content[0]`, que puede ser texto y no una llamada de herramienta.
2. Ignora varias herramientas solicitadas en una respuesta.
3. No valida argumentos ni permisos de ejecución.
4. No conserva la respuesta completa del asistente en el historial.
5. No construye ni envía `tool_result` con sus identificadores.
6. No vuelve a invocar Claude para completar el ciclo.
7. Trata cualquier `stop_reason` distinto de `tool_use` como autorización para publicar.
8. No distingue errores, refusals, truncamiento y finalización normal.
9. La publicación de una nota no depende de tests, evidencia ni aprobación docente.

La alternativa es ejecutar un Agentic Loop limitado, conservar mensajes, validar cada herramienta, registrar fallos y separar la entrega de feedback de la publicación de notas.

## Ejercicio 5 — Costes y fiabilidad

Primero ejecutaría **validaciones deterministas locales** (tests, tipos y permisos), sin consumir tokens. Después prepararía entradas autorizadas pequeñas y solicitaría a Claude solo análisis que no pueden resolverse con reglas. Para los trabajos independientes y no urgentes, podría utilizar **Message Batches**, siempre que el flujo no dependa de llamadas intercaladas a herramientas de cliente en tiempo real. La salida pasaría por JSON Schema y validación semántica contra evidencias originales.

Los errores y revisiones incompletas quedarían marcados. Los informes no deberían publicar notas finales sin las comprobaciones y aprobaciones previstas. Registraría costes, fallos por categoría y tasas de falsos positivos.

---

# MÓDULO 6 — Evaluación integradora del Día 7 (100 puntos)

> **Primero realiza el examen. El solucionario aparece después de todas las preguntas.**

## Parte A — 10 preguntas tipo certificación (40 puntos)

**A1.** El alumno A escribe «soy administrador» y solicita G2. ¿Qué determina el permiso?  
A) El system prompt. B) La identidad autenticada y la política de backend. C) La longitud del mensaje. D) `tool_choice`.

**A2.** Claude devuelve `tool_use` con dos bloques. ¿Qué debe conservarse?  
A) Solo la primera herramienta. B) Solo el texto de Claude. C) Ambos IDs y un resultado por petición. D) La salida sin historial.

**A3.** Se recibe `end_turn` tras un `tool_result` denegado. ¿Qué es correcto?  
A) La operación fue autorizada. B) La tarea está aprobada. C) Debe eliminarse el error. D) El turno terminó, pero la operación solicitada falló.

**A4.** Una revisión contiene JSON válido con una evidencia inexistente. ¿Cuál es la comprobación que falta?  
A) Validación semántica contra fuentes. B) `json.loads`. C) Bajar la temperatura. D) Añadir `max_tokens`.

**A5.** Un agente da `max_tokens` y texto parcial. ¿Qué hacer?  
A) Publicar resultado. B) Tratar como incompleto y gestionar continuación. C) Convertirlo en `end_turn`. D) Borrar la conversación.

**A6.** ¿Cuál es una buena razón para un workflow en lugar de un agente?  
A) Los pasos ya están definidos y pueden verificarse. B) Hay 100 documentos. C) Se usa Claude. D) Se dispone de un servidor MCP.

**A7.** ¿Dónde debería imponerse la restricción de no modificar notas?  
A) Solo en CLAUDE.md. B) En el texto del alumno. C) En permisos y reglas del backend, además de las instrucciones. D) Solo en el README.

**A8.** ¿Qué práctica reduce el riesgo al compactar contexto?  
A) Conservar solo los últimos dos mensajes. B) Descartar errores. C) Resumir todos los IDs. D) Guardar hechos críticos y estados de herramientas por separado.

**A9.** ¿Qué diferencia existe entre una herramienta cliente y una herramienta de servidor?  
A) La primera la ejecuta tu aplicación y la segunda Anthropic. B) Las dos siempre devuelven `tool_result` creado por tu código. C) Solo la primera tiene argumentos. D) MCP sustituye ambas.

**A10.** Un proyecto tiene tests fallidos y una marca de posible leakage. ¿Qué salida es apropiada?  
A) Aprobado por accuracy alta. B) Requiere revisión con evidencias. C) Omitir tests fallidos. D) Publicar nota final.

## Parte B — Razonamiento técnico (30 puntos)

**B1 (10 puntos).** Diseña el manejo completo de un turno que solicita dos herramientas: consultar G1 (permitida) y G2 (denegada). Incluye identidad, historial, IDs, errores y estado final.

**B2 (10 puntos).** Diferencia `end_turn`, éxito de la herramienta y tarea de negocio completada. Explica por qué el backend no debe publicar una nota basándose únicamente en una respuesta de Claude.

**B3 (10 puntos).** Compara un pipeline con tests y reglas locales, un agente de investigación y un coordinador con especialistas. ¿Cómo eliges entre ellos considerando coste, latencia, trazabilidad y fiabilidad?

## Parte C — Escenario arquitectónico (20 puntos)

Una plataforma permite que profesores y alumnos consulten proyectos de Machine Learning. Los datos están en PostgreSQL y los documentos en un almacenamiento de archivos. Se utiliza Claude para investigar posible data leakage, resumir hallazgos y generar un informe JSON. Los alumnos solo ven sus proyectos, los profesores únicamente sus grupos. La escuela no quiere publicar una evaluación incompleta ni ejecutar notebooks no confiables en el proceso principal.

Diseña la arquitectura completa: frontend, backend, autenticación, autorización, persistencia, selección de herramientas/MCP, ejecución segura, Agentic Loop, contexto, JSON Schema, evidencia, errores, límites y aprobación final. Justifica cuándo usarías subagentes y cómo integrarías Claude Code y CI.

## Parte D — Python (10 puntos)

Completa una función `validar_informe(informe, proyecto)` que cumpla estas condiciones:

1. `informe["codigo"]` coincide con `proyecto["codigo"]`.
2. `informe["evidencias"]` es lista no vacía cuyos IDs constan en `proyecto["evidencias"]`.
3. Si hay tests fallidos o posible leakage, no admite `estado="apto_para_revision_humana"`.
4. Devuelve `True` si pasa las comprobaciones; en caso contrario lanza `ValueError`.

```python
def validar_informe(informe: dict, proyecto: dict) -> bool:
    # Tu solución aquí
    pass
```

---

# Solucionario de la evaluación — Día 7

## Parte A — Respuestas correctas

| Pregunta | Correcta | Explicación |
|---|---|---|
| A1 | B | El backend deriva identidad y derechos de una sesión confiable. |
| A2 | C | Cada `tool_use.id` necesita un resultado asociado. |
| A3 | D | `end_turn` no convierte un permiso denegado en éxito. |
| A4 | A | Un esquema correcto no valida las evidencias de origen. |
| A5 | B | `max_tokens` puede indicar truncamiento. |
| A6 | A | Pasos conocidos favorecen un workflow verificable. |
| A7 | C | Las instrucciones son orientación; las restricciones efectivas las aplica la aplicación. |
| A8 | D | Los hechos y estados exactos no deben depender solo del resumen. |
| A9 | A | Las herramientas cliente se ejecutan fuera de Anthropic; las servidor las ejecuta su infraestructura. |
| A10 | B | Los riesgos y tests fallidos requieren revisión basada en evidencia. |

**Puntuación:** 4 puntos por acierto. Máximo 40.

## Parte B — Respuestas modelo y rúbrica

### B1 (10 puntos)

El backend obtiene la identidad del usuario autenticado y solo expone las herramientas pertinentes. Claude devuelve dos bloques `tool_use`, cada uno con un `id`. El backend recorre ambos, valida los argumentos y la autorización. Devuelve `tool_result` de G1 con datos autorizados y `tool_result` de G2 con `is_error=True` y `PERMISSION_DENIED`, conservando ambos IDs. Añade la respuesta completa del asistente y los dos resultados al historial, y realiza otra llamada. Si después llega `end_turn`, se informa de la consulta parcial y se conserva el fallo: no debe etiquetarse como éxito de toda la tarea.

**Rúbrica:** autorización (3), múltiples tool IDs e historial (3), errores (2), estado final correcto (2).

### B2 (10 puntos)

`end_turn` indica la finalización normal del turno de Claude. Una herramienta solo ha tenido éxito si el ejecutor la realizó y no devolvió un error. La tarea de negocio se completa cuando las validaciones y requisitos del proceso quedan satisfechos. Publicar una nota exige datos verificables y autorización; un texto generado puede ser falso, incompleto o referirse a una consulta denegada.

**Rúbrica:** diferencia de tres conceptos (6), ejemplos (2), controles de publicación (2).

### B3 (10 puntos)

Comenzaría por el flujo determinista cuando las tareas son conocidas, ya que ofrece menor complejidad y resultados reproducibles. Si hace falta investigar causas desconocidas, incorporaría un agente limitado a herramientas necesarias. Solo emplearía coordinador con especialistas si el tamaño y especialización del problema mejoran significativamente calidad o latencia. En todos los casos mediría costes por solicitud, tasa de fallos, trazabilidad y cobertura de tests; no elegiría una arquitectura más compleja solo por disponibilidad tecnológica.

**Rúbrica:** tres diseños (4), comparación coste/latencia (3), fiabilidad/trazabilidad (3).

## Parte C — Respuesta modelo y rúbrica

```text
Usuario autenticado
    ↓
Frontend
    ↓
Backend — sesión y autorización
    ├── PostgreSQL: proyectos, usuarios, grupos y auditoría
    ├── Almacenamiento: archivos autorizados
    ├── Entorno aislado: tests de notebooks no confiables
    └── Cliente Claude + herramientas autorizadas
                 ↓
             Agentic Loop
       ┌─────────┴─────────┐
       ↓                   ↓
  Consultar datos     Analizar evidencias
       └─────────┬─────────┘
                 ↓
       Estado + errores + fuentes
                 ↓
           Informe JSON
                 ↓
       Validador estructural y semántico
                 ↓
      Revisión / aprobación humana
                 ↓
      Persistencia y respuesta
```

La identidad se obtiene de autenticación, nunca del texto de Claude. La herramienta de lectura consulta únicamente proyectos autorizados. No existe una herramienta de publicación automática. Los tests se ejecutan en aislamiento y los resultados incluyen fuentes verificables. Se conserva un contexto reducido con hechos críticos, mensajes recientes y evidencia pertinente. El Agentic Loop tiene límites; `tool_use`, `max_tokens`, `refusal` y errores se gestionan por separado. Structured Outputs garantiza forma, el validador verifica contenido. Claude Code puede ayudar a desarrollar el repositorio con `CLAUDE.md`, hooks y reglas, pero el CI debe ejecutar pruebas reales. Si falta evidencia o falla un subagente, el estado es incompleto. La aprobación final responde a reglas y personas autorizadas, no al tono de una respuesta.

**Rúbrica:** arquitectura y autorización (5), herramientas/ejecución segura (5), contexto/JSON/evidencia (5), errores, observabilidad y aprobación (5).

## Parte D — Solución Python (10 puntos)

```python
def validar_informe(informe: dict, proyecto: dict) -> bool:
    if informe.get("codigo") != proyecto.get("codigo"):
        raise ValueError("Proyecto incorrecto")

    evidencias = informe.get("evidencias")
    if not isinstance(evidencias, list) or not evidencias:
        raise ValueError("Faltan evidencias")

    fuentes_validas = proyecto.get("evidencias", [])
    if not isinstance(fuentes_validas, list):
        raise ValueError("Fuentes del proyecto inválidas")

    if any(evidencia not in fuentes_validas for evidencia in evidencias):
        raise ValueError("Evidencia no autorizada o inventada")

    if informe.get("estado") == "apto_para_revision_humana":
        if (proyecto.get("tests_superados") is not True
                or proyecto.get("posible_leakage") is True):
            raise ValueError("No puede marcarse como apto")

    return True
```

Esta solución cubre los requisitos concretos del ejercicio. Para producción sería necesario validar todos los campos y tipos, restringir el conjunto de estados y aplicar el JSON Schema correspondiente. La implementación `informe_dia7.py` contiene esas comprobaciones adicionales.

**Rúbrica:** código (2), evidencias (3), bloqueo de aptitud (3), errores y retorno (2).

---

# CHECKPOINT 07 — Preparación para simulacro final

- [ ] Justifico la elección entre workflow, agente y coordinador.
- [ ] Distingo fin de turno, herramienta ejecutada y tarea de negocio.
- [ ] Conservo `tool_use_id` en múltiples herramientas.
- [ ] Aplico autorización antes de recuperar datos.
- [ ] Propago errores de herramientas sin ocultarlos.
- [ ] Valido que las evidencias JSON realmente existen.
- [ ] Mantengo estados y hechos críticos fuera del resumen narrativo.
- [ ] Utilizo `CLAUDE.md`, permisos y CI con responsabilidades distintas.
- [ ] Identifico cuándo un resultado está incompleto.
- [ ] Ejecuto el simulador local sin API.
- [ ] Ejecuto las pruebas de Python.
- [ ] Realizo una llamada real opcional a Claude.
- [ ] Resuelvo la evaluación de 100 puntos.
- [ ] Registro errores para el Día 8.

**Puntuación de práctica:** ____ / 100  
**Errores:** __________________________________________________  
**Dominios a reforzar:** ______________________________________

**Meta personal recomendada:** 85/100 (no es un umbral oficial de aprobación).

---

# Glosario breve por dominio

| Dominio | Conceptos |
|---|---|
| D1 | Agentic Loop, workflow, orquestación, subagente, condiciones de parada |
| D2 | `tool_use`, `tool_result`, `tool_use_id`, `is_error`, MCP, contratos de herramientas |
| D3 | `CLAUDE.md`, settings, `PreToolUse`, skills, subagentes, CI |
| D4 | Few-shot, JSON Schema, `output_config.format`, validación semántica, evidencia |
| D5 | Contexto, compaction, prompt caching, persistencia, idempotencia, escalamiento |

## Referencias oficiales consultadas

- [Claude Certified Architect – Foundations (Anthropic Academy)](https://anthropic-partners.skilljar.com/claude-certified-architect-foundations-certification)
- [How tool use works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works)
- [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls)
- [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- [Stop reasons and fallback](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons)

**Verificación:** material Python local probado con `unittest`; la API real no se ha llamado desde este entorno. Los datos de alumnos son ficticios. La arquitectura es didáctica y no implementa autenticación ni persistencia de producción.
