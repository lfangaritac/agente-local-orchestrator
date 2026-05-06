# Agent Runs

## Propósito

Bitácora visible de flujos de orquestación.

Cada ejecución relevante debe tener una carpeta propia:

`docs/agent_runs/<run-id>/`

## Estructura sugerida

- `RUN_SUMMARY.md`
- `TRACE.md`
- `handoffs/`
- `agent_outputs/`
- `decisions/`
- `escalations/`

## Criterio de transparencia

El usuario debe poder revisar:

- qué agente intervino;
- qué modelo se usó;
- qué contexto se consultó;
- qué alertas aplicaron;
- qué lecciones fueron relevantes;
- qué decisión tomó cada agente;
- qué quedó pendiente;
- qué requiere autorización humana.
