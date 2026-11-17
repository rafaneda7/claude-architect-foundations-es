# DÍA 5 · CCAR-F — D4: Prompt Engineering & Structured Output

**Certificación:** Claude Certified Architect – Foundations  
**Dominio:** D4 · Prompt Engineering & Structured Output (20 %)  
**Duración:** 4 horas  
**Entorno:** Windows 11, VS Code, Git Bash, Python 3.12, API de Claude (saldo previo de 5 USD).  
**Estado:** Material de estudio. Los ejercicios y preguntas son de elaboración propia, no oficiales.

## Índice

1. Criterios explícitos y reducción de falsos positivos (35 min)
2. Few-shot, XML y criterios de casos límite (35 min)
3. Structured Outputs y laboratorio Python real (75 min)
4. Validación semántica y reintentos con feedback (35 min)
5. Message Batches y revisión independiente (30 min)
6. Evaluación de 100 puntos y solucionario (30 min)
7. Checkpoint del Día 5

## Objetivos

- Distinguir criterios específicos de frases vagas como «sé conservador».
- Controlar falsos positivos con condiciones de inclusión/exclusión y severidades.
- Construir ejemplos few-shot representativos: positivos, negativos y ambiguos.
- Separar instrucciones y datos no confiables con XML.
- Reconocer diferencia entre JSON sugerido por prompt y JSON restringido mediante esquema.
- Utilizar `output_config.format` en Messages API y comprender `tool_use` estricto.
- Diseñar campos nullable, enums y validaciones posteriores.
- Implementar un extractor documental y 22 tests offline.
- Decidir cuándo un retry sirve y cuándo faltan datos de origen.
- Identificar Batches API y revisión multi-instancia/multi-pasada.

---

# Módulo 1 · Criterios explícitos y falsos positivos (35 min)

## 1.1. Una instrucción vaga no es un criterio comprobable

**Malo:** «Revisa el código y denuncia cualquier cosa sospechosa. Sé conservador».  
**Mejor:** «Reporta un comentario como incorrecto solo cuando su afirmación contradiga directamente lo que hace el código. No reportes comentarios incompletos pero ciertos ni preferencias de estilo».

El segundo prompt define **inclusión**, **exclusión** y el tipo de **evidencia** que exige la revisión.

Ejemplo A — `# Devuelve nombre completo` y `return usuario.nombre`: posible contradicción verificable.  
Ejemplo B — `# Valida datos` y `return 0 < edad < 120`: comentario poco específico, pero no falso; no reportarlo.

## 1.2. Severidad y evidencia

Diseña criterios operativos:

| Severidad | Condición explícita | Evidencia requerida |
|---|---|---|
| Crítica | Permite una operación no autorizada con datos ajenos | Ruta de ejecución y condición omitida |
| Alta | Error reproducible que rompe funcionalidad principal | Entrada, comportamiento real y esperado |
| Media | Fallo real en un caso de borde admitido | Caso concreto verificable |
| No reportar | Preferencia de formato sin impacto o comentario incompleto pero verdadero | — |

Evita sustituir estos criterios por un vago «solo reporta hallazgos de alta confianza»: puede reducir indiscriminadamente hallazgos sin resolver el problema.

## 1.3. Falsos positivos y confianza

Un *falso positivo* es un problema reportado que no cumple el criterio. Una categoría de revisión con muchos falsos positivos deteriora la confianza del equipo, incluso si otras categorías funcionan bien.

Mide las incidencias rechazadas por tipo de patrón (`detected_pattern`). Si una categoría es especialmente ruidosa, puedes desactivarla temporalmente, revisar el criterio, probarla y reincorporarla.

### Ejercicio 1

Redacta un prompt para revisar comentarios de funciones Python que:
1. Reporte solo contradicciones demostrables entre comentario y código.
2. No reporte falta de detalle o cambios estilísticos.
3. Distinga severidad alta y media con criterios concretos.
4. Devuelva archivo, línea, evidencia, `detected_pattern` y corrección sugerida.

---

# Módulo 2 · Few-shot, XML y casos límite (35 min)

## 2.1. Zero-shot frente a few-shot

**Zero-shot:** proporcionas instrucciones sin ejemplos.  
**Few-shot:** añades ejemplos entrada/salida que demuestran el comportamiento deseado, especialmente en casos ambiguos.

