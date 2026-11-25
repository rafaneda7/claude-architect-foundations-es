# Fundamentos de Claude Architect --- Solucionario

## Distribución de la evaluación

  Parte       Ejercicio                          Puntuación
  ----------- ---------------------------- ----------------
  A           10 preguntas tipo test              40 puntos
  B           3 preguntas técnicas                30 puntos
  C           1 escenario arquitectónico          20 puntos
  D           1 ejercicio Python                  10 puntos
  **TOTAL**                                  **100 puntos**

> Este documento contiene las respuestas correctas del test y respuestas
> modelo para las preguntas de desarrollo. En las preguntas abiertas
> pueden existir otras soluciones válidas si están técnicamente
> justificadas.

------------------------------------------------------------------------

# PARTE A --- TEST DE CONOCIMIENTOS

**Valor: 40 puntos · 4 puntos por pregunta**

  -----------------------------------------------------------------------
  Pregunta                Respuesta               Justificación
  ----------------------- ----------------------- -----------------------
  1                       **B**                   Un LLM procesa
                                                  información de entrada
                                                  y genera respuestas. No
                                                  sustituye por sí mismo
                                                  a la base de datos, al
                                                  gestor de sesiones ni
                                                  al entorno de
                                                  ejecución.

  2                       **B**                   La API define la
                                                  interfaz y las reglas
                                                  de comunicación. El SDK
                                                  es una biblioteca que
                                                  facilita consumir esa
                                                  API desde un lenguaje
                                                  de programación.

  3                       **B**                   En Messages API, las
                                                  instrucciones iniciales
                                                  del sistema se
                                                  proporcionan mediante
                                                  el parámetro superior
                                                  `system`.

  4                       **C**                   Claude solo dispone del
                                                  contexto incluido en la
                                                  solicitud actual. La
                                                  aplicación debe
                                                  reenviar los mensajes
                                                  anteriores que quiera
                                                  mantener como contexto.

  5                       **B**                   `max_tokens` establece
                                                  el máximo de tokens que
                                                  puede generar la
                                                  respuesta.

  6                       **A**                   `response.usage`
                                                  contiene información de
                                                  utilización, incluidos
                                                  los tokens de entrada y
                                                  salida.

  7                       **C**                   El streaming permite
                                                  recibir partes de la
                                                  respuesta a medida que
                                                  se generan, en lugar de
                                                  esperar a que termine
                                                  toda la generación.

  8                       **B**                   Un HTTP 401 indica un
                                                  problema de
                                                  autenticación. Se debe
                                                  revisar la API Key y la
                                                  configuración de
                                                  autenticación.

  9                       **C**                   Para un chatbot
                                                  sencillo, backend, SDK,
                                                  Messages API y gestión
                                                  de sesiones son una
                                                  arquitectura inicial
                                                  razonable.

  10                      **C**                   La selección del modelo
                                                  debe basarse en pruebas
                                                  de capacidad, coste,
                                                  latencia y calidad para
                                                  el caso de uso
                                                  concreto.
  -----------------------------------------------------------------------

**Plantilla de respuestas:** 1-B · 2-B · 3-B · 4-C · 5-B · 6-A · 7-C ·
8-B · 9-C · 10-C

------------------------------------------------------------------------

# PARTE B --- RAZONAMIENTO TÉCNICO

**Valor: 30 puntos · 10 puntos por pregunta**

## Pregunta 11 --- Gestión de sesiones

**Enunciado:** Una aplicación mezcla información de distintos usuarios
entre conversaciones.

### Respuesta modelo

1.  **Posible fallo arquitectónico:** puede existir un historial
    compartido entre usuarios, por ejemplo, una variable global en
    memoria, o una consulta a la base de datos que no filtre
    correctamente por usuario y conversación.
2.  **Componente responsable:** normalmente el backend o la capa de
    gestión de sesiones e historial. También debe revisarse la consulta
    y el esquema de persistencia.
3.  **Solución:** cada conversación debe estar asociada a un usuario
    autenticado. El backend debe recuperar el historial utilizando
    identificadores de usuario y conversación, y comprobar que el
    usuario tiene permiso para acceder a ella.
4.  **Medidas preventivas:**
    -   Autenticar al usuario en cada solicitud.
    -   Aplicar autorización antes de leer o modificar una conversación.
    -   Evitar variables globales para almacenar historiales de
        usuarios.
    -   Asociar cada conversación con su propietario en la base de
        datos.
    -   Aplicar filtros por usuario en todas las consultas.
    -   Añadir pruebas que verifiquen que un usuario no puede acceder a
        conversaciones ajenas.
    -   Registrar errores de autorización y accesos anómalos.

