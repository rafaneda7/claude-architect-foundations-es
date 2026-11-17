# CCAR-F — DÍA 4: Claude Code Configuration & Workflows

**Dominio principal:** D3 · Claude Code Configuration & Workflows (**20 %** del examen de referencia).  
**Duración:** 4 horas.  
**Prerrequisitos:** Días 1–3: Messages API, agentes, Tool Use y MCP.  
**Entorno:** Windows 11, VS Code, Git Bash, Python 3.12, `.venv`, cuenta de Anthropic Console con crédito API.  
**Estado:** material original de preparación; preguntas y evaluación didácticas, no oficiales.  
**Fuentes verificadas:** documentación Claude Code consultada el 16/11/2026 (enlaces al final).

> **Tesis del día:** un `CLAUDE.md` no implementa autorizaciones. Las instrucciones orientan al modelo; los permisos, hooks y las validaciones de la aplicación controlan qué puede ejecutarse. La seguridad sensible no debe depender únicamente de obedecer un prompt.

## Objetivos de aprendizaje

- [ ] Diferenciar instrucciones persistentes, ajustes de configuración, permisos, hooks, skills y subagentes.
- [ ] Crear `CLAUDE.md` a nivel de proyecto y distribuir normas específicas con `.claude/rules/`.
- [ ] Localizar configuraciones personal, compartida, local y administrada, y comprender precedencias.
- [ ] Diferenciar `permissions.allow`, `permissions.ask` y `permissions.deny`.
- [ ] Comprender `PreToolUse`, `PostToolUse` y su contrato de entrada/salida JSON.
- [ ] Probar un hook Python sin consumir tokens.
- [ ] Crear una skill reutilizable y un subagente de revisión con capacidades limitadas.
- [ ] Aplicar Plan Mode a una refactorización, reanudar sesiones y usar `claude -p` para scripts.
- [ ] Explicar por qué una ejecución local verificada no prueba la configuración del producto hasta probar Claude Code real.

## Programa (240 minutos)

| Tiempo | Módulo | Tema |
|---|---|---|
| 40 min | M1 | `CLAUDE.md`, jerarquía e instrucciones específicas |
| 40 min | M2 | Settings, permisos y precedencia |
| 50 min | M3 | Hooks, seguridad y práctica local Python |
| 45 min | M4 | Skills y subagentes |
| 35 min | M5 | Plan Mode, CLI y CI/CD |
| 30 min | M6 | Evaluación de 100 puntos y checkpoint |

---

# M1. `CLAUDE.md` y la organización de instrucciones (40 min)

## 1.1. Qué es `CLAUDE.md`

Es un archivo Markdown que aporta instrucciones persistentes para sesiones de Claude Code. Resulta útil para convenciones, comandos de prueba, arquitectura y decisiones del proyecto que no deseas repetir en cada turno.

**No es:** la clave de API, una política de autorización obligatoria, una base de datos ni el historial completo de un chat.

Imagina que trabajas en un repositorio de un bootcamp con tres carpetas (`src`, `tests`, `docs`). Si las instrucciones del proyecto indican «ejecutar tests antes de confirmar cambios», Claude conoce esa convención, pero necesita herramientas y permisos para cumplirla.

## 1.2. Jerarquía de instrucciones

| Alcance | Ubicación | Quién recibe las instrucciones |
|---|---|---|
| Administrado | Ubicación corporativa administrada | Organización |
| Usuario | `~/.claude/CLAUDE.md` | Tú en tus proyectos |
| Proyecto | `CLAUDE.md` o `.claude/CLAUDE.md` | Colaboradores que reciban el archivo en Git |
| Local | `CLAUDE.local.md` | Solo ese proyecto y usuario; excluir de Git |
| Subdirectorios | `CLAUDE.md` anidados | Se cargan cuando el trabajo requiere ese subárbol |

En Windows, `~/.claude` suele corresponder a `%USERPROFILE%\.claude`. El alcance de instrucciones no es exactamente igual al alcance de los archivos `settings.json` que veremos en el M2.

### Ejemplo de `CLAUDE.md` compartido

```markdown
# Convenciones del repositorio

- Python 3.12, anotaciones de tipos y docstrings claros.
- Antes de modificar código, leer los módulos relacionados.
- Para cambios de varios archivos, presentar un plan y pedir aprobación.
- No añadir claves, tokens ni contraseñas al repositorio.
- Ejecutar: python -m unittest discover -s tests -v
- Comunicar qué pruebas se ejecutaron realmente.
```