Los ejemplos deben ser variados. No bastan tres ejemplos con una única clase de error; deben incluir positivos, negativos y fronterizos. Como práctica, empieza con 2–4 ejemplos relevantes y evalúa su comportamiento.

## 2.2. Ejemplo aplicado: extracción de total

```xml
<instrucciones>
Extrae total_declarado y moneda únicamente si figuran en el texto.
Si no aparece un total explícito, total_declarado debe ser null.
No calcules ni inventes un total para rellenar ese campo.
</instrucciones>
<ejemplos>
  <ejemplo>
    <entrada>TOTAL 12,50 EUR</entrada>
    <salida>{"total_declarado": 12.5, "moneda": "EUR"}</salida>
  </ejemplo>
  <ejemplo>
    <entrada>2 artículos a 5 EUR cada uno</entrada>
    <salida>{"total_declarado": null, "moneda": "EUR"}</salida>
  </ejemplo>
  <ejemplo>
    <entrada>Total aproximado: no determinado</entrada>
    <salida>{"total_declarado": null, "moneda": "desconocida"}</salida>
  </ejemplo>
</ejemplos>
<documento>TOTAL 7,00 EUR</documento>
```

La salida de un ejemplo debe reflejar la instrucción de no inventar. Si el ejemplo «2 artículos a 5 EUR» mostrara `10` como total declarado, estaría enseñando el comportamiento equivocado.

Las etiquetas XML **organizan el prompt**, no son por sí mismas una garantía de seguridad. Un documento no confiable puede incluir texto parecido a instrucciones; la aplicación debe separar los roles y tratarlo como datos, nunca como autoridad superior.

### Ejercicio 2

Crea dos ejemplos few-shot para una herramienta de revisión de comentarios: uno donde la observación sea incorrecta y se deba reportar, y otro con comentario poco específico pero verdadero que no se deba reportar. Añade un tercer ejemplo para un total ausente, que deba permanecer como `null`.

---

# Módulo 3 · Structured Outputs y laboratorio Python (75 min)

## 3.1. Por qué «responde solo JSON» es insuficiente

Un prompt puede pedir JSON, pero no garantiza sintaxis, tipos ni campos. Para una integración que consume datos, utiliza esquemas restringidos mediante:

- **Structured JSON outputs:** `output_config={"format":{"type":"json_schema","schema": SCHEMA}}`.
- **Strict tool use:** herramientas con `strict: true`, útil cuando Claude debe suministrar entradas estructuradas para una herramienta.

**Atención a materiales anteriores:** algunas guías del examen enfatizan extraer argumentos de `tool_use` forzados. La Messages API actual también permite JSON restringido directamente con `output_config.format`. No son exactamente lo mismo. En ambos casos hay que validar **semántica**, permisos y consistencia después.

## 3.2. JSON Schema con datos ausentes

```python
SCHEMA = {
    "type": "object",
    "properties": {
        "tipo": {"type": "string", "enum": ["factura", "ticket", "otro"]},
        "moneda": {"type": "string", "enum": ["EUR", "USD", "desconocida"]},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "descripcion": {"type": "string"},
                    "cantidad": {"type": "number"},
                    "precio_unitario": {"type": "number"},
                    "evidencia": {"type": "string"}
                },
                "required": ["descripcion", "cantidad", "precio_unitario", "evidencia"],
                "additionalProperties": False
            }
        },
        "total_declarado": {"type": ["number", "null"]},
        "observaciones": {"type": "string"}
    },
    "required": ["tipo", "moneda", "items", "total_declarado", "observaciones"],
    "additionalProperties": False
}
```

`total_declarado` es **obligatorio como clave**, pero admite `null` como valor. Esto representa honestamente que el total no aparece en la fuente. Lo mismo puede expresarse con `anyOf`.

La documentación actual especifica que los objetos requieren `additionalProperties: false` y que restricciones como `minimum`, `maximum`, `minLength` y `maxLength` no se admiten dentro del esquema restringido. Aplícalas mediante validación local y reglas del negocio.

## 3.3. Configuración actual de la API

