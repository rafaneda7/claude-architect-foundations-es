# DÍA 6 — Context Management & Reliability con Claude

**Certificación:** Claude Certified Architect – Foundations (CCAR-F)  
**Dominio principal:** D5 · Context Management & Reliability · **15 %**  
**Duración:** 4 horas  
**Nivel:** Python intermedio · VS Code · Git Bash · API Claude opcional  
**Estado:** Material didáctico con ejercicios, solucionarios y evaluación de 100 puntos.

> La principal amenaza de la gestión del contexto no es solo agotar tokens: es perder información decisiva y seguir respondiendo como si se conservara. Nunca uses un resumen narrativo como única fuente de importes, fechas, identificadores, permisos y estados.

## Objetivos

- Diferenciar historial, ventana de contexto, resúmenes, memoria y recuperación.
- Preservar datos exactos en registros independientes del resumen.
- Construir contextos mínimos con mensajes recientes, hechos y evidencias.
- Evitar que la reducción de herramientas borre errores, IDs o fuentes.
- Utilizar token counting y conocer compaction, context editing y prompt caching.
- Gestionar fallos de la API, reintentos, gastos y escalamiento humano.
- Probar una implementación Python sin consumir crédito y ejecutar **opcionalmente** una llamada real.

## Plan de estudio

| Módulo | Minutos | Tema |
|---|---:|---|
| 1 | 40 | Ventana de contexto, resumen, caching y compaction |
| 2 | 40 | Memoria persistente, recuperación y herramientas |
| 3 | 65 | Laboratorio Python: contexto seguro y API |
| 4 | 35 | Fiabilidad, errores y reintentos |
| 5 | 30 | Escalamiento y coordinación multiagente |
| 6 | 30 | Examen, solucionario y checkpoint |

---

# MÓDULO 1 — Ventana de contexto y compactación

## 1.1 Conceptos

La **ventana de contexto** es la cantidad de información que el modelo puede procesar en una solicitud. Incluye instrucciones `system`, mensajes, resultados de herramientas, documentos y la generación asociada. `max_tokens` limita la salida, no la cantidad de información histórica guardada permanentemente. La Messages API ordinaria requiere que la aplicación incluya los mensajes que necesita el modelo.

- **Historial:** secuencia almacenada de mensajes.
- **Resumen:** descripción condensada de lo ocurrido; es una representación imperfecta.
- **Hechos persistentes:** campos guardados en aplicación/base de datos y no reconstruidos desde el resumen.
- **Recuperación (retrieval):** selección de fuentes pertinentes y autorizadas para la pregunta.
- **Compaction:** resumen que sustituye historia antigua en el contexto activo.
- **Prompt caching:** reutilización de prefijos para reducir costes de procesamiento; la caché sigue consumiendo ventana de contexto.

## 1.2 El anti-patrón

Un usuario tiene dos incidencias: `INC-204` devolución de **47.90 EUR** solicitada **2026-11-12**, estado **abierto**; `INC-205` cobro de **8.00 EUR**, estado **en investigación**. Resumirlas como «cliente con un problema de compra» borra identificadores, importes y estados; no debes confiar en ese resumen como único registro.

Diseño recomendado:

```text
Solicitud → autenticación/autorización → resumen narrativo
                                      + hechos estructurados
                                      + mensajes recientes
                                      + evidencias recuperadas
          → Claude → respuesta validada → persistencia/logs
```

```json
{
  "incidencia_id": "INC-204",
  "importe": "47.90",
  "fecha": "2026-11-12",
  "estado": "abierto",
  "siguiente_paso": "Verificar recepción del paquete",
  "fuente": "registro_devoluciones"
}
```

Las cifras y fechas son **datos ficticios del ejercicio**.

## 1.3 Funciones actuales de Anthropic

En la API actual, el conteo previo puede realizarse con:

```python
count = client.messages.count_tokens(
    model="claude-haiku-5-5",
    system="Responde en español, usando solo datos verificados.",
    messages=[{"role": "user", "content": "¿Cuál es el estado de INC-204?"}],
)
print(count.input_tokens)
```