**Consejo:** mantenlo breve y útil. Copiar manuales completos a `CLAUDE.md` genera más contexto, no una garantía de obediencia.

## 1.3. Reglas por ruta

Las reglas temáticas pueden vivir bajo `.claude/rules/`. Se pueden activar solo cuando Claude trabaja con archivos que coinciden con el frontmatter `paths`.

Archivo `.claude/rules/python.md`:

```markdown
---
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
---

# Reglas Python
- Validar entradas antes de calcular.
- Añadir pruebas si cambia el comportamiento.
- Ejecutar unittest y reportar el resultado real.
```

Una regla sin `paths` se carga en el contexto inicial. Una regla con `paths` se aplica condicionalmente cuando Claude accede a archivos compatibles por rutas de lectura/edición reconocidas. Evita asumir que una regla temporal se activará sin verificarlo.

## 1.4. Imports de instrucciones

Se pueden incluir archivos mediante `@ruta/relativa`. Los imports se expanden en el contexto del archivo que los importa; ayudan a organizar, pero **no ahorran automáticamente tokens**.

## 1.5. Dónde colocar cada instrucción

| Situación | Mecanismo adecuado |
|---|---|
| Convención general del repositorio | `CLAUDE.md` |
| Reglas solo para notebooks Python | `.claude/rules/` con `paths` |
| Flujo que se repite a petición del usuario | Skill |
| Política de prohibición de un comando | Permissions / hook / sandbox, no solo prompt |
| Revisor especializado que trabaja aislado | Subagente |

### Ejercicio 1 — Organiza las instrucciones

Tienes estas necesidades: A) todos los compañeros deben ejecutar `unittest`; B) solo los `.py` necesitan anotaciones de tipos; C) tu editor favorito es personal; D) debe impedirse el acceso a `.env`; E) revisar proyectos contra una rúbrica es una tarea repetible.

**Pregunta:** asigna a cada necesidad el mecanismo más adecuado y explica por qué no pondrías todas juntas en `CLAUDE.md`.

---

# M2. Settings, jerarquía y permisos (40 min)

## 2.1. Archivos de configuración

| Archivo | Alcance |
|---|---|
| `~/.claude/settings.json` | Configuración del usuario, en todos sus proyectos |
| `.claude/settings.json` | Configuración compartida en el proyecto |
| `.claude/settings.local.json` | Ajustes privados del proyecto; no versionar |
| Settings administrados | Política de la organización |

## 2.2. Precedencia de settings

Para claves escalares habituales, el orden de mayor a menor prioridad es:

1. Configuración administrada.
2. Opción de inicio `--settings`.
3. Configuración local del proyecto.
4. Configuración compartida del proyecto.
5. Configuración de usuario.

**Matiz esencial:** las listas, como `permissions.allow`, pueden combinarse entre archivos en lugar de sustituirse. Algunos ajustes de seguridad y banderas tienen reglas particulares. No memorices la secuencia como una fórmula universal para cualquier campo; consulta la referencia.

Comprobaciones útiles dentro de Claude Code:

```text
/status
/permissions
/config
```

Desde terminal:

```bash
claude doctor
```

## 2.3. `allow`, `ask` y `deny`

Un sistema de permisos puede permitir, solicitar confirmación o denegar herramientas.

```json
{
  "permissions": {
    "allow": [
      "Bash(python -m unittest discover -s tests -v)"
    ],
    "ask": [
      "Edit(./src/**)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  }
}
```

**Orden de evaluación de reglas:** `deny` → `ask` → `allow`. Una regla `allow` más específica no crea una excepción a una regla `deny` aplicable.

**Cuidado:** denegar `Read(.env)` no equivale a una barrera total frente a todas las formas de obtener secretos; también pueden existir comandos de shell, procesos externos, conexiones y copias. Para sistemas críticos, utiliza controles del SO, aislamiento y políticas administradas.

## 2.4. Plan Mode no es un permiso de escritura

Plan Mode permite investigar y proponer antes de modificar archivos, pero no sustituye las políticas de seguridad. En un flujo de desarrollo, conviene usarlo cuando los cambios son grandes o de consecuencias difíciles de revertir.

### Ejercicio 2 — Resolución de permisos

1. `settings.json` compartido deniega `Read(./.env)` y un archivo local permite `Read(./.env)`. ¿Cuál prevalece?
2. Una regla `ask` afecta a `Edit(./src/**)` y otra `allow` afecta a `Edit(./src/calificaciones.py)`. ¿Qué pasa?
3. El equipo necesita compartir un hook. ¿En qué archivo lo guardarías?
4. Quieres cambiar tu tema o modelo solo para ti. ¿Qué alcance corresponde?
5. Una variable `ANTHROPIC_API_KEY` figura en un commit público. ¿Basta con eliminarla en el siguiente commit?

