# CCAR-F — Día 7: integración de D1–D5

Este paquete es una jornada de estudio de cuatro horas con teoría, cinco ejercicios y soluciones, examen de 100 puntos con solucionario, laboratorio Python y checkpoint.

## Archivos

- `GUIA_DIA_07_COMPLETA.md` — teoría completa, ejercicios y solucionario.
- `motor_dia7.py` — herramientas autorizadas, agent loop y dictamen determinista.
- `demo_dia7.py` — simulación offline y ejecución real opcional.
- `informe_dia7.py` — Structured Outputs y validador semántico.
- `tests/` — pruebas locales sin saldo de Anthropic.
- `CHECKPOINT_07.md` — seguimiento del aprendizaje.
- `requirements.txt` — dependencias para la API real.

## Inicio en VS Code (Git Bash)

```bash
source ../../.venv/Scripts/activate  # ajusta ruta si .venv está en la raíz
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python demo_dia7.py
```

> Si estás en `claude_architect/Ckeckpoints/Dia7`, el entorno virtual de la raíz se accede con `../../.venv/Scripts/activate`.

### API real (solo si lo decides)

```bash
python demo_dia7.py --real
```

Necesita `ANTHROPIC_API_KEY` en la sesión. La ejecución real puede consumir saldo. No se ha realizado desde este entorno.

### Seguridad

Los datos son ficticios. `Identidad` representa una sesión ya autenticada: el código no implementa autenticación de producción. No ejecutes notebooks de terceros en el proceso principal. El resultado del agente **no publica calificaciones**.
