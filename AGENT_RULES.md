# AGENT_RULES.md  
## Protocolo operativo del sistema híbrido de agentes (Local + Replit + Premium)

---

## 1. PROPÓSITO DEL SISTEMA

Este sistema tiene como objetivo:

- Orquestar el desarrollo asistido por IA de forma controlada y trazable
- Maximizar el uso de capacidades locales
- Minimizar consumo de tokens externos
- Mantener memoria persistente del proyecto
- Integrar de forma eficiente:
  - Agente local de orquestación
  - Continue (copiloto)
  - OpenCode (ejecución técnica)
  - Replit (agente híbrido)
  - Modelos premium (criterio experto)

---

## 2. ROLES DEL SISTEMA

### 2.1 Agente de Orquestación Local

Es el núcleo del sistema.

Responsabilidades:

- recorrer el contexto total del proyecto
- filtrar y construir contexto relevante
- generar planes
- coordinar interacción entre agentes
- mantener documentación viva
- decidir cuándo escalar

---

### 2.2 Continue (Copiloto)

Responsable de:

- interacción con el usuario
- interpretación de solicitudes
- generación de planes iniciales
- síntesis de información
- construcción de respuesta unificada

---

### 2.3 OpenCode (Agente Técnico)

Responsable de:

- análisis técnico del repositorio
- validación de planes contra código real
- ejecución de cambios
- generación de archivos
- ejecución de comandos

---

### 2.4 Replit (Agente Híbrido)

Cumple doble función:

#### a. Validación continua

- valida planes
- confirma enfoque
- aporta mejoras si hay valor
- evita redundancia

#### b. Ejecución avanzada

- debugging complejo
- pruebas en entorno real
- despliegue
- validación de arquitectura

---

### 2.5 Modelos Premium

Se usan para:

- razonamiento complejo
- arquitectura crítica
- decisiones de alto impacto
- validación cuando hay incertidumbre

---

## 3. PRINCIPIO DE CONTEXTO

El agente local mantiene acceso total al contexto del proyecto:

- código
- documentación
- decisiones
- errores
- pruebas
- diffs
- logs
- configuraciones

---

### 3.1 Regla clave

NO se envía todo el contexto.

Siempre:

1. recorrer contexto completo
2. identificar relevancia
3. filtrar ruido
4. estructurar información
5. construir ventana depurada

---

## 4. PROTOCOLO DE CONCERTACIÓN INTER-AGENTE

Para tareas medianas o complejas:

### 4.1 Paso 1 – Plan inicial

Continue genera:

- interpretación de la solicitud
- plan propuesto

---

### 4.2 Paso 2 – Validación técnica

OpenCode en modo análisis:

- revisa plan contra código real
- identifica riesgos
- propone ajustes

---

### 4.3 Paso 3 – Síntesis

Continue:

- integra plan + validación técnica
- construye plan unificado

---

### 4.4 Regla clave

Debe existir una sola versión final del plan.

No se permite ejecución sin síntesis.

---

## 5. CICLO OPERATIVO ESTÁNDAR

### 5.1 Fase 1 – Solicitud

Usuario define requerimiento

---

### 5.2 Fase 2 – Construcción de contexto

Agente local:

- recorre documentación
- selecciona información relevante

---

### 5.3 Fase 3 – Planificación

- Continue propone plan
- OpenCode valida
- Continue sintetiza

---

### 5.4 Fase 4 – Validación con Replit (modo plan)

Replit:

- confirma enfoque
- aporta solo si agrega valor

---

### 5.5 Fase 5 – Ejecución

OpenCode:

- aplica cambios
- genera código
- ejecuta tareas

---

### 5.6 Fase 6 – Validación local

- pruebas
- revisión técnica
- análisis de resultados

---

### 5.7 Fase 7 – Documentación

Actualizar:

- PROJECT_CONTEXT.md
- decisiones
- errores
- resultados

---

### 5.8 Fase 8 – Validación con Replit (post-ejecución)

Replit:

- valida conformidad
- identifica mejoras

---

### 5.9 Fase 9 – Iteración

Si hay observaciones:

→ se reinicia el ciclo

---

## 6. ESCALAMIENTO A PREMIUM

Se activa cuando:

- capacidades locales son insuficientes
- Replit no resuelve el problema
- alta criticidad
- solicitud del usuario

---

### 6.1 Regla

El escalamiento debe ser:

- consciente
- justificado
- documentado

---

## 7. DOCUMENTACIÓN VIVA

Debe registrarse TODO:

- solicitudes
- planes
- validaciones
- errores
- pruebas
- diffs
- decisiones
- feedback de Replit
- ajustes
- aprendizajes

---

### 7.1 Objetivo

Construir memoria progresiva que:

- mejore decisiones futuras
- reduzca errores
- optimice contexto

---

## 8. CONTROL DE CAMBIOS

Antes de ejecutar:

- identificar impacto
- definir alcance

Después:

- validar resultado
- documentar cambios
- preparar commit

---

## 9. GIT (OBLIGATORIO)

Todo cambio debe:

- ser versionado
- tener mensaje claro
- ser reversible

---

## 10. SEGURIDAD

El sistema NO debe:

- exponer credenciales
- ejecutar comandos riesgosos sin control
- acceder fuera del proyecto sin autorización

---

## 11. PRINCIPIOS OPERATIVOS CLAVE

El sistema prioriza:

- coherencia sobre velocidad
- trazabilidad sobre automatización
- calidad sobre rapidez
- control sobre delegación

---

## 12. CRITERIO DE FINALIZACIÓN

Una tarea se considera completa cuando:

- cumple requerimiento funcional
- pasa validaciones
- está documentada
- está versionada
- ha sido validada por Replit si aplica

---

## 13. EVOLUCIÓN

Este documento:

- debe evolucionar
- debe adaptarse al proyecto
- debe enriquecerse con la experiencia

Pero nunca debe comprometer:

- seguridad
- trazabilidad
- control del sistema