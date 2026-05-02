# CONTINUE_USAGE_PROTOCOL.md

## Propósito

Este documento define cómo usar Continue en VS Code dentro del orquestador local de agentes.

Continue debe operar como copiloto principal de análisis, revisión, edición menor, preparación de tareas para OpenCode y preparación de handoffs hacia Replit.

El objetivo es trabajar de forma eficiente, sin generar documentación innecesaria y sin perder trazabilidad.

---

## Rol de Continue

Continue cumple estas funciones:

1. Leer y usar el contexto del proyecto.
2. Ayudar a clasificar tareas.
3. Recomendar modelo, agente o entorno según `MODEL_ROUTING.md`.
4. Proponer cambios controlados.
5. Ejecutar ediciones menores cuando el riesgo sea bajo.
6. Preparar tareas estructuradas para OpenCode.
7. Preparar handoffs compactos para Replit.
8. Revisar diffs, errores, logs y resultados de pruebas.
9. Ayudar a actualizar documentación mínima cuando haya cambios reales.

Continue no debe actuar como ejecutor autónomo de cambios complejos sin plan.

---

## Archivos de contexto que debe revisar

Antes de trabajar sobre un proyecto activado, Continue debe considerar estos archivos:

```text
AGENT_RULES.md
PROJECT_CONTEXT.md
MODEL_ROUTING.md
SECURITY_POLICY.md
REPLIT_HANDOFF.md
PROJECT_ACTIVATION_PROTOCOL.md
SECRETS_MANIFEST.md
QUICK_START.md
