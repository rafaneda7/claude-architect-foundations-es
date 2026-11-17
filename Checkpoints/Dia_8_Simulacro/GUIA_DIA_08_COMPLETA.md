# GUÍA COMPLETA — DÍA 8, SIMULACRO INTEGRADOR

**Día 8 — Claude Certified Architect – Foundations (CCAR-F)**  
**Duración:** 120 minutos · **Formato:** 60 preguntas, opción única · **Escenarios:** 4 × 15  
**Uso:** simulacro original no oficial; las respuestas correctas no permiten deducir la puntuación escalada de Anthropic.

## Plan de cuatro horas

| Etapa | Duración | Objetivo |
|---|---:|---|
| Preparación y lectura de escenarios | 15 min | Identificar restricciones del caso |
| Examen cerrado de 60 preguntas | 120 min | Simular el ritmo del examen |
| Corrección automática y análisis por dominio | 35 min | Encontrar fallos de criterio |
| Casos arquitectónicos y laboratorio offline | 50 min | Justificar decisiones y verificar controles |
| **Total** | **240 min** | **Cierre del plan de 8 días** |

## Estrategia durante el examen

**En cada pregunta:** identifica quién tiene autoridad, qué está probado, qué puede fallar y cuál alternativa impone un control verificable. Las opciones incorrectas suelen sonar razonables porque proponen solo prompts donde se requieren controles, pierden la procedencia de los datos o confunden `end_turn` con éxito de negocio.

**Preguntas de alta incertidumbre:** marca tu confianza en la hoja de respuestas; no uses un segundo modelo durante el simulacro. El criterio es medir tus decisiones, no la capacidad de buscar respuestas.

## Distribución

| Dominio | Preguntas | Peso oficial aproximado |
|---|---:|---:|
| D1 — Agentic Architecture & Orchestration | 16 | 27 % |
| D2 — Tool Design & MCP Integration | 11 | 18 % |
| D3 — Claude Code Configuration & Workflows | 12 | 20 % |
| D4 — Prompt Engineering & Structured Output | 12 | 20 % |
| D5 — Context Management & Reliability | 9 | 15 % |

---

# EXAMEN FINAL — SIN RESPUESTAS

**Día 8 — Claude Certified Architect – Foundations (CCAR-F)**  
**Duración:** 120 minutos · **Formato:** 60 preguntas, opción única · **Escenarios:** 4 × 15  
**Uso:** simulacro original no oficial; las respuestas correctas no permiten deducir la puntuación escalada de Anthropic.

## Instrucciones

- Trabaja sin consultar el solucionario ni la documentación.
- Selecciona **una opción** A, B, C o D por pregunta.
- No asumas que `end_turn` implica completar una operación de negocio.
- Cada pregunta vale un punto en esta evaluación didáctica.
- Puedes corregir el resultado con `python corrector_dia8.py respuestas.json`.

## Escenario 1 — Agente de soporte y devoluciones

Una tienda opera un agente de soporte con Claude Agent SDK y herramientas MCP: `get_customer`, `lookup_order`, `get_policy`, `process_refund`, `escalate_to_human`. Debe resolver incidencias de devoluciones y facturación. Los reembolsos por encima de 500 EUR necesitan aprobación humana; el pedido debe pertenecer al cliente verificado. A veces hay varios perfiles con el mismo nombre. Un usuario puede plantear varias incidencias en la misma conversación. El sistema debe conservar importes, fechas, estados y resultados de herramientas.

### Pregunta 1 · D1

**El agente llama a process_refund sin haber ejecutado get_customer. ¿Qué control evita devoluciones a la cuenta equivocada?**

- **A.** Reforzar el system prompt.
- **B.** Aumentar max_tokens.
- **C.** Bloquear programáticamente process_refund hasta verificar identidad y pedido.
- **D.** Eliminar todas las herramientas de lectura.

**Tu respuesta:** _____

### Pregunta 2 · D1

**Una clienta reclama un cargo duplicado y una devolución pendiente a la vez. ¿Cuál es el mejor diseño inicial?**

- **A.** Separar asuntos, reunir el contexto autorizado común y resolver cada uno con su estado.
- **B.** Forzar una sola herramienta para ambos.
- **C.** Ignorar el cargo duplicado y resolver primero la devolución.
- **D.** Crear una única nota sin identificadores de incidencia.

**Tu respuesta:** _____

### Pregunta 3 · D1

**Después de un tool_result que informa acceso denegado, Claude devuelve end_turn con una explicación. ¿Qué está realmente completado?**

- **A.** La operación de devolución.
- **B.** La verificación del pedido.
- **C.** Todos los requisitos de negocio.
- **D.** Solo el turno normal del modelo, no la acción denegada.

**Tu respuesta:** _____

### Pregunta 4 · D1

**Dos consultas de solo lectura independientes pueden ejecutarse sin cambiar estados. ¿Qué optimización tiene sentido?**

- **A.** Omitir uno de los tool_result.
- **B.** Ejecutarlas en paralelo y devolver un resultado por cada ID.
- **C.** Compartir el mismo tool_use_id.
- **D.** Publicar una respuesta antes de recibir resultados.

**Tu respuesta:** _____

### Pregunta 5 · D1

**La política exige aprobación humana para devoluciones superiores a 500 EUR. ¿Dónde debe imponerse?**

- **A.** En una validación de ejecución previa a process_refund.
- **B.** Solo en ejemplos few-shot.
- **C.** En una instrucción informal de la descripción.
- **D.** En el frontend, sin comprobación del servidor.

**Tu respuesta:** _____

### Pregunta 6 · D1

**El agente decide entre consultar pedido o revisar política según los hallazgos previos. ¿Qué lo distingue de un workflow fijo?**

- **A.** Siempre usa dos modelos.
- **B.** No tiene backend.
- **C.** El siguiente paso lo elige dinámicamente el modelo dentro de los límites.
- **D.** La ejecución es completamente aleatoria.

**Tu respuesta:** _____

### Pregunta 7 · D1

**Un cliente solicita explícitamente hablar con una persona. ¿Cuál es la actuación adecuada?**

- **A.** Insistir en resolver automáticamente tres veces.
- **B.** Escalar a atención humana sin condicionar la solicitud a la confianza del modelo.
- **C.** Ignorar la solicitud si el caso parece fácil.
- **D.** Solicitar una calificación de sentimiento.

**Tu respuesta:** _____

### Pregunta 8 · D1

**Un caso se escala y el agente humano no tiene acceso al chat completo. ¿Qué transferencia es mejor?**

- **A.** Únicamente “caso complicado”.
- **B.** Un resumen sin importes ni IDs.
- **C.** Los 400 mensajes sin filtrar.
- **D.** Expediente con identidad verificada, incidencias, importes, acciones, errores, fuentes y siguiente paso.

**Tu respuesta:** _____

### Pregunta 9 · D2

**Hay dos herramientas “get_data” y “lookup_info” con descripciones idénticas. ¿Qué cambio mejora la selección?**