La documentación también describe compaction por umbral, en beta, mediante `client.beta.messages.create`, `betas=["compact-2026-01-12"]` y `context_management={"edits": [{"type": "compact_20260112"}]}`. Por defecto, su umbral de activación es 150.000 tokens de entrada. No tiene sentido activarla para un ejemplo corto y no sustituye a la persistencia de datos exactos.

**Atención:** el Python SDK moderno no admite el antiguo `compaction_control` del tool runner. Para compactación del servidor utiliza la interfaz beta oficial correspondiente.

## Ejercicio 1

Dado `INC-204`, importe `47.90 EUR`, fecha `2026-11-12`, estado `abierto` y siguiente paso `Verificar recepción`, responde: (1) qué resumirías, (2) qué conservarías exactamente, (3) qué hacer si un resumen contradice la base de datos, (4) qué enviarías a Claude, (5) por qué prompt caching no sustituye compaction.

---

# MÓDULO 2 — Memoria, recuperación y evidencia

## 2.1 Cuatro fuentes de contexto

| Mecanismo | Beneficio | Riesgo |
|---|---|---|
| Mensajes recientes | Continuidad inmediata | Omisión de hechos antiguos |
| Resumen | Reducción de volumen | Pérdida o distorsión |
| Base de datos de hechos | Exactitud, estados y auditoría | Requiere mantenimiento y permisos |
| Retrieval | Aporta fuentes necesarias | Recuperación irrelevante o no autorizada |

## 2.2 Recuperación segura

Primero se identifica al usuario desde una sesión autenticada. Luego se restringe la búsqueda a sus documentos autorizados y se recuperan fuentes relevantes. **No basta con filtrar después de que los datos privados hayan sido enviados a Claude.**

```text
Consulta → identidad confiable → filtro permisos → ranking de documentos
        → evidencias con fuente/fecha → contexto → Claude
```

## 2.3 Reducir resultados de herramientas

No es suficiente devolver `{"resultado":"ok"}` o truncar al azar. Mantén los identificadores (`tool_use_id`, `operacion_id`), resultados, estado, importes, fechas, códigos de error, evidencia, fuente y pasos pendientes. Puedes descartar grandes volcados de depuración o datos binarios que no afecten la decisión, preservándolos en almacenamiento si son necesarios para auditoría.

Ejemplo reducido:

```json
{
  "tool_use_id": "toolu_demo",
  "operacion_id": "OP-105",
  "incidencia_id": "INC-204",
  "estado": "pendiente",
  "importe": "47.90",
  "fecha": "2026-11-15",
  "fuente": "registro_devoluciones",
  "error_code": null
}
```

## 2.4 Contexto entre subagentes

Cada subagente debe devolver una estructura con **hallazgo, fuente, fecha, estado, incertidumbre y siguiente paso**. El coordinador no debe afirmar que una operación fue completada si solo recibió un mensaje ambiguo como «parece correcto».

## Ejercicio 2

Una herramienta devuelve `operacion_id`, `incidencia_id`, `estado`, `importe`, `fecha`, `fuente`, `error_code`, un `debug_dump` enorme y `imagen_original` binaria. (1) Indica qué conservarías, (2) qué podrías omitir del contexto, (3) qué hacer con un error de permisos, (4) dónde debe filtrarse la identidad, (5) por qué debes mantener la fuente y la fecha.

---

# MÓDULO 3 — Laboratorio Python con VS Code

## 3.1 Estructura de archivos

```text
claude_architect/
├── .venv/
└── Ckeckpoints/
    └── Dia6/
        ├── contexto_dia6.py
        ├── cliente_real_dia6.py
        ├── tests/
        │   └── test_contexto.py
        ├── CHECKPOINT_06.md
        └── README.md
```

## 3.2 Preparar entorno

Desde Git Bash, situado en la raíz de tu repositorio:

```bash
source .venv/Scripts/activate
python -m pip install --upgrade anthropic
```

