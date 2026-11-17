# Glosario técnico CCAR-F — cinco dominios

Referencia terminológica para el estudio de **Claude Certified Architect – Foundations (CCAR-F)**. Reúne definiciones, criterios de aplicación, distinciones conceptuales y procedimientos de consulta relativos a la Anthropic API, Claude Code y Model Context Protocol (MCP).

| Dominio | Área de estudio | Competencia central |
|---|---|---|
| D1 | Agentic Architecture & Orchestration | Diseñar flujos de agentes y controlar sus decisiones, estados y límites. |
| D2 | Tool Design & MCP Integration | Definir herramientas seguras e integrar clientes y servidores MCP. |
| D3 | Claude Code Configuration & Workflows | Configurar permisos, herramientas, subagentes y flujos de desarrollo. |
| D4 | Prompt Engineering & Structured Output | Especificar instrucciones y garantizar contratos estructurales verificables. |
| D5 | Context Management & Reliability | Gestionar contexto, recuperación, seguridad, observabilidad y resiliencia. |

**Criterio de lectura:** cada entrada presenta una definición y una aplicación concreta. Los nombres de herramientas y opciones pueden depender de la versión de Claude Code, del modelo, del SDK o de la revisión de MCP utilizada.

## D1 — Agentic Architecture & Orchestration

### Fundamentos del sistema y responsabilidades

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Modelo de lenguaje (LLM) | Modelo estadístico que produce bloques de salida condicionados por tokens de entrada, instrucciones y contexto; no es una base de datos ni un ejecutor privilegiado por sí mismo. | Clave: generar una intención no equivale a haber realizado una acción. |
| Inferencia | Ejecución de una petición al modelo para obtener una respuesta o decisión; consume tokens y está sujeta a latencia, costes y límites. | Ejemplo: `client.messages.create(...)` solicita una inferencia. |
| Messages API | Interfaz de Anthropic para intercambiar mensajes y bloques de contenido con Claude; la aplicación administra el historial y las operaciones externas. | En una integración normal, la API no conserva por sí sola toda tu sesión como una base de datos de negocio. |
| SDK | Biblioteca que envuelve llamadas a una API y ofrece tipos, errores y utilidades en un lenguaje concreto. | `anthropic` para Python simplifica el acceso a Messages API. |
| Rol `user` | Emisor de una petición, dato u observación devuelta por una herramienta en el historial de mensajes. | Un `tool_result` de una herramienta del cliente se adjunta habitualmente dentro de un mensaje `user`. |
| Rol `assistant` | Turno generado por el modelo, que puede contener texto, razonamiento permitido o solicitudes de herramientas. | Un turno del asistente no implica que la operación solicitada se ejecutó. |
| System prompt | Instrucciones de nivel superior que configuran el comportamiento del modelo para una aplicación. | No sustituye los controles de seguridad del backend. |
| Bloque de contenido (`content block`) | Unidad tipada dentro de un mensaje, por ejemplo `text`, `tool_use` o `tool_result`; una respuesta puede contener varios bloques. | No asumas que `response.content[0]` es siempre texto. |
| `stop_reason` | Campo que indica por qué el modelo terminó su generación actual; sirve para decidir el siguiente paso del programa. | `tool_use`, `end_turn` y `max_tokens` exigen tratamientos diferentes. |
| `end_turn` | Razón de parada que normalmente señala que Claude terminó su turno. | No significa que una operación de negocio esté autorizada ni confirmada. |
| `max_tokens` | Razón de parada por alcanzar el límite de salida; puede dejar una respuesta o estructura incompleta. | No proceses una salida truncada como si fuera una respuesta final validada. |
| Orquestador | Componente de aplicación que dirige flujo, estado, herramientas, límites y decisiones de transición entre pasos. | La autoridad del orquestador procede del código y de la política, no de la redacción del prompt. |
| Plano de control (control plane) | Capa que define permisos, selección de pasos, presupuestos y políticas del sistema. | El modelo recomienda acciones; la capa de control decide si se permiten. |
| Plano de ejecución (execution plane) | Capa que efectivamente llama APIs, consulta bases de datos o modifica recursos autorizados. | Una ejecución debe registrar identidad, parámetros y resultado. |
| Determinismo de aplicación | Reglas verificables que produce el código sin depender de una interpretación probabilística del modelo. | Un importe superior al umbral debe activar aprobación mediante lógica de negocio. |

### Patrones de arquitectura

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Workflow | Secuencia relativamente predeterminada de tareas, donde el código sabe qué pasos se ejecutan y en qué orden. | Útil cuando el proceso es estable y requiere trazabilidad. |
| Agente | Sistema en el que el modelo puede elegir pasos o herramientas para cumplir un objetivo dentro de límites controlados. | No equivale a «dar un prompt largo». |
| Agentic loop | Bucle que envía estado a Claude, examina la respuesta, ejecuta herramientas autorizadas y reenvía resultados hasta terminar o alcanzar un límite. | Debe tener un criterio explícito de parada. |
| Prompt chaining | Patrón que divide un proceso en llamadas encadenadas con entradas y salidas de cada etapa. | Ejemplo: clasificar → extraer → resumir. |
| Routing | Selección de una ruta, herramienta, prompt o modelo según el tipo de petición. | Un clasificador puede derivar facturas a extracción y preguntas a búsqueda. |
| Parallelization | Ejecución simultánea de tareas independientes para reducir latencia o explorar alternativas. | Evita paralelizar acciones que dependan de un resultado aún no disponible. |
| Orchestrator–workers | Patrón en el que un coordinador descompone el trabajo y delega subtareas a trabajadores especializados. | Requiere reunir evidencias, errores y resultados parciales. |
| Evaluator–optimizer | Patrón en el que un generador produce una salida y un evaluador la compara con criterios para revisarla. | Definir criterio y límite de iteraciones evita bucles interminables. |
| Single-agent | Diseño con un único agente y herramientas seleccionadas; menor complejidad de coordinación. | Es preferible a multiagente cuando un solo contexto basta. |
| Multi-agent | Arquitectura con varios agentes, normalmente para especialización o aislamiento de contextos. | Más agentes no garantizan mayor precisión; añaden coste y sincronización. |
| Handoff | Transferencia controlada de una tarea o contexto de un componente a otro. | Se debe transferir el estado relevante, no toda la conversación indiscriminadamente. |
| Fan-out / fan-in | Distribuir una solicitud a varias ramas y reunir sus resultados en un punto de decisión. | Ejemplo: tres revisores analizan módulos distintos y un integrador consolida. |
| Supervisor | Agente o servicio que asigna y observa tareas subordinadas y decide reintentos o escalamiento. | No debe convertirse en una autorización implícita de acciones sensibles. |
| Planificación | Descomposición de un objetivo en pasos antes de ejecutarlos. | El plan es revisable; una orden de pago sigue requiriendo autorización. |
| Replanificación | Revisión del plan después de recibir nuevas observaciones o fallos. | Un error de permisos debe cambiar el curso, no disparar reintentos ciegos. |

### Estado, herramientas y límites

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Estado conversacional | Mensajes y resultados de turnos anteriores usados como contexto de la siguiente inferencia. | Debe limitarse y filtrarse por sesión y usuario. |
| Estado de negocio | Información autoritativa de operaciones, órdenes, pagos o expedientes guardada en sistemas controlados. | No depende de que Claude recuerde algo correctamente. |
| Estado de ejecución | Situación de una tarea: pendiente, en progreso, exitosa, fallida o cancelada. | Distinguirlo del estado conversacional permite reanudar trabajos. |
| `tool_use` | Bloque generado por Claude que solicita invocar una herramienta, con nombre, identificador y argumentos. | Es una petición de acción, no una acción ya ejecutada. |
| `tool_result` | Bloque enviado por la aplicación que comunica el resultado de la herramienta solicitada. | Se relaciona con la llamada original mediante `tool_use_id`. |
| `tool_use_id` | Identificador que empareja cada solicitud de herramienta y su respuesta. | Indispensable si se solicitan varias herramientas en el mismo turno. |
| Paralelismo de herramientas | Emisión de varias llamadas a herramientas que pueden ejecutarse de forma concurrente si no existen dependencias. | Comprueba que no producen efectos secundarios incompatibles. |
| Presupuesto de pasos | Límite máximo de turnos o acciones del bucle de un agente. | Previene costes sin límite y ciclos de error repetidos. |
| Presupuesto de tokens | Límite de consumo de entrada/salida o de gasto definido por la aplicación. | `max_tokens` por sí solo no limita el coste de toda una sesión. |
| Timeout | Límite de espera antes de considerar una operación demasiado lenta. | No demuestra que una operación remota no se haya completado. |
| Criterio de parada | Condición verificable para terminar un workflow o agentic loop. | Ejemplo: respuesta válida, cancelación, límite de pasos o error irrecuperable. |
| Idempotencia | Propiedad de una acción que, repetida con el mismo identificador, evita duplicar su efecto. | Crítica para reintentos de pagos, devoluciones o creación de tickets. |
| Idempotency key | Identificador estable asociado a una operación para reconocer duplicados. | No generes una clave nueva en cada reintento de la misma compra. |
| Efecto secundario (side effect) | Modificación observable del exterior: enviar un correo, crear un pedido, borrar un fichero o cobrar. | Requiere controles adicionales frente a una búsqueda solo de lectura. |
| Acción reversible | Operación que puede deshacerse de manera fiable dentro de un proceso definido. | Un borrador suele ser reversible; un pago externo quizá no. |
| Compensación | Operación correctiva que intenta neutralizar el efecto de un paso previo en un workflow distribuido. | No equivale a una transacción atómica. |
| Saga | Patrón para coordinar operaciones distribuidas mediante pasos y compensaciones. | Útil cuando no existe una transacción única entre distintos servicios. |
| Autorización humana (human-in-the-loop) | Revisión o aprobación explícita de una persona antes de una acción relevante. | El humano debe conocer qué se realizará, sobre qué recurso y con qué datos. |
| Escalamiento | Derivación a una persona o sistema especializado al cumplirse un criterio definido. | Puede activarse por política, riesgo, error o evidencia insuficiente. |

### Evaluación y escenarios

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Evaluación por escenarios | Prueba de decisiones arquitectónicas dentro de una historia con restricciones y objetivos de negocio. | Busca el control que resuelve la causa, no la opción con más complejidad. |
| Trade-off | Compromiso entre cualidades como coste, latencia, precisión, mantenibilidad y seguridad. | Mejorar una dimensión puede perjudicar otra. |
| Latencia extremo a extremo | Tiempo desde recibir la solicitud hasta entregar resultado, incluyendo modelo, herramientas, cola y validación. | Un agente con varios turnos puede ser más lento que un workflow fijo. |
| Throughput | Número de solicitudes o trabajos completados por unidad de tiempo. | Paralelizar ayuda al rendimiento total si los límites de API lo permiten. |
| Cuello de botella | Paso que limita la capacidad o velocidad del sistema completo. | Optimizar el prompt no arregla una base de datos saturada. |
| Fallback | Alternativa definida cuando falla el camino principal; puede cambiar de proveedor, modelo, herramienta o procedimiento. | Debe preservar restricciones y permisos. |
| Degradación controlada | Respuesta con funcionalidad reducida en lugar de inventar un resultado tras un fallo. | Ejemplo: mostrar «sin información actualizada» ante caída del buscador. |
| Prueba end-to-end | Prueba que verifica un flujo real entre varios componentes desde entrada hasta resultado. | Complementa pruebas unitarias; no las sustituye. |

### Diseño de agentes y planificación avanzada

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Arquitectura agéntica | Diseño donde un modelo puede decidir acciones dentro de un ciclo de observación y ejecución gobernado por código. | No todo chatbot ni toda automatización es un agente. |
| Autonomía acotada | Capacidad del agente para decidir operaciones dentro de permisos, presupuesto y alcance definidos. | Autonomía no significa acceso irrestricto. |
| Planner–executor | Separación entre quien propone una secuencia de pasos y quien la ejecuta y valida. | Sirve cuando un plan necesita revisión antes de actuar. |
| Plan–act–observe | Ciclo de planificar un paso, ejecutarlo mediante una herramienta y observar su resultado. | No confundas planificación con ejecución efectuada. |
| ReAct | Patrón conceptual de razonamiento orientado a elegir acciones y observar sus efectos iterativamente. | Requiere controles externos: las decisiones del modelo no son autorizaciones. |
| Reflexión (reflection) | Revisión de la propia solución o estrategia a partir de criterios y observaciones. | Sin evidencias nuevas puede limitarse a repetir errores. |
| Self-critique | Revisión crítica generada por el modelo sobre su resultado. | Es útil como señal, pero no equivale a una comprobación independiente. |
| Verificador independiente | Componente que comprueba condiciones con reglas, tests u otra fuente distinta del generador. | Preferible al mismo agente afirmando que su trabajo es correcto. |
| Máquina de estados (FSM) | Modelo formal de estados y transiciones permitidas entre ellos. | Ayuda a impedir saltos como pasar de pendiente a pagado sin autorización. |
| DAG (grafo acíclico dirigido) | Representación de tareas dependientes que no contiene ciclos. | Permite planificar paralelismo seguro entre etapas independientes. |
| Dependencia entre tareas | Relación por la que una etapa necesita la salida o finalización de otra. | Si B necesita A, no las paralelices sin coordinación. |
| Workflow determinista | Flujo cuyo orden y condiciones dependen de reglas programadas y no de decisiones libres del modelo. | Ideal para procesos auditables y estables. |
| Workflow híbrido | Flujo con pasos programados y decisiones acotadas delegadas a un LLM. | Suele equilibrar flexibilidad y previsibilidad. |
| Despachador (dispatcher) | Componente que asigna un trabajo a la herramienta o trabajador autorizado correspondiente. | Valida el destino antes de ejecutar. |
| Registro de herramientas (tool registry) | Catálogo de implementaciones y contratos de herramientas disponibles. | Descripción visible por el LLM y permisos reales son cosas distintas. |
| Broker de herramientas | Intermediario que valida, autoriza, ejecuta y registra las acciones solicitadas por agentes. | Evita dar acceso directo del modelo a servicios sensibles. |
| Contrato de delegación | Acuerdo explícito sobre objetivo, entradas, salidas, restricciones y criterio de éxito de una subtarea. | Reduce resultados imposibles de integrar. |
| Especialización de agentes | Separación de responsabilidades por conocimiento, herramientas o permisos. | Úsala para límites reales, no simplemente para añadir personajes. |
| Coordinación centralizada | Un componente supervisa asignación, dependencias y consolidación. | Facilita control, pero puede convertirse en cuello de botella. |
| Coordinación descentralizada | Varios agentes intercambian mensajes y acuerdan acciones sin un coordinador único. | Requiere resolver concurrencia, duplicados y conflictos. |
| Estado compartido mutable | Datos comunes que varios agentes pueden modificar. | Introduce riesgo de sobrescrituras y condiciones de carrera. |
| Buzón de mensajes (message queue) | Canal para desacoplar productores y consumidores de tareas. | Puede requerir deduplicación e idempotencia. |
| Event-driven orchestration | Activación de transiciones a partir de eventos de otros servicios. | Un evento recibido dos veces no debe duplicar un pago. |
| Condición de carrera (race condition) | Resultado incorrecto porque el orden relativo de operaciones concurrentes cambia. | Ejemplo: dos agentes editan la misma fila sin control de versiones. |
| Bloqueo mutuo (deadlock) | Situación en que dos o más procesos esperan recursos retenidos entre sí. | Diseña orden de adquisición y timeouts. |
| Concurrencia | Progreso de varias tareas durante el mismo intervalo, sin exigir ejecución simultánea real. | Distínguelo de paralelismo físico. |
| Fallo parcial | Una parte del workflow se completa y otra falla. | Debes conservar lo realizado y decidir compensación o reanudación. |
| Consistencia eventual | Las réplicas o servicios pueden converger al mismo estado después de un intervalo. | No presupongas lectura inmediatamente consistente. |
| Cancelación propagada | Transmisión de una orden de cancelación a subtareas y operaciones dependientes. | Detener el razonamiento no cancela automáticamente llamadas remotas. |
| Artefacto intermedio | Archivo o estructura persistida entre etapas, como un plan, CSV o reporte validado. | Mejor que confiar exclusivamente en mensajes resumidos. |
| Criterio de aceptación | Condición medible para considerar completada una tarea delegada. | Ejemplo: tests aprobados y datos contrastados, no «parece correcto». |

### Decisiones de producto y operación

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Intento del usuario (user intent) | Objetivo real que debe satisfacerse, distinto de una frase literal o una instrucción ambigua. | Confirma límites antes de acciones irreversibles. |
| Umbral de riesgo | Regla que eleva el nivel de validación o autorización según impacto o probabilidad de daño. | A más riesgo, menos autonomía automática. |
| Gating | Condición programática que impide avanzar hasta cumplir una validación o aprobación. | Usar gates es más fiable que pedir al modelo que «tenga cuidado». |
| Rollback | Restauración a un estado anterior cuando un cambio puede revertirse. | No aplica automáticamente a operaciones irreversibles de sistemas externos. |
| Checkpoint de ejecución | Estado guardado para reanudar una tarea tras una interrupción. | Debe identificar qué acciones ya se completaron. |
| Protocolo de handoff | Estructura para transferir estado, evidencias y pendientes entre agentes. | Evita pasar todo el historial sin filtrado. |
| Escalada por incertidumbre | Derivación cuando falta evidencia suficiente para una respuesta o una acción. | No equivale a un error técnico. |
| Presupuesto por subtarea | Límite local de coste, llamadas o tiempo asignado a cada trabajador. | Controla que una sola rama no consuma todo el presupuesto. |
| Trazabilidad de decisiones | Capacidad de explicar qué decisión condujo a qué herramienta, resultado y transición. | Útil en auditorías y debugging. |
| Separación de responsabilidades | Dividir planificación, autorización, ejecución y verificación entre componentes. | Evita que el mismo agente se autorice a sí mismo. |

## D2 — Tool Design & MCP Integration