- **A.** Aumentar temperatura.
- **B.** Nombres, límites y ejemplos de uso claramente diferenciados.
- **C.** Devolver siempre texto libre.
- **D.** Añadir otras 15 herramientas.

**Tu respuesta:** _____

### Pregunta 10 · D2

**lookup_order devuelve “timeout temporal”. ¿Cuál es el contrato de error más útil?**

- **A.** Una lista vacía.
- **B.** “Error” sin detalles.
- **C.** Éxito con orden desconocida.
- **D.** isError con categoría transient, causa y isRetryable=true.

**Tu respuesta:** _____

### Pregunta 11 · D2

**Una búsqueda válida no encuentra el pedido solicitado. ¿Cómo debe comunicarse?**

- **A.** Éxito con resultados vacíos, no un fallo de acceso.
- **B.** isError=true y PERMISSION_DENIED.
- **C.** Una orden ficticia.
- **D.** Timeout forzado.

**Tu respuesta:** _____

### Pregunta 12 · D2

**El agente de soporte necesita consultar pedidos, pero no modificar las políticas comerciales. ¿Qué diseño es mejor?**

- **A.** Dar todas las herramientas disponibles.
- **B.** Exponer process_refund a cualquier usuario.
- **C.** Ofrecer únicamente herramientas necesarias y validar permisos en backend.
- **D.** Confiar en que el modelo no descubra herramientas administrativas.

**Tu respuesta:** _____

### Pregunta 13 · D5

**Tras resumir la conversación, se pierde el importe exacto de la devolución. ¿Qué arquitectura evita la pérdida?**

- **A.** Enviar solo la última frase.
- **B.** Guardar importes, fechas e IDs en un registro estructurado de hechos del caso.
- **C.** Aumentar la temperatura.
- **D.** Eliminar todas las incidencias antiguas.

**Tu respuesta:** _____

### Pregunta 14 · D5

**get_customer devuelve dos clientes con el mismo nombre. ¿Qué debe hacer el agente?**

- **A.** Elegir el primer resultado.
- **B.** Seleccionar el de la compra más alta.
- **C.** Suponer que ambos son la misma persona.
- **D.** Solicitar un identificador adicional y verificarlo antes de operar.

**Tu respuesta:** _____

### Pregunta 15 · D5

**Se produce timeout al procesar un reembolso. ¿Cuál es el siguiente paso seguro?**

- **A.** Comprobar estado mediante identificador idempotente antes de repetir.
- **B.** Repetir de inmediato sin controles.
- **C.** Declarar reembolso cancelado.
- **D.** Ocultar el error y devolver éxito.

**Tu respuesta:** _____

## Escenario 2 — Claude Code en un repositorio y su CI

Un equipo de Python usa Claude Code para cambios, refactorizaciones, revisión de pull requests y generación de pruebas. Comparte reglas por Git, utiliza `.claude/rules/`, skills, subagentes, hooks y configuraciones de permisos. Sus PR necesitan pruebas deterministas y revisiones de calidad con hallazgos estructurados. Las personas del equipo tienen ajustes individuales y hay riesgo de falsos positivos en algunas categorías de revisión.

### Pregunta 16 · D3

**Un miembro nuevo no recibe las convenciones que otra persona guarda en ~/.claude/CLAUDE.md. ¿Dónde mover las reglas comunes?**

- **A.** Al fichero personal del nuevo usuario.
- **B.** A .env.
- **C.** A un CLAUDE.md versionado a nivel de proyecto.
- **D.** A un mensaje ad hoc cada día.

**Tu respuesta:** _____

### Pregunta 17 · D3

**Los tests Python están repartidos por varios directorios y necesitan reglas especiales. ¿Qué opción es más adecuada?**

- **A.** Reglas con frontmatter paths en .claude/rules/.
- **B.** Un CLAUDE.md enorme y sin filtros.
- **C.** Guardar las reglas en __pycache__.
- **D.** Borrar los tests.

**Tu respuesta:** _____

### Pregunta 18 · D3

**Se va a migrar una librería afectando 40 archivos y existen dos estrategias de refactorización plausibles. ¿Qué modo conviene primero?**

- **A.** Directo sin revisión.
- **B.** Escritura masiva antes de inspeccionar.
- **C.** Solo /compact.
- **D.** Plan Mode para explorar y comparar alternativas antes de ejecutar.

**Tu respuesta:** _____

### Pregunta 19 · D3

**Una revisión de repositorio genera mucho contexto exploratorio y no debe saturar la sesión principal. ¿Qué patrón utilizar?**

- **A.** Insertar todos los archivos en CLAUDE.md.
- **B.** Una skill con context: fork o un subagente de exploración.
- **C.** Borrar los logs originales.
- **D.** Aumentar indefinidamente el historial principal.

**Tu respuesta:** _____

### Pregunta 20 · D3

**El equipo quiere compartir un comando repetible para revisión de PR. ¿Dónde guardarlo?**

- **A.** En ~/.claude/commands/ de una persona.
- **B.** En un chat privado.
- **C.** En .claude/commands/ versionado.
- **D.** Dentro de secrets.json.

**Tu respuesta:** _____

### Pregunta 21 · D3

**¿Qué opción permite invocar Claude Code desde una pipeline sin esperar preguntas interactivas?**

- **A.** claude -p con instrucciones y salida controlada.
- **B.** claude --continue sin prompt.
- **C.** Abrir siempre la interfaz interactiva.
- **D.** Usar exclusivamente una sesión humana existente.

**Tu respuesta:** _____

### Pregunta 22 · D3

**Quieres publicar hallazgos de PR como objetos estructurados para otro sistema. ¿Qué estrategia es más sólida?**

- **A.** Extraer viñetas con regex frágil.
- **B.** Pedir “hazlo claro” y confiar.
- **C.** Convertir comentarios a JSON por recorte manual.
- **D.** Usar salida JSON/schema de CLI y validación posterior.

**Tu respuesta:** _____

### Pregunta 23 · D3

**Claude generó código y debe revisarse críticamente antes del merge. ¿Qué reduce sesgo de contexto?**

- **A.** Pedirle “revísate mejor” en el mismo hilo.
- **B.** Iniciar una revisión independiente sin el historial interno de generación.
- **C.** Omitir pruebas porque revisa un LLM.
- **D.** Dar acceso ilimitado al agente.

**Tu respuesta:** _____

### Pregunta 24 · D3

**Debes impedir programáticamente que Write modifique .env. ¿Qué control encaja mejor?**

- **A.** Añadir “por favor” al prompt.
- **B.** Ocultar .env en README.
- **C.** Hook PreToolUse y permisos del entorno que denieguen el cambio.
- **D.** Utilizar una temperature más baja.

**Tu respuesta:** _____

### Pregunta 25 · D3

**Edit falla porque el texto objetivo no es único. ¿Qué procedimiento es razonable?**

- **A.** Leer el archivo, seleccionar un ancla única o realizar sustitución controlada y probar.
- **B.** Repetir Edit sin cambios veinte veces.
- **C.** Eliminar el archivo para crearlo vacío.
- **D.** Aceptar un diff incorrecto.