```python
from anthropic import Anthropic
import json

client = Anthropic()
response = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=900,
    system="Extrae únicamente hechos presentes en el documento.",
    messages=[{"role": "user", "content": "TICKET: 2 cuadernos a 3,50 EUR. TOTAL 7 EUR"}],
    output_config={
        "format": {
            "type": "json_schema",
            "schema": SCHEMA
        }
    }
)
if response.stop_reason != "end_turn":
    raise RuntimeError(f"No completado: {response.stop_reason}")
texto = "".join(b.text for b in response.content if b.type == "text")
datos = json.loads(texto)
```

Se debe conservar `stop_reason`: en `refusal` o `max_tokens` la respuesta podría **no** seguir el esquema; tampoco debes suponer que una respuesta HTTP 200 equivale a extracción válida.

**Nota:** el helper `client.messages.parse(output_format=ModeloPydantic)` puede aceptar modelos Pydantic, pero **no** debes trasladar sin más `output_format={...}` a `messages.create()`. La forma actual de la petición directa es `output_config.format`.

## 3.4. Coste de tu API

Para practicar utiliza `claude-haiku-5-5` por su precio base publicado desde 0,10 USD por millón de tokens de entrada y desde 0,50 USD por millón de tokens de salida. Una llamada de ejemplo de 5.000 tokens de entrada y 1.000 de salida costaría aproximadamente 0,001 USD a esas tarifas base, sin otros cargos. Tu gasto real puede diferir.

El laboratorio limita a **dos llamadas por ejecución**, no ejecuta lotes ni tareas repetitivas automáticamente. Es un control de llamadas, **no un límite de facturación**.

## 3.5. Ejecutar el laboratorio

Carpeta recomendada:

```text
claude_architect/
├── .venv/
└── Ckeckpoints/
    └── Dia5/
        ├── GUIA_DIA_05_COMPLETA.md
        ├── extractor_dia5.py
        ├── requirements.txt
        ├── tests/
        │   └── test_extractor_dia5.py
        └── CHECKPOINT_05.md
```

Con Git Bash, desde la raíz del proyecto:

```bash
source .venv/Scripts/activate
python -m pip install -r Ckeckpoints/Dia5/requirements.txt
cd Ckeckpoints/Dia5
python -m unittest discover -s tests -v
```

Para una llamada real, **solo después** de las pruebas:

```bash
read -rs -p "API Key: " ANTHROPIC_API_KEY; echo; export ANTHROPIC_API_KEY
python extractor_dia5.py
```

El archivo `extractor_dia5.py` contiene:
1. `SCHEMA` compatible con Structured Outputs;
2. `extraer_json_respuesta()` que rechaza `max_tokens` y `refusal`;
3. `validar_extraccion()` para verificar evidencias literales, valores válidos y totales;
4. `extraer_con_claude()` con una recuperación dirigida cuando falla la validación semántica;
5. un caso de demostración con datos ficticios.

**Estado de verificación:** 22 pruebas locales superadas. No se ha probado una conexión real con tu cuenta ni la disponibilidad del modelo en esa cuenta.

### Ejercicio 3

1. Explica la diferencia entre `json.loads()`, un JSON Schema restringido y la validación semántica.
2. ¿Por qué `total_declarado` debe admitir `null`?
3. ¿Por qué un esquema que incluye `minimum: 0` puede producir HTTP 400 con Structured Outputs?
4. ¿Puede considerarse válida una respuesta con `stop_reason="max_tokens"` si parece JSON?
5. Modifica el esquema para incorporar `origen`: `"OCR" | "texto" | "otro"`, documentando cómo representar casos ambiguos.

---

# Módulo 4 · Validación semántica y reintentos (35 min)

## 4.1. JSON correcto no significa hecho correcto

Ejemplo de salida que cumple tipos pero **no es verdadera**:

```json
{
  "tipo": "ticket",
  "moneda": "EUR",
  "items": [{"descripcion":"cuadernos", "cantidad":2, "precio_unitario":3.5,
             "evidencia":"2 cuadernos a 3.50 EUR"}],
  "total_declarado": 8,
  "observaciones": ""
}
```

Si la fuente declara 7, el número 8 es un error **semántico**. Si `cantidad` es `"dos"`, tendrías además un error de **tipo/estructura**.

El programa comprueba lo que puede verificar determinísticamente:

