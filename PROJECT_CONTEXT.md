# PROJECT_CONTEXT.md
## Contexto vivo del proyecto — Agente Local + Replit + Premium

## 1. Propósito del proyecto

Construir una arquitectura híbrida de IA para apoyar desarrollo de software y gestión técnica de proyectos, combinando:

- entorno local de desarrollo;
- modelos locales vía Ollama;
- VS Code + Continue como copiloto;
- OpenCode como agente local operativo de codificación;
- Replit como agente híbrido de planificación, validación y ejecución avanzada;
- modelos premium como capa excepcional de razonamiento o ejecución crítica.

El objetivo no es reemplazar Replit ni modelos premium, sino optimizar su uso mediante contexto local persistente, planificación previa, filtrado de información y documentación continua.

---

## 2. Estado actual del entorno local

Equipo configurado con:

- Windows
- VS Code
- Git
- GitHub
- Python 3.13.13
- Docker Desktop
- Ollama
- Continue.dev
- Open WebUI vía Docker
- Repositorio local: `C:\Agente`
- Repositorio remoto: `https://github.com/lfangaritac/agente-local-orchestrator.git`

---

## 3. Modelos locales instalados

Modelos disponibles en Ollama:

- `qwen2.5-coder:7b`
- `deepseek-coder:6.7b`
- `mistral:7b`

Uso previsto:

- Qwen Coder: código diario, Flask, React, SQL, refactor básico.
- DeepSeek Coder: revisión técnica, debugging, código más complejo.
- Mistral: análisis funcional, documentación, síntesis y planeación general.

---

## 4. Componentes de la arquitectura

### 4.1 Agente de Orquestación Local

Actualmente es una capa lógica compuesta por:

- usuario;
- documentación viva;
- Continue;
- modelos locales;
- Git;
- reglas operativas.

A futuro podrá convertirse en un componente explícito mediante script, CLI, MCP server o agente local dedicado.

Responsabilidades:

- recorrer contexto total del proyecto;
- filtrar información relevante;
- construir ventanas depuradas de contexto;
- coordinar Continue, OpenCode, Replit y modelos premium;
- documentar decisiones, errores, aprendizajes y cambios;
- reducir consumo de tokens externos.

---

### 4.2 Continue

Rol:

- copiloto conversacional dentro de VS Code;
- interfaz de trabajo con modelos locales;
- generación de planes iniciales;
- análisis contextual;
- síntesis de respuestas;
- apoyo al usuario en lectura, edición y revisión.

Continue no debe entenderse como único orquestador definitivo, sino como interfaz/copiloto dentro del sistema de orquestación local.

---

### 4.3 OpenCode

Rol previsto:

- agente local especializado en codificación;
- operación sobre repositorio;
- creación y modificación de archivos;
- ejecución de comandos autorizados;
- generación de diffs;
- ejecución de pruebas;
- preparación de handoffs técnicos.

OpenCode no reemplaza a Continue ni a Replit. Actúa como ejecutor técnico local bajo reglas y trazabilidad.

---

### 4.4 Replit

Replit tiene doble rol:

1. Agente híbrido continuo:
   - planificación;
   - revisión;
   - validación;
   - arquitectura;
   - debugging;
   - ejecución en entorno Replit.

2. Capa de escalamiento avanzado:
   - cuando se requiere ejecución real;
   - cuando el entorno local es insuficiente;
   - cuando se requiere validación integrada, despliegue o revisión compleja.

La lógica deseada es que Replit no reciba contexto bruto, sino instrucciones depuradas y verificables generadas por el entorno local.

---

### 4.5 Modelos premium

Se consideran como soporte excepcional para:

- arquitectura crítica;
- razonamiento complejo;
- seguridad;
- fallos repetidos del loop local-Replit;
- decisiones de alto impacto.

El usuario podrá elegir entre opciones premium disponibles cuando el escalamiento sea necesario.

---

## 5. Flujo operativo deseado

1. Usuario plantea una necesidad.
2. Agente local recorre contexto total.
3. Agente local filtra y prepara contexto relevante.
4. Continue genera plan inicial.
5. OpenCode valida técnicamente contra el repositorio.
6. Continue sintetiza plan unificado.
7. Replit valida en modo plan si aplica.
8. OpenCode o entorno local ejecuta cambios.
9. Se ejecutan pruebas y revisión local.
10. Se actualiza documentación viva.
11. Se sincroniza código con Git/GitHub.
12. Replit valida conformidad si aplica.
13. Si hay observaciones, se reinicia el ciclo.
14. Si se superan capacidades locales o híbridas, se escala a modelo premium.

---

## 6. Principio de contexto vivo

Cada proyecto debe mantener documentación viva y acumulativa.

Debe registrarse:

- instrucciones relevantes;
- decisiones técnicas;
- planes;
- errores;
- pruebas;
- resultados;
- diffs;
- handoffs;
- feedback de Replit;
- aprendizajes;
- ajustes de arquitectura;
- criterios de escalamiento.

La documentación no debe simplificar aprendizajes previos válidos. Debe enriquecer progresivamente el contexto.

---

## 7. Archivos base del sistema

Este repositorio contiene:

- `AGENT_RULES.md`: protocolo operativo general.
- `PROJECT_CONTEXT.md`: contexto vivo principal.
- `MODEL_ROUTING.md`: criterios de selección de modelos.
- `REPLIT_HANDOFF.md`: reglas para entregar contexto a Replit.
- `SECURITY_POLICY.md`: reglas de seguridad y límites operativos.

---

## 8. Decisiones tomadas

- El agente local no reemplaza a Replit.
- El agente local debe funcionar como curador y orquestador de contexto.
- Replit participa como agente híbrido, no solo como escalamiento premium.
- Continue y OpenCode pueden participar en concertación estructurada, no en autonomía simultánea caótica.
- El sistema debe privilegiar trazabilidad, contexto depurado y control humano.
- GitHub `lfangaritac` será usado como identidad y repositorio remoto.
- El correo Git configurado es `felipe@onceasesores.net`.

---

## 9. Estado actual de Git

Repositorio local:

`C:\Agente`

Repositorio remoto:

`https://github.com/lfangaritac/agente-local-orchestrator.git`

Rama principal:

`main`

Primer commit realizado:

`Inicialización documentación base del agente local (rules, routing, context, seguridad, handoff)`

---

## 10. Próximos hitos

1. Completar `MODEL_ROUTING.md`.
2. Completar `REPLIT_HANDOFF.md`.
3. Completar `SECURITY_POLICY.md`.
4. Diseñar protocolo de concertación inter-agente.
5. Evaluar incorporación formal de OpenCode.
6. Definir protocolo `INIT_PROJECT`.
7. Construir router local v1.
8. Diseñar estructura de memoria por proyecto.
9. Integrar flujo GitHub/Replit.
10. Evaluar escalamiento premium bajo criterios técnicos y económicos.