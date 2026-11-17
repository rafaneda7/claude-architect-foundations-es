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