**Idea clave:** el aislamiento no debe depender de que Claude distinga a
los usuarios. Es responsabilidad de la aplicación y del backend.

## Pregunta 12 --- Gestión del contexto

**Enunciado:** Una empresa almacena 50 turnos y envía todo el historial
en cada solicitud.

### Respuesta modelo

1.  **Problemas:** se envía información que puede no ser relevante,
    aumenta el tamaño de las solicitudes y puede acercarse al límite de
    contexto del modelo. También se puede introducir ruido que dificulte
    identificar la información importante.
2.  **Consumo de tokens:** los mensajes anteriores se vuelven a enviar
    como parte del contexto de cada solicitud, por lo que se consumen
    tokens de entrada repetidamente.
3.  **Latencia y costes:** un contexto más grande puede aumentar el
    tiempo de procesamiento y el coste asociado al uso de tokens. El
    impacto concreto depende del modelo, del volumen y de la estrategia
    de uso.
4.  **Medidas de optimización:**
    -   **Resumen de conversación:** mantener un resumen actualizado de
        los hechos y decisiones relevantes de los turnos anteriores.
    -   **Selección de contexto:** combinar el resumen con los mensajes
        recientes y recuperar información adicional solo cuando sea
        pertinente para la petición actual.

**Idea clave:** no se trata de conservar únicamente los últimos
mensajes, sino de conservar la información útil para responder
correctamente.

## Pregunta 13 --- Responsabilidades arquitectónicas

**Enunciado:** ¿Por qué no debe delegarse toda la lógica empresarial en
Claude?

### Respuesta modelo

1.  **Inferencia:** proceso mediante el cual el modelo recibe una
    entrada y genera una salida a partir de su entrenamiento y del
    contexto proporcionado.
2.  **Ejecución:** realización de operaciones concretas por parte de la
    aplicación, como consultar una base de datos, ejecutar una función,
    validar permisos o llamar a un servicio externo.
3.  **Persistencia:** almacenamiento y recuperación de información para
    que permanezca disponible entre solicitudes. Normalmente se realiza
    mediante una base de datos u otro sistema de almacenamiento
    controlado por la aplicación.
4.  **Responsabilidades que conserva el backend:**
    -   Autenticación y autorización.
    -   Validación de entradas y salidas.
    -   Reglas de negocio.
    -   Ejecución controlada de herramientas y operaciones.
    -   Acceso a bases de datos y persistencia.
    -   Gestión de errores y límites.
    -   Protección de credenciales y secretos.
    -   Registro, auditoría y monitorización.
5.  **Riesgos de delegar demasiado control:** respuestas incorrectas o
    no deterministas, ejecución de operaciones no autorizadas,
    exposición de información sensible, incumplimiento de reglas de
    negocio, pérdida de trazabilidad y dificultad para auditar o
    reproducir errores.

**Idea clave:** Claude puede interpretar, razonar y proponer acciones;
el backend valida y controla qué acciones se ejecutan realmente.

------------------------------------------------------------------------

# PARTE C --- ESCENARIO ARQUITECTÓNICO

**Valor: 20 puntos**

## Pregunta 14 --- Diseño de un asistente empresarial

### Respuesta modelo

Para una academia con 500 usuarios, utilizaría una arquitectura
cliente-servidor con un backend que centralice la autenticación, la
autorización, la lógica de negocio, la comunicación con Claude y la
persistencia.

### 1. Componentes

  -----------------------------------------------------------------------
  Componente                          Responsabilidad
  ----------------------------------- -----------------------------------
  Frontend                            Interfaz utilizada por los
                                      instructores para enviar preguntas
                                      y consultar respuestas.

  Backend (por ejemplo, FastAPI)      Recibir solicitudes, autenticar
                                      usuarios, validar permisos,
                                      gestionar contexto y coordinar
                                      servicios.

  Anthropic Python SDK                Facilitar las llamadas desde Python
                                      a Messages API.

  Claude Messages API                 Procesar el contexto y generar
                                      respuestas.

  PostgreSQL                          Almacenar usuarios, conversaciones,
                                      mensajes, alumnos, proyectos y
                                      entregas.

  Sistema de logging y métricas       Registrar solicitudes, errores,
                                      latencia y consumo de tokens.

  Gestor de secretos o variables de   Proteger la API Key y otras
  entorno                             credenciales.
  -----------------------------------------------------------------------

### 2. Flujo de una solicitud

1.  El instructor escribe una pregunta en el frontend.
2.  El frontend envía la solicitud al backend junto con sus credenciales
    de autenticación.
3.  El backend identifica al usuario y comprueba que está autorizado
    para consultar los alumnos o proyectos solicitados.
4.  El backend recupera de PostgreSQL el historial y los datos
    relevantes.
