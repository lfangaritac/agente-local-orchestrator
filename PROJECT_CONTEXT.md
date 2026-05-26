# PROJECT_CONTEXT.md

---

## 1. PROPÓSITO

Este documento define la arquitectura, principios operativos y contexto estructural del sistema de agente híbrido local + Replit + modelos premium.

Su objetivo es:

- consolidar la lógica del sistema;
- garantizar coherencia entre componentes;
- servir como fuente de contexto para agentes;
- evolucionar como memoria viva del proyecto.

---

## 2. VISIÓN GENERAL DEL SISTEMA

El sistema es una arquitectura híbrida de agentes donde:

- un agente local orquesta;
- múltiples modelos locales ejecutan tareas;
- Replit actúa como agente híbrido de validación;
- modelos premium se utilizan bajo criterios controlados.

El sistema no depende de un modelo, sino de la **orquestación inteligente del contexto y capacidades**.

---

## 3. PRINCIPIOS FUNDAMENTALES

### 3.1 Orquestación sobre modelos

El valor del sistema no está en los modelos, sino en:

- la orquestación;
- la gestión del contexto;
- la trazabilidad;
- la validación estructurada.

---

### 3.2 Contexto como activo principal

El sistema debe:

- conservar el contexto completo del proyecto;
- construir contextos parciales optimizados por tarea;
- evitar enviar contexto irrelevante a modelos externos.

---

### 3.3 Trazabilidad total

Cada acción relevante debe quedar registrada:

- decisiones;
- instrucciones;
- errores;
- soluciones;
- cambios en código;
- validaciones.

---

### 3.4 Minimización de costo externo

El sistema debe:

1. resolver localmente;
2. validar externamente solo cuando aporte valor;
3. escalar solo cuando sea necesario.

---

### 3.5 Evolución continua

El sistema no es estático.

Debe:

- aprender de cada interacción;
- mejorar sus reglas;
- enriquecer su contexto;
- optimizar su comportamiento.

---

## 4. ARQUITECTURA DEL AGENTE LOCAL

---

### 4.1 Agente de Orquestación Local

El agente de orquestación local no es una única herramienta.

Es una **capa lógica compuesta por**:

- usuario;
- documentación viva (Markdown);
- Continue;
- Codex en VS Code (superficie equivalente a Continue);
- OpenCode;
- modelos locales (Ollama);
- Git;
- reglas operativas;
- futuras herramientas (scripts, MCP, CLI).


---

### 4.2 Responsabilidades del Agente Local

- recorrer el contexto completo del proyecto;
- identificar información relevante;
- construir ventanas de contexto optimizadas;
- coordinar la interacción entre agentes;
- definir cuándo usar modelos locales;
- definir cuándo validar con Replit;
- definir cuándo escalar a modelos premium;
- documentar cada paso relevante;
- mantener coherencia global del sistema.

---

### 4.3 Concertación entre Continue y OpenCode

Continue y OpenCode:

- acceden al mismo contexto relevante;
- analizan desde perspectivas distintas;
- aportan criterio dentro de su dominio;
- no actúan de forma autónoma descontrolada.

El sistema debe generar una **salida unificada**, no respuestas paralelas.

---

### 4.4 Continue

Rol:

- interpretación de instrucciones del usuario;
- comprensión semántica;
- construcción de contexto;
- generación de planes;
- síntesis de respuestas;
- coordinación conversacional.

Continue lidera la **fase de planeación y estructuración**.

### 4.4.1 Codex en VS Code (equivalente operativo)

Cuando el usuario inicia el trabajo desde Codex en Visual Studio Code, Codex asume el rol operativo que normalmente cumpliría Continue para esa sesión:

- curación de contexto;
- clasificación de tarea;
- preparación de instrucciones/handoffs;
- revisión y reporte.

Modo integrado (Codex contexto + codificación) solo por solicitud expresa del usuario y bajo `SECURITY_POLICY.md` + `DEVELOPMENT_CHECKS.md`.


---

### 4.5 OpenCode

Rol:

- análisis técnico del repositorio;
- validación de planes contra código real;
- identificación de riesgos de implementación;
- ejecución de cambios;
- generación de diffs;
- ejecución de pruebas;
- preparación de handoff técnico.

OpenCode participa en:

- validación técnica del plan;
- ejecución controlada de instrucciones.

---

## 5. MODELOS LOCALES

Modelos disponibles:

- Qwen (principal)
- DeepSeek (análisis)
- Mistral (fallback)

Uso:

- desarrollo estándar;
- análisis técnico;
- tareas de bajo costo;
- pre-validación antes de escalar.

---

## 6. REPLIT COMO AGENTE HÍBRIDO

Replit cumple dos roles:

---

### 6.1 Validación de planes

- recibe contexto filtrado;
- evalúa plan propuesto;
- responde con:
  - validación;
  - observaciones puntuales.

Debe evitar:

- redundancia;
- reescritura completa innecesaria.

---

### 6.2 Revisión técnica avanzada

- arquitectura;
- coherencia global;
- seguridad;
- calidad de solución.

Replit no reemplaza al agente local, lo complementa.

---

## 7. ESCALAMIENTO A MODELOS PREMIUM

Se activa cuando:

- el agente local detecta limitaciones;
- Replit lo recomienda;
- el usuario lo solicita.

Criterios:

- alta complejidad;
- ambigüedad;
- impacto crítico;
- necesidad de razonamiento profundo.

---

## 8. FLUJO OPERATIVO DEL SISTEMA

Flujo estándar:

1. Usuario emite instrucción
2. Agente local recorre contexto completo
3. Se construye contexto relevante
4. Continue genera plan
5. OpenCode valida factibilidad técnica
6. Se genera plan unificado
7. Replit valida (según criticidad)
8. OpenCode ejecuta cambios
9. Se ejecutan pruebas
10. Replit valida resultado
11. Se documenta
12. Se versiona en Git

---

## 9. GESTIÓN DEL CONTEXTO

El sistema debe mantener:

- documentación estructurada;
- historial de decisiones;
- contexto técnico del código;
- logs de errores y soluciones;
- evolución del proyecto.

El agente local actúa como **curador del contexto**.

---

## 10. MEMORIA VIVA DEL PROYECTO

El proyecto no depende de memoria de modelo.

Depende de:

- archivos Markdown;
- commits en Git;
- estructura documental;
- reglas operativas.

---

## 11. RELACIÓN CON GIT

Git es:

- registro de cambios;
- fuente de verdad;
- mecanismo de trazabilidad;
- base para reconstrucción de contexto.

Cada cambio relevante debe:

- documentarse;
- versionarse;
- justificarse.

---

## 12. CRITERIO DE FINALIZACIÓN

Una tarea se considera finalizada cuando:

- el código funciona correctamente;
- las pruebas pasan;
- la solución es coherente;
- la arquitectura es válida;
- la documentación está actualizada;
- el cambio está versionado.

---

## 13. EVOLUCIÓN

Este documento:

- debe evolucionar continuamente;
- debe adaptarse al proyecto;
- debe enriquecerse con la experiencia;
- debe incorporar mejoras del sistema.

No es un documento estático.

Es parte del sistema.

---