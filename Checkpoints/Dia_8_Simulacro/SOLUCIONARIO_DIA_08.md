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