---

# M3. Hooks de Claude Code y práctica Python (50 min)

## 3.1. Concepto de hook

Un hook es una acción programática ligada a un evento del ciclo de Claude Code. Puede auditar operaciones, enriquecer el contexto, solicitar confirmación o bloquear determinadas acciones antes de ejecutarse.

| Evento | Momento | Uso típico |
|---|---|---|
| `PreToolUse` | Antes de utilizar una herramienta | Validar o bloquear la llamada |
| `PostToolUse` | Después de ejecutar una herramienta | Registrar o comprobar resultados |
| `SessionStart` | Al comenzar la sesión | Preparar contexto o entorno |
| `Stop` | Al intentar terminar el turno | Comprobaciones finales |

La configuración es distinta de MCP: MCP expone herramientas y recursos; los hooks interceptan eventos de la aplicación Claude Code.

## 3.2. Contrato de `PreToolUse`

Claude Code entrega al hook información mediante JSON por `stdin`:

```json
{
  "tool_name": "Edit",
  "tool_input": {"file_path": ".env"}
}
```

Para denegar una llamada, un hook tipo `command` puede imprimir:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "No modificar secretos"
  }
}
```

`permissionDecision` admite `allow`, `ask`, `deny` y otros resultados dependiendo de modo y evento. Un hook `PreToolUse` que no emite una decisión puede dejar el comportamiento a los permisos normales. La decisión de un hook no sobreescribe necesariamente las políticas administradas.

## 3.3. Nuestro hook de ejemplo

Archivo: `.claude/hooks/proteger_secretos.py`. La versión completa está dentro del ZIP; este es el núcleo:

```python
from pathlib import PurePosixPath


def nombre_archivo(ruta: str) -> str:
    return PurePosixPath(ruta.replace("\\", "/")).name.casefold()


def decidir(evento: dict) -> dict | None:
    if evento.get("tool_name") not in {"Write", "Edit"}:
        return None

    entrada = evento.get("tool_input") or {}
    ruta = entrada.get("file_path")

    if not isinstance(ruta, str):
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Falta la ruta del archivo"
            }
        }

    nombre = nombre_archivo(ruta)
    if nombre == ".env" or nombre.startswith(".env."):
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "No editar secretos"
            }
        }

    return None
```

En el archivo completo también se protegen los nombres `secrets.json` y `credentials.json` y se procesa la entrada estándar. Las pruebas cubren rutas con separadores Windows y POSIX.

## 3.4. Registrar el hook

En `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/proteger_secretos.py\""
          }
        ]
      }
    ]
  }
}
```

El archivo real del ZIP fusiona este bloque con `permissions`, así que **no sustituyas el JSON del proyecto por el fragmento**: integra las claves dentro del mismo objeto.

La ruta utiliza `${CLAUDE_PROJECT_DIR}` y presupone que el comando `python` resuelve al intérprete adecuado en la sesión. En Windows, comprueba la integración con Git Bash y el `PATH`.

## 3.5. Pruebas sin API

Desde la carpeta raíz del proyecto de ejemplo:

```bash
python -m unittest discover -s tests -v
```

Resultado verificado en el entorno de creación: **17 tests `OK`**, de los cuales 7 prueban el hook y 10 prueban la lógica de notas.

Prueba manual de un evento (desde Git Bash):

```bash
printf '%s\n' '{"tool_name":"Write","tool_input":{"file_path":".env"}}' \
  | python .claude/hooks/proteger_secretos.py
```

La salida esperada contiene `"permissionDecision": "deny"`.

**Limitación explícita:** este hook es didáctico y se aplica únicamente a las llamadas `Write` y `Edit` que alcancen el evento. No bloquea lecturas mediante `Read`, operaciones `Bash`, enlaces simbólicos, escrituras externas ni otros vectores. Para proteger secretos en producción necesitas controles más amplios.

### Ejercicio 3 — Hooks

1. ¿Por qué una instrucción de `CLAUDE.md` que diga «no modificar .env» no equivale al hook anterior?
2. ¿Qué evento usarías para actuar antes de una escritura: `PreToolUse` o `PostToolUse`?
3. ¿Qué valor debe llevar `permissionDecision` para bloquear la llamada?
4. Amplía el hook para denegar también `tokens.json`. Añade una prueba unitaria.
5. ¿Por qué este hook no garantiza la protección total de una API Key?

---

# M4. Skills y subagentes (45 min)

## 4.1. Skill reutilizable

Las skills contienen instrucciones que Claude Code puede utilizar cuando corresponde o que tú puedes invocar con `/nombre`. Las skills de proyecto pueden estar en `.claude/skills/<nombre>/SKILL.md`.

Archivo `.claude/skills/revisar-python/SKILL.md`:

```markdown
---
name: revisar-python
description: Revisa código Python y entrega hallazgos con evidencia.
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash
---