**Tu respuesta:** _____

### Pregunta 26 · D4

**Una revisión reporta cientos de comentarios de estilo como errores críticos. ¿Cómo reducir falsos positivos?**

- **A.** Exigir “más confianza” sin criterios.
- **B.** Incluir cada comentario en el informe.
- **C.** Dejar que cada agente invente severidades.
- **D.** Definir categorías reportables y exclusiones verificables, con ejemplos.

**Tu respuesta:** _____

### Pregunta 27 · D4

**¿Qué selección de ejemplos few-shot ayuda a distinguir un bug real de una convención aceptable?**

- **A.** Solo bugs obvios.
- **B.** Ejemplos positivos, negativos y ambiguos con justificación.
- **C.** Un ejemplo irrelevante.
- **D.** Ninguno porque hay un JSON Schema.

**Tu respuesta:** _____

### Pregunta 28 · D4

**Un hallazgo “crítico” por una variable mal nombrada erosiona la confianza. ¿Qué debe cambiar?**

- **A.** Fijar niveles de severidad por impacto demostrado y excluir estilo menor.
- **B.** Eliminar logs.
- **C.** Cambiar el nombre de la categoría a “confianza”.
- **D.** Aumentar max_tokens.

**Tu respuesta:** _____

### Pregunta 29 · D4

**¿Para qué sirve detected_pattern en hallazgos estructurados?**

- **A.** Determinar la API Key del autor.
- **B.** Ordenar fechas del repositorio.
- **C.** Analizar qué patrones generan falsos positivos y corregir el evaluador.
- **D.** Reemplazar el identificador de línea.

**Tu respuesta:** _____

### Pregunta 30 · D5

**Reanudas una sesión de Claude Code tras cambiar muchos archivos desde fuera. ¿Cómo evitar basarte en información obsoleta?**

- **A.** Confiar en análisis anterior sin comprobar.
- **B.** Reiniciar el ordenador.
- **C.** Borrar los tests.
- **D.** Informar de los cambios y verificar archivos afectados, o iniciar contexto nuevo resumido.

**Tu respuesta:** _____

## Escenario 3 — Investigación multiagente con evidencias

Una plataforma investiga informes técnicos. Un coordinador delega en agentes de búsqueda, análisis documental, verificación y síntesis. Los subagentes tienen contextos aislados, costes limitados y acceso a herramientas distintas. Deben producir informes con procedencia de cada dato, fechas, limitaciones y tratamiento de fuentes contradictorias. Algunas fuentes no están accesibles temporalmente y el coordinador debe decidir cómo continuar.

### Pregunta 31 · D1

**El coordinador intenta generar subagentes con Claude Agent SDK, pero no aparece la herramienta Task. ¿Qué revisar?**

- **A.** Que allowedTools incluya Task y existan definiciones accesibles.
- **B.** Que max_tokens sea cero.
- **C.** Que el prompt incluya la palabra “equipo”.
- **D.** Que todos los agentes compartan historial automáticamente.

**Tu respuesta:** _____

### Pregunta 32 · D1

**Un subagente recibe “resume lo anterior”, pero no obtiene los hallazgos previos. ¿Por qué?**

- **A.** Porque MCP prohíbe documentación.
- **B.** Porque tool_result no admite texto.
- **C.** Porque su contexto está aislado y necesita los datos explícitos.
- **D.** Porque las fuentes externas se comparten automáticamente.

**Tu respuesta:** _____

### Pregunta 33 · D1

**La investigación tiene tres temas sin solapamiento. ¿Qué estrategia minimiza trabajo repetido?**

- **A.** Todos los subagentes investigan exactamente lo mismo.
- **B.** Asignar subtemas distintos y reunir resultados en el coordinador.
- **C.** Crear un único resumen antes de investigar.
- **D.** Eliminar los IDs de fuente.

**Tu respuesta:** _____

### Pregunta 34 · D1

**Dos subagentes independientes pueden comenzar a la vez. ¿Qué patrón de invocación es apropiado?**

- **A.** Invocar uno por turno aunque no exista dependencia.
- **B.** Compartir credenciales en sus prompts.
- **C.** Pedir a uno que finja el resultado del otro.
- **D.** Emitir varias invocaciones Task en un mismo turno, si el SDK lo admite.

**Tu respuesta:** _____

### Pregunta 35 · D1

**Los investigadores producen hallazgos, pero el sintetizador no sabe de qué fuente procede cada cifra. ¿Qué debe hacer el coordinador?**

- **A.** Transmitir hallazgos con metadatos de procedencia y citas.
- **B.** Eliminar nombres de documentos.
- **C.** Pedir una conclusión sin fuentes.
- **D.** Reemplazar fuentes por confianza autorreportada.

**Tu respuesta:** _____

### Pregunta 36 · D1

**La síntesis revela que falta un tema importante. ¿Cuál es la mejor continuación?**

- **A.** Publicar informe con una afirmación inventada.
- **B.** Repetir siempre toda la investigación.
- **C.** Re-delegar una consulta específica para cubrir la laguna y después reevaluar.
- **D.** Declarar completo por haber invocado todos los agentes.

**Tu respuesta:** _____

### Pregunta 37 · D1

**¿Cuándo elegirías descomposición dinámica en lugar de prompt chaining fijo?**

- **A.** Al convertir siempre un CSV con tres pasos conocidos.
- **B.** Cuando el siguiente subproblema depende de lo descubierto en la investigación.
- **C.** Al ejecutar un test unitario conocido.
- **D.** Cuando el número de archivos es uno.

**Tu respuesta:** _____

### Pregunta 38 · D1

**Dos enfoques de investigación deben explorarse desde un mismo análisis inicial sin contaminarse. ¿Qué técnica encaja?**

- **A.** Reanudar un solo hilo y sobrescribir resultados.
- **B.** Copiar el mismo tool_use_id.
- **C.** Usar una sola respuesta final sin ramas.
- **D.** Crear forks de sesión independientes desde una base común.

**Tu respuesta:** _____

### Pregunta 39 · D2

**El sintetizador tiene 18 herramientas disponibles aunque solo necesita leer evidencias y verificar hechos. ¿Qué harías?**

- **A.** Reducirlas a las necesarias para su especialidad.
- **B.** Dar todas para maximizar flexibilidad.
- **C.** Renombrarlas a letras.
- **D.** Impedir siempre todo tool_use.

**Tu respuesta:** _____

### Pregunta 40 · D2

**Los analistas desconocen qué documentos existen. ¿Cómo puede ayudar un servidor MCP?**

- **A.** Exponiendo credenciales en prompts.
- **B.** Añadiendo falsos resultados.
- **C.** Ofreciendo un catálogo de recursos con URIs y descripciones.
- **D.** Exigiendo leer todo el repositorio cada vez.

**Tu respuesta:** _____

### Pregunta 41 · D2

