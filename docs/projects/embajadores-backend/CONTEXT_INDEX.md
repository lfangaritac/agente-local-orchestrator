# CONTEXT_INDEX - embajadores-backend

Indice de contexto por referencias. No reemplaza fuentes originales.

## Documentacion encontrada

- `README.md`: quick start, endpoints iniciales, variables base y despliegue Replit/Azure.
- `replit.md`: vision mas actualizada; documenta arquitectura Flask, portal admin, Voiceflow, WhatsApp, Futbol, reportes, usuarios especiales, MRP y transcripcion VF.
- `docs/TECHNICAL_DOCUMENTATION.md`: documentacion tecnica extensa; contiene variables, arquitectura, endpoints y flujos.
- `frontend/src/app/api/APIContract.md`: contrato aspiracional/portal admin por dominios funcionales.
- Multiples documentos `.md` de troubleshooting e implementaciones Voiceflow/WhatsApp/FAQ/MRP.
- `.agents/skills/voiceflow-project-rules/SKILL.md`: reglas locales de Voiceflow; tratar como fuente relevante para flujos VF.

## Codigo y configuracion encontrados

- `app.py`: Flask principal y gran concentracion de rutas legacy.
- `main.py`: entrypoint.
- `db.py`: conexion DB y helpers multi-proyecto.
- `whatsapp_webhook.py`: webhook y envio WhatsApp.
- `voiceflow_client.py`: cliente Voiceflow Runtime.
- `routes/`: blueprints separados.
- `services/`: servicios de IA, reportes, blob, email, sync y usuarios especiales.
- `frontend/`: portal admin React/Vite.
- `.replit`: Replit autoscale, Gunicorn, Python/Node/Postgres modules, workflows.
- `.github/workflows/main_embajadores-backend.yml`: deploy Azure Web App via OIDC.

## Evidencia operativa

- `git status -sb` en repo objetivo: limpio tras clonacion.
- `git status -sb` en orquestador: cambios esperados en registry y scaffold.