### Contratos y diseño de herramientas

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Herramienta (tool) | Capacidad invocable que proporciona información o realiza una acción fuera de la inferencia del modelo. | La aplicación define quién ejecuta y qué permisos se requieren. |
| Herramienta del cliente (client tool) | Herramienta cuya ejecución corresponde al cliente o backend después de recibir `tool_use`. | Claude no ejecuta directamente la función Python del usuario. |
| Herramienta de servidor (server tool) | Capacidad ejecutada por infraestructura del proveedor como parte de una integración compatible. | El responsable y contrato de ejecución dependen de la herramienta concreta. |
| Tool definition | Declaración de nombre, descripción y esquema de entrada que se comunica al modelo. | Su precisión afecta a la selección y construcción de argumentos. |
| Tool name | Identificador estable de una herramienta. | `buscar_pedido` es preferible a `hacer_cosas`. |
| Tool description | Explicación operativa de cuándo utilizar la herramienta, qué devuelve y qué restricciones tiene. | Las exclusiones reducen selecciones equivocadas. |
| `input_schema` | JSON Schema que describe la estructura de los parámetros de una herramienta. | Tipos y campos obligatorios deben reflejar el contrato real de ejecución. |
| JSON Schema | Vocabulario para describir tipos, objetos, propiedades, restricciones y alternativas de documentos JSON. | Un esquema no demuestra que el contenido obtenido sea verdadero. |
| `properties` | Mapa de campos de un objeto dentro de JSON Schema. | Puede definir `type`, `description`, `enum` y otras restricciones por propiedad. |
| `required` | Lista de nombres de propiedades obligatorias en un objeto JSON. | Un campo incluido en `properties` no es automáticamente obligatorio. |
| `additionalProperties` | Regla que determina si un objeto admite claves no declaradas. | `false` facilita detectar argumentos imprevistos cuando es compatible. |
| `enum` | Conjunto cerrado de valores aceptados para un campo. | Ejemplo: `status` en `pending`, `approved` o `rejected`. |
| `format` | Anotación de formatos comunes en JSON Schema, como fecha o correo, cuyo efecto depende del validador. | Comprueba si el motor realmente valida ese formato. |
| Validación sintáctica | Comprobación de que la representación se puede analizar como JSON o estructura esperada. | JSON válido puede violar el esquema. |
| Validación estructural | Comprobación de tipos, campos obligatorios, valores admitidos y forma. | No demuestra que exista el pedido solicitado. |
| Validación semántica | Comprobación de consistencia y sentido real de los argumentos o resultados. | Una fecha en formato correcto puede estar fuera del periodo permitido. |
| Normalización de argumentos | Conversión controlada de parámetros a un formato canónico antes de ejecutar. | Por ejemplo, estandarizar zona horaria sin alterar el significado. |
| `tool_choice` | Configuración que controla cómo Claude puede elegir herramientas en una solicitud. | Las opciones admitidas dependen del modelo; revisa documentación actual. |
| `auto` | Modalidad que permite a Claude contestar directamente o solicitar una herramienta cuando corresponda. | Suele ser la opción predeterminada. |
| `none` | Modalidad que impide nuevas llamadas a herramientas en una solicitud. | Útil al pedir solo una síntesis a partir de datos ya obtenidos. |
| `any` | Modalidad de selección forzada de alguna herramienta cuando el modelo la admite. | No está disponible para todos los modelos actuales. |
| `tool` forzada | Opción que obliga a llamar a una herramienta específica cuando el modelo lo admite. | En modelos incompatibles puede devolver error en lugar de obedecer el prompt. |
| Strict tool use | Configuración que restringe la forma de los argumentos de una llamada al esquema admitido. | `strict: true` no otorga permisos ni garantiza verdad factual. |
| Herramienta de solo lectura | Operación que recupera información sin modificar recursos. | Puede seguir exponiendo datos sensibles y exige autorización. |
| Herramienta de escritura | Operación que crea, actualiza o elimina estado. | Requiere validación, permisos y potencialmente aprobación humana. |
| Principio de mínimo privilegio | Conceder a cada herramienta y proceso solo los permisos indispensables. | Una búsqueda de tickets no necesita permisos para cancelarlos. |
| Allowlist | Lista explícita de herramientas, dominios o acciones permitidas. | El modelo no debe poder ampliarla por sí mismo. |

### Errores, flujo y recuperación

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Resultado estructurado | Respuesta de herramienta con campos coherentes que permitan diferenciar éxito, ausencia de datos y fallo. | Prefiere códigos y datos sobre mensajes vagos. |
| Error estructurado | Respuesta de fallo con `code`, mensaje, contexto seguro y condición de recuperación. | `NOT_FOUND` no es lo mismo que `FORBIDDEN`. |
| `isError` (MCP) | Marcador del resultado de una llamada a herramienta MCP que señala fallo de ejecución de la herramienta. | Difiere de un error de transporte o de protocolo JSON-RPC. |
| `NOT_FOUND` | Código de aplicación que indica ausencia real del recurso solicitado entre los accesibles. | No debe usarse para esconder indiscriminadamente cualquier error de permisos sin una política explícita. |
| `FORBIDDEN` | Código de aplicación que indica que el actor no está autorizado para la acción. | Cambiar el prompt no debe habilitar ese acceso. |
| `UNAUTHORIZED` | Código de aplicación que suele indicar autenticación ausente o inválida. | Se diferencia de estar autenticado sin permisos suficientes. |
| `RATE_LIMITED` | Error por alcanzar cuotas o límites de solicitudes. | Maneja `Retry-After` si está disponible y evita ráfagas de reintentos. |
| Error transitorio | Fallo potencialmente recuperable, como una indisponibilidad temporal de red. | Solo reintenta cuando existe una estrategia segura. |
| Error permanente | Fallo que requiere cambiar entrada, permisos o configuración. | Repetirlo idéntico suele desperdiciar tokens y recursos. |
| Validación en frontera (boundary validation) | Comprobación de entrada/salida cuando los datos cruzan entre modelo, backend y sistemas externos. | Es independiente de que Claude haya emitido un JSON perfecto. |
| Mapeo de `tool_use_id` | Asociación precisa de cada resultado con la llamada que lo originó. | Evita cruzar resultados paralelos de diferentes solicitudes. |
| Dispatch de herramientas | Lógica que busca una implementación aprobada por el nombre recibido del modelo. | Nunca uses `eval()` para ejecutar nombres de función propuestos. |
| Registro de auditoría | Historial de decisiones, parámetros autorizados y efectos ejecutados, con tratamiento de datos sensibles. | Permite reconstruir una acción sin exponer secretos. |

### MCP: actores, capacidades y transporte

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| MCP (Model Context Protocol) | Protocolo abierto de interoperabilidad para exponer herramientas, recursos y prompts a aplicaciones de IA. | Es una interfaz de integración, no una autorización de acceso automático. |
| Host MCP | Aplicación que gestiona la conexión y experiencia con uno o varios servidores MCP. | Un host puede crear o controlar clientes MCP. |
| Cliente MCP | Componente del host que se comunica con un servidor MCP siguiendo una versión negociada o compatible del protocolo. | Descubre e invoca capacidades expuestas. |
| Servidor MCP | Proceso o servicio que publica capacidades MCP y gestiona las solicitudes según sus políticas. | Puede ser local o remoto. |
| MCP Tool | Capacidad ejecutable de un servidor MCP expuesta mediante las operaciones de herramientas. | Adecuada para consultar una API o ejecutar una acción. |
| MCP Resource | Fuente legible de contexto expuesta por URI o plantilla. | Adecuada para documentos, esquemas o datos de referencia. |
| MCP Prompt | Plantilla reutilizable de mensajes o instrucciones proporcionada por el servidor. | No es una función que ejecute acciones. |
| URI | Identificador de recurso, utilizado para localizar contenido MCP. | Una URI no demuestra que el contenido sea accesible por el usuario actual. |
| URI template | Plantilla parametrizada para resolver recursos, por ejemplo `docs://manual/{id}`. | Evita crear una herramienta solo para leer un recurso representable por URI. |
| `tools/list` | Operación MCP para descubrir herramientas declaradas por el servidor. | Descubrir una herramienta no implica poder usarla sin permisos. |
| `tools/call` | Operación MCP para solicitar la ejecución de una herramienta. | Debe aplicar autenticación y validación dentro del servidor/backend. |
| `resources/list` | Operación MCP para enumerar recursos disponibles. | Los recursos individuales suelen leerse con `resources/read`. |
| `resources/read` | Operación MCP para obtener contenido asociado a una URI. | El contenido es dato externo, no instrucción privilegiada. |
| `prompts/list` | Operación MCP para enumerar plantillas de prompt. | No confundir con un `system` prompt de la aplicación. |
| `prompts/get` | Operación MCP para recuperar una plantilla y sus argumentos cuando proceda. | No activa automáticamente ninguna acción de negocio. |
| JSON-RPC | Formato de mensajes usado por MCP para solicitudes, respuestas y errores. | Su error protocolario no equivale a `isError` dentro de un resultado de herramienta. |
| `stdio` | Transporte MCP que utiliza entrada y salida estándar entre procesos, habitual en servidores locales. | Reserva `stdout` al protocolo y envía logs a `stderr`. |
| Streamable HTTP | Transporte de comunicación MCP sobre HTTP utilizado para conexiones remotas en especificaciones compatibles. | Necesita seguridad de red y autenticación apropiadas. |
| SSE heredado | Estilo de transporte o entrega de eventos presente en integraciones anteriores de MCP. | No asumas que el transporte legacy sigue siendo el recomendado. |
| Versión MCP | Revisión de la especificación que determina envelope, ciclo de vida y capacidades disponibles. | Un cliente antiguo y uno moderno pueden implementar flujos distintos. |
| MCP 2025-11-25 | Revisión anterior frecuente en ejemplos de cursos, con inicialización y semánticas de sesión diferentes de las modernas. | Identifica la versión de cualquier tutorial antes de copiar su implementación. |
| MCP 2026-07-28 | Revisión que adopta núcleo sin sesión obligatoria, descubrimiento opcional de servidor y solicitudes multi-round-trip. | Cambia los detalles de inicialización; no basta memorizar ejemplos antiguos. |
| `server/discover` | Operación opcional de descubrimiento de servidor en MCP 2026-07-28. | No la confundas con el antiguo intercambio `initialize`/`initialized`. |
| Multi-Round-Trip Requests (MRTR) | Mecanismo de MCP 2026-07-28 que permite al servidor pedir información adicional y retomar la petición original. | Puede utilizarse para confirmación o parámetros faltantes. |
| `input_required` | Resultado intermedio de MRTR que expresa que falta una respuesta del cliente/usuario para finalizar el trabajo. | No es un resultado final satisfactorio. |
| MCP Inspector | Herramienta para descubrir y probar servidores MCP de forma interactiva. | Permite probar herramientas sin gastar tokens de la API del modelo. |
| `FastMCP` | Abstracción de SDK para crear servidores MCP con decoradores y menos código repetitivo. | Sintaxis exacta y rutas de importación dependen de la versión instalada. |
| OAuth | Marco de autorización usado para delegar acceso a recursos protegidos bajo alcances y consentimiento apropiados. | No confundas un token válido con permiso para cualquier operación. |
| Scope de autorización | Alcance otorgado a un cliente o token para recursos y acciones concretos. | Debe verificarse también en operaciones de escritura. |
| Prompt injection en herramientas | Instrucciones maliciosas insertadas en contenido externo que podría recibir Claude mediante una herramienta. | El resultado de una búsqueda nunca debe poder cambiar reglas de acceso. |

### Integración de herramientas y contratos de ejecución

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Descubrimiento de herramientas (tool discovery) | Mecanismo por el que un agente o cliente conoce las capacidades disponibles. | Descubrir una capacidad no autoriza utilizarla. |
| Búsqueda de herramientas (tool search) | Selección bajo demanda de definiciones relevantes cuando existen muchas herramientas. | Reduce contexto inicial, pero exige gestionar referencias a herramientas. |
| Carga diferida (`defer_loading`) | Opción documentada para no introducir una definición de herramienta al contexto hasta necesitarla. | No es lo mismo que ejecutar la herramienta en segundo plano. |
| Caller o invocador | Entidad autorizada que puede solicitar el uso de una herramienta. | Las políticas deben aplicarse en el backend. |
| Programmatic tool calling | Patrón en que un entorno programático aprobado coordina ciertas llamadas sin un turno individual del modelo por cada una. | No elimina la validación ni el control de permisos. |
| Tool runner (SDK) | Utilidad que automatiza partes del bucle de llamadas de herramientas y sus resultados. | Comprende el ciclo manual antes de delegarlo al SDK. |
| `name` de herramienta | Identificador concreto que el modelo envía para invocar una definición disponible. | Debe coincidir con un registro aprobado. |
| `description` de herramienta | Explicación de cuándo usar una capacidad y sus restricciones. | Una descripción ambigua provoca invocaciones incorrectas. |
| `input_examples` | Ejemplos de argumentos proporcionados en definiciones compatibles de herramientas. | Complementan, pero no sustituyen, al esquema. |
| `strict: true` | Opción que impone conformidad estructural en las llamadas a herramientas que la admiten. | Revisa compatibilidad según tipo de herramienta y modelo. |
| `eager_input_streaming` | Opción documentada para enviar fragmentos del argumento de una herramienta antes de completar toda su entrada. | Exige consumo incremental cuidadoso. |
| Streaming de herramientas | Recepción parcial de la salida del modelo mientras prepara una llamada de herramienta. | No ejecutes argumentos parciales como si fueran definitivos. |
| `tool_reference` | Referencia a una herramienta descubierta mediante búsqueda/carga diferida. | La disponibilidad puede depender de la configuración de herramientas. |
| `allowed_callers` | Restricción sobre los entornos o llamadores autorizados a invocar una herramienta compatible. | No debe confundirse con permisos del usuario final. |
| Esquema de salida (`outputSchema`) | Declaración MCP que describe cómo debe estructurarse el resultado de una herramienta. | No valida automáticamente la veracidad de esos datos. |
| `structuredContent` | Contenido estructurado opcional que una herramienta MCP puede devolver conforme a su contrato. | Distinto del texto explicativo del resultado. |
| `content` de herramienta | Bloques de información devueltos como texto, imágenes u otros formatos admitidos. | Un resultado puede contener más de un bloque. |
| Contenido multimodal | Respuesta que combina texto, imágenes, audio u otros tipos admitidos. | Los consumidores deben identificar los tipos antes de procesarlos. |
| MIME type | Etiqueta de tipo de contenido, como `application/json` o `text/plain`. | Ayuda a interpretar recursos y adjuntos. |
| Data URL | Representación de contenido incorporado directamente en una URL. | Considera tamaño y tratamiento de datos sensibles. |
| Tool-result poisoning | Inclusión de instrucciones maliciosas dentro de la respuesta de una herramienta. | El resultado de una herramienta es dato no confiable. |
| Confusión de herramientas (tool shadowing) | Dos capacidades con nombres o descripciones parecidas generan selección equivocada. | Usa contratos claros y namespaces. |

### MCP: comunicación, sesiones y descubrimiento

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Handshake MCP legado | Intercambio `initialize`/`initialized` utilizado por versiones anteriores del protocolo. | No lo impongas a implementaciones modernas sin verificar su versión. |
| `MCP-Protocol-Version` | Cabecera asociada a la versión de protocolo en el modelo HTTP moderno de MCP. | Ayuda a verificar compatibilidad entre extremos. |
| Sesión MCP | Estado de conexión utilizado por ciertos transportes y revisiones del protocolo. | El diseño moderno puede operar sin sesión de transporte. |
| Servidor sin estado (stateless) | Servicio que procesa cada solicitud con toda la información necesaria o con referencias explícitas. | Un cliente no debe suponer memoria implícita entre llamadas. |
| Identificador JSON-RPC (`id`) | Campo que relaciona una petición JSON-RPC con su respuesta. | No es el mismo identificador que `tool_use_id` de Messages API. |
| Notificación JSON-RPC | Mensaje de protocolo que no requiere respuesta con identificador. | Útil para avisos y cambios de disponibilidad compatibles. |
| Código de error JSON-RPC | Número de error del protocolo por petición inválida o fallo de enrutamiento. | Se diferencia de un `isError` en `tools/call`. |
| Paginación MCP | Distribución de listados extensos de recursos o herramientas en páginas. | Es necesario consumir sucesivos cursores cuando correspondan. |
| Cursor MCP | Referencia opaca usada para continuar un listado paginado. | No deduzcas su contenido ni fabriques cursores. |
| `notifications/tools/list_changed` | Notificación disponible en revisiones o servidores compatibles al cambiar el catálogo de herramientas. | El cliente debe refrescar la lista, no conservarla indefinidamente. |
| Suscripción a recursos | Mecanismo de avisos ante cambios de recursos, según compatibilidad del servidor. | Evita consultas repetitivas cuando está disponible. |
| Resource template | Patrón de URI para recursos parametrizados. | Un recurso es para lectura de contexto, no una orden ejecutable. |
| Embedded resource | Recurso presentado dentro de un resultado o bloque de contenido. | Trata su texto como entrada externa sin privilegios. |
| Resource link | Enlace a un recurso publicado por el servidor dentro de la respuesta de una herramienta. | Aplica autorización al leerlo. |
| `ttlMs` | Indicación temporal de caché incluida en ciertas respuestas de descubrimiento del MCP moderno. | Una política de caché no implica información eternamente válida. |
| `cacheScope` (MCP) | Campo relativo al alcance de caché en respuestas modernas del protocolo. | No es el `cache_control` de prompt caching de Anthropic. |
| Task handle (MCP) | Identificador de una operación larga cuyo estado puede consultarse más tarde. | Evita bloquear una llamada HTTP hasta terminar. |
| `tasks/get` | Operación para consultar el estado de una tarea MCP en implementaciones compatibles. | No equivale a repetir `tools/call`. |
| `tasks/cancel` | Operación de solicitud de cancelación de una tarea MCP compatible. | Cancelar puede requerir verificar si hubo efectos anteriores. |
| `tasks/update` | Operación relacionada con el intercambio de actualizaciones o entradas de tareas en el MCP moderno compatible. | Consulta el contrato de la versión antes de utilizarla. |
| Solicitud multi-vuelta | Interacción en varias fases cuando un servidor necesita información adicional para completar un trabajo. | En MCP moderno, evita asumir peticiones de servidor iniciadas fuera del modelo compatible. |
| Elicitación (elicitation) | Obtención de datos o consentimiento del usuario durante una interacción MCP. | No debe utilizarse para pedir secretos por canales inseguros. |
| Sampling MCP | Solicitud de generación al modelo desde un servidor MCP en protocolos que lo admiten. | La forma tradicional quedó obsoleta en MCP 2026-07-28. |
| Roots MCP | Información de raíces de archivos compartida entre cliente y servidor en revisiones antiguas. | El modelo tradicional de roots quedó obsoleto en MCP 2026-07-28. |