1. Inspecciona los archivos pertinentes.
2. Identifica problemas de tipos, errores y validaciones.
3. Ejecuta las pruebas permitidas.
4. Devuelve hallazgo, evidencia, gravedad y mejora.
5. Informa de las pruebas que no pudiste ejecutar.
```

El frontmatter `disable-model-invocation: true` impide que Claude active espontáneamente la skill; puedes invocarla manualmente por su nombre. En el ejemplo el contenido indica que no debe modificar archivos. Para seguridad real, las restricciones de permisos también deben permanecer en los settings o en el entorno.

Para utilizarla dentro de Claude Code:

```text
/revisar-python src/calificaciones.py
```

## 4.2. Subagente

Un subagente es un ejecutor especializado que puede trabajar en un contexto separado, con herramientas y responsabilidades definidas. Se crea en `.claude/agents/<nombre>.md`.

Archivo `.claude/agents/revisor-python.md`:

```markdown
---
name: revisor-python
description: Analiza código Python y propone mejoras sin editar archivos.
tools: Read, Glob, Grep
model: sonnet
---

Revisa el código, busca evidencia y entrega hallazgos técnicos.
No inventes resultados de pruebas ni modifiques archivos.
```

En esta definición **no se concede `Write`, `Edit` ni `Bash`**. El modelo `sonnet` es un alias de modelo cuyo coste y disponibilidad dependen de tu cuenta y configuración.

## 4.3. Cuándo usar qué

| Necesidad | Mejor opción |
|---|---|
| Norma siempre aplicable al proyecto | `CLAUDE.md` |
| Norma solo para determinados archivos | Regla por ruta |
| Procedimiento que invocas repetidamente | Skill |
| Trabajo especializado en contexto propio | Subagente |
| Denegar una operación determinada | Permiso/hook |

Un agente revisor no debería recibir herramientas de escritura por defecto. La separación de contextos permite reducir la contaminación de la conversación principal, pero no garantiza imparcialidad perfecta.

### Ejercicio 4 — Skill y subagente

1. Crea una skill `auditar-tests` que indique cómo revisar una suite de pruebas y preparar un informe, sin modificar archivos.
2. Diseña un subagente `revisor-seguridad` limitado a `Read`, `Grep` y `Glob`.
3. Explica qué ocurre si colocas el procedimiento de 50 pasos dentro del `CLAUDE.md` principal.
4. ¿Por qué limitar herramientas en el frontmatter del subagente es mejor que darle todas las herramientas y pedirle que no las use?
5. ¿Las instrucciones del subagente bastan para autorizar el acceso a información privada?

---

# M5. Workflows de Claude Code: planificar, sesiones y automatización (35 min)

## 5.1. Plan Mode

Plan Mode resulta apropiado cuando quieres inspeccionar y aprobar un diseño antes de modificar archivos. Se puede activar desde CLI:

```bash
claude --permission-mode plan
```

También puedes cambiar de modo con `Shift+Tab` en el terminal interactivo hasta ver la indicación de Plan Mode.

**Ejercicio con tu repositorio:** pide analizar si conviene extraer la validación de notas a un módulo separado. Antes de autorizar cambios, revisa el plan, las pruebas necesarias y los archivos afectados.

**Diferencia central:** planificar es una fase de diseño; ejecutar implica modificar archivos y probar. Un plan detallado no equivale a una modificación realizada.

## 5.2. Reanudar sesiones

```bash
claude --continue
```

Reanuda la sesión más reciente correspondiente al directorio actual si existe.

```bash
claude --resume
```

Permite seleccionar entre sesiones disponibles. En una sesión interactiva también existe `/resume`.

No confundas reanudar el historial conversacional con guardar permanentemente la información de negocio en una base de datos.

## 5.3. Modo no interactivo

`claude -p` permite ejecutar una consulta desde un script o pipeline sin abrir una sesión de chat interactiva:

```bash
claude -p "Explica los riesgos de src/calificaciones.py" --output-format json
```

Para reducir riesgo, comienza por tareas **solo de lectura**. Cualquier ejecución real de Claude Code utilizando la cuenta Console puede consumir tu saldo de API.

En tareas CI/CD, la regla es comprobar estados de salida, resultado estructurado, permisos y criterios deterministas fuera del texto del modelo. No utilices únicamente «Claude dijo que pasó» como verificación del pipeline.

### `--bare` y reproducibilidad

El modo `--bare` evita gran parte del descubrimiento automático de instrucciones, hooks, skills, subagentes, MCP y memoria. Puede resultar útil para CI reproducible, pero **si dependes de un hook de seguridad del proyecto, `--bare` no lo ejecutará**. En ese caso deberías hacer cumplir esa seguridad de otra manera, fuera de ese modo.

## 5.4. Instalar y activar Claude Code en Windows

Verifica primero:

```bash
claude --version
```

Si el comando no existe, la instalación recomendada está documentada para Windows mediante PowerShell o WinGet. Por ejemplo, en una terminal PowerShell:

```powershell
winget install Anthropic.ClaudeCode
```

Después abre una nueva terminal en VS Code y comprueba la versión. El primer inicio `claude` puede solicitar autenticación. Una cuenta Claude Console con saldo API puede utilizarse como fuente de facturación, pero la autenticación de Claude Code es distinta de importar el SDK Python; comprueba la cuenta y el método de facturación antes de seguir.

## 5.5. Laboratorio integrado

A. Crea `CLAUDE.md` y `.claude/rules/python.md`; comprueba la carga mediante `/memory` o `/status`.  
B. Confirma los permisos con `/permissions`.  
C. Ejecuta los tests offline.  
D. Comprueba el hook enviando JSON por stdin.  
E. Abre Claude Code y utiliza Plan Mode para solicitar una propuesta de refactorización sin aplicar cambios.  
F. Prueba la skill `/revisar-python` **solo si el consumo API previsto entra en tu presupuesto**.  
G. Registra qué comprobaciones realizaron realmente las herramientas y cuáles son recomendaciones no ejecutadas.

### Ejercicio 5 — Planificación y CI

Una plataforma docente quiere que Claude Code proponga mejoras de código y que un pipeline rechace cambios con tests fallidos.

1. ¿Qué modo usarías para inspeccionar primero la propuesta sin modificar archivos?
2. ¿Qué comando utilizarías para ejecutar tests locales sin gastar saldo Claude?
3. ¿Qué diferencia hay entre `claude --continue` y `claude -p`?
4. ¿Por qué el pipeline debe comprobar el código de salida de tests y no depender de un texto generado?
5. ¿Qué riesgo introduce `--bare` si las protecciones se apoyan en hooks del proyecto?

---

# M6. Evaluación del Día 4 — 100 puntos (30 min)

**Importante:** preguntas originales de entrenamiento, no ítems oficiales. Lee primero los enunciados sin consultar las respuestas; el solucionario está más abajo.

## Parte A — Test (10 preguntas × 4 puntos = 40)

**A1.** Una norma debe llegar a todo el equipo cuando clona el repositorio. ¿Dónde conviene incluirla?  
A. `.claude/settings.local.json` · B. `CLAUDE.md` del proyecto versionado · C. `~/.claude/CLAUDE.md` solo tuyo · D. Un comentario no versionado.

**A2.** ¿Qué mecanismo aplica una regla solo a archivos `src/**/*.py`?  
A. `.claude/rules/*.md` con frontmatter `paths` · B. Un API Key distinto · C. `tool_result` · D. `max_tokens`.

**A3.** Una regla `deny` y otra `allow` coinciden con la misma herramienta. ¿Qué prevalece?  
A. La más específica siempre · B. La última del JSON · C. `deny` · D. `allow`.

**A4.** ¿Qué archivo se recomienda para ajustes privados de un único repositorio?  
A. `CLAUDE.md` versionado · B. `.claude/settings.local.json` · C. `src/main.py` · D. `README.md`.

**A5.** ¿Qué evento puede bloquear una operación antes de ejecutarla?  
A. `PostToolUse` · B. `SessionEnd` · C. `PreToolUse` · D. `Stop`.

**A6.** ¿Cómo se comunica una denegación desde un hook `PreToolUse`?  
A. Texto natural en `CLAUDE.md` · B. `hookSpecificOutput.permissionDecision='deny'` · C. `tool_choice='none'` · D. Un `tool_result` de la Messages API.

**A7.** ¿Dónde se define una skill de proyecto?  
A. `.claude/skills/<nombre>/SKILL.md` · B. `.venv/Scripts/activate` · C. `.claude.json` obligatorio · D. `pip.ini`.

**A8.** ¿Qué implica `disable-model-invocation: true` en una skill?  
A. La borra · B. Impide la invocación automática por Claude · C. Deniega todos los archivos · D. Obliga a usar MCP.

**A9.** ¿Cuál es la opción apropiada para revisar un plan antes de permitir modificaciones?  
A. `--permission-mode plan` · B. `--dangerously-skip-permissions` · C. `--output-format stream-json` · D. `--resume`.

**A10.** ¿Qué advertencia es correcta sobre `claude --bare -p`?  
A. Incluye siempre los hooks del proyecto · B. Nunca puede leer código · C. Desactiva el descubrimiento automático de hooks y otras extensiones, por lo que no debes depender de ellos · D. Convierte Claude Code en un servidor MCP.

## Parte B — Razonamiento técnico (3 × 10 = 30)

**B1. Jerarquía.** Un equipo puso sus instrucciones en `~/.claude/CLAUDE.md`, y el resto de colaboradores no las recibe. Explica el error y diseña una distribución coherente entre `CLAUDE.md`, `.claude/rules/python.md` y `.claude/settings.local.json`.

**B2. Seguridad.** Un ingeniero escribe «Nunca accedas a `.env`» dentro de `CLAUDE.md` y afirma que ya es una política de seguridad. Explica qué falta, qué controles usarías y las limitaciones del hook `PreToolUse` que construimos.

**B3. Workflows.** Compara Plan Mode, una skill y un subagente. Indica cuándo utilizar cada uno en una refactorización de código y cómo comprobarías el resultado.

## Parte C — Escenario arquitectónico (20)

Una escuela tiene un repositorio con código Python, notebooks y documentación. Quiere que Claude Code ayude a profesores y alumnos sin exponer secretos, aplique convenciones compartidas, permita revisiones especializadas y pueda ejecutar pruebas en CI. Diseña estructura `.claude/`, jerarquía de ajustes, permisos, hooks, skill, subagente y pipeline. Explica los límites de seguridad y de gasto.

## Parte D — Python (10)

Implementa `decidir(evento: dict) -> dict | None` para un hook `PreToolUse` que:

1. Intercepte solo `Write` y `Edit`.
2. Extraiga `file_path` con tratamiento robusto de separadores Windows/POSIX.
3. Devuelva `permissionDecision='deny'` si el archivo se llama `.env` o empieza por `.env.`.
4. No adopte una decisión para otros archivos o herramientas.
5. No dependa de llamar a Claude.

```python
from pathlib import PurePosixPath


def decidir(evento: dict) -> dict | None:
    # Tu solución
    pass
```

---

# Solucionario de ejercicios (M1–M5)

## Ejercicio 1 — Organización

A) `CLAUDE.md` de proyecto compartido: comando de tests y convención común. B) `.claude/rules/python.md` con `paths: ["**/*.py"]`: solo se activa en código Python. C) `~/.claude/settings.json` o `~/.claude/CLAUDE.md` para preferencias personales, según si son ajustes o instrucciones. D) Denegar accesos mediante permisos y controles del sistema: no basta con redactar una instrucción. E) Skill: es un procedimiento reutilizable invocado cuando se necesite, no una norma para cada petición.

