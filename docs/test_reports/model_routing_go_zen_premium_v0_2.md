# Reporte de implementación — Model Routing Go + Zen + Premium v0.2

## Fecha

2026-05-05

## Objetivo

Implementar documentalmente la arquitectura de modelos, agentes y orquestación para el uso coordinado de:

- Continue + Gemini API gratuita.
- OpenCode Go.
- OpenCode Zen como continuidad.
- OpenCode Zen como escalamiento económico o premium.
- Replit como entorno remoto de validación.

## Archivos actualizados o creados

- `AGENT_ORCHESTRATION.md`
- `MODEL_ROUTING.md`
- `AGENT_RULES.md`
- `CONTINUE_USAGE_PROTOCOL.md`
- `REPLIT_HANDOFF.md`
- `opencode.config.example.json`

## Decisiones implementadas

### 1. Go como primera línea

OpenCode Go será la primera línea operativa para tareas ordinarias:

- clasificación;
- validación de contexto;
- planificación simple/media;
- ejecución controlada;
- cambios pequeños;
- debugging moderado;
- revisión normal de diffs;
- documentación técnica no crítica;
- handoffs no críticos.

### 2. Zen como continuidad

Zen no se interpreta únicamente como premium.

Cuando Go se agote, Zen podrá continuar la tarea usando el mismo modelo si existe o un equivalente funcional.

### 3. Zen como escalamiento económico o premium

Zen económico se usará para continuidad, segundo criterio, contraste o volumen alto no sensible.

Zen premium se usará por:

- solicitud del usuario;
- seguridad;
- auth;
- permisos;
- secrets;
- datos personales;
- debugging crítico;
- arquitectura;
- migraciones;
- deployment;
- volumen alto sensible;
- revisión final sensible.

### 4. Transferencia de insumos

Cuando una tarea escala desde Go hacia Zen o premium, el resultado de primera línea debe convertirse en insumo estructurado.

El modelo escalado debe validar, corregir, completar o profundizar el resultado previo, no empezar desde cero.

### 5. Continue + Gemini

Continue queda definido como copiloto contextual, no como ejecutor principal de cambios críticos.

### 6. Replit

Replit queda definido como entorno remoto de validación, runtime, preview, secrets reales, deployment y pruebas de integración.

## Validación ejecutada

Se ejecutó una prueba de consistencia documental verificando que los archivos clave existen y contienen las secciones esperadas.

Resultado:

- OK: `AGENT_ORCHESTRATION.md`
- OK: `MODEL_ROUTING.md`
- OK: `AGENT_RULES.md`
- OK: `CONTINUE_USAGE_PROTOCOL.md`
- OK: `REPLIT_HANDOFF.md`
- OK: `opencode.config.example.json`

## Resultado

La arquitectura documental Go + Zen + Premium v0.2 quedó incorporada correctamente en el orquestador local.

## Próximos pasos recomendados

1. Revisar el archivo `opencode.config.example.json` contra la documentación oficial vigente de OpenCode antes de usarlo como configuración activa.
2. Definir dónde debe vivir la configuración real de OpenCode en este entorno.
3. Ejecutar una prueba controlada de flujo:
   - `classifier`
   - `context-validator`
   - `planner`
   - escalamiento simulado a premium.
4. Documentar resultados de la prueba controlada.
5. Luego decidir si se activa OpenCode Go y Zen en el entorno real.