### MCP: operación y autenticación

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| `.mcp.json` | Archivo de configuración de servidores MCP de ámbito de proyecto usado por Claude Code. | Revisar el archivo antes de aprobar y versionar; no guardar tokens. |
| `claude mcp add` | Comando para registrar un servidor MCP en Claude Code. | Elegir correctamente transporte y ámbito. |
| `claude mcp list` | Comando para enumerar los servidores MCP configurados. | Útil para diagnosticar servidores no cargados. |
| `claude mcp get` | Comando que consulta configuración o estado de un servidor MCP por nombre. | Confirma su conexión antes de depurar herramientas. |
| `claude mcp remove` | Comando para retirar una configuración de servidor MCP. | No implica borrar datos del servicio remoto. |
| Scope MCP: local | Configuración que se aplica al proyecto local para el usuario actual. | No se comparte automáticamente con el repositorio. |
| Scope MCP: project | Configuración compartible mediante `.mcp.json` del repositorio. | Puede requerir aprobación de confianza. |
| Scope MCP: user | Configuración disponible para varios proyectos del mismo usuario. | Más amplia que project y local. |
| `npx` | Ejecuta paquetes Node.js, frecuentemente servidores MCP publicados en npm. | Fija versiones para mejorar reproducibilidad. |
| `uvx` | Ejecuta herramientas Python en entornos gestionados por uv. | Útil para levantar servidores MCP Python sin instalaciones permanentes. |
| `pipx` | Instala y ejecuta aplicaciones Python aisladas en un entorno por aplicación. | No es idéntico a `uvx` ni a `pip` del proyecto. |
| OAuth 2.0 | Marco de autorización delegado para obtener tokens con permisos acotados. | No equivale a enviar la API key del usuario al modelo. |
| PKCE | Refuerzo de OAuth que vincula el intercambio del código de autorización al cliente que inició el flujo. | Especialmente relevante para clientes públicos. |
| Audience de token | Destinatario para el cual se emitió un token. | Un servidor debe rechazar tokens destinados a otra API. |
| Expiración de token | Momento a partir del cual una credencial deja de ser válida. | Una conexión que funcionaba ayer puede fallar hoy. |
| SSRF | Ataque que induce a un servidor a realizar peticiones de red hacia destinos no autorizados. | Valida URL, DNS y destinos en herramientas de fetch. |

## D3 — Claude Code Configuration & Workflows

### Arquitectura de Claude Code y memoria

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Claude Code | Entorno de desarrollo asistido por Claude capaz de inspeccionar archivos, proponer cambios y usar herramientas bajo permisos. | No lo confundas con llamadas directas al SDK de Messages API. |
| CLI | Interfaz de línea de comandos para interactuar con herramientas y programas desde una terminal. | Claude Code ofrece una CLI, pero también otras superficies de uso. |
| Workspace | Directorio o conjunto de archivos accesible a una sesión de trabajo. | El directorio inicial influye en qué configuración se carga. |
| `CLAUDE.md` | Archivo de instrucciones persistentes para el proyecto o usuario, usado para convenciones y contexto de trabajo. | Es una guía de comportamiento, no un secreto ni un control de seguridad. |
| Memoria de proyecto | Conjunto de instrucciones o notas relevantes para trabajar en un repositorio específico. | Separa lo que vale para todos de tus preferencias personales. |
| Memoria de usuario | Instrucciones que se aplican a proyectos del mismo usuario cuando el entorno las carga. | No las uses para reglas particulares de un único cliente o repositorio. |
| `~/.claude/CLAUDE.md` | Ubicación habitual de instrucciones personales de Claude Code en el directorio del usuario. | Afecta a más de un proyecto; evita detalles internos que no deban difundirse. |
| `./CLAUDE.md` | Instrucciones del repositorio que pueden versionarse con Git. | Incluye comandos, arquitectura y acuerdos de estilo mantenidos por el equipo. |
| `CLAUDE.local.md` | Archivo de instrucciones locales utilizado en entornos que admiten esta convención. | No lo publiques si contiene rutas o preferencias privadas; verifica soporte según versión. |
| `.claude/rules/` | Directorio para organizar instrucciones temáticas o condicionadas por rutas. | Una regla de Python no tiene por qué contaminar revisiones de documentación. |
| Reglas condicionadas por rutas | Instrucciones que se aplican cuando los archivos coinciden con ciertos patrones. | Facilitan convenciones diferentes para `src/**` y `tests/**`. |
| Importación de instrucciones | Referencia a documentación adicional desde instrucciones compatibles para evitar duplicación. | Mantén rutas válidas y evita ciclos confusos. |
| Concentración de contexto | Técnica de mantener instrucciones breves, accionables y relacionadas con el trabajo actual. | Un `CLAUDE.md` enorme compite por tokens con el problema real. |

### Settings y precedencia

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| `settings.json` | Archivo JSON que define opciones de Claude Code, incluyendo permisos, hooks o preferencias según su alcance. | Su ubicación modifica a qué usuarios o proyectos se aplica. |
| `~/.claude/settings.json` | Configuración de usuario que afecta a proyectos de esa instalación. | Adecuada para preferencias personales globales. |
| `.claude/settings.json` | Configuración compartida del proyecto, normalmente versionable con el repositorio. | Útil para normas y hooks del equipo. |
| `.claude/settings.local.json` | Configuración local de un proyecto, destinada a ajustes particulares y generalmente excluida de Git. | No la uses como política corporativa común. |
| Managed settings | Configuración administrada por una organización con prioridad y restricciones superiores a ajustes individuales. | Una excepción local no debe saltarse políticas gestionadas. |
| Precedencia de configuración | Regla que resuelve valores coincidentes procedentes de distintos ámbitos. | La configuración gestionada tiene prioridad sobre ajustes de usuario. |
| Fusión de listas de permisos | Comportamiento por el que algunas listas se combinan entre archivos en vez de sustituirse. | No des por hecho que «override» elimina todos los permisos anteriores. |
| Permiso `allow` | Regla que autoriza automáticamente ciertas herramientas o acciones dentro de un alcance. | Configúrala estrechamente para comandos de bajo riesgo. |
| Permiso `ask` | Regla que solicita consentimiento interactivo antes de ejecutar acciones concretas. | No garantiza disponibilidad de aprobación en flujos no interactivos. |
| Permiso `deny` | Regla que bloquea determinadas acciones o recursos. | Es más robusta que pedir en texto «no abras ese archivo». |
| Principio de privilegio mínimo en Claude Code | Restringir lectura, escritura y ejecución a las capacidades necesarias para cada tarea. | No habilites comandos amplios para resolver un caso puntual. |
| Permission mode | Política de interacción y autorización aplicada a las herramientas de la sesión. | El modo de planificación no debería interpretarse como permiso general de escritura. |
| Plan Mode | Modo orientado a explorar y planificar cambios antes de ejecutarlos. | Útil al revisar una migración grande o una refactorización delicada. |
| Sandbox | Entorno restringido para ejecutar operaciones con menos acceso al sistema anfitrión. | No sustituye validación de datos o permisos remotos. |
| Workspace trust | Evaluación de confianza del repositorio o entorno antes de adoptar determinadas configuraciones. | Un `settings.json` de una procedencia desconocida puede contener hooks peligrosos. |
| `/status` | Comando de Claude Code para inspeccionar información de sesión y fuentes de configuración cargadas. | Útil al diagnosticar por qué una regla no se aplica. |
| `claude doctor` | Comprobación diagnóstica de entorno y configuración de Claude Code. | Ayuda a detectar configuraciones inválidas o dependencias ausentes. |

### Hooks, habilidades y subagentes

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Hook | Programa o mecanismo ejecutado al producirse un evento del ciclo de trabajo de Claude Code. | Se utiliza para aplicar controles, automatizar comprobaciones o aportar contexto. |
| `PreToolUse` | Evento de hook antes de ejecutar una herramienta. | Punto adecuado para examinar y, si procede, bloquear operaciones de riesgo. |
| `PostToolUse` | Evento que se activa tras ejecutar una herramienta. | Útil para registrar resultados o lanzar comprobaciones automáticas. |
| `SessionStart` | Evento del comienzo de una sesión cuando está soportado por la versión del entorno. | Permite inicializar contexto no sensible. |
| `Stop` | Evento relacionado con el final de una respuesta o ejecución de Claude. | No significa automáticamente que todas las pruebas estén aprobadas. |
| Hook matcher | Patrón que determina qué herramientas o eventos activan un hook. | Mantén coincidencias específicas para no bloquear todo el entorno. |
| Código de salida de hook | Señal del proceso que indica finalización o fallo y cuyo significado de control depende del evento. | Verifica el contrato del hook antes de usar códigos para denegar operaciones. |
| Hook fail-open / fail-closed | Decisión sobre permitir o bloquear si la validación de un hook falla. | Para operaciones destructivas se suele preferir una política conservadora. |
| Skill | Capacidad reutilizable documentada con instrucciones y, a veces, scripts o recursos auxiliares. | Adecuada para procesos repetibles como revisar notebooks. |
| `SKILL.md` | Archivo que define cómo usar una skill y qué procedimiento debe seguirse. | Describe prerrequisitos, secuencia y criterios de comprobación. |
| Slash command | Comando invocable desde la interfaz para activar acciones o flujos admitidos. | No es sinónimo exacto de skill; la implementación puede variar por versión. |
| Subagente | Especialista separado, normalmente con instrucciones, herramientas y contexto propios. | Sirve para aislar tareas como revisión de seguridad o tests. |
| Aislamiento de contexto del subagente | Separación de mensajes y material de trabajo entre el agente principal y un especialista. | Reduce ruido y evita mezclar conversaciones independientes. |
| Agente de revisión | Subagente encargado de evaluar cambios respecto a criterios definidos. | Debe solicitar evidencias de pruebas en vez de dar aprobaciones vacías. |
| Agente explorador | Subagente orientado a localizar archivos, dependencias o información relevante. | Limita herramientas si no necesita modificar código. |
| Delegación de tareas | Asignación de una subtarea con objetivo, alcance, entradas y salida esperada. | Una orden vaga aumenta el trabajo de integración. |

### Flujos de ingeniería y automatización

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| `claude -p` | Modo de ejecución no interactiva que permite integrar Claude Code en scripts o automatizaciones compatibles. | Requiere planificar cómo funcionarán permisos y errores sin usuario presente. |
| Salida no interactiva | Resultado de un comando diseñado para ser consumido por scripts, no solo mostrado en una terminal. | Usa formatos analizables y códigos de salida. |
| Reanudación de sesión | Continuar trabajo con historial o estado recuperado por la herramienta. | No sustituye persistencia de los datos de negocio. |
| Git branch | Rama de trabajo para aislar cambios respecto a otras líneas de desarrollo. | Útil para experimentar sin comprometer `main`. |
| Pull request (PR) | Propuesta de integración de cambios que puede incluir revisión y comprobaciones. | Un PR aprobado no reemplaza controles automáticos. |
| CI (integración continua) | Ejecución automática de tests, lint y otros controles cuando cambia el código. | Recomendable antes de fusionar una rama. |
| CD (entrega/despliegue continuo) | Automatización de entrega o despliegue después de verificaciones definidas. | Separar aprobación de despliegue según riesgo. |
| GitHub Actions | Plataforma de automatización basada en workflows del repositorio. | No incluyas secretos en logs ni artefactos de pruebas. |
| Test unitario | Prueba aislada de una función o clase en condiciones controladas. | Un mock evita depender de la API real para evaluar la lógica. |
| Test de integración | Prueba del acoplamiento entre módulos o servicios. | Puede descubrir errores que pasan desapercibidos en unit tests. |
| Mock | Sustituto controlado de una dependencia externa para ejecutar pruebas reproducibles. | No demuestra que la API real se comporte siempre igual. |
| Dry run | Ejecución de previsualización sin aplicar cambios reales. | Especialmente útil para scripts que mueven o eliminan archivos. |
| Lint | Análisis estático de estilo y patrones potencialmente problemáticos. | No garantiza corrección funcional. |
| Formateador | Herramienta que ajusta automáticamente estilo del código según reglas. | Mantén formateo separado de modificaciones lógicas grandes. |
| Diff | Comparación entre versiones de archivos. | Es la base de una revisión cuidadosa antes de `git add` o `git commit`. |
| Commit | Registro versionado de un conjunto coherente de cambios. | Evita mezclar documentación, claves y experimentos en un mismo commit. |
| Rama protegida | Rama cuyas actualizaciones están sujetas a políticas como PR y pruebas obligatorias. | No sustituye la revisión del código ejecutado por CI. |
| Dependencias reproducibles | Versiones y pasos de instalación suficientes para reconstruir el entorno. | Publica manifiestos, no tu carpeta `.venv/`. |
| `pyproject.toml` | Archivo de metadatos, construcción y configuración de proyectos Python modernos. | Facilita instalar tu paquete en modo editable. |
| `pip install -e .` | Instalación editable de un paquete Python desde la raíz del proyecto. | Permite importar módulos de `src/` desde notebooks con el mismo entorno. |
| `__init__.py` | Archivo de inicialización de un paquete Python convencional. | Puede estar vacío; ayuda a organizar imports explícitos. |

### Herramientas nativas de Claude Code: localizar, leer y modificar

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| `Glob` | Herramienta de Claude Code para localizar rutas cuyos nombres coinciden con patrones comodín. | Busca archivos por ruta/nombre; ejemplo conceptual: `**/*.py`. |
| `Grep` | Herramienta de Claude Code para localizar coincidencias de contenido en archivos, habitualmente mediante expresiones regulares. | Busca texto/código dentro de archivos; ejemplo: `ANTHROPIC_API_KEY`. |
| Glob pattern | Expresión de coincidencia por nombre/ruta que utiliza comodines; no es una expresión regular. | `**/*.ipynb` busca notebooks, no contenido de notebooks. |
| Grep pattern | Patrón de búsqueda de contenido, normalmente regex. | `def\s+\w+` localiza definiciones de funciones en texto Python. |
| `*` en glob | Comodín para secuencias de caracteres dentro del segmento de ruta según implementación. | `*.py` busca nombres con extensión `.py` en el ámbito seleccionado. |
| `**` en glob | Comodín utilizado habitualmente para abarcar subdirectorios recursivamente. | `**/test_*.py` localiza archivos de prueba en varias carpetas. |
| `?` en glob | Comodín de un único carácter en patrones glob convencionales. | `dia?.md` coincide con `dia1.md`, no con `dia10.md`. |
| Clases de caracteres glob | Patrón como `[ab]` que representa un carácter del conjunto en motores compatibles. | No confundas este mecanismo con clases completas de regex. |
| Regex (expresión regular) | Lenguaje de patrones de texto con cuantificadores, clases y grupos. | Es central para `Grep`/`rg`, pero no equivale a glob. |
| Regex literal | Parte de un patrón regex que representa caracteres sin semántica especial. | Escapa metacaracteres si buscas texto literal. |
| `\d` | Patrón regex habitual para encontrar un dígito. | `ID-\d+` coincide con una serie de dígitos tras el prefijo. |
| `\s` | Patrón regex habitual para espacios y otros caracteres de separación. | `def\s+main` detecta espacios entre ambas palabras. |
| `^` y `$` en regex | Anclas de inicio y final de línea o texto, según modo. | Útiles para localizar declaraciones y evitar coincidencias parciales. |
| Alternancia regex (`a\|b`) | Operador lógico de alternativa entre patrones. | Para buscar `error` o `warning`, usa una regex con alternancia. |
| Diferencia Glob / Grep | Glob selecciona rutas por nombre; Grep inspecciona contenido para localizar coincidencias. | Si sabes extensión, empieza por Glob; si buscas una función, Grep. |
| Filtro por extensión | Restricción de resultados a un tipo de archivo. | Limita una búsqueda textual a `*.py` para evitar binarios y notebooks ajenos. |
| Búsqueda recursiva | Exploración de un directorio y sus subdirectorios. | Evita leer manualmente toda una estructura grande. |
| Búsqueda sensible a mayúsculas | Comparación que distingue `Client` de `client`. | La semántica exacta depende de herramienta, flags y plataforma. |
| Archivos ocultos (dotfiles) | Entradas cuyo nombre empieza por punto, como `.env` y `.gitignore`. | La visibilidad en herramientas de búsqueda depende de su configuración. |
| `Read` | Herramienta de Claude Code que lee el contenido de archivos disponibles. | Para comprender `config.py`, primero localízalo y luego léelo. |
| `Edit` | Herramienta que modifica contenido de un archivo existente mediante ediciones controladas. | Inspecciona el diff y valida que la coincidencia sea la correcta. |
| `Write` | Herramienta que crea o reemplaza contenido de un archivo autorizado. | Trátala como operación de escritura, no como lectura. |
| `NotebookEdit` | Herramienta especializada para editar celdas o contenido de notebooks Jupyter cuando está disponible. | Preserva la estructura del notebook y revisa sus outputs. |
| `Bash` | Herramienta de Claude Code para ejecutar comandos de shell conforme a permisos. | `Bash` no es un lenguaje Python ni sustituye las herramientas específicas de archivos. |
| `PowerShell` | Herramienta de ejecución de comandos PowerShell en entornos y versiones compatibles. | Su sintaxis difiere de Git Bash y debe verificarse. |
| `WebSearch` | Herramienta de Claude Code para buscar información en la web cuando está habilitada. | Un snippet no equivale a evidencia verificada. |
| `WebFetch` | Herramienta para recuperar contenido de una URL accesible en las condiciones permitidas. | El contenido remoto nunca hereda privilegios de instrucciones. |
| `Agent` | Herramienta de Claude Code para delegar trabajo a un subagente. | No es un equivalente de `Grep`: crea una ejecución con contexto y recursos propios. |
| `AskUserQuestion` | Herramienta de ciertos flujos de Claude Code para solicitar decisiones o aclaraciones al usuario. | Úsala si una acción exige una elección no inferible. |
| Modo de solo lectura | Operación en la que se permite explorar sin modificar archivos ni ejecutar efectos de escritura. | Adecuada para comprender antes de editar. |