No hace falta descargar modelos ni configurar bases de datos reales. Todo el laboratorio utiliza información ficticia y una capa de persistencia **en memoria** para comprender el patrón.

## 3.3 Registro exacto de una incidencia

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Incidencia:
    incidencia_id: str
    usuario_id: str
    descripcion: str
    estado: str
    importe: str | None = None
    fecha: str | None = None
    siguiente_paso: str | None = None
    fuente: str | None = None
```

Guardamos el importe como cadena decimal para preservar su representación y verificamos su validez mediante `Decimal`. Un resumen narrativo puede cambiar, pero el registro mantiene los hechos explícitos.

## 3.4 Aislamiento por usuario

```python
def exigir_acceso(conversacion, usuario_autenticado):
    if conversacion.propietario_id != usuario_autenticado:
        raise AccesoDenegado("Acceso a conversación no autorizado")
```

La aplicación debe obtener `usuario_autenticado` de una sesión validada. En el laboratorio se simula esta identidad con `alumno_demo`: **no es un sistema real de autenticación**.

## 3.5 Recuperación y construcción del contexto

`buscar_documentos` filtra por propietario **antes** de evaluar relevancia y `crear_contexto` organiza los datos en resumen, incidencias exactas, documentos relevantes y mensajes recientes.

```python
messages = crear_contexto(
    conversacion=conversacion,
    usuario_autenticado="alumno_demo",
    pregunta="¿Cuál es el siguiente paso de INC-001?",
    documentos=documentos,
    max_recientes=4,
)
```

Para evitar que una función didáctica rompa un ciclo activo, `crear_contexto` rechaza compactar o recortar cuando `tiene_herramienta_pendiente=True`. En producción necesitarías reconciliar todos los bloques de herramientas pendientes antes de reconstruir el historial.

## 3.6 Reducir resultados sin perder decisiones

```python
reducido = reducir_resultado_herramienta({
    "tool_use_id": "toolu_001",
    "estado": "error",
    "error_code": "TIMEOUT",
    "fuente": "api_externa",
    "debug_dump": "Miles de líneas irrelevantes"
})
```

`reducido` conserva `tool_use_id`, estado, error y fuente; omite `debug_dump` del **contexto enviado al modelo**. Nunca elimines el error para aparentar éxito.

## 3.7 Ejecución local sin coste

En `Dia6`:

```bash
python -m unittest discover -s tests -v
python cliente_real_dia6.py
```

La segunda orden funciona en modo demostración: **no llama a Claude**.

## 3.8 Ejecución opcional con tu API

Tu API Key debe estar en el entorno, nunca en un archivo versionado. Desde Git Bash:

```bash
read -rs -p "Introduce tu API Key: " ANTHROPIC_API_KEY
echo
export ANTHROPIC_API_KEY
python cliente_real_dia6.py --real
```

La llamada opcional primero estima el contexto con `client.messages.count_tokens`, impone un umbral de práctica de 2500 tokens y después realiza como máximo **una** generación con `max_tokens=300`, `max_retries=0`. El límite de tokens **no es un tope monetario garantizado**. Puedes usar `ANTHROPIC_MODEL` para cambiar de modelo; el valor por defecto es `claude-haiku-5-5`.

La respuesta solo se considera terminada normalmente cuando `stop_reason == "end_turn"`. Rechazos, `max_tokens`, errores y falta de texto no se publican como resolución confirmada.

## 3.9 Pruebas de verificación

Se incluyen **30 pruebas locales** que verifican acceso, separación de documentos, conservación de hechos, reducción segura de resultados, estados, clasificadores de errores y escalamiento. No validan la conexión externa; eso se realiza opcionalmente con `--real`.

## Ejercicio 3

Amplía el proyecto con (1) una incidencia `INC-002` para otro usuario, (2) un test que compruebe que `alumno_demo` no puede añadirla ni verla, (3) un campo `fuente` y fecha de un segundo documento y (4) una prueba de que `error_code` se conserva al reducir resultados. Explica qué cambiarías para utilizar PostgreSQL en lugar de memoria.

---

# MÓDULO 4 — Fiabilidad, fallos y reintentos

## 4.1 Diferenciar fallos

| Situación | Diagnóstico | Conducta |
|---|---|---|
| 400 petición inválida | Contrato o contenido erróneo | Corregir solicitud |
| 401 credenciales | API Key no válida | Verificar autenticación |
| 403 permisos | Acceso insuficiente | Detener acción no autorizada |
| 429 por RPM/tokens | Rate limit transitorio | `retry-after` y backoff |
| 429 por tope de gasto | Límite mensual | Detener, no insistir |
| 500/504/529 | Error transitorio o saturación | Reintentos limitados, si son seguros |
| `max_tokens` | Respuesta posiblemente truncada | No declarar finalización |
| `end_turn` | Finalización normal del turno | Evaluar calidad antes de publicar |

La documentación distingue varios motivos de `429`, incluido el tope de gasto que no se resuelve con reintentos. El SDK ya implementa reintentos automáticos por defecto ante algunos errores; en nuestro script se usa `max_retries=0` para que el comportamiento sea explícito.

## 4.2 Reintentar no siempre es seguro

Para una operación de lectura, repetir tras un fallo transitorio puede ser razonable. Si un pago o reembolso falló por timeout, **no sabes si llegó a ejecutarse**. Consulta su estado mediante un identificador de operación o clave de idempotencia antes de intentar repetir una acción con efectos secundarios.

## 4.3 Preservar errores entre agentes

No conviertas `{"is_error": true, "error_code": "PERMISSION_DENIED"}` en `{"resultado": []}`. Un resultado vacío es éxito sin coincidencias; un error exige tratamiento específico.

## Ejercicio 4

Clasifica (1) `401`, (2) `429` con `retry-after`, (3) `429` por gasto mensual, (4) `529`, (5) `max_tokens`, (6) timeout de un reembolso, y explica cuáles permiten reintento y cuáles necesitan revisión.

---

# MÓDULO 5 — Escalamiento y coordinación

## 5.1 No depender de la confianza autorreportada

«Estoy seguro al 98 %» no es una regla operativa suficiente: el número puede ser inventado por el modelo o no estar calibrado. Igual ocurre con escalar solo porque un usuario se exprese de forma enfadada. Las reglas deben depender de condiciones verificables: importe, riesgo, acción irreversible, permisos, cumplimiento, fallos repetidos o solicitud explícita de una persona.

## 5.2 Reglas deterministas de escalamiento

```python
if requiere_aprobacion_humana or riesgo_alto:
    escalar = True