```python
calculado = sum(item["cantidad"] * item["precio_unitario"] for item in datos["items"])
if datos["total_declarado"] is not None and abs(calculado - datos["total_declarado"]) > 0.01:
    raise ValueError("Totales inconsistentes")
```

Una salvedad: una factura puede incluir impuestos, descuentos y envío. En producción, la suma simple debe reemplazarse por una regla de negocio que contemple esos componentes o evitar suposiciones.

## 4.2. Reintento con feedback específico

**Malo:** «Vuelve a intentarlo».  
**Mejor:** «El total declarado por la fuente es 7,00 EUR, pero devolviste 8,00 EUR. Usa solo el documento original y conserva el esquema».

El segundo mensaje ofrece un error concreto para corregir la extracción. Debe contener la fuente relevante, el resultado anterior y el error de validación.

**No reintentar inútilmente:** si el documento no contiene un número, no puedes inventarlo mediante múltiples llamadas. Debes representarlo como ausente (`null` cuando el esquema lo admita) o pedir una fuente adicional.

## 4.3. Evidencia y seguimiento de errores

Una salida de revisión de código puede registrar `detected_pattern` y `evidence_location`. Luego, el equipo puede medir qué patrones reportados son descartados habitualmente. No incluyas cadenas de pensamiento internas como campo obligatorio; pide una justificación breve y verificable.

### Ejercicio 4

Para la fuente «2 cuadernos a 3,50 EUR. TOTAL 7,00 EUR», Claude devuelve 8,00. Escribe el mensaje de feedback que enviarías en un único reintento. Explica qué harías si la fuente no mostrase ningún total y si la respuesta acabara por `max_tokens`.

---

# Módulo 5 · Batches API y revisión independiente (30 min)

## 5.1. Mensajes individuales frente a Message Batches

| Criterio | Messages API normal | Message Batches API |
|---|---|---|
| Latencia | Para respuestas interactivas | Asíncrona, tolera espera |
| Coste | Tarifa base | Descuento publicado del 50 % |
| Uso | Validación de PR antes de merge | Auditorías nocturnas y reportes semanales |
| Relación entre solicitudes | Puede orquestarse iterativamente en backend | Cada solicitud del lote es independiente |
| Correlación | ID de respuesta | `custom_id` del envío |

Los lotes pueden tardar hasta 24 horas sin SLA de respuesta inmediata. No son apropiados para una comprobación que bloquea un merge esperando una respuesta. Dentro de una solicitud del lote no puedes ejecutar herramientas del cliente entre turnos y devolver sus resultados para continuar ese mismo ciclo agéntico.

Ejemplo conceptual de estructura de envío (no lo ejecutes en esta práctica):

```python
requests = [
    {
        "custom_id": "proyecto_G1",
        "params": {
            "model": "claude-haiku-5-5",
            "max_tokens": 512,
            "messages": [{"role":"user", "content":"Resume el proyecto G1"}]
        }
    },
    {
        "custom_id": "proyecto_G2",
        "params": {
            "model": "claude-haiku-5-5",
            "max_tokens": 512,
            "messages": [{"role":"user", "content":"Resume el proyecto G2"}]
        }
    }
]
```

No emparejes resultados por posición; utiliza `custom_id`. Reenvía solo los casos fallidos tras diagnosticar la causa.

## 5.2. Revisión independiente y multipasada

Un modelo que acaba de redactar código puede tener sesgos de continuidad con sus decisiones anteriores. Para revisión más independiente, utiliza otra instancia/sesión sin el razonamiento previo y proporciona únicamente el artefacto y criterios claros.

Para repositorios grandes: primera pasada por archivo (fallos locales) y segunda pasada transversal (interfaces, permisos y flujos de datos entre archivos).

```text
Archivos → Revisión local por archivo → Hallazgos verificables
                                          ↓
                        Revisión transversal de dependencias
                                          ↓
                          Consolidación sin duplicados
```

### Ejercicio 5

Decide entre Messages API y Batches para: A) bloqueo de PR; B) auditoría nocturna de 500 archivos; C) informe semanal de tests. Explica cómo correlacionarías resultados y por qué separarías la revisión local de la transversal.

---

# Solucionario de los cinco ejercicios

## Solución 1 · Criterios explícitos

