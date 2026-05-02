# CONTINUE_USAGE_PROTOCOL.md

## Propósito

Guía operativa mínima para usar Continue dentro de VS Code.

## Archivos que Continue debe considerar

- AGENT_RULES.md
- PROJECT_CONTEXT.md
- MODEL_ROUTING.md
- SECURITY_POLICY.md
- REPLIT_HANDOFF.md
- PROJECT_ACTIVATION_PROTOCOL.md
- SECRETS_MANIFEST.md

## Prompts sugeridos

### Revisar contexto

Revisa AGENT_RULES.md, PROJECT_CONTEXT.md, MODEL_ROUTING.md y SECURITY_POLICY.md. Luego resume qué debes tener en cuenta antes de modificar este proyecto.

### Elegir modelo/agente

Según MODEL_ROUTING.md, clasifica esta tarea y dime si conviene resolverla con Continue, OpenCode, Replit o un modelo premium.

### Preparar tarea para OpenCode

Prepara una tarea estructurada para OpenCode con objetivo, alcance, archivos relevantes, restricciones, pruebas esperadas y formato de handoff.

### Preparar handoff para Replit

Usando REPLIT_HANDOFF.md, prepara un handoff compacto para Replit con el contexto mínimo necesario, cambios recientes, pruebas y pregunta concreta.

## Límites

Continue no debe inventar secrets, asumir comandos no verificados, hacer cambios multiarchivo complejos sin plan, modificar seguridad o despliegue sin revisión ni sustituir pruebas reales.
