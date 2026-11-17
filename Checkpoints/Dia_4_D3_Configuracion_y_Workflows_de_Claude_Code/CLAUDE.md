# Convenciones del proyecto CCAR-F — Día 4

## Contexto
Proyecto de práctica Python 3.12 para estudiar Claude Code. No contiene datos reales de alumnos.

## Flujo de trabajo
- Antes de modificar archivos, inspeccionar la estructura y explicar el cambio previsto.
- Para refactorizaciones que afecten varios archivos, proponer un plan y solicitar revisión.
- No modificar archivos de secretos ni incluir credenciales en respuestas, logs o commits.
- Aplicar cambios pequeños que sean fáciles de revisar.
- Tras cambiar código, ejecutar `python -m unittest discover -s tests -v`.
- Indicar qué comprobaciones se han ejecutado realmente y cuáles no.

## Calidad
- Python 3.12, anotaciones de tipos, funciones pequeñas y tests.
- No aceptar booleanos como notas ni valores NaN o infinitos.
- No alterar reglas de negocio sin autorización.

## Límites
Estas son instrucciones orientativas: los permisos reales están en settings y en el sistema operativo.