> Revisa comentarios Python. **Reporta** cuando el comentario indique un comportamiento que el código contradiga directamente (por ejemplo, promete el nombre completo y retorna solo el nombre). **No reportes** comentarios incompletos pero verdaderos, preferencias de estilo ni cambios de redacción. Clasifica como **alta** una contradicción que pueda afectar seguridad o funcionalidad principal; como **media**, una contradicción demostrable sin ese impacto. Devuelve archivo, línea, evidencia literal del comentario y del código, `detected_pattern`, severidad y corrección. Si no hay contradicción comprobable, devuelve lista vacía.

La severidad se funda en impacto observable, no en una sensación vaga de confianza.

## Solución 2 · Few-shot

```xml
<examples>
  <example>
    <input>Comentario: "Devuelve el nombre completo" / Código: return usuario.nombre</input>
    <output>Reportar contradicción: solo devuelve nombre</output>
  </example>
  <example>
    <input>Comentario: "Valida el rango" / Código: return 0 <= edad <= 120</input>
    <output>No reportar: el comentario es genérico pero verdadero</output>
  </example>
  <example>
    <input>Fuente: "2 cuadernos a 3 EUR"</input>
    <output>{"total_declarado": null}</output>
  </example>
</examples>
```

El tercero evita inventar un total a partir de la multiplicación.

## Solución 3 · Structured Outputs

1. `json.loads()` verifica sintaxis y convierte texto a objetos Python; **no** valida reglas de negocio. El esquema restringido condiciona la forma de la respuesta durante la generación. La validación semántica comprueba significado, cifras y evidencia.
2. `null` representa que el total no está presente en la fuente; convertirlo en cero o inventar un valor sería incorrecto.
3. `minimum` y `maximum` no están disponibles en el subconjunto actual de esquemas restringidos; aplicar esas reglas después.
4. No. `max_tokens` indica truncamiento potencial, incluso si hay texto recuperable.
5. `"origen": {"type":"string", "enum":["OCR","texto","otro"]}`; añadir al array `required`, y un campo `origen_detalle` nullable para otras variantes. Tratar ambigüedades como `otro` con descripción, o ampliar enum con `desconocido` si es necesario.

## Solución 4 · Reintentos

> Validación fallida: el total que devolviste es 8,00 EUR, pero en la fuente figura explícitamente «TOTAL 7,00 EUR». Vuelve a revisar el texto fuente, conserva el esquema y corrige solo los datos incorrectos; no inventes campos ni valores ausentes.

Si no existe total, devolver `null`, sin reintentar esperando obtener información inexistente. Si llega `max_tokens`, el sistema debe marcar la respuesta como incompleta y gestionar una nueva petición con mayor límite o una estrategia apropiada, no aceptar el JSON como definitivo.

## Solución 5 · Batches y revisión

A) Comprobación que bloquea PR: API síncrona. B) Auditoría nocturna de 500 archivos: Batches. C) Informe semanal: Batches. Identificar cada respuesta por `custom_id` y no por orden. La primera pasada identifica problemas locales; la transversal busca inconsistencias entre archivos (interfaces, tipos, permisos) que una inspección aislada no detecta.

---

# Evaluación del Día 5 (100 puntos)

**Nota:** evaluación propia de preparación; el examen de certificación no utiliza esta rúbrica de 100 puntos.

## Parte A · Test (10 × 4 = 40 puntos)

1. Un revisor genera muchos avisos sobre comentarios vagos pero correctos. ¿Qué mejora es más útil?  
   A. «Sé conservador». B. Definir contradicciones reportables y exclusiones explícitas. C. Subir temperatura. D. Añadir más adjetivos.
2. ¿Qué conjunto de ejemplos es más útil para casos ambiguos?  
   A. Solo positivos. B. Solo casos sencillos. C. Positivos, negativos y casos frontera. D. Un ejemplo aleatorio.
3. Un ticket no declara el total. ¿Qué valor debe emitir el campo nullable?  
   A. null. B. 0. C. 999. D. Precio estimado.
4. ¿Cómo se solicita JSON restringido hoy mediante `messages.create()`?  
   A. Texto «solo JSON». B. `temperature=0`. C. `output_config.format` con `json_schema`. D. `max_tokens=0`.
5. ¿Qué comprobación queda pendiente tras una salida que cumple el JSON Schema?  
   A. Ninguna. B. Verificar semántica y evidencias. C. Forzar XML. D. Eliminar logs.