**El equipo quiere compartir un servidor MCP para todo el repositorio. ¿Cuál es la ubicación adecuada?**

- **A.** ~/.claude.json de una sola persona.
- **B.** Un .mcp.json versionado con variables de entorno para secretos.
- **C.** La carpeta .venv/site-packages.
- **D.** El cuerpo de cada prompt.

**Tu respuesta:** _____

### Pregunta 42 · D2

**Una búsqueda falló dos veces por timeout pero tiene hallazgos parciales. ¿Qué debe devolver el subagente al coordinador?**

- **A.** Una lista vacía como si hubiera éxito.
- **B.** Solo “no disponible”.
- **C.** Una conclusión definitiva inventada.
- **D.** Tipo de fallo, intentos, parciales, fuentes y alternativas de recuperación.

**Tu respuesta:** _____

### Pregunta 43 · D5

**Dos fuentes fiables ofrecen cifras diferentes para un indicador. ¿Qué debe hacer la síntesis?**

- **A.** Seleccionar la mayor por intuición.
- **B.** Promediar sin conocer metodologías.
- **C.** Mostrar ambas con fuentes y metodologías, anotando la discrepancia.
- **D.** Descartar una sin explicación.

**Tu respuesta:** _____

### Pregunta 44 · D5

**Un informe de 2024 y otro de 2026 tienen porcentajes distintos sobre la misma métrica. ¿Qué metadato resulta esencial?**

- **A.** Fecha de publicación o recogida de datos de cada fuente.
- **B.** Color de la portada.
- **C.** Longitud del PDF.
- **D.** Nombre del agente que escribió el resumen.

**Tu respuesta:** _____

### Pregunta 45 · D5

**Un subagente falla al descargar un documento, pero otro aporta evidencias válidas. ¿Qué debe hacer el coordinador?**

- **A.** Detener todo el sistema en cualquier fallo.
- **B.** Publicar el informe como completo sin mencionar límites.
- **C.** Eliminar la fuente fallida del registro.
- **D.** Continuar con cobertura parcial explícita y el error estructurado; recuperar si es viable.

**Tu respuesta:** _____

## Escenario 4 — Extracción documental estructurada y fiabilidad

Una empresa procesa facturas, tickets y contratos con Claude. Necesita salidas JSON con tipos y campos consistentes, totales verificados, valores ausentes explícitos y evidencias ligadas a los documentos. Un pipeline nocturno procesa cientos de archivos; otro flujo bloquea merges o aprobaciones de alto impacto en tiempo real. También utiliza un servidor MCP y herramientas de Claude Code. Los validadores locales deben detectar incongruencias sin depender de que el modelo se autoevalúe.

### Pregunta 46 · D2

**El servicio documental expone “consultar factura” y “actualizar factura”. ¿Qué diseño de MCP minimiza riesgos?**

- **A.** Una única herramienta genérica con acceso total.
- **B.** Separar lectura/escritura, describir límites y autorizar cada operación.
- **C.** Permitir actualizaciones por el texto del usuario.
- **D.** No validar documentos por seguridad.

**Tu respuesta:** _____

### Pregunta 47 · D2

**La aplicación exige ejecutar primero extract_metadata y después interpretar el resultado. En un modelo compatible, ¿qué usarías en la primera llamada?**

- **A.** tool_choice={"type":"tool","name":"extract_metadata"}, luego permitir continuación.
- **B.** tool_choice={"type":"none"} en todas las vueltas.
- **C.** Aumentar la temperatura.
- **D.** Forzar siempre esa herramienta en todas las vueltas.

**Tu respuesta:** _____

### Pregunta 48 · D2

**Claude Code debe localizar todos los archivos .py que incluyen "parse_invoice". ¿Cuál es el orden eficiente?**

- **A.** Write y después Bash sin inspección.
- **B.** Solo Read de cada archivo del repositorio.
- **C.** Solo editar archivos por nombre supuesto.
- **D.** Glob para localizar rutas, Grep para contenido y Read de coincidencias.

**Tu respuesta:** _____

### Pregunta 49 · D3

**Un conjunto de reglas de parsing se aplica solo a *.py en src y tests. ¿Dónde expresarlo?**

- **A.** Un prompt informal en el chat.
- **B.** En un token del MCP.
- **C.** Un archivo en .claude/rules/ con patterns paths correspondientes.
- **D.** En un documento PDF externo que no se carga.

**Tu respuesta:** _____

### Pregunta 50 · D3

**Tras un nuevo commit, el revisor CI vuelve a comentar defectos corregidos en la versión anterior. ¿Qué mejora es adecuada?**

- **A.** Ignorar todas las revisiones.
- **B.** Proporcionar hallazgos previos y pedir solo problemas nuevos o aún vigentes.
- **C.** Reescribir todo el repositorio.
- **D.** Repetir exactamente la revisión sin contexto del cambio.

**Tu respuesta:** _____

### Pregunta 51 · D4

**¿Cómo se solicita hoy una respuesta JSON restringida con raw schema en Messages API?**

- **A.** output_config={"format":{"type":"json_schema","schema":...}}.
- **B.** Unicamente “devuelve JSON” en system.
- **C.** max_tokens=0.
- **D.** Un campo required fuera del esquema.

**Tu respuesta:** _____

### Pregunta 52 · D4

**Un JSON pasa el esquema, pero cantidad 2 × precio 3.5 no coincide con un total extraído de 9. ¿Qué falla?**

- **A.** La sintaxis JSON.
- **B.** El nombre de la herramienta.
- **C.** La autenticación.
- **D.** La coherencia semántica de los datos.

**Tu respuesta:** _____

### Pregunta 53 · D4

**El documento omite un total declarado. ¿Qué diseño reduce invenciones?**

- **A.** Obligar un número positivo siempre.
- **B.** Admitir null y ordenar no inventar valores ausentes.
- **C.** Copiar el primer precio como total.
- **D.** Estimar el total sin dejar constancia.

**Tu respuesta:** _____

### Pregunta 54 · D4

**¿Qué restricción no admite actualmente el subconjunto de Structured Outputs de Anthropic?**

- **A.** enum.
- **B.** required.
- **C.** minimum/maximum numéricos.
- **D.** additionalProperties:false.

**Tu respuesta:** _____

### Pregunta 55 · D4

**Una extracción tiene un total contradictorio con la fuente. ¿Qué reintento es más útil?**

- **A.** Entregar documento, extracción previa y error concreto para corregirlo.
- **B.** Repetir “inténtalo” sin detalles.
- **C.** Inventar un total distinto.
- **D.** Reintentar indefinidamente sin límite.

**Tu respuesta:** _____

### Pregunta 56 · D4

**El número de pedido no figura en ninguno de los documentos aportados. ¿Qué actuación es correcta?**

- **A.** Forzar cinco reintentos para obtenerlo.
- **B.** Usar el ID de otro expediente.
- **C.** Asumir que es el mismo del ejemplo few-shot.
- **D.** Representar la ausencia y solicitar fuente adicional si se necesita.

**Tu respuesta:** _____

