---
name: revisar-python
description: Revisa cambios Python de este proyecto y propone correcciones justificadas con pruebas.
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash
---

Revisa los archivos Python indicados por el usuario.
1. Identifica el comportamiento observable y los riesgos.
2. Comprueba validaciones, errores y tipos.
3. Ejecuta únicamente las pruebas unitarias permitidas.
4. Devuelve hallazgos con archivo, evidencia, gravedad y propuesta.
5. Si una prueba no pudo ejecutarse, indícalo explícitamente.
No modifiques archivos: esta skill es solo de revisión.
