# Agent Queue

## Propósito

Carpeta operativa para soportar la fase semiautomática de mini-orquestación entre Continue, OpenCode, Zen, Replit y modelos premium.

Esta cola permite registrar solicitudes, handoffs, respuestas, validaciones, escalamiento y resultados sin depender exclusivamente de copiar y pegar manualmente entre chats.

## Estructura

- `inbox/`: solicitudes o paquetes pendientes para un agente.
- `outbox/`: resultados devueltos por un agente.
- `runs/`: trazabilidad de ejecuciones.
- `escalations/`: paquetes canónicos para Zen, premium o Replit.

## Regla

Todo paquete debe conservar:

- `run_id`
- `step_id`
- `project_id`
- `source_agent`
- `target_agent`
- `scenario`
- `risk_level`
- `information_volume`
- `model_decision`
- `context_sources`
- `alerts_checked`
- `lessons_checked`
- `status`
- `result`
