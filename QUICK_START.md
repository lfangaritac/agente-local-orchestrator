# QUICK_START.md

## Uso rapido del orquestador local

Este repositorio contiene el nucleo base para activar el sistema operativo de agentes en proyectos locales, proyectos existentes y proyectos conectados a Replit.

## Comandos principales

### Activar o validar sistema de agentes

`powershell
.\activate-agents.bat
python .\scripts\check_env.py
git status
`",
",


Cuando el orquestador se aplica a un proyecto externo, scripts/check_env.py se copia como plantilla inicial.

Cada proyecto destino debe ajustar ese archivo segun sus propias variables reales, stack e integraciones, y debe actualizar SECRETS_MANIFEST.md sin incluir valores sensibles.
