# REPLIT_HANDOFF.md

---

## 1. PROPÓSITO

Definir cómo interactuar con Replit como agente híbrido dentro del sistema.

El objetivo es:

- maximizar valor de validación
- minimizar consumo de tokens
- evitar respuestas redundantes
- obtener feedback técnico preciso

---

## 2. PRINCIPIO FUNDAMENTAL

Replit NO es un generador principal.

Replit es:

- validador de planes
- revisor técnico
- verificador de calidad

---

## 3. TIPOS DE INTERACCIÓN

---

### 3.1 Validación de plan

Uso:

- antes de ejecutar cambios
- en tareas complejas
- en decisiones arquitectónicas

Entrada a Replit:

- contexto filtrado
- plan estructurado

Salida esperada:

- ✔ validación (si es correcto)
- ⚠ observaciones puntuales (si aplica)

Formato esperado:

- respuestas cortas
- sin reescritura completa
- sin redundancia

---

### 3.2 Revisión de implementación

Uso:

- después de ejecutar cambios
- antes de cerrar tarea

Entrada:

- resumen de cambios
- diffs relevantes
- objetivo inicial

Salida esperada:

- validación de coherencia
- detección de problemas
- sugerencias puntuales

---

### 3.3 Validación arquitectónica

Uso:

- cambios estructurales
- decisiones de diseño
- integraciones complejas

Entrada:

- contexto estructurado
- propuesta de arquitectura

Salida esperada:

- evaluación crítica
- riesgos
- recomendaciones

---

## 4. FORMATO DE HANDOFF

---

### 4.1 Estructura de entrada

Siempre enviar:

- objetivo
- contexto relevante (NO completo)
- plan o cambios realizados

Ejemplo:


Objetivo:
[descripción clara]

Contexto relevante:
[solo lo necesario]

Plan / Cambios:
[resumen estructurado]


---

### 4.2 Reglas de contenido

NO enviar:

- historial completo
- documentación innecesaria
- contexto redundante

SÍ enviar:

- información precisa
- contexto filtrado
- datos estructurados

---

## 5. EXPECTATIVA DE RESPUESTA

---

### 5.1 Respuesta ideal

- breve
- técnica
- directa
- sin redundancia

---

### 5.2 Tipos de respuesta

1. Validación:

✔ "El enfoque es correcto."

2. Validación con mejora:

✔ "El enfoque es correcto, pero considera..."

3. Corrección:

⚠ "Hay un problema en..."

---

### 5.3 Respuesta NO deseada

- reescritura completa del código
- explicaciones extensas
- respuestas genéricas
- duplicación del plan

---

## 6. CRITERIOS PARA USAR REPLIT

---

### 6.1 CUÁNDO usarlo

- tareas complejas
- impacto arquitectónico
- incertidumbre técnica
- validación final

---

### 6.2 CUÁNDO NO usarlo

- tareas simples
- cambios menores
- debugging básico
- generación trivial

---

## 7. OPTIMIZACIÓN DE COSTO

---

### 7.1 Minimizar uso

Regla:

1. resolver localmente
2. validar solo si aporta valor

---

### 7.2 Minimizar tokens

El agente local debe:

- resumir
- estructurar
- filtrar

ANTES de enviar

---

## 8. INTEGRACIÓN EN EL FLUJO

---

Flujo:

1. Continue genera plan
2. OpenCode valida técnicamente
3. (Opcional) Replit valida plan
4. OpenCode ejecuta
5. Replit valida resultado
6. Continue documenta

---

## 9. PRINCIPIO CLAVE

Replit NO agrega valor por volumen de respuesta.

Agrega valor por:

- precisión
- criterio
- capacidad de detectar errores

---

## 10. EVOLUCIÓN

Este documento debe:

- ajustarse con experiencia real
- optimizar prompts
- reducir consumo de tokens
- mejorar calidad de validación