elif intentos_fallidos >= 2:
    escalar = True
else:
    escalar = False
```

El código del paquete implementa `decidir_escalado(incidencia, ...)` y devuelve motivos trazables. Las cifras y límites son **reglas ilustrativas**, no requisitos oficiales universales.

## 5.3 Coordinación entre agentes

Un investigador debería entregar al coordinador al menos:

```json
{
  "incidencia_id": "INC-204",
  "estado": "abierto",
  "fuente": "registro_devoluciones",
  "fecha": "2026-11-15",
  "limitaciones": "Recepción sin confirmar",
  "siguiente_paso": "Verificar recepción"
}
```

La síntesis debe distinguir **hallazgos confirmados, hipótesis, errores y trabajo pendiente**. No puede presentar una operación fallida como éxito ni inventar pruebas.

## Ejercicio 5

Diseña un sistema que escala cuando (1) la operación requiere aprobación humana, (2) el riesgo supera un umbral definido por la organización o (3) ha fallado repetidamente. ¿Qué datos mínimos enviarías a la persona que recibe el caso? ¿Por qué no utilizarías solo el sentimiento o la autoconfianza del modelo?

---

# SOLUCIONARIO DE LOS EJERCICIOS

## Ejercicio 1 — Contexto exacto

1. Resumiría la historia general: «hay una devolución pendiente».
2. Conservaría exactamente `INC-204`, `47.90 EUR`, `2026-11-12`, `abierto`, compromiso y siguiente paso, con fuente.
3. Consultaría la fuente de verdad, marcaría inconsistencia y no produciría una respuesta definitiva basada en el resumen contradictorio.
4. Enviaría resumen, registro estructurado, últimos mensajes y evidencia relevante autorizada.
5. Prompt caching reduce coste de procesamiento de prefijos; no reduce necesariamente la cantidad de contexto y no reemplaza una compactación ni la persistencia.

## Ejercicio 2 — Reducción de herramientas

1. Mantendría `operacion_id`, `incidencia_id`, estado, importe, fecha, fuente y `error_code`, además de evidencias o pasos pendientes si existen.
2. Omitiría los grandes dumps y bytes binarios **solo del contexto**, conservando su rastro de auditoría si hace falta.
3. Un `PERMISSION_DENIED` debe mantenerse como error; no devolver una lista vacía fingiendo éxito.
4. El backend aplica permisos **antes** de recuperación y ejecución, y los vuelve a verificar en operaciones sensibles.
5. Fuente y fecha permiten trazabilidad, actualidad y contraste de versiones.

## Ejercicio 3 — Python y PostgreSQL

```python
from contexto_dia6 import Conversacion, Incidencia, agregar_incidencia