### Consola y patrones de búsqueda que debes distinguir

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| `grep` (comando) | Utilidad tradicional de terminal para buscar líneas coincidentes con un patrón. | `grep -n 'API_KEY' config.example.py` muestra línea y coincidencia. |
| `rg` / ripgrep | Herramienta de terminal para búsquedas de contenido rápidas, usada también en integraciones de búsqueda de Claude Code. | `rg -n 'def main' src/`. |
| `rg --files` | Lista rutas de archivos encontradas por ripgrep sin inspeccionar el texto como un `rg` convencional. | Es una alternativa en terminal para descubrir archivos. |
| `rg -n` | Muestra números de línea junto a coincidencias. | Ayuda a saltar desde resultados a VS Code. |
| `rg -l` | Lista solo archivos donde aparece una coincidencia. | Útil si quieres nombres de archivos, no todas las líneas. |
| `rg -i` | Realiza una búsqueda de texto sin distinguir mayúsculas en ripgrep. | Ejemplo: `rg -i 'timeout' docs/`. |
| `rg -g` | Aplica un filtro glob a los archivos examinados por ripgrep. | `rg 'Anthropic' -g '*.py'` mezcla regex de contenido y glob de nombre. |
| `rg --hidden` | Incluye archivos ocultos en la búsqueda de ripgrep, sujeto a otras reglas de exclusión. | Evita buscar secretos por accidente. |
| `rg -F` | Interpreta el patrón como texto literal en lugar de expresión regular. | Útil para buscar `client.messages.create(` tal cual. |
| `find` (comando) | Utilidad Unix de búsqueda de archivos y carpetas por criterios como nombre o tipo. | `find . -name '*.py'` busca rutas, no cadenas dentro del archivo. |
| `ls` | Lista entradas de un directorio. | `ls -la` revela también entradas ocultas en Git Bash. |
| `pwd` | Imprime el directorio de trabajo actual. | Confirma desde dónde se interpretan rutas relativas. |
| `cd` | Cambia el directorio activo de la terminal. | `cd Checkpoints/Dia_3...` modifica la base de rutas. |
| `cat` | Muestra o concatena texto de archivos. | Evita imprimir archivos con secretos en logs públicos. |
| `head` | Muestra las primeras líneas de un archivo o flujo. | `head -n 20 README.md`. |
| `tail` | Muestra las últimas líneas de un archivo o flujo. | Útil para logs extensos. |
| `sed` | Utilidad de procesamiento de texto por expresiones y rangos. | Puede modificar archivos; revisa siempre la variante y flags. |
| `awk` | Lenguaje de procesamiento de registros y campos de texto. | Útil para columnas de salida de terminal, no imprescindible para MCP. |
| Tubería (`\|`) | Conecta salida estándar de un comando con entrada de otro en la shell. | `rg 'error' logs/ \| head` limita lo que se muestra. |
| Redirección (`>` / `>>`) | Envía stdout a un archivo, sobrescribiendo o añadiendo según el operador. | Puede crear o modificar archivos, así que requiere permisos de escritura. |
| Código de salida de proceso | Entero que resume éxito o fallo de un proceso (`0` suele indicar éxito). | Fundamental para hooks, CI y scripts. |
| `stderr` | Canal estándar para diagnósticos y errores. | En servidores MCP por `stdio`, evita escribir logs en `stdout`. |
| `stdout` | Canal estándar de salida del proceso. | En un MCP `stdio` se reserva para mensajes del protocolo. |
| `which` / `command -v` | Localizan el ejecutable que resolverá la shell para un nombre. | Verifica el Python del `.venv` antes de ejecutar. |
| `env` (comando) | Muestra o manipula el entorno del proceso en la terminal. | No publiques su salida: puede revelar credenciales. |

### Claude Code: comandos, permisos y sesiones

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| `/init` | Comando disponible para iniciar instrucciones de proyecto y orientación de Claude Code. | Revisa el contenido generado antes de versionar `CLAUDE.md`. |
| `/compact` | Comando para resumir el contexto de una conversación extensa. | Puede perder detalles no incluidos en el resumen. |
| `/clear` | Comando para limpiar el contexto conversacional de la sesión según el modo. | No borra archivos del repositorio. |
| `/context` | Vista para diagnosticar el uso del contexto en versiones compatibles. | No es una herramienta para buscar archivos. |
| `/mcp` | Comando para inspeccionar servidores o conexiones MCP desde Claude Code. | Útil cuando `tools/list` o una conexión falla. |
| `/agents` | Interfaz para gestionar o inspeccionar subagentes personalizados. | Los agentes no se crean simplemente por escribirles un nombre en el prompt. |
| `/permissions` | Interfaz para inspeccionar o cambiar reglas de permiso del entorno. | Comprueba precedencias y restricciones gestionadas. |
| `/config` | Interfaz de configuración de Claude Code. | Separa ajustes de usuario, proyecto y organización. |
| `/model` | Selector de modelo disponible para una sesión. | El alias y disponibilidad dependen de la versión y la cuenta. |
| `claude --model` | Selecciona el modelo para una invocación desde la CLI. | No cambia el modelo indicado por llamadas Python independientes a Messages API. |
| `claude --max-turns` | Limita turnos agénticos en modo de impresión sin interacción. | No equivale a `max_tokens` del modelo. |
| `claude --output-format json` | Produce formato de resultado procesable por aplicaciones compatibles en modo no interactivo. | No implica que la respuesta de negocio siga un JSON Schema propio. |
| `claude --output-format stream-json` | Emite eventos del proceso en formato JSON por líneas cuando está admitido. | Necesita un consumidor que procese eventos, no un simple `json.loads` de todo el stream. |
| `claude --allowedTools` | Define herramientas preautorizadas para una ejecución de CLI, según los permisos vigentes. | No desactiva por sí solo las herramientas no incluidas. |
| `claude --disallowedTools` | Declara herramientas que deben rechazarse en una ejecución. | Se diferencia de una lista de preaprobación. |
| `claude --permission-mode` | Selecciona modo de autorización para una sesión. | No utilices bypass sin aislamiento y revisión de riesgo. |
| `claude --add-dir` | Añade directorios de trabajo accesibles cuando está permitido. | Ampliar rutas también amplía la superficie de datos. |
| `claude --continue` | Retoma la conversación más reciente del contexto correspondiente. | No reconstruye acciones externas perdidas. |
| `claude --resume` | Reanuda una sesión identificable mediante opciones del CLI. | Contrasta el identificador y estado de la sesión. |
| `PermissionRequest` | Hook que interviene cuando se solicita autorización de uso de una herramienta. | Distinto de `PreToolUse`, que se activa antes del uso según el ciclo del sistema. |
| `PostToolUseFailure` | Hook que reacciona cuando falla una operación de herramienta. | Útil para registros y recuperación, no para repetir ciegamente operaciones de escritura. |
| `UserPromptSubmit` | Hook invocado al enviar un prompt del usuario. | No transformes datos no confiables en permisos. |
| `SubagentStart` | Hook asociado al inicio de un subagente. | Permite instrumentar delegaciones. |
| `SubagentStop` | Hook asociado a la finalización de un subagente. | Sirve para trazar resultados y limpiar recursos. |
| `PreCompact` | Hook asociado al momento previo a compactar contexto. | Útil para preservar estado relevante. |
| `SessionEnd` | Hook del fin de sesión cuando se produce el evento compatible. | No sustituye el cierre transaccional de servicios externos. |
| `Notification` | Hook que recibe notificaciones de Claude Code de tipos admitidos. | Es un evento, no necesariamente una petición de permiso. |
| `WorktreeCreate` | Hook para personalizar la creación de entornos de trabajo aislados en versiones compatibles. | No es equivalente a `git branch`. |
| `WorktreeRemove` | Hook asociado a retirada de un worktree controlado por Claude Code. | Verifica cambios pendientes antes de borrar el entorno. |
| `Git worktree` | Copia de trabajo adicional vinculada a un mismo repositorio Git. | Permite a agentes trabajar en paralelo sin pisar el mismo árbol de archivos. |
| `Git diff` | Diferencia textual de cambios entre versiones o estados. | Inspección imprescindible antes de un commit generado por agente. |
| `Git status` | Resumen de cambios preparados, no preparados y archivos sin seguimiento. | Revisa que `.env` no vaya a subirse. |
| `Git restore` | Restaura archivos o contenido según el estado de Git. | Puede descartar modificaciones: comprueba el alcance. |
| `Git switch` | Cambia de rama o crea una rama con opciones adecuadas. | Prefiere ramas aisladas para experimentos. |
| `Git merge` | Integra historias de dos ramas. | Puede producir conflictos y exige validación de tests. |
| `Git rebase` | Reaplica commits sobre otra base histórica. | Cuidado con reescribir ramas compartidas. |
| `Git stash` | Guarda temporalmente cambios locales para despejar la carpeta de trabajo. | No es una copia de seguridad definitiva. |
| `Git worktree add` | Crea una carpeta de trabajo adicional asociada al mismo repositorio. | Útil para pruebas paralelas de agentes. |
| `uv` | Gestor de entornos, proyectos y dependencias Python. | Puedes usarlo para entornos reproducibles; no es una herramienta Claude Code. |
| `uv sync` | Sincroniza el entorno con las dependencias del proyecto según su configuración y lockfile. | Debe ejecutarse en el proyecto correcto. |
| `uv run` | Ejecuta un comando en el entorno administrado por uv. | Útil para lanzar tests sin activar manualmente la venv. |
| `pip` | Gestor de paquetes de Python instalado en un entorno. | `python -m pip` evita confundir intérpretes. |
| `pip freeze` | Lista paquetes instalados con versiones de un entorno. | No reemplaza una definición deliberada de dependencias directas. |
| `pytest` | Framework Python para declarar y ejecutar pruebas automáticas. | Prueba herramientas mock antes de gastar tokens de API. |
| `ruff` | Herramienta de lint y formato de código Python. | Su aprobación no demuestra la corrección funcional del agente. |
| `pre-commit` | Sistema de hooks Git para ejecutar comprobaciones locales al hacer commit. | Distinto de los hooks de Claude Code. |

## D4 — Prompt Engineering & Structured Output

### Diseño de instrucciones

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Prompt | Conjunto de instrucciones, datos y contexto enviados al modelo para orientar una respuesta. | Un prompt útil tiene objetivo, entrada, restricciones y salida esperada. |
| Prompt engineering | Diseño iterativo de prompts y pruebas para mejorar la estabilidad de un comportamiento. | No reemplaza validación de backend ni evaluaciones reales. |
| Zero-shot | Enfoque que pide resolver una tarea sin ejemplos de referencia dentro del prompt. | Suele bastar para tareas simples y definidas. |
| One-shot | Enfoque que incluye un ejemplo de entrada/salida. | Puede fijar un formato cuando una instrucción sola resulta ambigua. |
| Few-shot | Enfoque que incorpora varios ejemplos representativos. | Incluye ejemplos normales, negativos y de frontera para reducir ambigüedad. |
| Ejemplo negativo | Caso que muestra lo que no debe clasificarse como coincidencia o error. | Reduce falsos positivos en auditorías. |
| Contraejemplo | Caso cuidadosamente elegido para desmontar una regla intuitiva pero incorrecta. | Ejemplo: «total» no siempre es «subtotal + impuestos» si hay descuentos. |
| Instrucción explícita | Regla que define una acción o condición de forma verificable. | «Marca solo errores con evidencia de línea» es mejor que «sé riguroso». |
| Contexto delimitado | Datos de entrada encerrados mediante etiquetas, separadores o bloques claramente identificados. | Evita confundir datos externos con instrucciones de usuario. |
| Etiquetas XML | Marcadores como `<documento>` y `<criterios>` para segmentar material textual. | Son delimitadores útiles, no un mecanismo de seguridad por sí solos. |
| Rol / persona | Descripción de la perspectiva o función que debe adoptar el modelo. | «Actúa como auditor» no concede acceso a sistemas ni mejora resultados automáticamente. |
| Objetivo y criterio de éxito | Resultado específico y comprobable que orienta una tarea. | Ejemplo: «extrae total y moneda citando la línea fuente». |
| Restricción de salida | Condición sobre longitud, tono, estructura o contenido de la respuesta. | Mejor si puede verificarse automáticamente. |
| Criterios de exclusión | Reglas explícitas que definen qué casos no deben considerarse hallazgos. | Evitan auditorías excesivamente sensibles. |
| Casos límite (edge cases) | Entradas que aparecen en límites o excepciones del problema. | Ejemplo: factura sin NIF, fecha ilegible o importe negativo. |
| Descomposición de tareas | Separar una solicitud amplia en subtareas con contratos claros. | Puede reducir errores frente a un prompt único excesivamente cargado. |
| Prompt template | Plantilla con instrucciones estables y variables de entrada definidas. | La interpolación debe proteger delimitadores y contenido no confiable. |
| Variables de prompt | Marcadores que se sustituyen por información concreta durante la ejecución. | Valida tipos y longitud antes de interpolar. |
| Prompt versioning | Registro de versiones de instrucciones para poder comparar cambios. | Guarda la versión del prompt junto al resultado de evaluación. |
| Separación datos/instrucciones | Principio de mantener documentos externos como material a analizar, sin permitir que redefinan normas. | Una página web no puede convertirse en `system`. |

### Calidad, evidencia y clasificación

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Clasificación | Asignación de una categoría a una entrada según reglas. | La categoría «desconocido» suele ser necesaria en casos ambiguos. |
| Extracción | Identificación de campos o hechos contenidos en una fuente. | No inventes un número de factura ausente. |
| Resumen | Reducción de un documento preservando los hechos relevantes. | Resumir no autoriza completar lagunas con suposiciones. |
| Evidencia | Texto, dato o resultado trazable que respalda una afirmación. | Un hallazgo sin fuente merece revisión o rechazo. |
| Provenance (procedencia) | Registro de la fuente y transformación de cada dato o afirmación. | Ayuda a detectar mezclas entre documentos. |
| Cita (citation) | Referencia a fuente, fragmento o posición que permite comprobar un hallazgo. | Debe respaldar la afirmación exacta, no un tema general. |
| Grounding | Restricción de una respuesta a información recuperada o suministrada con evidencia. | Es distinto de citar material irrelevante. |
| Alucinación | Salida plausible pero no respaldada por las fuentes o hechos disponibles. | Un JSON correcto puede contener alucinaciones. |
| Falso positivo | Caso que el sistema marca como hallazgo sin cumplir la regla definida. | Perjudica precisión y credibilidad. |
| Falso negativo | Caso que cumple una regla y el sistema no detecta. | Perjudica cobertura y sensibilidad. |
| Precisión (precision) | Proporción de positivos predichos que realmente lo son: `TP/(TP+FP)`. | Importa cuando revisar alertas falsas es caro. |
| Exhaustividad (recall) | Proporción de positivos reales detectados: `TP/(TP+FN)`. | Importa cuando omitir casos relevantes es costoso. |
| F1-score | Media armónica de precisión y recall, útil para equilibrar ambas. | Puede ocultar diferencias entre clases. |
| Rúbrica | Conjunto explícito de criterios con los que se evalúa una salida. | Reduce discrepancias entre revisores. |
| Evaluación humana | Inspección de resultados por personas con criterios compartidos. | Es esencial para tareas subjetivas o de alto riesgo. |
| Evaluador LLM | Modelo que puntúa o clasifica resultados de otro modelo. | Debe calibrarse frente a ejemplos revisados por humanos. |
| Sesgo del evaluador | Preferencia sistemática por cierto estilo, orden o longitud de respuestas. | Aleatoriza el orden y usa criterios verificables. |
| Confidence score | Estimación de confianza declarada por un sistema o modelo. | La confianza autorreportada no demuestra exactitud ni sustituye validación. |

### JSON, esquema y garantías

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| JSON | Formato textual de datos con objetos, arrays y tipos simples. | Exige comillas dobles en claves y cadenas. |
| JSON Schema | Lenguaje que especifica forma y restricciones de documentos JSON. | «Responde en JSON» no equivale a imponer un esquema. |
| Structured outputs | Función que restringe una salida de Claude a una estructura admitida por la API, habitualmente basada en JSON Schema. | Verifica el soporte y las limitaciones del modelo elegido. |
| `output_config.format` | Campo documentado para solicitar determinados formatos de salida estructurada en la API actual. | La sintaxis puede evolucionar; no reutilices ejemplos sin comprobar su versión. |
| `strict: true` | Opción documentada en herramientas compatibles para imponer conformidad de argumentos al esquema admitido. | No evita datos inventados ni concede permisos. |
| `type: object` | Declaración de que la estructura JSON esperada es un objeto. | Suele usarse en esquemas de extracción con campos nombrados. |
| `type: array` | Declaración de una lista JSON cuyos elementos pueden tener restricciones. | El orden de los elementos puede tener significado en el dominio. |
| `type: string` | Declaración de un valor de texto. | Un importe como cadena puede necesitar conversión y validación posterior. |
| `type: number` | Declaración de valor numérico JSON general. | Evita floats binarios para dinero si necesitas exactitud contable. |
| `type: integer` | Declaración de número entero JSON. | Una edad puede ser entera, pero sigue requiriendo validar un rango válido. |
| `type: boolean` | Declaración de los valores literales JSON `true` y `false`. | No los confundas con cadenas `"true"` y `"false"`. |
| `null` | Valor JSON que representa ausencia o desconocimiento de un dato. | Úsalo con reglas claras; no inventes una cadena vacía con significado ambiguo. |
| Nullable | Propiedad que permite a un campo admitir `null` además de otro tipo. | Útil para información que quizá no aparezca en la fuente. |
| `required` | Lista de campos cuya presencia es obligatoria en un objeto JSON. | El campo puede requerirse y admitir `null` si el esquema lo permite. |
| `additionalProperties: false` | Restricción que prohíbe claves inesperadas cuando el soporte del esquema la admite. | Reduce salidas con campos no pactados. |
| `enum` | Restricción a una lista finita de valores posibles. | Ejemplo: `estado` como `aprobado`, `pendiente` o `rechazado`. |
| `oneOf` / `anyOf` | Construcciones para expresar alternativas de esquema con semánticas distintas. | Comprueba si el modo de salida estructurada concreto soporta esas construcciones. |
| Parseo | Transformación de texto JSON en estructuras de un lenguaje, como `dict` de Python. | Un parseo exitoso no prueba exactitud. |
| Esquema inválido | Definición de estructura no admitida o contradictoria para el validador o modo API utilizado. | Debe corregirse antes de pedir reintentos al modelo. |
| Validación de negocio | Evaluación de reglas del dominio después de parsear y validar la forma. | `total` debe corresponder a los importes y condiciones de factura reales. |
| Error de truncamiento | Respuesta incompleta porque se alcanzó un límite de generación o transferencia. | No intentes completar campos ausentes con valores inventados. |
| Repair / re-prompt | Reintento controlado en el que se explica una violación concreta para solicitar una corrección. | Limita intentos y no pidas al modelo «validarse a sí mismo» sin una prueba externa. |
| Salida parcial | Resultado que contiene solo parte de los campos esperados o datos verificables. | Debe declararse explícitamente para no parecer un éxito completo. |

### Procesamiento y optimización

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Message Batches API | Servicio que procesa múltiples solicitudes independientes de manera asíncrona y permite recuperar resultados posteriormente. | Conviene cuando no necesitas respuesta inmediata. |
| Batch | Conjunto de solicitudes independientes enviadas a un procesador por lotes. | No es un historial conversacional compartido. |
| `custom_id` | Identificador propio de cada solicitud de un batch, usado para asociar su resultado. | El orden de retorno no está garantizado. |
| Batch polling | Consulta periódica del estado de un procesamiento por lotes. | Añade backoff y límite de frecuencia. |
| Batch result | Registro individual de un batch que puede ser satisfactorio o contener error. | El éxito general del lote no implica éxito de cada solicitud. |
| Trade-off coste-latencia | Decisión entre ahorrar coste y obtener una respuesta antes. | El batch suele priorizar eficiencia sobre inmediatez. |
| Revisión multipasada | Proceso que realiza extracción, comprobación y síntesis en etapas separadas. | Evita que un mismo razonamiento circular se convierta en evidencia. |