5.  El backend construye el contexto y envía la solicitud a Claude
    mediante el SDK y Messages API.
6.  Claude genera una respuesta.
7.  El backend procesa la respuesta, gestiona posibles errores y aplica
    las validaciones necesarias.
8.  El backend almacena el mensaje y los metadatos de uso.
9.  El frontend recibe y muestra la respuesta en español.

### 3. Almacenamiento de datos

En PostgreSQL almacenaría, como mínimo:

-   **Usuarios:** identificador, datos de cuenta y permisos.
-   **Conversaciones:** identificador, propietario, fecha de creación y
    estado.
-   **Mensajes:** conversación asociada, rol, contenido y fecha.
-   **Alumnos:** identificador y datos académicos autorizados.
-   **Proyectos y entregas:** información académica y relaciones
    correspondientes.
-   **Uso de API:** modelo, tokens de entrada, tokens de salida, fecha,
    latencia y coste calculado cuando se disponga de la tarifa
    aplicable.

Las tablas de conversaciones y mensajes deben permitir filtrar y
comprobar la propiedad de cada conversación. Las consultas sobre alumnos
y proyectos también deben respetar los permisos del instructor.

### 4. Respuestas en español

No es necesario incorporar automáticamente un servicio de traducción. Se
puede indicar en el parámetro `system` que Claude debe responder en
español. El backend también puede validar o controlar el idioma cuando
sea un requisito estricto.

### 5. Seguridad y observabilidad

-   Mantener la API Key exclusivamente en el backend.
-   No confiar en identificadores de usuario enviados por el frontend
    sin validarlos.
-   Comprobar los permisos antes de recuperar datos.
-   Evitar que un instructor consulte información de alumnos fuera de su
    ámbito.
-   Registrar errores, latencia y consumo de tokens.
-   Evitar guardar secretos o datos sensibles innecesarios en los logs.

**Idea clave:** PostgreSQL conserva los datos y el historial; el backend
controla el acceso y la lógica; Claude se encarga de la inferencia y
generación de respuestas.

------------------------------------------------------------------------

# PARTE D --- EJERCICIO PYTHON

**Valor: 10 puntos**

## Pregunta 15 --- Extracción de contenido de Messages API

### Solución

``` python
def extract_text(response) -> str:
    text_parts = []

    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)

    return "\n".join(text_parts)
```

### Ejemplo de uso

``` python
response = client.messages.create(
    model=CLAUDE_MODEL,
    max_tokens=MAX_OUTPUT_TOKENS,
    system=SYSTEM_PROMPT,
    messages=[
        {
            "role": "user",
            "content": "hola"
        }
    ]
)

result = extract_text(response)

print(result)
print(type(result))
```

### Resultado esperado

La función devuelve una cadena (`str`) con el contenido de todos los
bloques de tipo `text`, separados por saltos de línea.

### Pregunta adicional --- Bloques `tool_use` o `thinking`

La función debe ignorar los bloques cuyo tipo no sea `text`. Por tanto:

-   Los bloques `tool_use` no se añaden a la cadena.
-   Los bloques `thinking` no se añaden a la cadena.
-   Los bloques `text` sí se incorporan al resultado.
-   Si no hay bloques de texto, devuelve una cadena vacía (`""`).

La función no debe intentar acceder a `block.text` en bloques de otros
tipos.

### Prueba conceptual

Si `response.content` contiene:

-   Un bloque `text` con `"Hola"`.
-   Un bloque `tool_use`.
-   Otro bloque `text` con `"¿En qué puedo ayudarte?"`.

El resultado será:

``` text
Hola
¿En qué puedo ayudarte?
```

Y `type(result)` devolverá:

``` python
<class 'str'>
```

------------------------------------------------------------------------

# CRITERIOS DE CORRECCIÓN

  ------------------------------------------------------------------------
  Parte                 Criterio principal                      Puntuación
  --------------------- --------------------- ----------------------------
  A --- Test            Selección de las                                40
                        respuestas correctas  

  B --- Razonamiento    Precisión conceptual,                           30
                        explicación y medidas 
                        técnicas              

  C --- Arquitectura    Componentes, flujo,                             20
                        persistencia,         
                        seguridad y           
                        observabilidad        

  D --- Python          Filtrado correcto,                              10
                        concatenación y tipo  
                        de retorno            

  **TOTAL**                                                        **100**
  ------------------------------------------------------------------------

## Escala de valoración

       Nota Nivel
  --------- --------------
    90--100 Excelente
     80--89 Muy bueno
     70--79 Bueno
     60--69 Básico
      0--59 Insuficiente

**Nota:** las respuestas de desarrollo son modelos de referencia, no la
única redacción válida. Se debe valorar que la solución propuesta sea
correcta, completa y esté bien argumentada.