6. ¿Cuál de estas restricciones no se admite en el esquema restringido de la API actual?  
   A. `required`. B. `additionalProperties: false`. C. `enum`. D. `minimum`.
7. La respuesta devuelve `stop_reason="refusal"`. ¿Qué debes hacer?  
   A. Publicar el JSON sin comprobarlo. B. Marcar la extracción como no completada/rehusada. C. Reintentar indefinidamente. D. Ignorar el stop reason.
8. La validación detecta total calculado 7 frente a declarado 8. ¿Qué tipo de fallo es?  
   A. Semántico. B. Error de sintaxis JSON. C. Fallo de red garantizado. D. Configuración de transporte MCP.
9. ¿Para qué caso resulta apropiada la Message Batches API?  
   A. Chat en tiempo real de respuesta inmediata. B. Bloqueo de merge urgente. C. Auditoría nocturna de cientos de archivos. D. Bucle de herramientas cliente entre turnos dentro de una única solicitud del lote.
10. ¿Por qué revisar mediante una segunda instancia independiente?  
   A. Para saltarse validaciones. B. Para reducir el sesgo de continuidad del contexto generado. C. Para forzar resultados correctos siempre. D. Para evitar ejecutar tests.

### Soluciones y explicaciones de la Parte A

| # | Correcta | Explicación |
|---|---|---|
| 1 | B | Criterios de reporte y exclusión concretos reducen falsos positivos mejor que instrucciones vagas. |
| 2 | C | Few-shot debe cubrir bordes, negativos y positivos para generalizar. |
| 3 | A | `null` representa dato no declarado; cero sería un hecho nuevo. |
| 4 | C | El parámetro actual es `output_config.format`. |
| 5 | B | La forma JSON no garantiza verdad ni coherencia aritmética. |
| 6 | D | `minimum` no está soportado en el esquema de generación restringida. |
| 7 | B | Un rechazo prevalece sobre la expectativa del esquema. |
| 8 | A | La inconsistencia de totales es semántica. |
| 9 | C | Batch favorece tareas diferibles; no bloqueos inmediatos. |
| 10 | B | La separación de contexto facilita una revisión menos anclada. |

## Parte B · Razonamiento técnico (3 × 10 = 30 puntos)

### B1 · Precisión (10 puntos)

**Pregunta:** Diseña criterios explícitos para una revisión que marque comentarios falsos de código Python, con severidad, evidencia y exclusiones. Explica por qué «solo reporta errores de alta confianza» resulta insuficiente.

**Respuesta modelo:** Reportar solo contradicciones directas entre comentario y ejecución observable. Excluir comentarios genéricos pero verdaderos y estilo. Severidad alta si afecta seguridad o funcionalidad principal, media para contradicciones menores verificables. Cada hallazgo requiere archivo, línea, comparación de afirmación vs código y `detected_pattern`. La etiqueta «alta confianza» no especifica qué clasifica como fallo y puede producir falsos positivos o perder errores reales.

**Rúbrica:** inclusión/exclusión (4), evidencia (2), severidades (2), crítica a instrucciones vagas (2).

### B2 · Salida estructurada (10 puntos)

**Pregunta:** Compara JSON solicitado mediante prompt, `output_config.format` y `strict: true` en herramientas. ¿Qué validaciones mantendrías después de generar la salida?

**Respuesta modelo:** El prompt solo orienta; `output_config.format` restringe la forma de una respuesta JSON; `strict: true` restringe las entradas de herramientas. Ambos mecanismos estructurados siguen requiriendo validación semántica, permisos y verificación contra fuente; los rechazos o truncamientos deben gestionarse explícitamente. Si falta un campo en la fuente, debe representarse como ausente, no inventarse.

**Rúbrica:** distinciones (5), semántica (3), excepciones (2).

### B3 · Retries, batches y revisión (10 puntos)

**Pregunta:** Diseña un proceso que reciba 500 documentos para auditoría nocturna; algunos tienen totales inconsistentes y otros carecen de importe. Explica reintentos, envíos y revisión.