## Ejercicio 2 — Permisos

1. `deny` prevalece sobre `allow` si ambas reglas coinciden; el archivo local no abre una excepción.
2. `ask` prevalece sobre `allow` cuando ambas coinciden; el usuario debe aprobar la operación.
3. `.claude/settings.json` versionado, sabiendo que permisos adicionales del equipo pueden requerir confianza en el repositorio.
4. `~/.claude/settings.json` para preferencias de usuario, o `.claude/settings.local.json` para ese proyecto únicamente.
5. No. Una clave expuesta debe **revocarse o rotarse** y retirarse de repositorios e historial cuando corresponda; borrar un commit posterior no deshace una exposición previa.

## Ejercicio 3 — Hooks

1. Un prompt es orientativo; un hook intercepta programáticamente el evento que cubre.
2. `PreToolUse`; `PostToolUse` se ejecuta después.
3. `permissionDecision: "deny"` dentro de `hookSpecificOutput`.
4. En `proteger_secretos.py`, incorporar `or nombre == "tokens.json"` a la condición; añadir prueba con `Write` dirigido a `tokens.json` y afirmar el resultado `deny`.
5. El hook de ejemplo solo observa herramientas `Write` y `Edit`; otros mecanismos de lectura/escritura y rutas indirectas pueden escapar a su alcance. Para secretos reales usa permisos, aislamiento y gestión segura de claves.