c = Conversacion("C1", "alumno_demo")
incidencia_ajena = Incidencia("INC-002", "otro_usuario", "Cobro", "abierto")

try:
    agregar_incidencia(c, "alumno_demo", incidencia_ajena)
except PermissionError:
    print("Acceso denegado correctamente")
```

En PostgreSQL utilizaría `usuarios`, `conversaciones`, `incidencias`, `mensajes` y `documentos`, con claves foráneas y consultas que apliquen siempre el usuario autenticado. Los tests del paquete incluyen acceso ajeno y recuperación autorizada. La capa de ejemplo es en memoria y **no tiene autenticación real**.

## Ejercicio 4 — Errores

- `401`: credenciales; no reintentar sin corregir.
- `429` transitorio: respetar `retry-after`, usar reintentos limitados.
- `429` por gasto: no reintentar; revisar la cuenta.
- `529`: saturación transitoria; aplicar backoff acotado.
- `max_tokens`: salida posiblemente incompleta; manejar explícitamente, no publicar como solución final.
- Timeout de reembolso: comprobar el estado mediante identificador/idempotencia antes de repetir.

## Ejercicio 5 — Escalamiento

La regla debe comprobar criterios de negocio observables: aprobación requerida, riesgo alto y fallos reiterados. El expediente debe conservar ID, problema, intentos, acciones realizadas, evidencias, fechas, importe, permisos y siguiente paso. El sentimiento no equivale a complejidad; la autoconfianza del modelo no constituye una medida calibrada.

---

# EVALUACIÓN DEL DÍA 6 — 100 PUNTOS

## Parte A — Test (10 × 4 = 40 puntos)

**A1.** ¿Qué debe preservarse fuera de un resumen narrativo?  
A. Solo los saludos · **B. Importes, fechas, IDs y estados exactos** · C. Solo últimas frases · D. Nada

**A2.** ¿Qué cambia prompt caching?  
A. Elimina el historial · B. Impide tool_use · **C. Reutiliza prefijos y puede reducir coste, pero siguen ocupando ventana** · D. Persistencia garantizada

**A3.** Un subagente devuelve «parece resuelto» sin fuente. ¿Qué hacer?  
A. Cerrar caso · **B. Pedir evidencia y estado verificable** · C. Inventar fecha · D. Marcar reembolso pagado

**A4.** ¿Dónde filtrar documentos por permisos?  
A. Tras enviarlos a Claude · **B. En la aplicación, antes de recuperar o enviar datos** · C. Solo en el prompt · D. No hace falta

**A5.** ¿Qué se debe mantener al reducir un resultado de herramienta?  
A. Solo descripción breve · B. Solo texto bonito · C. Solo bytes binarios · **D. IDs, estado, errores, fuente y datos decisivos**

**A6.** Una búsqueda sin coincidencias, pero ejecutada correctamente, es:  
**A. Éxito vacío** · B. Permiso denegado · C. Error 529 · D. Timeout

**A7.** Un 429 por tope de gasto mensual significa:  
A. Reintentar cien veces · B. Cambiar `stop_reason` · **C. Detener y revisar el límite de la cuenta** · D. Eliminar logs

**A8.** Un timeout durante un reembolso:  
A. Garantiza fracaso · B. Garantiza éxito · **C. Exige comprobar el estado antes de repetir** · D. Obliga a llamar otro modelo

**A9.** ¿Qué criterio de escalamiento es más fiable?  
A. «El modelo dice 99 %» · **B. Necesita aprobación humana o acción de alto riesgo** · C. Usuario utiliza mayúsculas · D. Respuesta extensa

**A10.** ¿Qué hacer con `stop_reason="max_tokens"`?  
A. Marcar completado · B. Ignorarlo · C. Publicar siempre · **D. Tratar la respuesta como posiblemente incompleta**

### Clave A con explicaciones

| Pregunta | Respuesta | Explicación |
|---|---|---|
| A1 | B | El resumen puede omitir hechos decisivos. |
| A2 | C | La caché no amplía la ventana de contexto. |
| A3 | B | La síntesis exige evidencia verificable. |
| A4 | B | La autorización precede al envío de datos privados. |
| A5 | D | Recortar no es borrar identidad, fallos y trazabilidad. |
| A6 | A | No hallar resultados no equivale a fallo. |
| A7 | C | Un tope de gasto no se resuelve con backoff. |
| A8 | C | Puede existir un efecto secundario pese al timeout. |
| A9 | B | La política debe basarse en hechos comprobables. |
| A10 | D | `max_tokens` no significa finalización normal. |

## Parte B — Razonamiento técnico (3 × 10 = 30 puntos)

### B1 (10 puntos)

**Pregunta:** Diseña el contexto para una conversación de 200 mensajes que contiene dos devoluciones, cifras y fechas importantes. Explica cómo evitas perder hechos y filtrar información ajena.

**Respuesta modelo:** Mantendría resumen narrativo, registros independientes por incidencia, mensajes recientes y retrieval de documentos autorizados. La consulta se ejecuta bajo la identidad autenticada y con filtros de propietario antes de enviar resultados. Las cifras, fechas, fuentes y estados no dependen únicamente del resumen. Se preservan los vínculos de tool_use/tool_result pendientes. La respuesta se valida antes de publicar. **Rúbrica:** capas de contexto (4), exactitud (3), permisos (2), protocolo (1).

### B2 (10 puntos)

**Pregunta:** Diferencia compactación, prompt caching y persistencia, e indica cuándo usarías `count_tokens`.

**Respuesta modelo:** Compaction resume el contexto activo; caching reutiliza prefijos para reducir coste de procesamiento sin sacarlos de la ventana; persistencia almacena hechos/historial entre sesiones. `count_tokens` estima la entrada antes de llamar, permite decidir si recuperar menos fuentes o compactar y ayuda a evitar desbordamientos. Ninguno garantiza por sí solo verdad o permisos. **Rúbrica:** tres definiciones (6), uso de conteo (2), limitaciones (2).

### B3 (10 puntos)

**Pregunta:** Un agente falla tres veces con un 429; un usuario pide realizar una devolución de alto importe. Diseña la recuperación y el escalamiento.

**Respuesta modelo:** Primero diferenciaría 429 de rate limit temporal frente a tope de gasto. Si hay `retry-after`, lo respetaría y aplicaría reintentos limitados. Si es límite de gasto, detendría. Una devolución de alto impacto requeriría autorización y, según política, aprobación humana antes de ejecutarla. Mantendría identificadores, error, intentos y evidencia. **Rúbrica:** diagnóstico 429 (3), reintentos seguros (3), aprobación (2), trazabilidad (2).

## Parte C — Escenario arquitectónico (20 puntos)

**Enunciado:** Diseña una plataforma de soporte con Claude y PostgreSQL para 10.000 clientes, con historial largo, múltiples incidencias por cliente, herramientas de consultas y reembolsos, subagentes, errores recuperables y escalamiento a humanos. La plataforma no debe mezclar conversaciones ni perder importes, fechas o compromisos.

**Respuesta modelo:**

```text
Usuario → frontend → backend (autenticación/autorización)
                           ├── PostgreSQL: casos, mensajes, hechos, permisos
                           ├── Retrieval autorizado: documentos con fuente/fecha
                           ├── Constructor de contexto: resumen + hechos + recientes
                           ├── Claude: decisiones/herramientas
                           ├── Ejecutor: comprobación permisos y operaciones idempotentes
                           ├── Observabilidad: request_id, errores, tokens, estados
                           └── Motor de reglas: escalamiento y aprobaciones