### Pregunta 57 · D4

**Se quieren procesar 800 facturas durante la noche y correlacionar fallos por archivo. ¿Qué opción encaja?**

- **A.** Una llamada sin IDs de documentos.
- **B.** Message Batches con custom_id y tratamiento de resultados fallidos.
- **C.** Un workflow que bloquea cada aprobación durante 24h.
- **D.** Un único prompt con los 800 documentos sin comprobar límites.

**Tu respuesta:** _____

### Pregunta 58 · D4

**Un extractor registra “total_declarado” y “total_calculado”. ¿Qué comprobación mejora fiabilidad?**

- **A.** Suprimir uno de los campos.
- **B.** Convertir ambos a texto sin analizar.
- **C.** Verificar diferencia, impuestos/descuentos aplicables y evidencias antes de aceptar.
- **D.** Confiar si el JSON está bien formateado.

**Tu respuesta:** _____

### Pregunta 59 · D5

**El extractor muestra precisión agregada del 97 %, pero falla en facturas manuscritas. ¿Cómo medirlo?**

- **A.** Evaluar resultados por tipo de documento y campo, con muestras estratificadas.
- **B.** Publicar que alcanza 97 % en todos los segmentos.
- **C.** Ignorar el segmento pequeño.
- **D.** Pedir más confianza al modelo.

**Tu respuesta:** _____

### Pregunta 60 · D5

**Una síntesis toma afirmaciones de tres documentos y elimina la referencia a cuál las sustentó. ¿Qué control falta?**

- **A.** Aumentar max_tokens sin límites.
- **B.** Resumir más intensamente.
- **C.** Ordenar por longitud del documento.
- **D.** Mantener pares afirmación-fuente, ubicación y fecha durante cada transformación.

**Tu respuesta:** _____


---

## Práctica final de arquitectura — cuatro escenarios explicados

### Caso A — Reembolso de alto impacto

**Reto:** El cliente tiene dos reclamaciones; `get_customer` devuelve dos candidatos; Claude pide `process_refund(650)` y después `end_turn`.

**Respuesta razonada:** Mantener las reclamaciones separadas; pedir datos adicionales para identificar al cliente; bloquear el reembolso hasta verificar identidad, pertenencia del pedido y aprobación por superar 500 EUR; devolver error estructurado por las herramientas denegadas; enviar el caso con identificadores, importe, evidencias y siguientes pasos a una persona si corresponde. `end_turn` no significa que el reembolso haya sucedido.

### Caso B — PR de Python con falsos positivos

**Reto:** Una revisión de CI devuelve 60 avisos de estilo y 2 errores funcionales. Hay una migración de 40 archivos pendiente.

**Respuesta razonada:** Definir criterios explícitos de reporte de errores funcionales y seguridad, desactivar temporalmente categorías de falsos positivos, validar tests con Python, dividir revisión local y transversal, usar Plan Mode antes de la migración, aplicar reglas de proyecto en `CLAUDE.md`/`.claude/rules`, ejecutar revisión independiente y recopilar hallazgos en formato estructurado con evidencia.

### Caso C — Agentes investigadores y datos contradictorios

**Reto:** Dos fuentes fiables ofrecen cifras diferentes; el analista documental dejó de responder y la síntesis perdió las citas originales.

**Respuesta razonada:** Requerir pares afirmación-fuente con fechas y métodos; mantener los dos valores cuando no se puedan reconciliar; propagar el error y hallazgos parciales del agente fallido; realizar reintentos limitados y re-delegación dirigida; presentar explícitamente la cobertura incompleta en el informe final.

### Caso D — Extracción de facturas

**Reto:** Un documento declara TOTAL 7,00 EUR, pero la salida JSON válida contiene 8,00; otros documentos carecen de total; el equipo quiere ejecutar un lote nocturno.

**Respuesta razonada:** Especificar `output_config.format` con esquema compatible; separar `total_declarado` nullable de `total_calculado`; validar evidencias y totales en backend, contemplando descuentos/impuestos; reintentar el caso corregible con feedback concreto, no inventar totales ausentes; procesar documentos independientes mediante Message Batches usando `custom_id`; revisar resultados por segmento y campo, no solo precisión global.

---

## Laboratorio offline — validador de decisiones arquitectónicas

El laboratorio `motor_dia8.py` no necesita una API Key ni consume saldo. Su objetivo es verificar condiciones que **no deberían depender solo de un prompt**.

1. Autoriza la consulta de casos por usuario y marca la denegación explícitamente.
2. Bloquea reembolsos sin cliente verificado, pertenencia de pedido o aprobación necesaria.
3. Valida `tool_result` y sus IDs sin convertir errores en éxitos vacíos.
4. Extrae datos de facturas, preservando `None` si el total no fue declarado.
5. Rechaza un JSON aparentemente correcto cuando los totales son inconsistentes.

Ejecuta:

```bash
python -m unittest discover -s tests -v
python demo_dia8.py
python corrector_dia8.py respuestas.json
```

En esta jornada **no es necesario utilizar tus 5 USD de saldo de Anthropic** para demostrar lo aprendido. La capacidad de diseñar y comprobar controles deterministas es parte esencial del examen.

---

## Cómo interpretar la nota

La evaluación didáctica usa **1 punto por pregunta**, con desglose por dominio. La guía oficial indica puntuación escalada **100–1000** y aprobado a partir de **720**; **no se puede convertir legítimamente un porcentaje de esta prueba en una nota oficial**.

### Umbrales de repaso recomendados (no oficiales)

| Resultado | Recomendación |
|---|---|
| 54–60 aciertos | Consolidación: repasar fallos y casos frontera |
| 48–53 aciertos | Refuerzo dirigido de dominios con peores porcentajes |
| 42–47 aciertos | Repaso de D1/D2/D3/D4/D5 según la matriz de errores |
| 0–41 aciertos | Rehacer prácticas por dominio antes de repetir el simulacro |

**No basta con una nota global alta**: si D1 tiene 14/16 y D2 solo 4/11, el siguiente repaso debe priorizar D2. Repite las preguntas falladas después de revisar el concepto, con un intervalo temporal en lugar de memorizar la letra.

### Cierre de la preparación

- [ ] He terminado las 60 preguntas en máximo 120 minutos, sin ayudas.
- [ ] He registrado respuestas y nivel de confianza.
- [ ] He corregido por dominio.
- [ ] Puedo explicar cada error sin mirar el solucionario.
- [ ] He resuelto los cuatro casos arquitectónicos.
- [ ] He ejecutado el laboratorio offline y las pruebas.
- [ ] He comprobado las prácticas que requerían API durante los días anteriores.
- [ ] He definido un plan realista de repaso.

---

# SOLUCIONARIO DEL SIMULACRO FINAL

**Día 8 — Claude Certified Architect – Foundations (CCAR-F)**  
**Duración:** 120 minutos · **Formato:** 60 preguntas, opción única · **Escenarios:** 4 × 15  
**Uso:** simulacro original no oficial; las respuestas correctas no permiten deducir la puntuación escalada de Anthropic.

