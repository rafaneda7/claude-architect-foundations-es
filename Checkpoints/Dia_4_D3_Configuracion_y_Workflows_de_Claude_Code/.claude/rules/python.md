---
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
---

# Reglas para Python

- Usar anotaciones de tipos y docstrings concisas.
- Mantener las funciones deterministas y comprobables sin API.
- Añadir o modificar tests cuando se cambie el comportamiento.
- No aceptar booleanos como notas numéricas.
- Ejecutar `python -m unittest discover -s tests -v` después de cambios.