```

Cada incidencia se almacena en registro separado con ID, estado, importe, fecha, fuente, expectativas y siguiente paso. Los resultados de los subagentes deben conservar evidencia y errores. El backend aplica permisos y no publica éxito sin confirmar efectos secundarios. En tareas largas utiliza compactación y retrieval, pero preserva datos exactos y relaciones de herramientas. Los reintentos se limitan y el escalamiento depende de reglas comprobables. **Rúbrica:** diseño/persistencia (5), contexto/evidencia (5), permisos/ejecución (5), recuperación/escalamiento (5).

## Parte D — Python (10 puntos)

**Enunciado:** Implementa `reducir_resultado_herramienta(resultado)` que conserve los campos `tool_use_id`, `operacion_id`, `estado`, `error_code`, `importe`, `fecha`, `fuente` e `is_error`, y omita campos como `debug_dump` o `imagen_original`. Debe rechazar entradas no diccionario.

**Solución:**

```python
def reducir_resultado_herramienta(resultado: dict) -> dict:
    if not isinstance(resultado, dict):
        raise TypeError("Se espera un diccionario")

    conservar = {
        "tool_use_id", "operacion_id", "estado", "error_code",
        "importe", "fecha", "fuente", "is_error",
    }

    return {k: v for k, v in resultado.items() if k in conservar}
