# Claude Certified Architect – Foundations (CCAR-F)

**Ruta de preparación práctica en español para la certificación Claude Certified Architect – Foundations.** El repositorio reúne fundamentos de arquitectura agéntica, ejercicios en Python, integración de herramientas y MCP, flujos con Claude Code, técnicas de prompting, gestión de contexto, pruebas y simulacros.

> Proyecto educativo independiente, **no afiliado ni avalado por Anthropic**. Las preguntas y los casos prácticos son propios, no pertenecen a ningún examen oficial. Las características de la API y del examen pueden cambiar; verifica la [documentación de Anthropic](https://platform.claude.com/docs/en/home) y la guía de certificación antes de presentarte.

## Objetivo y metodología

El recorrido está organizado en ocho jornadas. Las seis primeras desarrollan los cinco dominios mediante teoría y práctica; la séptima integra decisiones arquitectónicas y la octava se dedica al simulacro final. La dedicación sugerida es de unas cuatro horas por jornada, adaptable al ritmo de cada persona.

Está orientado a quienes ya manejan los fundamentos de Python y quieren aprender a diseñar, implementar y evaluar soluciones con Claude, incluso si empiezan sin experiencia previa en agentes o MCP.

## Dominios de estudio

| Dominio | Área | Competencias principales |
|---|---|---|
| **D1** | Agentic Architecture & Orchestration | Bucles agénticos, workflows, patrones de orquestación, gestión de estado, delegación y límites de ejecución. |
| **D2** | Tool Design & MCP Integration | Contratos de herramientas, validación de argumentos, flujo `tool_use`/`tool_result`, clientes y servidores MCP. |
| **D3** | Claude Code Configuration & Workflows | `CLAUDE.md`, permisos, hooks, skills, subagentes, herramientas de archivos y flujos de desarrollo. |
| **D4** | Prompt Engineering & Structured Output | Diseño de instrucciones, few-shot, esquemas, JSON, validación y evaluación de resultados. |
| **D5** | Context Management & Reliability | Ventana de contexto, memoria, RAG, caching, seguridad, observabilidad y recuperación ante fallos. |

## Itinerario de ocho días

| Día | Dominio | Contenidos | Material |
|---|---|---|---|
| **01** | D1 | Fundamentos de Claude, Messages API, tokens y ciclo de inferencia. | [Día 1](Checkpoints/Dia_1_D1_Fundamentos_de_Claude_y_Anthropic_API/) |
| **02** | D1 | Agentic loop, herramientas, decisiones y orquestación. | [Día 2](Checkpoints/Dia_2_D1_Arquitectura_agentica_y_orquestacion_con_Claude/) |
| **03** | D2 | Diseño de herramientas, clientes y servidores MCP, manejo de errores. | [Día 3](Checkpoints/Dia_3_D2_Herramientas_y_MCP/) |
| **04** | D3 | Claude Code, configuración, permisos, hooks, skills y subagentes. | [Día 4](Checkpoints/Dia_4_D3_Configuracion_y_Workflows_de_Claude_Code/) |
| **05** | D4 | Prompt engineering, extracción estructurada y validación. | [Día 5](Checkpoints/Dia_5_D4_Prompt_Engineering_&_Structured_Output/) |
| **06** | D5 | Gestión de contexto, recuperación, costes y fiabilidad. | [Día 6](Checkpoints/Dia_6_D5_Context_Management_&_Reliability_con_Claude/) |
| **07** | D1–D5 | Arquitectura integradora, decisiones técnicas y evaluación. | [Día 7](Checkpoints/Dia_7_D1_5_Simulacro_integrador_de_arquitectura_Claude/) |
| **08** | D1–D5 | Simulacro de certificación, corrección y análisis de errores. | [Día 8](Checkpoints/Dia_8_Simulacro/) |

## Documentación y recursos de consulta

El [índice de materiales](docs/INDICE.md) permite acceder directamente a las guías, prácticas y evaluaciones de cada jornada.

El [glosario técnico de los cinco dominios](docs/GLOSARIO_D1_D5.md) reúne definiciones y criterios de aplicación, e incorpora recursos específicos para resolver escenarios:

- [Matriz de distinciones conceptuales](docs/GLOSARIO_D1_D5.md#matriz-de-distinciones-conceptuales): compara 114 pares o grupos de términos, con criterios de elección y errores habituales.
- [Casos de aplicación](docs/GLOSARIO_D1_D5.md#casos-de-aplicación): relaciona problemas técnicos con decisiones arquitectónicas.
- [Guía de referencia y repaso](docs/GLOSARIO_D1_D5.md#guía-de-referencia-y-repaso): sintetiza patrones, herramientas, comandos y procedimientos de diagnóstico.
- [Referencias técnicas](docs/GLOSARIO_D1_D5.md#referencias-técnicas): enlaces a documentación de Anthropic, Claude Code y MCP.

## Estructura del repositorio

```text
claude-architect-foundations-es/
├── .github/workflows/       # Pruebas automatizadas
├── Checkpoints/             # Guías, prácticas y evaluaciones de los días 1–8
├── docs/
│   ├── GLOSARIO_D1_D5.md
│   └── INDICE.md
├── scripts/                 # Utilidades de pruebas y trabajo local
├── .env                     # Plantilla de variables de entorno
├── config.py                # Configuración Python
├── requirements.txt         # Dependencias compartidas
├── .gitignore
└── README.md
```

Cada carpeta de `Checkpoints/` contiene los materiales correspondientes a su jornada. Las prácticas pueden incluir scripts, notebooks, pruebas y configuraciones específicas del dominio.

## Instalación y configuración

**Requisitos recomendados:** Python 3.12, Git, VS Code y la extensión Jupyter. Para realizar solicitudes reales a Claude se necesita una clave de Anthropic API; las pruebas locales pueden ejecutarse sin ella.

En **Git Bash (Windows)**, desde la ubicación donde quieras guardar el proyecto:

```bash
git clone https://github.com/rafaneda7/claude-architect-foundations-es.git
cd claude-architect-foundations-es

python -m venv .venv
source .venv/Scripts/activate

python -m pip install -r requirements.txt
```

Para las prácticas que utilicen la API, crea un archivo `.env` a partir de la plantilla y configura allí tu clave:

```bash
cp .env.example .env
```

Selecciona el intérprete de `.venv` como kernel de los notebooks en VS Code. Revisa las dependencias específicas de cada jornada cuando su guía las indique.

## Ejecución de pruebas y simulacros

Desde la raíz del proyecto, las pruebas unitarias disponibles pueden ejecutarse sin llamadas a la API:

```bash
python scripts/ejecutar_pruebas.py
```

Para preparar el **simulacro final**, consulta la [guía del Día 8](Checkpoints/Dia_8_Simulacro/GUIA_DIA_08_COMPLETA.md) o abre el [simulador interactivo HTML](Checkpoints/Dia_8_Simulacro/simulacro_dia8.html). La práctica contempla **60 preguntas y 120 minutos**.

También puedes realizar el [examen en Markdown](Checkpoints/Dia_8_Simulacro/EXAMEN_DIA_08.md) y contrastar tus respuestas con el [solucionario](Checkpoints/Dia_8_Simulacro/SOLUCIONARIO_DIA_08.md) al finalizar.

Para corregir una hoja de respuestas desde la terminal:

```bash
cd Checkpoints/Dia_8_Simulacro
cp respuestas.example.json respuestas.json
python corrector_dia8.py respuestas.json
```

Las puntuaciones y objetivos de las actividades del repositorio son **referencias pedagógicas**; no equivalen a la calificación oficial de la certificación.

## Seguridad y buenas prácticas

No subas claves de API, archivos `.env`, entornos `.venv`, historiales locales ni respuestas personales. Revisa especialmente las salidas de los notebooks antes de publicar cambios. El archivo `.gitignore` evita incorporar determinados archivos nuevos, pero no elimina los secretos que ya se hayan registrado en Git.

Para ejercicios que puedan consumir créditos de API, verifica el modelo, los límites de tokens y la configuración antes de ejecutar solicitudes reales.

## Documentación oficial

- [Anthropic API](https://platform.claude.com/docs/en/home)
- [Claude Code](https://code.claude.com/docs/en/overview)
- [Model Context Protocol](https://modelcontextprotocol.io/)

La disponibilidad de funciones, los identificadores de modelos y los requisitos de certificación pueden cambiar. Consulta la documentación correspondiente a la versión que utilices.

## Autoría

**Rafael Neda Perdomo**  
Proyecto de estudio y divulgación técnica en español.

[GitHub](https://github.com/rafaneda7) · [LinkedIn](https://www.linkedin.com/in/rafael-neda/) · [Repositorio](https://github.com/rafaneda7/claude-architect-foundations-es)
