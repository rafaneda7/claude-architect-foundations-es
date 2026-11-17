# Día 6 — Context Management & Reliability

## Archivos
- `GUIA_DIA_06_COMPLETA.md`: teoría, 5 ejercicios y sus soluciones, examen de 100 puntos y respuestas.
- `CHECKPOINT_06.md`: seguimiento.
- `contexto_dia6.py`: funciones puras y registro en memoria con autorización ilustrativa.
- `cliente_real_dia6.py`: demo local y llamada opcional a Claude.
- `tests/test_contexto.py`: 30 pruebas unitarias sin API.
- `requirements.txt`: dependencia para el cliente real.

## Instalar y practicar desde la raíz del repositorio

```bash
source .venv/Scripts/activate
python -m pip install -r Ckeckpoints/Dia6/requirements.txt
cd Ckeckpoints/Dia6
python -m unittest discover -s tests -v
python cliente_real_dia6.py
```

## Una llamada opcional (consume crédito)

```bash
read -rs -p "API Key: " ANTHROPIC_API_KEY
echo
export ANTHROPIC_API_KEY
python cliente_real_dia6.py --real
```

No pegues la clave en el repositorio ni la muestres en pantalla. Se usa `claude-haiku-5-5` por defecto y se puede cambiar con `ANTHROPIC_MODEL`. El script hace como máximo una generación y bloquea el ejemplo cuando el recuento previo excede 2500 tokens, sin garantizar un límite monetario absoluto.

## Alcance y límites

El almacén es **en memoria**, el ranking de documentos es por coincidencia de palabras y la identidad está simulada. **No es un servicio de producción**, ni proporciona autenticación real, búsqueda semántica ni persistencia en PostgreSQL. La integración de red con Anthropic no se prueba dentro de los tests.