### Diseño de prompts y técnicas avanzadas

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Instruction hierarchy | Prioridad de instrucciones entre reglas del sistema, aplicaciones, usuarios y datos no confiables. | Un texto recuperado no puede convertirse en instrucción superior. |
| Separadores de contenido | Delimitadores que separan instrucciones, ejemplos, datos y documentos. | Reducen confusiones de origen del texto. |
| Prefill (prefijado de respuesta) | Técnica de proporcionar comienzo de respuesta del asistente cuando la API/modelo lo admite. | La compatibilidad varía; no sustituye Structured Outputs. |
| Prompt injection indirecta | Instrucción maliciosa oculta en recursos, webs o resultados externos incluidos en el contexto. | La respuesta correcta es aislarla como datos. |
| Chain-of-thought prompting | Petición de razonamiento paso a paso como técnica histórica de prompting. | En producción evalúa resultados observables; no dependas de revelar razonamiento privado. |
| Stepwise decomposition | Organización de una tarea compleja en etapas con criterios verificables. | Usa checkpoints entre extracción y decisiones finales. |
| Plan-and-solve | Prompt que pide un plan y una resolución según ese plan. | Necesita verificación independiente para evitar errores encadenados. |
| Self-consistency | Comparación de varias soluciones candidatas para seleccionar una respuesta robusta. | Añade coste y las coincidencias pueden compartir el mismo error. |
| Temperature | Parámetro de muestreo que afecta variación de salidas en modelos y modos donde está disponible. | Menor aleatoriedad no garantiza verdad. |
| Top-p | Parámetro de muestreo que limita un conjunto probabilístico de tokens en modelos compatibles. | No asumas que combina libremente con todos los modos. |
| Stop sequences | Secuencias definidas para detener una generación cuando se admiten. | Diferentes de `stop_reason` y del límite de tokens. |
| `stop_sequence` | Razón de parada cuando se alcanza una secuencia de detención configurada. | No confundir con `end_turn`. |
| Output contract | Descripción formal de la forma, campos, restricciones y semántica de la salida. | Más útil que pedir «devuélveme algo estructurado». |
| Esquema canónico | Contrato estable acordado entre productor y consumidor de datos. | Evita que cada agente invente nombres de campos. |
| Separación de extracción e inferencia | Distinción entre extraer datos expresos y deducir información no declarada. | Marca lo inferido y su evidencia. |
| Respuesta abstentiva | Salida explícita de insuficiencia de evidencia en lugar de inventar datos. | Incluye una razón operativa o un campo nulo cuando el esquema lo permita. |
| Calibración | Ajuste de la interpretación de confianza declarada frente a aciertos observados. | El confidence score de un LLM no está automáticamente calibrado. |
| Contradicción de fuentes | Situación en que dos textos recuperados afirman hechos incompatibles. | Prioriza autoridad y actualidad; señala incertidumbre. |
| Métricas por campo | Evaluación individual de la calidad de campos de una extracción estructurada. | Un documento correcto globalmente puede ocultar errores en fechas o importes. |
| Exact match | Métrica de coincidencia exacta de texto o estructura frente a una respuesta esperada. | Penaliza reformulaciones equivalentes si no normalizas. |
| Semantic similarity | Comparación de equivalencia aproximada de significado entre textos. | No es adecuada para validar importes, claves o fechas. |
| Test adversarial | Prueba diseñada para forzar comportamientos incorrectos o límites del sistema. | Incluye instrucciones maliciosas en documentos recuperados. |
| Matriz de confusión | Tabla de verdaderos/falsos positivos y negativos para clasificadores. | Permite calcular precisión y recall. |
| Macro-F1 | Promedio de F1 entre clases sin ponderar por frecuencia. | Resalta clases poco frecuentes. |
| Micro-F1 | Métrica calculada agregando los conteos de todas las clases. | En clasificación multiclase de etiqueta única coincide con accuracy. |
| Parser tolerante | Analizador que intenta recuperar datos de salidas imperfectas. | Nunca debe ocultar silenciosamente que la respuesta violó el contrato. |
| Validación con Pydantic | Verificación Python de objetos mediante esquemas y tipos definidos. | Valida estructura y reglas especificadas, no datos externos inexistentes. |
| Validador de negocio | Código que comprueba restricciones del dominio, como límites de importe o relación entre fechas. | Complemento obligatorio del JSON Schema. |
| Esquema versionado | Contrato de salida con versión identificable para permitir migraciones. | Cambiar un campo sin versionar puede romper consumidores. |
| Compatibilidad hacia atrás | Capacidad de mantener funcionando clientes antiguos al evolucionar un contrato. | Prefiere cambios aditivos o versionado explícito. |
| Distinción `null` / omitido | `null` declara ausencia de valor; un campo omitido no fue suministrado. | `required` exige presencia, no necesariamente un valor no nulo. |
| False refusal | Rechazo de una solicitud que sí debería haberse respondido según el ámbito y las políticas. | Evalúalo junto con respuestas inseguras o incorrectas. |
| Prompt optimizer | Proceso que revisa sistemáticamente instrucciones y ejemplos a partir de evaluaciones. | Evita optimizar solo por una muestra de tests. |
| Prompt test suite | Conjunto versionado de entradas, salidas esperadas y criterios. | Ejecutar al cambiar prompts o modelos. |

## D5 — Context Management & Reliability

### Tokens, contexto y memoria

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Token | Unidad de texto utilizada para medir entrada, salida y consumo del modelo. | No coincide siempre con una palabra o carácter. |
| Ventana de contexto | Capacidad máxima de información procesable por el modelo en una solicitud, sujeta a restricciones del modelo y API. | Suma instrucciones, historial, herramientas y datos relevantes. |
| Context budget | Asignación de tokens disponible para cada tipo de contenido dentro del contexto. | Reserva margen para resultados de herramientas y respuesta final. |
| Input tokens | Tokens procesados como entrada de una petición. | Incluyen mensajes previos y datos que el modelo vuelve a recibir. |
| Output tokens | Tokens generados como resultado de una petición. | El límite por llamada debe contemplar la estructura que esperas. |
| Token counting | Estimación o cálculo previo de tokens de una solicitud mediante herramientas de la plataforma. | Útil para controlar costes y evitar desbordamientos. |
| Truncamiento | Recorte de contenido por límites de longitud, tokens o transmisión. | Puede perder justamente la condición de negocio más importante. |
| Context overflow | Situación en la que el material enviado supera el contexto admitido o un límite operativo. | Requiere recorte o compactación consciente, no reintentos idénticos. |
| Context rot | Deterioro de la utilidad del contexto cuando crece el volumen de información irrelevante, obsoleta o redundante. | Más tokens no siempre producen mejores respuestas. |
| Compactación | Sustitución de parte del historial por una representación más breve que conserve lo esencial. | Preserva decisiones, datos pendientes, permisos y errores relevantes. |
| Resumen de estado | Síntesis estructurada de decisiones, resultados, restricciones y próximos pasos de una tarea. | No basta con un resumen narrativo sin identificadores ni fuentes. |
| Context editing | Función o estrategia de limpieza selectiva del contexto, por ejemplo retirando resultados de herramientas que ya no son necesarios. | Debe evitar borrar la única evidencia de una conclusión. |
| Pruning | Eliminación dirigida de contenido que aporta poco valor al siguiente paso. | Retira ruido antes que hechos críticos. |
| Compaction trigger | Condición que activa una reducción del contexto, por ejemplo un umbral de tokens. | Un disparador anticipado permite reservar espacio para la respuesta. |
| Estado persistente | Información almacenada fuera del contexto del modelo para recuperarla entre solicitudes o sesiones. | Una sesión de chat no debe ser la única fuente de verdad de pedidos. |
| Memoria episódica | Registro de experiencias o eventos previos recuperables para dar continuidad. | Necesita fecha, alcance y políticas de retención. |
| Memoria semántica | Conjunto de hechos, reglas o conocimientos recuperables en lugar de episodios completos. | Debe indicar procedencia y posibilidad de actualización. |
| Memoria de trabajo | Información transitoria necesaria para resolver la tarea actual. | Se descarta cuando deja de ser pertinente. |
| Estado autoritativo | Registro que una aplicación considera fuente oficial del estado del negocio. | El modelo puede consultarlo, pero no inventarlo. |
| Prompt caching | Reutilización del procesamiento de prefijos de prompt compatibles para reducir costes o latencia según la API. | No es persistencia de memoria entre sesiones. |
| Cache hit | Reutilización exitosa de un prefijo o bloque previamente cacheado. | Requiere cumplir reglas de coincidencia, modelo y vigencia del caché. |
| Cache miss | Imposibilidad de reutilizar un bloque de caché previo. | Cambiar instrucciones del principio puede invalidar gran parte del prefijo. |
| `cache_control` | Configuración explícita de un punto o política de caché en interfaces compatibles. | Su forma exacta depende de la API y modelo vigentes. |
| `cache_creation_input_tokens` | Métrica de tokens de entrada dedicados a crear contenido cacheado según el registro de uso. | No equivale a tokens de salida. |
| `cache_read_input_tokens` | Métrica de tokens recuperados del caché de prompt. | Sirve para estimar el beneficio real del caché. |
| TTL (time to live) | Tiempo de vigencia de un dato o entrada de caché. | No confundas vigencia técnica con frescura factual. |

### Recuperación y procedencia

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Retrieval | Recuperación selectiva de información desde una fuente externa al contexto inicial. | Debe aplicar filtros de acceso antes de entregar datos. |
| RAG (retrieval-augmented generation) | Arquitectura que incorpora información recuperada para fundamentar respuestas del modelo. | No garantiza por sí sola ausencia de alucinaciones. |
| Embeddings | Representaciones numéricas de contenido usadas para medir similitud semántica. | Similitud semántica no implica autorización o veracidad. |
| Vector store | Sistema de almacenamiento y consulta de vectores, habitual para recuperar fragmentos relacionados con una pregunta. | Puede combinarse con filtros tradicionales. |
| Búsqueda léxica | Recuperación por coincidencias de términos, como BM25 o búsqueda textual. | Es útil para identificadores y términos exactos. |
| Búsqueda híbrida | Combinación de métodos semánticos y léxicos para mejorar cobertura de recuperación. | Los identificadores pueden necesitar coincidencia exacta prioritaria. |
| Chunk | Fragmento de un documento utilizado como unidad de indexación o recuperación. | Un corte incorrecto puede separar una condición de su excepción. |
| Chunking | Estrategia de segmentación de documentos para indexación y recuperación. | Debe respetar límites lógicos como títulos, tablas y artículos. |
| Reranking | Reordenación de resultados recuperados según relevancia respecto a la consulta. | Aplica filtros de autorización antes de exponer contenido al modelo. |
| Metadata filtering | Restricción de búsqueda mediante atributos como usuario, organización, fecha o tipo. | Es esencial para aislamiento entre clientes. |
| Top-k retrieval | Selección de los `k` resultados mejor posicionados por un algoritmo. | `k` grande puede elevar ruido y coste de contexto. |
| Source of truth | Sistema o documento cuyo estado se usa como referencia oficial para un hecho concreto. | Para saldos, consulta la base de datos, no un resumen antiguo. |
| Provenance | Registro de origen, versión, fecha y transformación de un dato. | Facilita auditorías y corrección de respuestas. |
| Citas trazables | Referencias específicas a pasajes o registros que justifican una respuesta. | Un enlace genérico no prueba el valor exacto de una factura. |
| Conflicto de fuentes | Situación en la que documentos recuperados sostienen afirmaciones incompatibles. | Deben compararse fecha, autoridad y alcance antes de elegir. |
| Frescura de datos | Cercanía temporal de la información respecto al instante en que se usa. | Un precio histórico no es automáticamente el actual. |

### Seguridad, privacidad y acceso

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Autenticación | Comprobación de identidad de quien realiza una petición. | Responde a «¿quién eres?». |
| Autorización | Comprobación de los permisos de una identidad para una acción sobre un recurso específico. | Responde a «¿puedes hacer esto?». |
| Aislamiento multiusuario | Separación de información y estado entre usuarios o inquilinos de una aplicación. | Nunca se delega únicamente al prompt. |
| Tenant | Organización, cliente o espacio lógico cuyos datos deben quedar aislados en un sistema compartido. | Filtra por tenant en consultas y almacenamiento. |
| RBAC | Modelo de permisos basado en roles, como lector o administrador. | El rol debe validarse en el servidor. |
| ABAC | Modelo que autoriza según atributos del actor, recurso, acción y contexto. | Ejemplo: un asesor solo ve casos de su cartera. |
| Least privilege | Estrategia de conceder la mínima capacidad necesaria para realizar una función. | Limita el impacto de errores y abuso. |
| Defense in depth | Aplicación de varias barreras independientes, como autenticación, filtros de datos, validación y auditoría. | Una sola instrucción de sistema no basta. |
| Prompt injection | Intento de introducir instrucciones no autorizadas mediante contenido que el modelo debe analizar. | Puede aparecer en documentos, web, repositorios o resultados de herramientas. |
| Indirect prompt injection | Inyección que llega a través de una fuente secundaria, no del usuario que formula la solicitud. | Ejemplo: un PDF que pide exfiltrar claves. |
| Frontera de confianza (trust boundary) | Límite entre información o componentes con distintos niveles de autoridad. | Un resultado MCP es dato, no política. |
| Exfiltración | Extracción no autorizada de datos hacia un destino externo. | Bloquea destinos y datos sensibles desde la capa de ejecución. |
| PII (información personal identificable) | Datos capaces de identificar a una persona directa o indirectamente. | Aplica minimización, redacción y controles de acceso. |
| Redacción de datos | Supresión u ocultación de campos sensibles antes de enviarlos a registros o modelos. | No registres tokens de acceso ni secretos de entorno. |
| Secreto | Credencial, token, clave o dato reservado que permite acceder a servicios. | Guárdalo en entorno o gestor de secretos, nunca en un repo público. |
| Auditoría | Registro revisable de accesos, decisiones y acciones relevantes. | Incluye motivo y resultado sin difundir datos privados innecesarios. |

### Fiabilidad y operación

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Fiabilidad (reliability) | Capacidad de un sistema para cumplir su función esperada bajo condiciones definidas de carga y fallo. | Se mide con métricas, no con la seguridad verbal del modelo. |
| Robustez | Capacidad de mantener un comportamiento útil ante entradas extrañas, errores y variaciones razonables. | Prueba casos límite y errores deliberados. |
| Resiliencia | Capacidad de recuperarse de fallos y mantener un nivel aceptable de servicio. | Combina reintentos, fallback, límites y observabilidad. |
| Retry | Repetición controlada de una operación después de un fallo. | Solo es segura si conoces efectos secundarios e idempotencia. |
| Backoff exponencial | Aumento progresivo de la espera entre reintentos, típicamente multiplicando el intervalo. | Reduce presión sobre servicios inestables. |
| Jitter | Aleatorización del tiempo de espera para evitar que muchos clientes reintenten al mismo tiempo. | Complementa backoff exponencial. |
| Circuit breaker | Mecanismo que deja temporalmente de llamar a una dependencia cuando acumula fallos. | Evita cascadas de saturación. |
| Dead-letter queue (DLQ) | Cola de trabajos que no pudieron procesarse tras la política de reintentos. | Permite inspección sin bloquear el flujo principal. |
| Deduplicación | Detección y eliminación de operaciones o eventos repetidos. | Necesaria cuando una cola entrega mensajes más de una vez. |
| At-least-once delivery | Garantía de entregar un mensaje una o más veces, aceptando duplicados. | Diseña consumidores idempotentes. |
| At-most-once delivery | Garantía de no repetir una entrega, aceptando que alguna pueda perderse. | Puede ser inapropiada para pagos o eventos críticos. |
| Exactly-once effect | Objetivo de aplicar un efecto una sola vez pese a reenvíos; suele requerir idempotencia y transacciones. | No lo confundas con una entrega de red literalmente única. |
| Timeout de herramienta | Tiempo máximo permitido para esperar un resultado de una dependencia. | Puede haber ejecución remota después del timeout local. |
| Rate limit | Restricción de número de peticiones o tokens permitidos en un intervalo. | Aplica gestión de colas y reintentos con límites. |
| Observabilidad | Capacidad de entender el estado de un sistema mediante logs, métricas y trazas. | Sin correlación entre pasos es difícil diagnosticar agentes. |
| Logs | Registros de eventos relevantes en una ejecución. | Evita registrar prompts completos con información sensible sin justificación. |
| Métricas | Medidas agregadas como tasa de éxito, latencia, coste y errores. | Deben distinguir fallo de herramienta y fallo de validación. |
| Traza distribuida | Secuencia correlacionada de operaciones entre servicios o agentes. | Incluye IDs de correlación para reconstruir un caso. |
| Correlation ID | Identificador que enlaza solicitudes, herramientas y registros del mismo flujo. | No sustituyas el ID por información personal del usuario. |
| SLA | Compromiso de nivel de servicio acordado con usuarios o clientes. | Es un objetivo contractual, no necesariamente una métrica técnica. |
| SLO | Objetivo cuantitativo interno de fiabilidad o rendimiento. | Ejemplo: 99,9 % de solicitudes correctas en un periodo. |
| SLI | Indicador medible del comportamiento de un servicio. | Ejemplo: porcentaje de respuestas correctas y a tiempo. |
| Runbook | Procedimiento operativo documentado para investigar y responder a incidentes. | Debe incluir diagnóstico, mitigación y escalamiento. |
| Fallback seguro | Ruta alternativa que conserva restricciones de privacidad y autorización. | Una respuesta más simple es mejor que revelar datos de otro usuario. |
| Fail-safe | Política que adopta un estado conservador si una comprobación esencial no puede completarse. | Si falla la comprobación de permisos, no se ejecuta el reembolso. |
| Human escalation | Transferencia a una persona cuando los criterios de riesgo o incertidumbre lo requieren. | No depende de una autoconfianza elevada del LLM. |

### Evaluación de sistemas completos

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Test de regresión | Prueba que verifica que cambios recientes no reintroducen fallos ya resueltos. | Conserva casos reales y pruebas de seguridad. |
| Evaluación offline | Comparación de resultados con conjuntos de prueba sin tráfico de producción. | Ideal para revisar prompts antes del despliegue. |
| Evaluación online | Medición con tráfico o interacciones reales bajo controles apropiados. | Requiere gestión de riesgos y privacidad. |
| Golden dataset | Conjunto de entradas y resultados de referencia cuidadosamente revisados. | Documenta criterios de anotación y errores esperados. |
| Success rate | Proporción de ejecuciones que cumplen criterios de éxito definidos. | No cuentes como éxito un JSON válido con contenido incorrecto. |
| Error budget | Margen tolerado de fallos respecto a un objetivo de fiabilidad. | Puede orientar el ritmo de cambios en producción. |
| Coste por tarea | Gastos de modelo, herramientas e infraestructura asociados a una unidad de trabajo completada. | Compara coste por éxito, no solo tokens por llamada. |
| Tasa de escalamiento | Fracción de casos derivados a revisión humana. | Una tasa baja puede reflejar omisiones de riesgo, no solo eficiencia. |