**Respuesta modelo:** Probar primero el prompt en muestra representativa. Usar lotes independientes con `custom_id`; validar semántica por documento. Reintentar casos corregibles con errores concretos y solo los fallidos. Los totales ausentes se marcan `null`/requieren datos adicionales; no se inventan. Separar extracción y revisión independiente para detectar incoherencias. No utilizar batch para una comprobación que deba responder inmediatamente.

**Rúbrica:** selección batch (3), custom_id (2), retries (3), revisión (2).

## Parte C · Escenario arquitectónico (20 puntos)

**Pregunta:** Diseña una plataforma que revisa 500 pull requests semanales, minimiza falsos positivos, entrega feedback estructurado y no bloquea merges por resultados todavía pendientes. También genera un informe semanal diferido.

**Respuesta modelo:** Primero definir categorías explícitas y severidades verificables, con pocos ejemplos positivos/negativos/ambiguos. Para revisión que bloquea merge, utilizar ejecución síncrona y pruebas deterministas; un JSON restringido proporciona hallazgos estructurados (`archivo`, `linea`, `categoria`, `severidad`, `evidencia`, `detected_pattern`, `solucion`). Validar localmente que la línea y evidencia existen, sin asumir que JSON correcto es verdad. Separar revisión por archivo e integración transversal; usar una sesión revisora independiente. Para el informe semanal, enviar tareas independientes a Batches, con `custom_id`. Monitorizar falsos positivos por patrón y desactivar temporalmente categorías ruidosas. No publicar una aprobación hasta completar los controles obligatorios.

**Rúbrica:** criterios/evaluación (5), salida y validación (5), arquitectura de revisión (5), elección API/batch y errores (5).

## Parte D · Python (10 puntos)

**Pregunta:** Implementa una función `extraer_json_respuesta(response)` que: compruebe `end_turn`, ignore bloques no textuales, gestione ausencia de texto y JSON malformado, exija objeto raíz y devuelva el `dict`. No realices llamadas a la API.

**Solución:**

```python
import json


def extraer_json_respuesta(response) -> dict:
    if response.stop_reason != "end_turn":
        raise ValueError(f"No completado: {response.stop_reason}")

    partes = [
        bloque.text
        for bloque in response.content
        if getattr(bloque, "type", None) == "text"
    ]
    if not partes:
        raise ValueError("Respuesta sin texto")

    try:
        datos = json.loads("".join(partes))
    except json.JSONDecodeError as error:
        raise ValueError("JSON inválido") from error

    if not isinstance(datos, dict):
        raise ValueError("Se esperaba un objeto JSON")

    return datos
```

**Rúbrica:** `stop_reason` (2), filtro de bloques (2), vacío (1), JSON/error (3), raíz `dict` (2).

---

# CHECKPOINT 05

**Estado:** Pendiente hasta completar laboratorio, preguntas y evaluación.  
**Meta personal sugerida:** 85/100 (no es nota oficial).

- [ ] Distingo criterios explícitos de instrucciones vagas.
- [ ] Defino exclusiones y severidad de hallazgos.
- [ ] Preparo 2–4 ejemplos few-shot útiles.
- [ ] Comprendo que las etiquetas XML organizan, no autorizan.
- [ ] Utilizo `output_config.format` con JSON Schema.
- [ ] Distingo JSON outputs y strict tool use.
- [ ] Represento campos no presentes con null.
- [ ] Conozco limitaciones de JSON Schema restringido.
- [ ] Rechazo refusals, truncamientos y bloques vacíos.
- [ ] Valido números, evidencias y coherencia semántica.
- [ ] Gestiono reintentos con errores específicos y límites.
- [ ] Distingo Messages API síncrona de Batches.
- [ ] Identifico resultados batch por custom_id.
- [ ] Diseño revisión local por archivo y transversal independiente.
- [ ] He ejecutado las 22 pruebas locales.
- [ ] He ejecutado una práctica real con Claude.
- [ ] He respondido el examen sin mirar el solucionario.

**Puntuación:** A ___/40 · B ___/30 · C ___/20 · D ___/10 · Total ___/100.

**Errores pendientes:**
1.
2.
3.

## Referencias oficiales

- Structured Outputs: https://platform.claude.com/docs/en/build-with-claude/structured-outputs
- Prompting Best Practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Stop Reasons: https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons
- Modelos y precios: https://platform.claude.com/docs/en/models/haiku-5-5/overview