**Importante:** el solucionario incluye explicación y confusión frecuente. No equivale a las respuestas del examen oficial.

## Escenario 1 — Agente de soporte y devoluciones

### Pregunta 1 · D1 — C

**El agente llama a process_refund sin haber ejecutado get_customer. ¿Qué control evita devoluciones a la cuenta equivocada?**

**Justificación:** La identidad y la pertenencia del pedido son prerrequisitos ejecutados por el backend, no simples instrucciones.

**Confusión que debes evitar:** La obediencia al prompt no ofrece una garantía de autorización.

### Pregunta 2 · D1 — A

**Una clienta reclama un cargo duplicado y una devolución pendiente a la vez. ¿Cuál es el mejor diseño inicial?**

**Justificación:** Separar asuntos evita mezclar estados y permite una síntesis final de ambos resultados.

**Confusión que debes evitar:** Confundir una sola conversación con una sola incidencia.

### Pregunta 3 · D1 — D

**Después de un tool_result que informa acceso denegado, Claude devuelve end_turn con una explicación. ¿Qué está realmente completado?**

**Justificación:** end_turn describe el estado de generación, no la satisfacción de requisitos de negocio.

**Confusión que debes evitar:** Confundir stop_reason con estado del proceso de negocio.

### Pregunta 4 · D1 — B

**Dos consultas de solo lectura independientes pueden ejecutarse sin cambiar estados. ¿Qué optimización tiene sentido?**

**Justificación:** Las lecturas independientes pueden paralelizarse; hay que conservar la correspondencia individual de los resultados.

**Confusión que debes evitar:** Paralelizar no autoriza a fusionar identificadores ni a omitir errores.

### Pregunta 5 · D1 — A

**La política exige aprobación humana para devoluciones superiores a 500 EUR. ¿Dónde debe imponerse?**

**Justificación:** Las políticas obligatorias deben aplicarse mediante controles deterministas del servicio.

**Confusión que debes evitar:** Confundir orientación al modelo con cumplimiento obligatorio.

### Pregunta 6 · D1 — C

**El agente decide entre consultar pedido o revisar política según los hallazgos previos. ¿Qué lo distingue de un workflow fijo?**

**Justificación:** La selección adaptativa de herramientas es una característica central de la arquitectura agéntica.

**Confusión que debes evitar:** El número de herramientas no determina si existe un agente.

### Pregunta 7 · D1 — B

**Un cliente solicita explícitamente hablar con una persona. ¿Cuál es la actuación adecuada?**

**Justificación:** La petición explícita de atención humana activa el criterio de escalamiento.

**Confusión que debes evitar:** Reemplazar una preferencia explícita por una estimación del modelo.

### Pregunta 8 · D1 — D

**Un caso se escala y el agente humano no tiene acceso al chat completo. ¿Qué transferencia es mejor?**

**Justificación:** Un handoff estructurado permite continuar el trabajo con datos exactos y trazabilidad.

**Confusión que debes evitar:** La compresión no debe borrar hechos que guían acciones.

### Pregunta 9 · D2 — B

**Hay dos herramientas “get_data” y “lookup_info” con descripciones idénticas. ¿Qué cambio mejora la selección?**

**Justificación:** Las descripciones y contratos concretos reducen ambigüedades entre funciones similares.

**Confusión que debes evitar:** Más herramientas no mejora necesariamente la selección.

### Pregunta 10 · D2 — D

**lookup_order devuelve “timeout temporal”. ¿Cuál es el contrato de error más útil?**

**Justificación:** El error estructurado ayuda a planificar una recuperación limitada sin ocultar el fallo.

**Confusión que debes evitar:** Un error de acceso no es una consulta válida sin coincidencias.

### Pregunta 11 · D2 — A

**Una búsqueda válida no encuentra el pedido solicitado. ¿Cómo debe comunicarse?**

**Justificación:** Una operación ejecutada correctamente puede no encontrar registros.

**Confusión que debes evitar:** No confundir ausencia de resultados con error técnico.

### Pregunta 12 · D2 — C

**El agente de soporte necesita consultar pedidos, pero no modificar las políticas comerciales. ¿Qué diseño es mejor?**

**Justificación:** La separación de capacidades por rol reduce errores y superficie de ataque.

**Confusión que debes evitar:** Ocultar una herramienta no sustituye a comprobar permisos.

### Pregunta 13 · D5 — B

**Tras resumir la conversación, se pierde el importe exacto de la devolución. ¿Qué arquitectura evita la pérdida?**

**Justificación:** Los hechos transaccionales deben persistirse fuera del resumen narrativo.

**Confusión que debes evitar:** Un resumen no debe ser la fuente de verdad para importes.

### Pregunta 14 · D5 — D

**get_customer devuelve dos clientes con el mismo nombre. ¿Qué debe hacer el agente?**

**Justificación:** La ambigüedad de identidad exige aclaración, no selección heurística.

**Confusión que debes evitar:** Elegir por plausibilidad puede revelar o modificar cuentas ajenas.

### Pregunta 15 · D5 — A

**Se produce timeout al procesar un reembolso. ¿Cuál es el siguiente paso seguro?**

**Justificación:** La operación puede haber ocurrido aunque se perdiera la respuesta; se requiere reconciliación.

**Confusión que debes evitar:** Timeout no significa que la transacción haya fallado.

## Escenario 2 — Claude Code en un repositorio y su CI

### Pregunta 16 · D3 — C

**Un miembro nuevo no recibe las convenciones que otra persona guarda en ~/.claude/CLAUDE.md. ¿Dónde mover las reglas comunes?**

**Justificación:** Las instrucciones de usuario no viajan con el repositorio; las de proyecto sí pueden versionarse.

**Confusión que debes evitar:** Confundir alcance de usuario con alcance de equipo.

### Pregunta 17 · D3 — A

**Los tests Python están repartidos por varios directorios y necesitan reglas especiales. ¿Qué opción es más adecuada?**

**Justificación:** Las reglas por patrones permiten aplicar convenciones a archivos dispersos.

**Confusión que debes evitar:** La ubicación en varios directorios no obliga a duplicar instrucciones.

### Pregunta 18 · D3 — D

**Se va a migrar una librería afectando 40 archivos y existen dos estrategias de refactorización plausibles. ¿Qué modo conviene primero?**

**Justificación:** Los cambios complejos justifican planificar y analizar dependencias antes de editar.

**Confusión que debes evitar:** No confundir velocidad inicial con coste total del cambio.

### Pregunta 19 · D3 — B

**Una revisión de repositorio genera mucho contexto exploratorio y no debe saturar la sesión principal. ¿Qué patrón utilizar?**

**Justificación:** La ejecución aislada conserva el resultado útil sin incorporar todo el proceso a la conversación principal.

**Confusión que debes evitar:** El aislamiento de contexto no significa ausencia de transferencia de resultados.

### Pregunta 20 · D3 — C

