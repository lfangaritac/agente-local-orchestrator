# PROJECT_ACTIVATION_PROTOCOL.md

## Propósito

Protocolo operativo mínimo para activar el sistema de agentes en un proyecto.

## Ciclo esperado

VS Code local -> Continue -> OpenCode o agente coder local -> Git/GitHub -> Replit -> pruebas, logs, documentación y handoff.

## Activación mínima

1. Crear núcleo documental.
2. Identificar stack.
3. Identificar secrets requeridos.
4. Crear SECRETS_MANIFEST.md.
5. Crear scripts/check_env.py.
6. Validar entorno.
7. Versionar cambios.
8. Probar en Replit cuando aplique.

## Criterio de éxito

El proyecto queda activado cuando puede ejecutarse el ciclo: definir tarea -> revisar contexto -> elegir agente/modelo -> ejecutar -> probar -> versionar -> validar en Replit.
