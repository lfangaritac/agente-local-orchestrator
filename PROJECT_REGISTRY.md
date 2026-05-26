# PROJECT_REGISTRY.md

## Propósito

Registro maestro de proyectos objetivo habilitados en el orquestador local.

## Estado

Pendiente de poblar mediante el protocolo `ENABLE_TARGET_PROJECT`.

## Campos mínimos por proyecto

- project_id:
- nombre_canónico:
- alias_permitidos:
- ruta_local:
- repositorio_remoto:
- origen: local | replit | github | nuevo | importado
- stack_detectado:
- documentación_principal:
- código_fuente_relevante:
- estado_sincronización:
- alertas_críticas:
- lecciones_locales:
- último_análisis:
- responsable:

## Proyectos registrados

<!--
Nota de parsing (scripts/apply_to_project.py):
- Cada proyecto es un bloque de líneas 'key: value' separado por una línea en blanco.
- alias_permitidos debe ser lista en una sola línea separada por comas.
- Evitar valores multi-línea.
-->

### data-privacy-management-d

project_id: data-privacy-management-d
nombre_canónico: DataPrivacyManagement(D) Workspace
alias_permitidos: dpm, data-privacy-management, dataprivacymanagement-d, dpm-replit
ruta_local:
repositorio_remoto: https://github.com/lfangaritac/DataPrivacyManagement
origen: replit
environment_type: replit-git
repo_url: https://github.com/lfangaritac/DataPrivacyManagement
replit_workspace_path: /home/runner/workspace
local_path: null
stack_detectado: unknown
documentación_principal:
código_fuente_relevante:
estado_sincronización: test_active
alertas_críticas:
lecciones_locales:
último_análisis:
responsable: unknown

### embajadores-backend

project_id: embajadores-backend
nombre_canónico: Embajadores Backend
alias_permitidos: embajadores, embajadores-backend
ruta_local: C:\Users\murfe\source\repos\embajadores-backend
repositorio_remoto: https://github.com/lfangaritac/embajadores-backend.git
origen: github
environment_type: github
repo_url: https://github.com/lfangaritac/embajadores-backend.git
replit_workspace_path: 
replit_join_url: 
local_path: C:\Users\murfe\source\repos\embajadores-backend
stack_detectado: Python 3.11 Flask/Gunicorn + React/Vite admin portal + MySQL/Azure/Replit integrations
documentación_principal: README.md, replit.md, docs/TECHNICAL_DOCUMENTATION.md, frontend/src/app/api/APIContract.md
código_fuente_relevante: main.py, app.py, db.py, env_loader.py, whatsapp_webhook.py, voiceflow_client.py, routes/, services/, frontend/
estado_sincronización: initial_analysis_completed
alertas_críticas: docs/projects/embajadores-backend/CRITICAL_ALERTS.md
lecciones_locales: docs/projects/embajadores-backend/LESSONS_LOCAL.md
último_análisis: 2026-05-26
responsable: unknown