## Ejercicio 4 — Skills y subagentes

**Skill propuesta (`.claude/skills/auditar-tests/SKILL.md`):**

```markdown
---
name: auditar-tests
description: Revisa cobertura y calidad de pruebas Python sin modificar archivos.
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash
---

1. Localiza archivos test_*.py.
2. Identifica casos borde, errores y permisos no comprobados.
3. Si está permitido, ejecuta unittest.
4. Devuelve hallazgos y pruebas realizadas.
5. No modifiques archivos ni inventes resultados.
```

**Subagente propuesto (`.claude/agents/revisor-seguridad.md`):**

```markdown
---
name: revisor-seguridad
description: Revisor de seguridad de código sin permisos para modificar.
tools: Read, Grep, Glob
model: sonnet
---

Revisa entradas, control de permisos y secretos.
Devuelve evidencia, gravedad y recomendaciones; no edites archivos.
```

3. Un procedimiento extenso en `CLAUDE.md` ocupa contexto de todas las sesiones y reduce claridad: conviene extraerlo a skill.
4. Limitar las herramientas reduce la superficie disponible, no solo la probabilidad de obedecer una instrucción textual.
5. No. Autorización y acceso a información privada deben comprobarse fuera del subagente.

## Ejercicio 5 — Plan y CI