**El equipo quiere compartir un comando repetible para revisión de PR. ¿Dónde guardarlo?**

**Justificación:** Los comandos a nivel de proyecto pueden distribuirse con Git.

**Confusión que debes evitar:** Una ruta personal no garantiza disponibilidad al equipo.

### Pregunta 21 · D3 — A

**¿Qué opción permite invocar Claude Code desde una pipeline sin esperar preguntas interactivas?**

**Justificación:** El modo print/no interactivo está diseñado para automatizaciones y CI.

**Confusión que debes evitar:** En CI no debe dependerse de una sesión interactiva.

### Pregunta 22 · D3 — D

**Quieres publicar hallazgos de PR como objetos estructurados para otro sistema. ¿Qué estrategia es más sólida?**

**Justificación:** El esquema facilita el consumo automático; la validación semántica continúa siendo necesaria.

**Confusión que debes evitar:** Salida estructurada no verifica evidencias ni su relevancia.

### Pregunta 23 · D3 — B

**Claude generó código y debe revisarse críticamente antes del merge. ¿Qué reduce sesgo de contexto?**

**Justificación:** Un revisor independiente puede cuestionar supuestos del generador; no sustituye pruebas.

**Confusión que debes evitar:** Autorrevisión y revisión independiente no son equivalentes.

### Pregunta 24 · D3 — C

**Debes impedir programáticamente que Write modifique .env. ¿Qué control encaja mejor?**

**Justificación:** El hook puede interceptar la operación antes de ejecutarla; debe complementarse con permisos reales.

**Confusión que debes evitar:** Un hook limitado a Write no cubre necesariamente Bash.

### Pregunta 25 · D3 — A

**Edit falla porque el texto objetivo no es único. ¿Qué procedimiento es razonable?**

**Justificación:** Una modificación segura debe revisar contexto, asegurar la ubicación y verificar resultados.

**Confusión que debes evitar:** No siempre la primera herramienta elegida sirve para la modificación.

### Pregunta 26 · D4 — D

**Una revisión reporta cientos de comentarios de estilo como errores críticos. ¿Cómo reducir falsos positivos?**

**Justificación:** Las reglas explícitas y ejemplos frontera mejoran la precisión.

**Confusión que debes evitar:** Instrucciones vagas de confianza no reemplazan criterios.

### Pregunta 27 · D4 — B

**¿Qué selección de ejemplos few-shot ayuda a distinguir un bug real de una convención aceptable?**

**Justificación:** Los ejemplos frontera muestran qué no denunciar y cómo responder a casos nuevos.

**Confusión que debes evitar:** JSON Schema define formato, no criterio de hallazgo.

### Pregunta 28 · D4 — A

**Un hallazgo “crítico” por una variable mal nombrada erosiona la confianza. ¿Qué debe cambiar?**

**Justificación:** La gravedad debe depender de riesgos o fallos verificables.

**Confusión que debes evitar:** La severidad no es sinónimo de incomodidad estética.

### Pregunta 29 · D4 — C

**¿Para qué sirve detected_pattern en hallazgos estructurados?**

**Justificación:** Permite agrupar rechazos de revisores y mejorar categorías problemáticas.

**Confusión que debes evitar:** El problema no se resuelve simplemente con más texto.

### Pregunta 30 · D5 — D

**Reanudas una sesión de Claude Code tras cambiar muchos archivos desde fuera. ¿Cómo evitar basarte en información obsoleta?**

**Justificación:** Una sesión reanudada puede contener observaciones previas que ya no describen el repositorio.

**Confusión que debes evitar:** Persistencia de conversación no asegura frescura de evidencia.

## Escenario 3 — Investigación multiagente con evidencias

### Pregunta 31 · D1 — A

**El coordinador intenta generar subagentes con Claude Agent SDK, pero no aparece la herramienta Task. ¿Qué revisar?**

**Justificación:** El coordinador necesita permiso/herramienta Task para invocar subagentes en este patrón de Agent SDK.

**Confusión que debes evitar:** Una intención textual no habilita herramientas no permitidas.

### Pregunta 32 · D1 — C

**Un subagente recibe “resume lo anterior”, pero no obtiene los hallazgos previos. ¿Por qué?**

**Justificación:** La delegación debe incluir datos y criterios relevantes en el mensaje del subagente.

**Confusión que debes evitar:** Contexto del coordinador no es memoria compartida implícita.

### Pregunta 33 · D1 — B

**La investigación tiene tres temas sin solapamiento. ¿Qué estrategia minimiza trabajo repetido?**

**Justificación:** La partición por subtemas reduce duplicación y facilita cobertura y procedencia.

**Confusión que debes evitar:** Más agentes no implica mejor cobertura sin descomposición.

### Pregunta 34 · D1 — D

**Dos subagentes independientes pueden comenzar a la vez. ¿Qué patrón de invocación es apropiado?**

**Justificación:** Las tareas independientes se pueden delegar concurrentemente, preservando resultados aislados.

**Confusión que debes evitar:** Paralelización no significa perder coordinación.

### Pregunta 35 · D1 — A

**Los investigadores producen hallazgos, pero el sintetizador no sabe de qué fuente procede cada cifra. ¿Qué debe hacer el coordinador?**

**Justificación:** La transferencia estructurada de afirmación a fuente conserva atribución verificable.

**Confusión que debes evitar:** Resumir sin procedencia destruye capacidad de verificación.

### Pregunta 36 · D1 — C

**La síntesis revela que falta un tema importante. ¿Cuál es la mejor continuación?**

**Justificación:** El coordinador debe diagnosticar la laguna e iterar de forma dirigida.

**Confusión que debes evitar:** Cobertura no equivale al número de agentes usados.

### Pregunta 37 · D1 — B

**¿Cuándo elegirías descomposición dinámica en lugar de prompt chaining fijo?**

**Justificación:** La descomposición dinámica sirve para investigación abierta, con caminos impredecibles.

**Confusión que debes evitar:** La incertidumbre del trabajo importa más que el tamaño literal del archivo.

### Pregunta 38 · D1 — D

**Dos enfoques de investigación deben explorarse desde un mismo análisis inicial sin contaminarse. ¿Qué técnica encaja?**

**Justificación:** Las ramas permiten explorar alternativas desde un punto inicial sin mezclar su desarrollo.

**Confusión que debes evitar:** Reanudar y bifurcar no resuelven el mismo problema.

### Pregunta 39 · D2 — A

**El sintetizador tiene 18 herramientas disponibles aunque solo necesita leer evidencias y verificar hechos. ¿Qué harías?**

**Justificación:** Una selección acotada mejora fiabilidad y sigue el principio de mínimo privilegio.

**Confusión que debes evitar:** Más herramientas pueden empeorar el enrutamiento.

### Pregunta 40 · D2 — C

**Los analistas desconocen qué documentos existen. ¿Cómo puede ayudar un servidor MCP?**

**Justificación:** Los resources facilitan descubrimiento de contenido disponible antes de llamar a herramientas.

**Confusión que debes evitar:** No confundir resource de información con una acción de modificación.

