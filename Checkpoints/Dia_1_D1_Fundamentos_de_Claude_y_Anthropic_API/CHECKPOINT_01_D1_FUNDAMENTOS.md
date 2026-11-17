
# CHECKPOINT 01 — Fundamentos de Arquitectura con Claude

**Certificación:** Claude Certified Architect – Foundations (CCAR-F)  
**Dominio principal:** D1 · Agentic Architecture & Orchestration  
**Peso del dominio:** 27 %  
**Jornada:** Día 1 de 8  
**Estado:** 🟡 Fundamentos completados — dominio en progreso  
**Evaluación inicial:** 75/100

---

## 1. Objetivo del checkpoint

Comprender los componentes fundamentales de una aplicación
que utiliza Claude mediante una API, identificar las
responsabilidades del modelo y del backend y reconocer
los principios básicos de una arquitectura segura.

> Este checkpoint no representa la finalización del D1.
> Se han trabajado sus fundamentos arquitectónicos.

---

## 2. Contenidos estudiados

### 2.1. Fundamentos de los LLM

- [x] Qué es un Large Language Model (LLM).
- [x] Qué es la inferencia.
- [x] Diferencia entre modelo y aplicación.
- [x] Responsabilidades y limitaciones del LLM.
- [x] Generación de respuestas a partir del contexto.

**Concepto clave:**

El modelo procesa información de entrada y genera
una respuesta. No administra automáticamente usuarios,
bases de datos ni sesiones de una aplicación.

### 2.2. API y SDK

- [x] Qué es una API.
- [x] Diferencias entre API y SDK.
- [x] Comunicación cliente-servidor.
- [x] Introducción a HTTP y JSON.
- [x] Autenticación mediante API Key.
- [x] Introducción al SDK de Anthropic para Python.

**Concepto clave:**

La API define la interfaz de comunicación con el
servicio. El SDK proporciona herramientas para
interactuar con esa API desde un lenguaje como Python.

### 2.3. Messages API

- [x] Introducción a `client.messages.create()`.
- [x] Parámetros `model`, `max_tokens` y `messages`.
- [x] Uso del parámetro `system`.
- [x] Roles y estructura de mensajes.
- [x] Interpretación de `response.content`.
- [x] Lectura de `response.usage`.
- [x] Introducción a `stop_reason`.
- [x] Concepto de streaming.

**Concepto clave:**

Las instrucciones de sistema se envían mediante el
parámetro `system`. Los mensajes de la conversación
se envían en `messages`.

### 2.4. Arquitectura básica de una aplicación

- [x] Diferencia entre frontend, backend y LLM.
- [x] Responsabilidad del backend.
- [x] Introducción a la gestión de sesiones.
- [x] Introducción a la persistencia de datos.
- [x] Uso de PostgreSQL como posible almacenamiento.
- [x] Registro del consumo de tokens.
- [x] Separación entre lógica de negocio e inferencia.

**Flujo conceptual:**

```text
Usuario
   |
   v
Frontend
   |
   v
Backend
   |
   +--> Autenticación y autorización
   |
   +--> Recuperación del contexto autorizado
   |
   +--> Anthropic SDK / Messages API
   |         |
   |         v
   |       Claude
   |         |
   |         v
   |      Respuesta
   |
   +--> Validación y gestión de errores
   |
   +--> Persistencia y registro de uso
   |
   v
Frontend
   |
   v
Usuario
```

### 2.5. Contexto y sesiones

- [x] Qué es el contexto de una conversación.
- [x] Por qué el modelo no conserva automáticamente el historial.
- [x] Necesidad de enviar los mensajes relevantes.
- [x] Problemas de historiales demasiado extensos.
- [x] Introducción al resumen de conversaciones.
- [x] Riesgos de mezclar sesiones entre usuarios.

**Concepto clave:**

El backend debe recuperar únicamente el historial
autorizado para el usuario y conversación actuales.

Una estrategia de contexto puede combinar:

1. Resumen de mensajes antiguos.
2. Mensajes recientes.
3. Información relevante para la consulta.

### 2.6. Seguridad y confiabilidad

- [x] Identificación del riesgo de compartir historiales.
- [x] Introducción a autenticación y autorización.
- [x] Interpretación básica de errores HTTP.
- [x] Identificación del error 401.
- [x] Importancia de gestionar credenciales.
- [x] Introducción al manejo de errores del backend.

**Concepto clave:**

La autenticación identifica al usuario.

La autorización determina qué información y
operaciones puede utilizar ese usuario.

Ambas deben gestionarse desde la aplicación.

### 2.7. Procesamiento de respuestas con Python

- [x] Recorrer `response.content`.
- [x] Identificar bloques de tipo `text`.
- [x] Extraer el atributo `.text`.
- [x] Concatenar múltiples bloques de texto.
- [x] Diferenciar `return` de `print`.
- [x] Reconocer bloques que no contienen texto.

**Ejemplo práctico:**

```python
def extract_text(response) -> str:
    texts = []

    for block in response.content:
        if block.type == "text":
            texts.append(block.text)

    return "\n".join(texts)
```

La función ignora bloques no textuales, como
`tool_use` o `thinking`, y devuelve una cadena vacía
si no encuentra bloques de texto.