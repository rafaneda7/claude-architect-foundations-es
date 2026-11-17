# SOLUCIONARIO — EVALUACIÓN DÍA 7

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