### Gestión avanzada del contexto y recuperación

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Needle-in-a-haystack test | Prueba que mide si el modelo recupera un detalle insertado en un contexto muy largo. | No sustituye evaluar tareas reales. |
| Lost-in-the-middle | Fenómeno por el cual algunos modelos aprovechan peor información situada en posiciones intermedias del contexto. | Selecciona y jerarquiza contexto relevante. |
| Selección de contexto | Elección de datos necesarios para una inferencia en vez de incluir todos los documentos disponibles. | Reduce ruido y riesgo de inyección. |
| Compresión con pérdida | Resumen que descarta detalles para reducir tokens. | Conserva estado autoritativo fuera del resumen. |
| Compresión sin pérdida | Transformación que permite recuperar exactamente el contenido original. | No toda compactación de conversación cumple esto. |
| Resumen jerárquico | Síntesis por niveles de documentos o subprocesos. | Útil en repositorios extensos con fases de análisis. |
| Contexto por agente | Conjunto de mensajes, recursos y herramientas visibles para un subagente. | Aislamiento de contexto no implica aislamiento de permisos. |
| Inyección de herramientas | Inclusión de definiciones de herramientas en el contexto del modelo. | Catálogos excesivos aumentan coste y confusión. |
| Prompt cache prefix | Porción inicial reutilizable de la petición que un mecanismo de caching compatible puede reconocer. | Cambios al prefijo pueden invalidar el hit. |
| Invalidación de caché | Pérdida de reutilización al modificar contenido o condiciones que formaban la entrada cacheada. | No confundas caché de prompts con persistencia de memoria. |
| Warm cache / cold cache | Estado con prefijo reutilizable disponible o sin él. | Las pruebas de coste/latencia deben comparar condiciones equivalentes. |
| Cache poisoning | Alteración o incorporación de material no confiable a una caché de resultados. | La frontera de confianza se conserva aunque el dato esté cacheado. |
| Índice invertido | Estructura de búsqueda que mapea términos a documentos donde aparecen. | Base frecuente de la recuperación léxica. |
| BM25 | Función de ranking léxico que pondera presencia de términos y longitud de documentos. | Complementa embeddings en una búsqueda híbrida. |
| Recall@k | Proporción de elementos relevantes recuperados entre los primeros k resultados. | Si el documento correcto no se recupera, el LLM no puede citarlo. |
| Precision@k | Proporción de resultados relevantes entre los primeros k recuperados. | Indica cuánto ruido llega al modelo. |
| MRR | Métrica que valora qué tan pronto aparece el primer resultado relevante. | Útil para sistemas de pregunta-respuesta con una evidencia principal. |
| NDCG | Métrica de ranking que pondera relevancia y posición de múltiples resultados. | Mejor que exact match para listas graduadas. |
| Query rewriting | Reformulación de la consulta para recuperar documentos más relevantes. | Preserva restricciones del usuario y evita inventar entidades. |
| Query expansion | Añadir sinónimos y variantes para ampliar cobertura de búsqueda. | Puede empeorar precisión si amplía demasiado. |
| Multi-query retrieval | Ejecutar varias consultas sobre la misma necesidad y fusionar resultados. | Deduplica fuentes antes de enviarlas al LLM. |
| Document fingerprint | Huella de contenido usada para detectar duplicados o versiones. | Evita citar varias veces el mismo documento copiado. |
| Chunk overlap | Solapamiento deliberado entre fragmentos de documentos. | Puede preservar contexto, pero aumenta coste y duplicados. |
| Chunk de tamaño variable | Fragmentación según límites semánticos, no solo número fijo de caracteres. | Mejor para secciones, funciones y tablas. |
| Recuperación sensible a ACL | Filtrado de documentos de acuerdo con permisos del usuario antes de enviarlos al modelo. | RAG no evita filtraciones por sí solo. |
| Cross-tenant leakage | Exposición de datos de una organización a usuarios de otra. | Se previene con controles en consultas, índices y almacenamiento. |
| Freshness check | Verificación de fecha, versión o vigencia de información recuperada. | Un documento correcto hace un año puede estar obsoleto. |
| Retrieval poisoning | Introducción de documentos manipulados en un índice de búsqueda. | Exige procedencia, filtrado y controles de contenido. |
| Groundedness | Grado en que cada afirmación de una respuesta está respaldada por evidencia recuperada. | Diferente de que la respuesta sea fluida o razonable. |
| Faithfulness | Fidelidad de la respuesta respecto al contenido real de las fuentes. | Una cita inventada no es evidencia. |

### Seguridad y resiliencia de producción

| Concepto | Definición | Aplicación / para recordar |
|---|---|---|
| Secrets rotation | Sustitución periódica o reactiva de credenciales. | Claves expuestas deben revocarse, no solo borrarse del Git actual. |
| Secret scanning | Revisión automática del repositorio en busca de patrones de credenciales. | Añádela a CI sin mostrar secretos detectados. |
| Data minimization | Uso de la menor cantidad de datos personales necesaria para la tarea. | No envíes un expediente completo si bastan tres campos. |
| Retención de datos | Política sobre cuánto tiempo conservar historiales, logs y artefactos. | Debe definirse por tipo de dato y finalidad. |
| Cifrado en tránsito | Protección de datos durante conexiones de red, habitualmente mediante TLS. | No implica cifrado del almacenamiento. |
| Cifrado en reposo | Protección del contenido almacenado en discos, servicios o bases de datos. | No corrige una autorización incorrecta. |
| Política de egreso (egress policy) | Restricción de destinos de red que un servicio puede contactar. | Reduce exfiltración por herramientas de fetch. |
| Aprobación de acción sensible | Confirmación explícita antes de operaciones con impacto alto. | Debe incluir parámetros reales de ejecución. |
| Verificación de salida de herramienta | Comprobación de formato, autorización y plausibilidad de datos externos. | Tool success técnico no implica verdad del dato. |
| P95 latency | Latencia bajo la cual termina el 95 % de las operaciones medidas. | Expone colas lentas que la media oculta. |
| P99 latency | Latencia bajo la cual termina el 99 % de las operaciones medidas. | Importante en cadenas de herramientas con colas largas. |
| Cold start | Latencia adicional al arrancar un servicio o función no calentada. | Puede influir en servidores MCP bajo demanda. |
| Health check | Comprobación de que un servicio responde y dispone de dependencias esenciales. | Diferencia disponibilidad de capacidad funcional real. |
| Readiness probe | Señal de que un servicio está listo para recibir peticiones. | No basta con que el proceso exista. |
| Liveness probe | Señal de que un proceso sigue activo y puede requerir reinicio si falla. | No equivale a una prueba de negocio. |
| Bulkhead | Aislamiento de recursos para impedir que fallos de un componente saturen todo el sistema. | Limita concurrencia por herramienta o proveedor. |
| Load shedding | Rechazo controlado de nuevas solicitudes ante sobrecarga. | Protege peticiones en curso y servicios críticos. |
| Backpressure | Señal para ralentizar productores cuando consumidores están saturados. | Evita colas sin límite. |
| Queue depth | Número de trabajos pendientes en una cola. | Un crecimiento sostenido revela capacidad insuficiente. |
| Retry budget | Límite de reintentos por petición o periodo. | Evita tormentas de reintentos ante una caída externa. |
| Poison message | Trabajo que falla repetidamente por datos inválidos y bloquea una cola. | Derívalo a DLQ con observabilidad. |
| Chaos testing | Pruebas que introducen fallos controlados en dependencias o red. | Comprueba que los agentes no repiten acciones peligrosas. |
| Canary deployment | Despliegue inicial a un subconjunto pequeño de tráfico. | Observa errores y calidad antes de ampliar. |
| Feature flag | Interruptor que habilita o deshabilita una capacidad sin desplegar código nuevo. | Útil para cortar acciones de alto riesgo. |
| Kill switch | Control que detiene rápidamente una funcionalidad o agente. | Debe operar fuera de la lógica generativa. |
| Cost attribution | Asociación de consumo y gasto con usuario, agente, modelo o etapa. | Permite encontrar dónde se agota el presupuesto. |
| Cost guardrail | Límite que rechaza o degrada operaciones al superar una cuota. | Mejor que confiar en que el prompt no gastará demasiado. |
| Model drift | Cambio en el comportamiento o calidad observada de modelos usados con el tiempo. | Ejecuta evaluaciones al cambiar versión o proveedor. |
| Dataset drift | Cambio en la distribución de datos reales frente a los utilizados en pruebas. | Una buena nota offline puede dejar de representar producción. |
| Trace span | Unidad temporal dentro de una traza de ejecución distribuida. | Una llamada MCP puede tener spans de autenticación, lectura y respuesta. |
| OpenTelemetry | Estándar para instrumentar y exportar trazas, métricas y logs. | Útil para correlacionar inferencias con llamadas a herramientas. |

## Matriz de distinciones conceptuales

Las siguientes tablas comparan términos con funciones cercanas. La columna «Criterio de decisión» señala cuándo aplicar cada opción; «Confusión habitual» identifica el error de interpretación que se debe evitar.

### D1 — Arquitectura de agentes y orquestación

| Términos | Diferencia fundamental | Criterio de decisión | Confusión habitual |
|---|---|---|---|
| Agente / workflow | El agente decide dinámicamente pasos y herramientas; el workflow define transiciones predominantemente programadas. | Prioriza un workflow para procesos previsibles; utiliza un agente si hay decisiones abiertas. | Suponer que encadenar llamadas convierte automáticamente un sistema en agente. |
| Agentic loop / prompt chaining | El bucle observa resultados y decide si continuar; el encadenamiento conecta etapas definidas de antemano. | Usa bucles para exploración; cadenas para procesos estables. | Confundir repetición controlada con una secuencia fija. |
| Single-agent / multi-agent | Un agente concentra decisiones; varios separan funciones, contextos o tareas. | Divide solo cuando la especialización compense coordinación y coste. | Pensar que más agentes implican mejores resultados. |
| Orchestrator–workers / evaluator–optimizer | El primero distribuye subtareas; el segundo critica y revisa una solución. | Distribución para subtareas independientes; evaluación para mejora iterativa. | Pedir al mismo modelo que replique un análisis sin criterios de evaluación. |
| Routing / handoff | Routing selecciona una ruta; handoff transfiere la responsabilidad o contexto de una tarea. | Clasifica antes de decidir un destino; delega cuando cambia el responsable. | Tratar cualquier cambio de herramienta como delegación de agente. |
| Fan-out / fan-in | Fan-out dispersa trabajo; fan-in agrega resultados y resuelve discrepancias. | Define ambas fases si ejecutas ramas paralelas. | Distribuir sin planificar la integración final. |
| Paralelización / concurrencia | Paralelización ejecuta trabajo simultáneamente; concurrencia solapa tareas, no necesariamente a la vez. | Paraleliza solo tareas independientes y seguras. | Ejecutar escrituras dependientes sin sincronización. |
| Planificación / replanificación | Planificar establece pasos; replanificar ajusta el plan tras nueva evidencia. | Replanifica ante bloqueos, resultados inesperados o cambios de objetivo. | Reintentar indefinidamente un plan inviable. |
| Estado conversacional / estado de negocio | Uno representa contexto textual; el otro es la información autoritativa del sistema. | Consulta siempre el origen de verdad para pagos, permisos y datos. | Confiar en una afirmación del chat como prueba de una operación. |
| Estado de ejecución / estado conversacional | Uno registra progreso de tareas; el otro conserva mensajes. | Persiste ambos por separado si necesitas reanudar tareas. | Creer que el historial de mensajes garantiza reanudación fiable. |
| Orquestador / modelo | El orquestador valida y ejecuta reglas; el modelo propone acciones o textos. | Mantén permisos y límites en código. | Delegar decisiones de autorización en instrucciones del prompt. |
| Supervisor / trabajador | El supervisor coordina; el trabajador completa una subtarea delimitada. | Establece entregables y permisos específicos para cada trabajador. | Conceder a todos los agentes las mismas capacidades. |
| `tool_use` / ejecución real | `tool_use` es una solicitud generada por Claude; el ejecutor externo realiza la acción. | Valida argumentos y permisos antes de ejecutar. | Dar por realizada una operación solo porque el modelo la solicitó. |
| `end_turn` / éxito de negocio | `end_turn` indica cierre del turno, no confirmación de una escritura o transacción. | Verifica el resultado en la herramienta y el sistema de registro. | Anunciar éxito antes de consultar la operación real. |
| `max_tokens` / respuesta final | El límite de salida puede cortar una respuesta; una respuesta final requiere comprobar completitud. | Trata la salida truncada como incompleta. | Parsear JSON interrumpido como si fuera válido. |
| Human-in-the-loop / aprobación automática | El primero requiere intervención humana; el segundo aplica reglas previamente autorizadas. | Introduce aprobación humana en operaciones irreversibles o sensibles. | Confundir una explicación del modelo con consentimiento del usuario. |

### D2 — Herramientas, contratos y MCP

| Términos | Diferencia fundamental | Criterio de decisión | Confusión habitual |
|---|---|---|---|
| Client tool / server tool | En herramientas de cliente, la aplicación ejecuta la operación; en ciertas herramientas alojadas por el proveedor, la ejecución se realiza en el entorno del proveedor. | Determina primero dónde se ejecuta y quién autoriza la acción. | Suponer que Claude ejecuta directamente cualquier función Python anunciada. |
| `tool_use` / `tool_result` | El primero describe una llamada solicitada; el segundo contiene el resultado comunicado a Claude. | Conserva el identificador que vincula solicitud y resultado. | Devolver una respuesta de herramienta sin asociarla correctamente. |
| Definición de herramienta / implementación | La definición describe nombre y argumentos; la implementación ejecuta lógica real. | Diseña el contrato y su backend como capas separadas. | Creer que publicar un esquema implementa la función. |
| JSON Schema / validación de negocio | El esquema comprueba estructura y tipos; las reglas de negocio comprueban coherencia y permisos. | Aplica validaciones estructurales y semánticas en etapas distintas. | Aceptar un importe incorrecto porque cumple el esquema. |
| `strict: true` / autorización | Un mecanismo estricto condiciona la estructura de argumentos; la autorización permite o rechaza una acción. | Aplica RBAC, comprobación de recursos y políticas en el backend. | Confundir argumentos válidos con acceso legítimo. |
| `input_schema` / `output_schema` | Uno describe argumentos aceptados; el otro, cuando está soportado, la estructura de resultados. | Define cada contrato según su flujo de datos. | Validar solo la entrada e ignorar datos devueltos. |
| `tool_choice: auto` / `any` / `tool` | `auto` permite decidir; `any` fuerza alguna herramienta; `tool` selecciona una concreta, según compatibilidad. | Revisa las opciones admitidas por tu modelo antes de elegir. | Dar por universal una configuración dependiente del modelo. |
| `required` / no nulo | `required` exige presencia; no nulo restringe valores `null` de acuerdo con el esquema. | Define presencia y nulabilidad por separado. | Tratar un campo obligatorio como necesariamente no nulo. |
| `enum` / `const` | `enum` admite un conjunto de valores; `const` fija uno. | Usa `enum` para estados posibles y `const` para un valor único. | Dar por válida cualquier cadena con formato parecido. |
| MCP tool / resource / prompt | Tool invoca acciones; resource expone contenido; prompt ofrece plantillas. | Elige la primitiva acorde a operación, lectura o plantilla. | Modelar toda fuente de datos como herramienta ejecutable. |
| MCP host / client / server | El host contiene la aplicación; el cliente gestiona una conexión; el servidor expone capacidades. | Traza qué proceso descubre y llama cada recurso. | Llamar «servidor» a cualquier aplicación que usa MCP. |
| `stdio` / Streamable HTTP | `stdio` comunica procesos por entrada/salida estándar; HTTP comunica mediante peticiones de red. | Usa `stdio` para procesos locales y HTTP para servicios remotos cuando corresponda. | Confundir transporte con semántica de las herramientas. |
| MCP handshake / MCP stateless | Revisiones anteriores negocian sesión; la revisión moderna 2026-07-28 usa un ciclo sin sesión de protocolo. | Selecciona implementación y manejo de estado según revisión. | Suponer que clientes y servidores de distintas eras son intercambiables. |
| `initialize` / `server/discover` | `initialize` pertenece a la era basada en handshake; `server/discover` a la era moderna. | Identifica primero la versión del protocolo. | Aplicar el flujo de inicialización antiguo a un servidor moderno. |
| `isError` / error JSON-RPC | `isError` señala fallo de una herramienta; un error JSON-RPC señala fallo al procesar un mensaje RPC. | Registra y recupera ambos niveles por separado. | Reintentar un error de parámetros como si fuera de transporte. |
| Autenticación / autorización | La primera determina identidad; la segunda decide acceso a una operación concreta. | Verifica identidad, ámbito y propiedad del recurso. | Asumir que tener un token permite cualquier operación. |
| Idempotency key / request ID | La clave de idempotencia previene duplicados; el request ID correlaciona una petición. | Conserva la misma clave al reintentar una escritura incierta. | Duplicar un pago al usar un ID nuevo tras un timeout. |
| Timeout / rate limit | Timeout limita la espera; rate limit controla la frecuencia o volumen de llamadas. | Aplica políticas de recuperación distintas para cada causa. | Reintentar errores 429 sin respetar límites. |
| Paginación / batching | La primera divide resultados de lectura; el segundo agrupa operaciones. | Pagina listados grandes; agrupa tareas cuando el API lo permita. | Suponer que una página es un lote de ejecución. |
| Elicitation / sampling | Elicitation solicita información al usuario; sampling solicita generación de un modelo en los flujos que lo admiten. | Comprueba soporte según revisión MCP; la semántica y los flujos han evolucionado. | Suponer que todas las versiones permiten las mismas peticiones servidor→cliente. |
| OAuth scopes / roles RBAC | Los scopes acotan un token; los roles asocian permisos a identidades según política. | Combina el ámbito del token con la autorización de recurso. | Aceptar un token válido como permiso universal. |
| Tool discovery / tool invocation | Discovery anuncia herramientas; invocation ejecuta una herramienta elegida. | Descubre contratos antes de emitir llamadas. | Tratar el listado de herramientas como si fuera una ejecución. |

### D3 — Claude Code, terminal y repositorios

