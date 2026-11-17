# EXAMEN DEL DÍA 7 — CCAR-F

Sin soluciones. Puntuación: 100 puntos.

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