1. Plan Mode (`claude --permission-mode plan`).
2. `python -m unittest discover -s tests -v`.
3. `--continue` reanuda la sesión más reciente; `-p` ejecuta un prompt no interactivo para automatizaciones.
4. La evidencia debe ser verificable mediante tests y códigos de salida; un texto generado puede ser incorrecto.
5. `--bare` no ejecuta los hooks y ajustes autodetectados del proyecto; si dependes de ellos, pierdes esas defensas en esa ejecución.

---

# Solucionario de evaluación (100 puntos)

## Parte A — Respuestas explicadas

| Pregunta | Respuesta | Explicación |
|---|---|---|
| A1 | B | Un `CLAUDE.md` del proyecto versionado llega a colaboradores. |
| A2 | A | El frontmatter `paths` aplica reglas por ruta. |
| A3 | C | `deny` se evalúa antes de `ask` y `allow`. |
| A4 | B | `settings.local.json` es personal de ese repositorio. |
| A5 | C | `PreToolUse` se activa antes de ejecutar la herramienta. |
| A6 | B | El hook devuelve su decisión mediante `hookSpecificOutput`. |
| A7 | A | Las skills de proyecto viven bajo `.claude/skills/`. |
| A8 | B | `disable-model-invocation` impide activación automática por Claude. |
| A9 | A | Plan Mode permite revisar el diseño antes de modificar. |
| A10 | C | Bare mode omite la autodetección de hooks y extensiones. |

## Parte B — Modelos de respuesta

**B1 (10):** Las instrucciones del directorio de usuario no se comparten con el equipo. Trasladaría convenciones comunes a `CLAUDE.md` de la raíz versionado, reglas condicionadas para Python a `.claude/rules/python.md` y ajustes personales a `.claude/settings.local.json`, excluido de Git. Confirmaría carga con `/memory` o `/status` y validaría rutas, sin asumir que todos los archivos se cargan siempre. **Rúbrica:** diagnóstico (3), ubicación (4), verificación (3).

**B2 (10):** `CLAUDE.md` orienta, pero no impide por sí solo leer o modificar secretos. Aplicaría permisos `deny`, gestión de claves, aislamiento y un `PreToolUse` de bloqueo para acciones concretas. El hook del laboratorio intercepta `Write` y `Edit`; no cubre `Bash`, `Read` ni procesos externos. Un control seguro debe complementarse con políticas administradas y restricciones de sistema operativo. **Rúbrica:** límites del prompt (3), controles externos (4), límites del hook (3).

**B3 (10):** Plan Mode sirve para explorar y proponer sin editar hasta la aprobación; una skill codifica un procedimiento reusable; un subagente encapsula una revisión especializada con herramientas y contexto propios. Primero planificaría, después autorizaría cambios controlados y finalmente delegaría la revisión con herramientas de lectura, ejecutando pruebas deterministas y comprobando diffs. **Rúbrica:** tres definiciones (6), ejemplo integrado (2), comprobación independiente (2).

## Parte C — Arquitectura modelo