| Términos | Diferencia fundamental | Criterio de decisión | Confusión habitual |
|---|---|---|---|
| `Glob` / `Grep` | `Glob` localiza rutas mediante comodines; `Grep` busca coincidencias en el contenido de archivos. | Conoces ruta o extensión → `Glob`; conoces símbolo o texto → `Grep`. | Buscar una función con `Glob` o nombres de archivos con un patrón textual. |
| Glob / regex | Glob describe rutas; regex describe patrones de texto con operadores diferentes. | `**/*.py` corresponde a glob; `^def\s+` corresponde a regex. | Aplicar `**` como si significara lo mismo en ambos lenguajes. |
| `Grep` de Claude Code / `rg` de terminal | Uno es una herramienta de Claude Code; el otro es el ejecutable ripgrep. | Elige la herramienta integrada o ejecuta `rg` desde la shell según el entorno. | Escribir `Grep` en Git Bash esperando el mismo contrato de Claude Code. |
| `grep` / `rg` | Ambos buscan texto; `rg` suele incorporar búsqueda recursiva eficiente y respeto por exclusiones del repositorio. | Usa `rg` si está instalado; verifica opciones concretas en cada herramienta. | Dar por idénticos todos los argumentos. |
| `find` / `rg --files` | `find` recorre rutas con filtros del sistema; `rg --files` enumera archivos respetando configuraciones de ripgrep. | Selecciona según portabilidad, exclusiones y criterios. | Suponer que mostrarán siempre el mismo conjunto de archivos. |
| `rg -F` / `rg` con regex | `-F` interpreta el patrón como texto literal; sin `-F`, `rg` usa regex. | Busca fragmentos de código literales con `-F`. | No escapar paréntesis y obtener coincidencias inesperadas. |
| `rg -g` / `rg --glob` / glob puro | `-g` y `--glob` filtran rutas en ripgrep; un glob puro no busca contenido. | Combina `rg 'patrón' -g '*.py'` para filtrar y buscar a la vez. | Confundir filtro de archivos con expresión del contenido. |
| `Read` / `Grep` | `Read` recupera contenido de un archivo conocido; `Grep` localiza coincidencias entre archivos. | Busca primero y lee después cuando no conozcas la ubicación. | Abrir cientos de archivos para encontrar una línea. |
| `Read` / `WebFetch` | `Read` se aplica a archivos del entorno; `WebFetch` consulta contenido web permitido. | Usa origen local o remoto según procedencia. | Otorgar a texto remoto autoridad de instrucciones. |
| `Edit` / `Write` | `Edit` modifica fragmentos; `Write` crea o reemplaza archivos según permisos. | Prefiere cambios localizados en archivos existentes. | Sobrescribir un archivo completo para arreglar una línea. |
| `NotebookEdit` / `Edit` | `NotebookEdit` opera sobre estructura de celdas; `Edit` trata contenido de archivo. | Usa edición especializada para `.ipynb` cuando esté disponible. | Romper metadatos del notebook al editar JSON manualmente. |
| `Bash` / herramientas de archivos | `Bash` ejecuta comandos; `Glob`, `Grep`, `Read` y `Edit` tienen propósitos delimitados. | Prefiere herramientas específicas cuando cubran la tarea. | Ejecutar comandos de shell para toda consulta simple. |
| `CLAUDE.md` / `settings.json` | `CLAUDE.md` contiene contexto e instrucciones; `settings.json` configura opciones, permisos y hooks. | Define reglas operativas en la configuración, no solo en prosa. | Creer que una advertencia en Markdown impide una operación. |
| `settings.json` / `settings.local.json` | Uno corresponde a ajustes compartibles del proyecto; el archivo local suele contener preferencias no destinadas al repositorio. | Comparte política del equipo y conserva excepciones locales fuera de Git. | Publicar autorizaciones o rutas específicas de un equipo. |
| Skill / subagente | Skill empaqueta un procedimiento; subagente delega una tarea a un contexto especializado. | Skill para repetir un método; subagente para separar ejecución. | Tratar un documento de instrucciones como otro agente activo. |
| Skill / comando de barra | Una skill es una capacidad reutilizable; los comandos de barra son una forma de invocar acciones disponibles, según versión. | Examina el mecanismo instalado y su ruta de definición. | Suponer que todo comando es una herramienta de la API. |
| Hook / instrucción de prompt | Un hook ejecuta lógica programada en un evento; el prompt expresa una orientación al modelo. | Usa hooks y permisos para controles verificables. | Considerar una instrucción textual como control de seguridad. |
| `PreToolUse` / `PostToolUse` | Uno actúa antes de la llamada; el otro después de que se produzca. | Bloquea antes; registra, inspecciona o informa después. | Intentar evitar una acción peligrosa únicamente con un evento posterior. |
| `allow` / `ask` / `deny` | Permiten, solicitan aprobación o deniegan una operación según política. | Configura mínimo privilegio, especialmente para escrituras y red. | Asumir que «no preguntar» equivale a «seguro». |
| `Agent` / `Grep` | `Agent` delega trabajo a otro contexto; `Grep` localiza texto. | Usa búsqueda para preguntas sencillas y delegación para análisis complejos. | Iniciar subagentes para tareas de consulta triviales. |
| Subagente / equipo de agentes | Subagente ejecuta una tarea delegada; un equipo coordina múltiples participantes con interacción más compleja cuando se admite. | Evalúa coste de coordinación y necesidad de colaboración. | Presuponer que ambas funciones tienen igual estado o permisos. |
| `git status` / `git diff` | `status` enumera cambios; `diff` muestra diferencias de contenido. | Inspecciona estado y después diff antes del commit. | Revisar solo nombres y no el contenido que vas a publicar. |
| `git add` / `git commit` / `git push` | Preparar cambios / registrar una confirmación local / enviarla al remoto. | Comprueba archivos preparados con `git diff --cached`. | Pensar que `commit` ya publica en GitHub. |
| `.gitignore` / `git rm --cached` | `.gitignore` evita nuevos seguimientos; `git rm --cached` deja de rastrear archivos ya indexados. | Retira del índice secretos previamente añadidos y rota credenciales expuestas. | Creer que ignorar un archivo borra su historial de Git. |
| `.env` / `.env.example` | `.env` contiene valores locales potencialmente secretos; `.env.example` muestra nombres de variables sin credenciales. | Publica solo la plantilla. | Copiar tokens reales dentro del ejemplo. |
| Rama / worktree | Rama identifica una línea de commits; worktree permite directorios de trabajo adicionales para una rama. | Usa worktrees para trabajar simultáneamente con ramas separadas. | Creer que cada rama requiere un repositorio clonado. |

### D4 — Prompt engineering y salidas estructuradas

| Términos | Diferencia fundamental | Criterio de decisión | Confusión habitual |
|---|---|---|---|
| Zero-shot / few-shot | Zero-shot no incluye ejemplos; few-shot aporta ejemplos de entradas y salidas. | Añade ejemplos cuando mejoren consistencia o resuelvan ambigüedad. | Suponer que más ejemplos garantizan mayor calidad. |
| System prompt / mensaje de usuario | El primero define instrucciones de nivel superior de la aplicación; el segundo transmite la petición del usuario. | Separa comportamiento estable y solicitud puntual. | Insertar reglas de seguridad únicamente en el mensaje del usuario. |
| Instrucción de formato / Structured Outputs | Una instrucción pide una forma; Structured Outputs aplica controles de estructura según soporte. | Usa esquemas cuando otro programa debe consumir la respuesta. | Dar por garantizado un JSON solo porque el prompt lo solicita. |
| JSON sintácticamente válido / dato correcto | Sintaxis correcta no implica valores verdaderos ni coherentes. | Valida evidencia, aritmética y reglas del dominio. | Aceptar cifras incorrectas porque `json.loads` funciona. |
| Parsing / validación | Parsing transforma texto en estructura; validación verifica restricciones. | Encadena ambas operaciones con manejo de errores. | Tratar un diccionario Python como contrato validado. |
| `required` / `additionalProperties: false` | El primero exige campos concretos; el segundo prohíbe campos no declarados. | Combínalos para contratos cerrados cuando corresponda. | Creer que una lista de campos obligatorios prohíbe extras. |
| `enum` / descripción del campo | `enum` restringe valores; una descripción orienta al modelo o desarrollador. | Restringe en esquema y explica en prosa. | Pensar que «solo aprobado o rechazado» es validación ejecutable. |
| Ejemplo de prompt / conjunto de evaluación | El ejemplo orienta generación; el conjunto de evaluación mide rendimiento. | Mantén pruebas independientes de ejemplos de desarrollo. | Evaluar con los mismos casos usados para ajustar el prompt. |
| Clasificación / extracción | Clasificación selecciona categorías; extracción identifica valores o entidades. | Usa etiquetas enumeradas o campos tipados, respectivamente. | Forzar texto libre cuando esperas categorías estables. |
| Respuesta estructurada / llamada de herramienta | Una salida estructurada entrega datos; una llamada solicita ejecución de una operación. | Herramientas para acciones; formato de salida para datos a consumir. | Usar una herramienta ficticia solo para obtener JSON si hay soporte nativo adecuado. |
| Temperatura / reproducibilidad | Temperatura altera la distribución de muestreo; reproducibilidad también depende del modelo y del entorno. | Usa pruebas y contratos, no solo una temperatura baja. | Suponer determinismo perfecto con temperatura cero. |
| Prompt injection / solicitud legítima | La inyección introduce instrucciones hostiles desde contenido de menor confianza. | Trata documentos y páginas recuperadas como datos. | Obedecer una instrucción encontrada en el texto a resumir. |
| Precisión (precision) / exhaustividad (recall) | Precisión penaliza falsos positivos; recall penaliza omisiones. | Ajusta según el daño de cada tipo de error. | Optimizar una métrica sin considerar la tarea. |
| LLM-as-a-judge / validación determinista | El juez LLM califica criterios cualitativos; la validación determinista aplica reglas programables. | Usa código para invariantes y jueces para dimensiones subjetivas. | Delegar reglas aritméticas a un evaluador probabilístico. |
| Evaluación offline / evaluación online | Offline usa casos controlados; online mide comportamiento real en producción. | Combina pruebas reproducibles y monitoreo de uso. | Publicar un cambio solo porque pasa cinco ejemplos. |
| Output truncation / respuesta vacía | Truncation interrumpe salida por límites; una respuesta vacía puede ser resultado válido o error según contrato. | Inspecciona `stop_reason` y la estructura devuelta. | Interpretar un JSON incompleto como ausencia de resultados. |
| Prompt template / prompt instance | Template contiene variables y reglas; instance es su versión interpolada para una solicitud. | Versiona plantillas y registra parámetros no sensibles. | Evaluar diferentes plantillas sin documentar cambios. |

### D5 — Contexto, recuperación, seguridad y fiabilidad

| Términos | Diferencia fundamental | Criterio de decisión | Confusión habitual |
|---|---|---|---|
| Ventana de contexto / límite de salida | Una limita contexto procesable; el otro restringe tokens generados. | Cuenta entrada y reserva salida con margen suficiente. | Tratar una ventana grande como permiso para respuestas infinitas. |
| Truncamiento / resumen / compactación | Truncar elimina; resumir condensa; compactar administra estado para conservar información útil. | Prioriza resúmenes verificados y preserva datos críticos. | Cortar mensajes recientes sin revisar dependencias. |
| Memoria persistente / prompt caching | Memoria conserva datos; caching reutiliza procesamiento de prefijos cuando aplica. | Persiste hechos en almacenamiento y usa caché para optimizar coste. | Suponer que un prefijo cacheado recordará al usuario en otra sesión. |
| RAG / fine-tuning | RAG recupera información externa en tiempo de consulta; fine-tuning modifica comportamiento a través de entrenamiento. | Elige RAG para conocimientos cambiantes y fuentes citables. | Reentrenar para actualizar información que cambia cada semana. |
| Retrieval / reranking | Retrieval obtiene candidatos; reranking reordena los recuperados. | Recupera con amplitud y reordena para mejorar relevancia. | Esperar que reranking encuentre documentos nunca recuperados. |
| BM25 / embeddings densos | BM25 explota coincidencia léxica; los vectores densos captan similitud semántica. | Combina ambos en búsquedas híbridas cuando convenga. | Pensar que la búsqueda vectorial siempre encuentra identificadores exactos. |
| Chunking / contexto completo | Chunking divide documentos para recuperar fragmentos; contexto completo envía grandes bloques íntegros. | Fragmenta cuando reduzca ruido y mejore búsqueda. | Dividir una regla sin preservar sus excepciones. |
| Grounding / exactitud factual | Grounding vincula una respuesta a fuentes; exactitud evalúa si la conclusión es correcta. | Contrasta afirmaciones con evidencias y reglas del dominio. | Dar por verdadero un texto solo porque incluye cita. |
| Cita / evidencia | La cita identifica una fuente; la evidencia sostiene una afirmación específica. | Comprueba que el pasaje citado demuestra el enunciado. | Añadir enlaces genéricos como sustituto de validación. |
| Filtrado por permisos / reranking | Los permisos limitan qué puede verse; reranking ordena lo ya autorizado. | Filtra antes de recuperar o exponer contenido, según arquitectura. | Reordenar información de otro usuario como si eso protegiera su acceso. |
| Timeout / cancelación | Timeout limita espera; cancelación solicita detener el trabajo. | Define ambos cuando el backend pueda seguir ejecutando tras abandonar el cliente. | Reintentar una escritura que todavía se procesa. |
| Retry / backoff / circuit breaker | Retry repite; backoff espacía intentos; circuit breaker evita llamadas a un servicio degradado. | Combínalos según el tipo de fallo y presupuesto. | Reintentar sin límites un servicio caído. |
| Idempotencia / exactly-once | Idempotencia protege el efecto repetido; exactly-once es una garantía operativa más fuerte y difícil. | Usa claves idempotentes y conciliación para pagos o escrituras. | Dar por posible exactly-once solo por usar HTTP. |
| Autenticación / autorización | Autenticación verifica quién actúa; autorización verifica qué puede hacer. | Verifica ambos en la fuente de verdad. | Aceptar la titularidad de un recurso porque el usuario inició sesión. |
| Prompt injection / data poisoning | La primera intenta desviar instrucciones durante una interacción; el segundo contamina datos utilizados por un sistema. | Aísla confianza de fuentes y protege datos de indexación. | Tratar una página manipulada como política de aplicación. |
| Mínimo privilegio / sandbox | Mínimo privilegio reduce permisos; sandbox limita entorno de ejecución. | Combina permisos mínimos, límites de recursos y aislamiento. | Pensar que un sandbox autoriza exfiltrar datos legítimos. |
| Logging / métricas / tracing | Logs registran eventos; métricas agregan magnitudes; trazas vinculan pasos de una operación. | Usa las tres señales según necesidades de diagnóstico. | Creer que muchos logs sustituyen correlación de una ejecución. |
| Latencia / throughput | Latencia es duración por solicitud; throughput, número procesado por unidad de tiempo. | Optimiza ambas en función del SLO. | Aumentar paralelismo sin medir saturación. |
| p50 / p95 / p99 | Percentiles describen latencias de distintos segmentos de la distribución. | Usa percentiles altos para detectar experiencia degradada en la cola. | Presentar solo promedio ocultando solicitudes lentas. |
| SLI / SLO / SLA | Indicador medido / objetivo interno / compromiso formal de servicio. | Define primero una medición fiable y su objetivo. | Confundir el objetivo de ingeniería con un contrato externo. |
| RTO / RPO | RTO marca tiempo objetivo de recuperación; RPO, pérdida temporal máxima tolerada de datos. | Diseña copias y recuperación para ambos umbrales. | Confundir rapidez de recuperación con integridad del estado. |
| Redacción de datos / cifrado | Redacción oculta o elimina información; cifrado la protege mediante claves. | Redacta secretos en logs y cifra datos sensibles cuando proceda. | Guardar contraseñas en un log porque el disco está cifrado. |
| Error transitorio / permanente | El transitorio puede resolverse al reintentar; el permanente exige corregir petición, permisos o configuración. | Clasifica el error antes de la política de recuperación. | Reintentar indefinidamente un `FORBIDDEN`. |

### Distinciones transversales

| Términos | Diferencia fundamental | Criterio de decisión | Confusión habitual |
|---|---|---|---|
| Herramienta MCP / herramienta nativa de Claude Code | La primera pertenece a un servidor MCP integrado; la segunda es una capacidad ofrecida por Claude Code. | Identifica origen, permisos y contrato de cada herramienta. | Suponer que toda herramienta disponible proviene de MCP. |
| API Key / token OAuth | La API key identifica y autoriza una integración según proveedor; OAuth delega acceso con ámbitos y ciclo de autorización. | Elige el mecanismo exigido por la plataforma y el caso de uso. | Usar una clave de servicio como credencial personal compartida. |
| Política de permisos / prompt de seguridad | La política se impone en controles técnicos; el prompt describe comportamiento deseado. | Aplica controles fuera del modelo para acciones sensibles. | Considerar una instrucción textual como una barrera de acceso. |
| Evaluación del modelo / evaluación del sistema | La primera mide un componente; la segunda incluye herramientas, fuentes, permisos y efectos. | Evalúa el recorrido extremo a extremo antes de producción. | Atribuir todos los fallos al modelo cuando el problema es del backend. |
| Guardrail de formato / guardrail de contenido | Uno restringe estructura; el otro controla políticas y riesgos semánticos. | Prueba ambas capas con casos adversariales. | Confundir JSON válido con respuesta permitida. |
| Instrucción / dato recuperado | Una instrucción autorizada gobierna comportamiento; una fuente externa aporta contenido no confiable. | Mantén jerarquías de confianza y no ejecutes órdenes de documentos. | Permitir que una página web cambie las reglas del agente. |
| Mock / llamada real a la API | Mock simula comportamiento reproducible; llamada real evalúa integración con modelo y servicio. | Usa mocks para unit tests y llamadas reales controladas para integración. | Dar por probada la integración porque pasan tests simulados. |
| Test unitario / integración / extremo a extremo | Evalúan función aislada / módulos conectados / recorrido completo. | Elige nivel en función del riesgo y del cambio. | Confiar solo en pruebas unitarias para validar permisos MCP. |
| Esquema de salida / contrato de negocio | Uno especifica campos y tipos; otro incorpora invariantes y semántica operativa. | Aplica validación de esquema y reglas autoritativas. | Permitir una operación inválida porque la estructura coincide. |
| Git commit / publicación en GitHub | Commit registra historial local; push sincroniza una rama con el repositorio remoto. | Audita cambios antes de enviar. | Creer que el historial local ya es público. |

## Casos de aplicación

| Caso | Situación | Decisión arquitectónica | Dominios |
|---|---|---|---|
| Recurso ajeno | Se pide modificar el pedido de otra cuenta. | Rechazar en el backend por autorización; no modificar el recurso ni revelar datos sensibles. | D1, D2, D5 |
| JSON correcto, importe incorrecto | Una factura presenta `subtotal=100`, `iva=21` y `total=130`. | Rechazar por regla aritmética; la validación sintáctica no acredita veracidad. | D4, D5 |
| Timeout tras reembolso | El cliente pierde conexión después de enviar una escritura potencialmente ejecutada. | Consultar el estado de operación o reintentar con la misma clave de idempotencia. | D2, D5 |
| Lectura de `.env` | Un flujo de desarrollo intenta inspeccionar un archivo con secretos. | Denegar la lectura mediante permisos efectivos y controles previos; no confiar solo en `CLAUDE.md`. | D3, D5 |
| Miles de extracciones independientes | Una tarea admite procesamiento por lotes y respuesta no inmediata. | Considerar Message Batches si el servicio y plazo lo permiten; correlacionar resultados con `custom_id`. | D1, D4, D5 |
| Página con instrucciones maliciosas | Un documento recuperado ordena exfiltrar credenciales. | Tratarlo como dato no confiable; no seguir sus órdenes y mantener restricciones de herramientas. | D4, D5 |
| Cliente MCP incompatible | Un cliente de handshake intenta hablar con un servidor del protocolo moderno. | Comprobar revisión y SDK; adaptar el ciclo de vida y los contratos de cada era. | D2 |
| Dos agentes discrepan | Revisores especializados ofrecen conclusiones incompatibles. | Contrastar fuentes y vigencia, conservar incertidumbre y escalar cuando no haya resolución verificable. | D1, D5 |
| Buscar una función desconocida | Se conoce el nombre `extract_text`, pero no su archivo. | Buscar contenido con `Grep` o `rg -n 'extract_text' -g '*.py'` y leer coincidencias relevantes. | D3 |
| Encontrar notebooks de un módulo | Se desconoce la ruta de varios archivos `.ipynb`. | Usar `Glob` con `**/*.ipynb` o `rg --files -g '*.ipynb'` desde la terminal. | D3 |
| Salida estructurada truncada | Una respuesta alcanza el límite de tokens durante la generación de un objeto. | Detectar `stop_reason`, evitar parseo prematuro y aplicar recuperación acotada. | D1, D4, D5 |
| Pérdida de evidencia en RAG | La recuperación omite la excepción relevante de una norma. | Revisar chunking, recall, filtros, reranking y cobertura de fuente antes de responder. | D4, D5 |