### Pregunta 41 · D2 — B

**El equipo quiere compartir un servidor MCP para todo el repositorio. ¿Cuál es la ubicación adecuada?**

**Justificación:** El alcance de proyecto comparte configuración sin incluir tokens en el archivo.

**Confusión que debes evitar:** Compartir configuración no autoriza compartir credenciales.

### Pregunta 42 · D2 — D

**Una búsqueda falló dos veces por timeout pero tiene hallazgos parciales. ¿Qué debe devolver el subagente al coordinador?**

**Justificación:** Los errores estructurados permiten al coordinador recuperar y reportar cobertura parcial.

**Confusión que debes evitar:** Ocultar fallos convierte limitaciones reales en certezas falsas.

### Pregunta 43 · D5 — C

**Dos fuentes fiables ofrecen cifras diferentes para un indicador. ¿Qué debe hacer la síntesis?**

**Justificación:** Cuando las fuentes discrepan hay que conservar la incertidumbre y su procedencia.

**Confusión que debes evitar:** Fuentes aparentemente contradictorias pueden medir cosas distintas.

### Pregunta 44 · D5 — A

**Un informe de 2024 y otro de 2026 tienen porcentajes distintos sobre la misma métrica. ¿Qué metadato resulta esencial?**

**Justificación:** Sin contexto temporal no puede saberse si hay contradicción o cambio real.

**Confusión que debes evitar:** Los valores aislados de sus fechas pueden interpretarse mal.

### Pregunta 45 · D5 — D

**Un subagente falla al descargar un documento, pero otro aporta evidencias válidas. ¿Qué debe hacer el coordinador?**

**Justificación:** La recuperación local y la propagación de limitaciones permiten un informe honesto sin fallo global innecesario.

**Confusión que debes evitar:** Las lagunas de cobertura deben ser visibles.

## Escenario 4 — Extracción documental estructurada y fiabilidad

### Pregunta 46 · D2 — B

**El servicio documental expone “consultar factura” y “actualizar factura”. ¿Qué diseño de MCP minimiza riesgos?**

**Justificación:** Las capacidades separadas y permisos explícitos reducen modificaciones indebidas.

**Confusión que debes evitar:** La descripción no es autorización.

### Pregunta 47 · D2 — A

**La aplicación exige ejecutar primero extract_metadata y después interpretar el resultado. En un modelo compatible, ¿qué usarías en la primera llamada?**

**Justificación:** Forzar una herramienta inicialmente puede establecer un prerrequisito; después no debes impedir la salida final.

**Confusión que debes evitar:** Las llamadas forzadas dependen de compatibilidad de modelo y configuración.

### Pregunta 48 · D2 — D

**Claude Code debe localizar todos los archivos .py que incluyen "parse_invoice". ¿Cuál es el orden eficiente?**

**Justificación:** Glob y Grep resuelven búsquedas de rutas y contenido respectivamente.

**Confusión que debes evitar:** No recorrer indiscriminadamente todo el código si no hace falta.

### Pregunta 49 · D3 — C

**Un conjunto de reglas de parsing se aplica solo a *.py en src y tests. ¿Dónde expresarlo?**

**Justificación:** Las reglas por ruta se activan al trabajar en archivos que coinciden con el patrón.

**Confusión que debes evitar:** Las reglas específicas no necesitan saturar instrucciones universales.

### Pregunta 50 · D3 — B

**Tras un nuevo commit, el revisor CI vuelve a comentar defectos corregidos en la versión anterior. ¿Qué mejora es adecuada?**

**Justificación:** El contexto de hallazgos previos permite deduplicar comentarios y revisar qué persiste.

**Confusión que debes evitar:** Un revisor sin historial de comentarios puede repetirlos.

### Pregunta 51 · D4 — A

**¿Cómo se solicita hoy una respuesta JSON restringida con raw schema en Messages API?**

**Justificación:** La interfaz documentada utiliza output_config.format para el esquema JSON.

**Confusión que debes evitar:** Las instrucciones textuales no imponen una estructura garantizada.

### Pregunta 52 · D4 — D

**Un JSON pasa el esquema, pero cantidad 2 × precio 3.5 no coincide con un total extraído de 9. ¿Qué falla?**

**Justificación:** La validez estructural no prueba que los importes sean consistentes.

**Confusión que debes evitar:** No confundir validación de estructura con comprobación de negocio.

### Pregunta 53 · D4 — B

**El documento omite un total declarado. ¿Qué diseño reduce invenciones?**

**Justificación:** La ausencia de información debe representarse explícitamente; no forzar un dato inexistente.

**Confusión que debes evitar:** Un total calculado no necesariamente está declarado.

### Pregunta 54 · D4 — C

**¿Qué restricción no admite actualmente el subconjunto de Structured Outputs de Anthropic?**

**Justificación:** Las restricciones numéricas deben validarse después en la aplicación.

**Confusión que debes evitar:** No asumir soporte total de JSON Schema.

### Pregunta 55 · D4 — A

**Una extracción tiene un total contradictorio con la fuente. ¿Qué reintento es más útil?**

**Justificación:** El feedback específico permite localizar la incoherencia y mantener un límite de reintentos.

**Confusión que debes evitar:** Los reintentos genéricos pueden reproducir el error.

### Pregunta 56 · D4 — D

**El número de pedido no figura en ninguno de los documentos aportados. ¿Qué actuación es correcta?**

**Justificación:** No puede recuperarse un dato que la fuente no contiene por repetir la inferencia.

**Confusión que debes evitar:** No inventar identificadores para cumplir el esquema.

### Pregunta 57 · D4 — B

**Se quieren procesar 800 facturas durante la noche y correlacionar fallos por archivo. ¿Qué opción encaja?**

**Justificación:** Los lotes son apropiados para trabajo independiente tolerante a latencia; custom_id conserva la correspondencia.

**Confusión que debes evitar:** Los resultados de lotes pueden llegar en orden distinto.

### Pregunta 58 · D4 — C

**Un extractor registra “total_declarado” y “total_calculado”. ¿Qué comprobación mejora fiabilidad?**

**Justificación:** La validación de negocio debe contemplar reglas de la fuente y contextos como descuentos e impuestos.

**Confusión que debes evitar:** Una resta simple puede ser insuficiente si existen cargos adicionales.

### Pregunta 59 · D5 — A

**El extractor muestra precisión agregada del 97 %, pero falla en facturas manuscritas. ¿Cómo medirlo?**

**Justificación:** El rendimiento agregado puede ocultar subgrupos con tasas de error peligrosas.

**Confusión que debes evitar:** La precisión promedio no basta para automatizar casos vulnerables.

### Pregunta 60 · D5 — D

**Una síntesis toma afirmaciones de tres documentos y elimina la referencia a cuál las sustentó. ¿Qué control falta?**

**Justificación:** La procedencia debe preservarse a lo largo de todas las fases para permitir auditoría.

**Confusión que debes evitar:** Sin trazabilidad no se puede validar lo afirmado.

