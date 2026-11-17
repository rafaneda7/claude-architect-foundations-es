# Día 8 — Simulacro final CCAR-F

El material contiene 60 preguntas originales de respuesta única, basadas en **4 escenarios ficticios** y distribuidas por los cinco dominios.

## Archivos

- `GUIA_DIA_08_COMPLETA.md`: guía, examen, casos, soluciones y laboratorio.
- `EXAMEN_DIA_08.md`: examen cerrado sin respuestas.
- `SOLUCIONARIO_DIA_08.md`: justificación de cada pregunta.
- `banco_preguntas.json`: datos estructurados del simulacro.
- `respuestas.json`: plantilla para responder (A/B/C/D).
- `HOJA_DE_RESPUESTAS.csv`: hoja alternativa con columna confianza.
- `simulacro_dia8.html`: simulacro interactivo offline con temporizador, revisión y exportación.
- `corrector_dia8.py`: puntuación y diagnóstico por dominios.
- `motor_dia8.py`, `demo_dia8.py`, `tests/`: laboratorio offline y pruebas unitarias.
- `CHECKPOINT_08.md`: registro de resultados.

## Ejecutar desde VS Code / Git Bash

```bash
python -m unittest discover -s tests -v
python demo_dia8.py
python corrector_dia8.py respuestas.json
```

También puedes abrir `simulacro_dia8.html` directamente en tu navegador; no utiliza internet ni una API Key.

**Advertencia:** este material no reproduce preguntas oficiales ni permite obtener una puntuación escalada comparable a la certificación.