## Guía de referencia y repaso

### Selección del patrón arquitectónico

| Necesidad | Patrón recomendado | Verificación imprescindible |
|---|---|---|
| Transformar datos en etapas fijas | Prompt chaining o workflow determinista | Validar salida de cada etapa. |
| Elegir entre tareas distintas | Routing | Trazar la decisión y el criterio de clasificación. |
| Analizar documentos independientes | Parallelization y fan-in | Controlar concurrencia, costes y agregación. |
| Descomponer un objetivo cambiante | Orchestrator–workers o agentic loop | Presupuesto de pasos, permisos y criterio de parada. |
| Revisar un borrador contra criterios | Evaluator–optimizer | Evaluación reproducible y límite de revisiones. |
| Ejecutar una acción sensible | Human-in-the-loop y backend autorizado | Confirmación explícita, identidad y trazabilidad. |
| Reanudar una ejecución | Estado persistido y mecanismo de reanudación | Identificador, transiciones y deduplicación. |
| Resolver evidencia contradictoria | Evaluación de procedencia y escalado | No ocultar la incertidumbre. |

### Ciclo de herramientas con Claude

| Fase | Qué ocurre | Validación exigida | Fallo frecuente |
|---|---|---|---|
| 1. Declaración | La aplicación anuncia herramientas y esquemas disponibles. | Nombres, descripciones y `input_schema` consistentes. | Exponer herramientas demasiado amplias. |
| 2. Inferencia | Claude responde con texto o solicitudes `tool_use`. | Revisar `content` y `stop_reason`. | Asumir que todos los bloques son texto. |
| 3. Despacho | El orquestador identifica la herramienta solicitada. | Lista de herramientas permitidas y correspondencia de IDs. | Ejecutar una herramienta no registrada. |
| 4. Validación | El backend verifica argumentos, identidad y límites. | Tipos, reglas de negocio, propiedad del recurso. | Confiar exclusivamente en JSON Schema. |
| 5. Ejecución | El ejecutor realiza la acción autorizada. | Timeout, idempotencia, cuota y registro. | Repetir una escritura después de un timeout incierto. |
| 6. Resultado | La aplicación devuelve un `tool_result` asociado al `tool_use`. | Preservar el ID y representar errores de forma útil. | Perder correlación o exponer secretos en el resultado. |
| 7. Continuación | Claude interpreta el resultado y puede continuar o cerrar el turno. | Límite de iteraciones, coste y condición final. | Confundir una explicación con confirmación autoritativa. |

### Integración MCP: decisiones rápidas

| Pregunta técnica | Criterio recomendado | Comprobación |
|---|---|---|
| ¿Necesito invocar una operación? | Exponer una *tool*. | Esquema de entrada, permisos y efectos secundarios. |
| ¿Necesito presentar datos consultables? | Exponer un *resource* si encaja con el cliente. | URI, acceso, tamaño y actualización. |
| ¿Necesito una plantilla reutilizable? | Exponer un *prompt*. | Parámetros y separación respecto a políticas de seguridad. |
| ¿El servidor corre dentro de mi máquina? | Considerar transporte `stdio`. | Proceso lanzado, rutas y entorno. |
| ¿Es un servicio remoto? | Considerar transporte HTTP compatible con revisión y cliente. | Red, autenticación, origen y timeout. |
| ¿Existe fallo por incompatibilidad? | Identificar revisión MCP antes de depurar handlers. | Era handshake frente a protocolo moderno sin sesión. |
| ¿Una herramienta devuelve un error? | Separar error de negocio, de herramienta, de protocolo y de transporte. | `isError`, estado HTTP, respuesta JSON-RPC y logs. |
| ¿La herramienta modifica datos? | Autorizar por usuario y recurso; controlar reintentos. | Mínimo privilegio, idempotencia y auditoría. |
| ¿Hay respuestas grandes? | Paginación para listados, límites para resultados y resumen controlado. | Continuaciones, completitud y coste. |
| ¿Se solicitan datos al usuario o al modelo? | Revisar soporte de elicitation o sampling según era. | Capacidades negociadas y versión implementada. |

### Claude Code: búsqueda y operación sobre archivos

| Objetivo | Herramienta Claude Code o comando de terminal | Ejemplo de referencia | Interpretación |
|---|---|---|---|
| Localizar todos los notebooks | `Glob` / `rg --files` | `**/*.ipynb` o `rg --files -g '*.ipynb'` | Coincidencia por ruta. |
| Localizar tests | `Glob` / `rg --files` | `**/test_*.py` | Patrones sobre nombres de archivos. |
| Buscar un símbolo Python | `Grep` / `rg` | `rg -n 'def extract_text' -g '*.py'` | Coincidencias dentro de archivos. |
| Buscar varias palabras | `Grep` / `rg` | `rg -n 'timeout\|retry' src/` | Alternancia regex. |
| Buscar texto literal con paréntesis | `Grep` / `rg -F` | `rg -n -F 'messages.create(' src/` | El patrón no interpreta regex. |
| Filtrar por extensión | `Glob` o `rg -g` | `rg -n 'Anthropic' -g '*.py'` | Solo Python. |
| Buscar archivos ignorados deliberadamente | Terminal `rg --hidden --no-ignore` con extrema cautela | `rg --files --hidden --no-ignore` | Puede incluir `.env`, `.venv` y secretos: restringe rutas y no publiques resultados. |
| Buscar archivos con `find` | Terminal `find` | `find . -name '*.md'` | Recorre rutas; comportamiento distinto al de ripgrep. |
| Leer un módulo | `Read` | Ruta precisa y rango relevante | Lectura del contenido local. |
| Modificar una función | `Edit` | Archivo y fragmento objetivo | Edición localizada y revisión del diff. |
| Crear módulo | `Write` | `src/claude_architect/utils.py` | Escritura de contenido autorizado. |
| Modificar notebook | `NotebookEdit` cuando esté disponible | Cuaderno y celda objetivo | Edición estructural de `.ipynb`. |
| Ejecutar pruebas | `Bash` / terminal | `python -m pytest -q` | Ejecuta un proceso local. |
| Consultar el estado de Git | `Bash` / terminal | `git status --short` | Muestra cambios pendientes. |
| Examinar diferencias | `Bash` / terminal | `git diff` | Compara cambios no preparados. |
| Examinar lo preparado | `Bash` / terminal | `git diff --cached` | Verifica el contenido del siguiente commit. |
| Comprobar exclusiones | `Bash` / terminal | `git check-ignore -v .env` | Identifica regla de exclusión. |
| Verificar seguimiento de secretos | `Bash` / terminal | `git ls-files .env` | Si devuelve `.env`, el archivo ya está rastreado. |
| Retirar archivo del índice | `Bash` / terminal | `git rm --cached .env` | Deja de rastrearlo; no elimina el historial publicado. |
| Consultar servidores MCP configurados | CLI de Claude Code | `claude mcp list` | Lista configuraciones conocidas. |
| Consultar opciones CLI | CLI de Claude Code | `claude --help` | Fuente local para opciones de la versión instalada. |
| Delegar análisis extenso | `Agent` según disponibilidad | Investigación delimitada y sin cambios | Contexto delegado con permisos controlados. |
| Buscar información externa | `WebSearch` / `WebFetch` cuando se admitan | Buscar fuente, luego leerla | El contenido externo tiene menor nivel de confianza. |

### Claude Code: archivos de configuración y seguridad

| Elemento | Propósito | Regla de uso |
|---|---|---|
| `CLAUDE.md` | Instrucciones y contexto del proyecto. | No sustituye permisos efectivos. |
| `.claude/settings.json` | Ajustes compartidos a nivel de proyecto. | Revisar reglas y cambios antes de publicar. |
| `.claude/settings.local.json` | Preferencias locales cuando se usan. | No publicarlo salvo decisión deliberada. |
| `.claude/skills/<nombre>/SKILL.md` | Procedimiento y conocimientos reutilizables. | Incluir alcance, instrucciones y entradas esperadas. |
| `.claude/agents/` | Configuraciones de subagentes cuando se utilizan. | Limitar herramientas y contexto del agente. |
| `.mcp.json` | Servidores MCP asociados a un proyecto. | Evitar credenciales incrustadas. |
| `permissions.allow` | Operaciones permitidas. | Mantener permisos ajustados al trabajo. |
| `permissions.ask` | Operaciones que requieren consulta. | Reservar aprobación para acciones relevantes. |
| `permissions.deny` | Operaciones prohibidas. | Verificar su comportamiento efectivo y precedencia. |
| `PreToolUse` | Evento previo a una herramienta. | Aplicar restricciones y validaciones antes de ejecutar. |
| `PostToolUse` | Evento posterior a una herramienta. | Registrar y revisar resultados, no bloquear retroactivamente. |
| `.env` | Variables locales, incluidas credenciales. | Ignorar en Git y mantener fuera de salidas. |
| `.env.example` | Lista de variables requeridas. | Publicar solo ejemplos sin secretos. |

### Prompt engineering: contrato de salida y evaluación

| Situación | Enfoque | Validación de salida |
|---|---|---|
| Clasificación de categorías cerradas | Etiquetas `enum` y ejemplos si aportan precisión. | Pertenencia a la enumeración. |
| Extracción de documentos | Campos con tipos explícitos y evidencia asociada. | JSON Schema, presencia, tipos y veracidad. |
| Respuesta consumida por un programa | Structured Outputs cuando el modelo lo permita. | Parseo y reglas de negocio. |
| Campos que pueden faltar | Decidir opcionalidad o nulabilidad según contrato. | Distinguir ausente de `null`. |
| Evitar campos inesperados | Esquema cerrado cuando proceda. | `additionalProperties: false`. |
| Control de cálculos | Cálculos programáticos y fuentes verificadas. | Invariantes numéricas y consistencia. |
| Salida truncada | Revisar motivo de finalización. | No aceptar estructuras incompletas. |
| Clasificación evaluable | Dataset con verdad de referencia. | Precision, recall, F1 y matriz de confusión. |
| Criterios cualitativos | Rúbrica reproducible, eventualmente juez LLM. | Muestras auditadas y consistencia entre evaluadores. |
| Modificar un prompt | Versionado y evaluación comparativa. | Comparar contra casos de regresión y adversariales. |

### Contexto, RAG y fiabilidad

| Problema | Técnica de referencia | Señal de verificación |
|---|---|---|
| Contexto excesivo | Recorte deliberado, resumen o compactación con retención de hechos críticos. | Ausencia de información esencial y errores de referencia. |
| Entradas repetidas | Prompt caching cuando sea compatible. | Coste y tokens procesados, sin confundirlo con memoria. |
| Conocimiento externo cambiante | RAG sobre fuentes actualizadas. | Relevancia, vigencia y permisos de la fuente. |
| Consultas con identificadores exactos | Búsqueda léxica o híbrida. | Recall de nombres y códigos concretos. |
| Consultas semánticas | Recuperación vectorial. | Recall de significado y calidad del embedding. |
| Muchos candidatos poco relevantes | Reranking y filtros. | Precision@k y cobertura. |
| Fragmentos descontextualizados | Ajustar chunking y preservar metadatos. | Capacidad de recuperar excepciones y contexto. |
| Documentos con instrucciones hostiles | Separación de datos e instrucciones. | Pruebas de inyección y control de acceso a herramientas. |
| Servicios saturados | Rate limiting, backoff y límites de concurrencia. | Respuestas 429, latencia y tasa de éxito. |
| Fallos transitorios | Retry acotado con backoff. | Clasificación de error y presupuesto de intentos. |
| Fallos persistentes | Circuit breaker y degradación controlada. | Tasa de fallo y recuperación. |
| Reintentos de escritura | Idempotencia y reconciliación. | Estado final y ausencia de operaciones duplicadas. |
| Diagnóstico de un flujo agente | Logs, métricas y trazas correlacionadas. | IDs, latencia de pasos y causas de fallo. |
| Operaciones críticas | Aprobación y auditoría. | Identidad, autorización, resultado y reversibilidad. |

### Interpretación de indicadores

| Indicador | Qué expresa | Interpretación práctica |
|---|---|---|
| Precision | `TP / (TP + FP)` | De los positivos detectados, proporción correcta. |
| Recall | `TP / (TP + FN)` | De los positivos reales, proporción recuperada. |
| F1 | Media armónica de precision y recall. | Útil para equilibrar ambas cuando procede. |
| Precision@k | Fracción relevante de los primeros `k` resultados. | Evalúa calidad de resultados en primeras posiciones. |
| Recall@k | Proporción de relevantes recuperados en los primeros `k`. | Evalúa cobertura de búsqueda. |
| Tasa de éxito de herramientas | Ejecuciones completadas correctamente / intentos válidos. | Separar errores de herramienta y fallos del modelo. |
| p50 de latencia | Mediana de tiempos. | Experiencia típica, no casos lentos. |
| p95 de latencia | El 95 % de observaciones no supera ese umbral. | Experiencia de la cola de solicitudes. |
| Tasa de errores | Fallos / operaciones medidas. | Agrupar por tipo y severidad. |
| Coste por solicitud | Consumo asociado a una ejecución. | Incluye pasos del agente, reintentos y herramientas facturables. |

### Lista de verificación para ejercicios y simulacros

| Dominio | Antes de considerar una respuesta correcta | Error que debe descartarse |
|---|---|---|
| D1 | ¿Está justificada la autonomía? ¿Existe criterio de parada? ¿El estado es autoritativo? | Agente innecesario, bucle sin límites o acción asumida. |
| D2 | ¿Quién ejecuta? ¿Qué valida el backend? ¿Qué versión de MCP se utiliza? | Confusión entre esquema, autorización y ejecución. |
| D3 | ¿Buscas rutas o contenido? ¿Qué permiso permite el cambio? ¿El diff es verificable? | Usar `Glob` para contenido, confiar solo en `CLAUDE.md` o ignorar secretos. |
| D4 | ¿La salida cumple esquema y reglas semánticas? ¿Se evalúa con casos independientes? | JSON válido pero falso o evaluación contaminada. |
| D5 | ¿La fuente es confiable? ¿Se respeta el aislamiento? ¿Hay recuperación frente a fallos? | Inyección, fuga de contexto o reintento duplicado. |

### Secuencia de diagnóstico para escenarios

| Orden | Pregunta | Acción recomendada |
|---|---|---|
| 1 | ¿Qué resultado de negocio se necesita? | Definir éxito verificable, no solo texto de respuesta. |
| 2 | ¿Existe un flujo determinista suficiente? | Priorizar el diseño más simple que resuelva el caso. |
| 3 | ¿Qué decisiones debe tomar el modelo? | Aislar decisiones probabilísticas de políticas fijas. |
| 4 | ¿Qué datos y herramientas se necesitan? | Seleccionar fuentes y herramientas mínimas. |
| 5 | ¿Qué contenido es confiable? | Clasificar instrucciones, resultados y documentos externos. |
| 6 | ¿Qué permisos rigen la acción? | Validar identidad, autorización y propiedad del recurso. |
| 7 | ¿Qué restricciones estructurales aplican? | Definir y validar esquemas de entrada y salida. |
| 8 | ¿Qué pasa si la llamada falla? | Diseñar timeout, retry y estrategias de idempotencia. |
| 9 | ¿Cómo se demuestra el éxito? | Confirmar en sistema de registro y trazar ejecución. |
| 10 | ¿Cómo se mide el comportamiento? | Definir tests, métricas y umbrales de aceptación. |

## Referencias técnicas

| Área | Documentación | Aspecto que conviene verificar |
|---|---|---|
| Certificación | [Claude Certified Architect – Foundations](https://anthropic-partners.skilljar.com/claude-certified-architect-foundations-certification) | Temario y alcance vigente. |
| Anthropic API | [Tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) | Ciclo `tool_use` y `tool_result`. |
| Anthropic API | [Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools) | Esquemas y contratos de herramientas. |
| Anthropic API | [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) | Modelos compatibles y garantías de estructura. |
| Anthropic API | [Context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing) | Gestión del contexto en sesiones extensas. |
| Anthropic API | [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | Reutilización de contexto y medición de costes. |
| Anthropic API | [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) | Presupuestos de tokens. |
| Anthropic API | [Message Batches](https://platform.claude.com/docs/en/build-with-claude/batch-processing) | Operaciones por lotes y procesamiento diferido. |
| Claude Code | [Settings](https://code.claude.com/docs/en/settings) | Archivos de configuración y precedencia. |
| Claude Code | [Permissions](https://code.claude.com/docs/en/permissions) | Reglas de acceso y herramientas. |
| Claude Code | [CLI reference](https://code.claude.com/docs/en/cli-reference) | Sintaxis de terminal. |
| Claude Code | [Sub-agents](https://code.claude.com/docs/en/sub-agents) | Delegación y contextos especializados. |
| Claude Code | [Hooks](https://code.claude.com/docs/en/hooks) | Eventos y controles programables. |
| Claude Code | [Skills](https://code.claude.com/docs/en/skills) | Procedimientos y capacidades reutilizables. |
| Claude Code | [MCP integration](https://code.claude.com/docs/en/mcp) | Conexión de servidores. |
| MCP | [Especificación](https://modelcontextprotocol.io/specification) | Revisiones, mecanismos y compatibilidad. |
| MCP | [Protocol versions (SDK)](https://ruby.sdk.modelcontextprotocol.io/protocol-versions/) | Diferencias entre generaciones del protocolo. |
| MCP | [Especificación y cambios](https://modelcontextprotocol.io/specification/draft/changelog) | Modificaciones de protocolo en revisión. |

**Compatibilidad:** los contratos y las opciones pueden diferir entre versiones de Claude, Claude Code y MCP. Para implementar código productivo, contrasta siempre la documentación correspondiente a la versión instalada y valida el comportamiento con pruebas.