**Propuesta:** `CLAUDE.md` versionado con convenciones y comando de pruebas; `.claude/rules/python.md` para `src` y `tests`; `.claude/settings.json` con permisos `deny`, `ask` y hooks; `.claude/skills/revisar-python/SKILL.md` invocable por el usuario; `.claude/agents/revisor-python.md` con herramientas solo lectura. La autenticación y autorización de alumnos y profesores permanecerán en la aplicación real y en sus servicios, nunca únicamente en prompts. Los secretos residirán fuera del repositorio. Para cambios no triviales, iniciar con Plan Mode y revisión humana. En CI se ejecutan `unittest` y validadores deterministas, con aprobación para operaciones de impacto. Si se utiliza `claude -p` se controlan costes, herramientas permitidas, salida estructurada y códigos de salida; si se usa `--bare`, no se presupone ejecución de los hooks locales. El pipeline reporta fallos sin ocultarlos.

**Rúbrica:** organización de archivos (5), permisos y secretos (5), skills/subagentes (4), plan/CI y pruebas (4), observabilidad y costes (2).

## Parte D — Solución Python

```python
from pathlib import PurePosixPath


def decidir(evento: dict) -> dict | None:
    if evento.get("tool_name") not in {"Write", "Edit"}:
        return None

    entrada = evento.get("tool_input") or {}
    ruta = entrada.get("file_path")
    if not isinstance(ruta, str):
        return None

    nombre = PurePosixPath(ruta.replace("\\", "/")).name.casefold()
    if nombre == ".env" or nombre.startswith(".env."):
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Archivo de entorno protegido"
            }
        }
    return None
```

**Explicación:** comprueba el nombre de herramienta, obtiene `file_path`, normaliza separadores de Windows y POSIX para identificar el nombre final, bloquea archivos `.env*` y no interfiere en otros casos. **Rúbrica:** filtro de herramienta (2), ruta y separadores (2), denegación estructurada (3), otros casos (2), ausencia de API (1).

**Nota de diseño:** el hook completo del ZIP es más conservador: si falta `file_path` para una escritura, deniega la operación. Es aceptable como medida didáctica más estricta, aunque el enunciado del examen no exige ese caso.

---

# CHECKPOINT 04 — Para VS Code

```markdown
# CHECKPOINT 04 — Claude Code Configuration & Workflows

Dominio: D3 (20 %)
Día: 4/8
Evaluación: ___ / 100

## Instrucciones
- [ ] Diferencio CLAUDE.md de settings.json.
- [ ] Comprendo jerarquías de instrucciones.
- [ ] Sé crear reglas con paths.

## Seguridad
- [ ] Comprendo deny, ask y allow.
- [ ] Sé qué hace PreToolUse.
- [ ] Reconozco límites de un hook.

## Skills y agentes
- [ ] Creé una skill SKILL.md.
- [ ] Creé un subagente de revisión.
- [ ] Sé limitar herramientas.

## Workflows
- [ ] Utilicé Plan Mode.
- [ ] Sé reanudar una sesión.
- [ ] Sé utilizar claude -p.
- [ ] Comprendo la diferencia entre --bare y los hooks.

## Verificación
- [ ] He ejecutado 17 tests locales.
- [ ] He probado la carga de config con Claude Code.
- [ ] He documentado cualquier verificación pendiente.

Errores:
1.
2.
3.
```

**Objetivo orientativo:** 85/100 en esta evaluación propia, sin presentarlo como nota oficial de aprobación.

---

# Referencias de documentación oficial

- Instrucciones `CLAUDE.md` y reglas: https://code.claude.com/docs/en/memory
- Settings y jerarquía: https://code.claude.com/docs/en/settings
- Permisos: https://code.claude.com/docs/en/permissions
- Hooks: https://code.claude.com/docs/en/hooks
- Skills: https://code.claude.com/docs/en/skills
- Subagentes: https://code.claude.com/docs/en/sub-agents
- Workflows y Plan Mode: https://code.claude.com/docs/en/common-workflows
- Uso no interactivo: https://code.claude.com/docs/en/headless
- Instalación: https://code.claude.com/docs/en/quickstart

## Alcance de las comprobaciones

- **Verificado localmente:** sintaxis de scripts Python y 17 pruebas unitarias con `unittest` sin API.
- **Por verificar en tu equipo:** instalación de Claude Code, carga efectiva de settings/rules/skills, ejecución de hooks dentro de Claude Code, costes y compatibilidad de las funciones con tu versión del CLI.
- **Material didáctico:** preguntas de práctica, rúbricas y criterio 85/100 son propios, no oficiales.