```

La función impide que un volcado enorme ocupe innecesariamente el contexto. **No elimina el error** ni el identificador de la solicitud. En producción se debe ampliar el contrato con evidencia, ID de incidencia y demás campos necesarios para la decisión. **Rúbrica:** tipo (2), lista de campos (3), errores e ID (3), exclusión segura (2).

---

# CHECKPOINT 06

- [ ] Comprendo el coste y la ventana de contexto.
- [ ] Distingo resumen, memoria persistente, retrieval y caching.
- [ ] Conservo cantidades, fechas y estados estructurados.
- [ ] Reduzco resultados de herramientas conservando errores.
- [ ] Aplico permisos antes de recuperar documentos.
- [ ] Mantengo continuidad de bloques de herramientas pendientes.
- [ ] Conozco `count_tokens` y compaction beta.
- [ ] Clasifico correctamente 400, 401, 403, 429, 5xx y 529.
- [ ] Comprendo idempotencia y reintentos.
- [ ] Defino reglas de escalamiento humano.
- [ ] He ejecutado 30 pruebas locales.
- [ ] He probado opcionalmente una llamada con mi API.
- [ ] He completado la evaluación de 100 puntos.

**Puntuación:** Parte A ___/40 · Parte B ___/30 · Parte C ___/20 · Parte D ___/10 · **TOTAL ___/100**  
**Objetivo personal sugerido:** 85/100 (no es un umbral oficial).  
**Errores pendientes:** 1. ____  2. ____  3. ____

## Referencias

- [Context windows — Anthropic](https://platform.claude.com/docs/en/build-with-claude/context-windows)
- [Token counting — Anthropic](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- [Compaction at a token threshold — Anthropic](https://platform.claude.com/docs/en/build-with-claude/compaction-threshold)
- [Prompt caching — Anthropic](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Claude API errors — Anthropic](https://platform.claude.com/docs/en/api/errors)
- [Rate limits — Anthropic](https://platform.claude.com/docs/en/api/rate-limits)
