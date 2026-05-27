# SEMANTIC_TAG_INDEX - embajadores-backend

Canonical semantic index for context retrieval. Generated from project docs/code by references only.

Rules:
- Do not paste dumps or logs here.
- Keep sources as paths/references; preserve original docs as source of truth.
- Update only when a change affects reusable project context.

## Tags

### auth.jwt
- criticality: `critical_before_build`
- freshness: `requires_review`
- signals: `auth`, `authorization`, `jwt`, `login`, `permisos`, `require_auth`, `token`
- sources:
  - `docs/TECHNICAL_DOCUMENTATION.md` (doc; score=31; signals=`auth`, `authorization`, `jwt`, `login`, `require_auth`, `token`)
  - `auth_web.py` (code; score=28; signals=`auth`, `authorization`, `jwt`, `login`, `token`)
  - `routes/auth_special_routes.py` (code; score=28; signals=`auth`, `authorization`, `jwt`, `login`, `token`)
  - `utils/token_utils.py` (code; score=28; signals=`auth`, `authorization`, `jwt`, `login`, `token`)
  - `.agents/skills/voiceflow-project-rules/SKILL.md` (doc; score=27; signals=`auth`, `authorization`, `jwt`, `permisos`, `require_auth`, `token`)
  - `replit.md` (doc; score=25; signals=`auth`, `jwt`, `login`, `token`)
  - `services/special_user_auth_service.py` (code; score=25; signals=`auth`, `jwt`, `login`, `token`)
  - `decorators/require_auth_especial.py` (code; score=24; signals=`auth`, `authorization`, `jwt`, `require_auth`, `token`)

### db.mysql
- criticality: `critical_before_build`
- freshness: `requires_review`
- signals: `azure`, `database`, `db`, `insert`, `migration`, `mysql`, `select`, `sql`, `tabla`, `table`
- sources:
  - `replit.md` (doc; score=34; signals=`azure`, `database`, `db`, `insert`, `mysql`, `select`, `sql`, `tabla`, `table`)
  - `db.py` (code; score=34; signals=`azure`, `database`, `db`, `insert`, `mysql`, `select`, `sql`, `tabla`, `table`)
  - `README.md` (doc; score=28; signals=`azure`, `database`, `db`, `migration`, `mysql`, `select`, `sql`)
  - `app.py` (code; score=28; signals=`azure`, `database`, `db`, `insert`, `mysql`, `select`, `sql`)
  - `svc.py` (code; score=28; signals=`database`, `db`, `insert`, `mysql`, `select`, `sql`, `table`)
  - `auth_web.py` (code; score=27; signals=`db`, `insert`, `mysql`, `select`, `sql`, `tabla`, `table`)
  - `routes/futbol_routes.py` (code; score=27; signals=`db`, `insert`, `mysql`, `select`, `sql`, `tabla`, `table`)
  - `docs/TECHNICAL_DOCUMENTATION.md` (doc; score=24; signals=`azure`, `db`, `insert`, `mysql`, `sql`, `tabla`)

### replit.deployment
- criticality: `critical_before_build`
- freshness: `requires_review`
- signals: `autoscale`, `deploy`, `deployment`, `gunicorn`, `replit`, `secrets`, `workflow`
- sources:
  - `.replit` (config; score=34; signals=`autoscale`, `deploy`, `deployment`, `gunicorn`, `replit`, `workflow`)
  - `README.md` (doc; score=31; signals=`deploy`, `deployment`, `gunicorn`, `replit`, `secrets`)
  - `docs/TECHNICAL_DOCUMENTATION.md` (doc; score=27; signals=`autoscale`, `deploy`, `gunicorn`, `replit`, `secrets`)
  - `replit.md` (doc; score=21; signals=`deploy`, `deployment`, `replit`)
  - `gunicorn.conf.py` (code; score=21; signals=`deploy`, `deployment`, `gunicorn`)
  - `.agents/skills/voiceflow-project-rules/SKILL.md` (doc; score=14; signals=`deploy`, `gunicorn`)
  - `app.py` (code; score=14; signals=`deploy`, `deployment`)
  - `session_store.py` (code; score=10; signals=`autoscale`, `replit`)

### reports.special_users
- criticality: `critical_before_build`
- freshness: `requires_review`
- signals: `especial`, `permitewhatsapp`, `report`, `reporte`, `reportes`, `special`, `special_users`, `usuarioespecialid`, `usuarios_especiales`
- sources:
  - `docs/TECHNICAL_DOCUMENTATION.md` (doc; score=34; signals=`especial`, `permitewhatsapp`, `report`, `reporte`, `reportes`, `special`, `special_users`, `usuarioespecialid`, `usuarios_especiales`)
  - `services/authz_context_service.py` (code; score=34; signals=`especial`, `permitewhatsapp`, `report`, `reporte`, `reportes`, `special`, `special_users`, `usuarioespecialid`, `usuarios_especiales`)
  - `repositories/special_users_repository.py` (code; score=34; signals=`especial`, `permitewhatsapp`, `report`, `reporte`, `reportes`, `special`, `special_users`, `usuarioespecialid`, `usuarios_especiales`)
  - `services/agentic_query_service.py` (code; score=31; signals=`especial`, `report`, `reporte`, `reportes`, `special`, `special_users`, `usuarioespecialid`, `usuarios_especiales`)
  - `services/special_users_service.py` (code; score=31; signals=`especial`, `permitewhatsapp`, `report`, `reporte`, `special`, `special_users`, `usuarioespecialid`, `usuarios_especiales`)
  - `services/special_user_auth_service.py` (code; score=31; signals=`especial`, `permitewhatsapp`, `report`, `reporte`, `special`, `special_users`, `usuarioespecialid`, `usuarios_especiales`)
  - `services/special_user_recognition_service.py` (code; score=31; signals=`especial`, `permitewhatsapp`, `report`, `reporte`, `reportes`, `special`, `special_users`, `usuarioespecialid`)
  - `.agents/skills/voiceflow-project-rules/SKILL.md` (doc; score=28; signals=`especial`, `permitewhatsapp`, `report`, `reporte`, `reportes`, `special`, `usuarios_especiales`)

### voiceflow.identity
- criticality: `critical_before_build`
- freshness: `requires_review`
- signals: `identity_context`, `numeroid`, `tipoid`, `user_id`, `userid`, `verificar_registro`, `vf`, `voiceflow`, `wa_from`, `wa_id`
- sources:
  - `docs/TECHNICAL_DOCUMENTATION.md` (doc; score=36; signals=`identity_context`, `numeroid`, `tipoid`, `user_id`, `userid`, `verificar_registro`, `vf`, `voiceflow`, `wa_from`, `wa_id`)
  - `.agents/skills/voiceflow-project-rules/SKILL.md` (doc; score=33; signals=`numeroid`, `tipoid`, `user_id`, `userid`, `verificar_registro`, `vf`, `voiceflow`, `wa_from`, `wa_id`)
  - `whatsapp_webhook.py` (code; score=30; signals=`identity_context`, `numeroid`, `tipoid`, `verificar_registro`, `vf`, `voiceflow`, `wa_from`, `wa_id`)
  - `replit.md` (doc; score=27; signals=`identity_context`, `numeroid`, `tipoid`, `verificar_registro`, `vf`, `voiceflow`, `wa_from`)
  - `services/voiceflow_normalizer.py` (code; score=27; signals=`numeroid`, `tipoid`, `userid`, `verificar_registro`, `vf`, `voiceflow`, `wa_id`)
  - `app.py` (code; score=24; signals=`numeroid`, `tipoid`, `user_id`, `verificar_registro`, `vf`, `voiceflow`)
  - `decorators/require_auth_especial.py` (code; score=22; signals=`identity_context`, `numeroid`, `tipoid`, `userid`, `vf`, `wa_from`, `wa_id`)
  - `routes/futbol_routes.py` (code; score=20; signals=`numeroid`, `tipoid`, `user_id`, `vf`, `voiceflow`, `wa_id`)

### whatsapp.delivery
- criticality: `recommended_for_plan`
- freshness: `requires_review`
- signals: `delivery`, `document`, `documento`, `entrega`, `enviar`, `reporte`, `send`, `telefono`, `wa_from`, `wa_id`, `whatsapp`
- sources:
  - `docs/TECHNICAL_DOCUMENTATION.md` (doc; score=39; signals=`delivery`, `document`, `documento`, `entrega`, `enviar`, `reporte`, `send`, `telefono`, `wa_from`, `wa_id`)
  - `whatsapp_webhook.py` (code; score=36; signals=`delivery`, `document`, `documento`, `entrega`, `enviar`, `send`, `telefono`, `wa_from`, `wa_id`, `whatsapp`)
  - `routes/special_reports_routes.py` (code; score=35; signals=`delivery`, `document`, `documento`, `entrega`, `enviar`, `reporte`, `send`, `telefono`, `wa_from`, `whatsapp`)
  - `.agents/skills/voiceflow-project-rules/SKILL.md` (doc; score=33; signals=`document`, `documento`, `entrega`, `enviar`, `reporte`, `telefono`, `wa_from`, `wa_id`, `whatsapp`)
  - `replit.md` (doc; score=23; signals=`delivery`, `document`, `reporte`, `telefono`, `wa_from`, `whatsapp`)
  - `message_router.py` (code; score=23; signals=`delivery`, `entrega`, `enviar`, `send`, `wa_from`, `whatsapp`)
  - `decorators/require_auth_especial.py` (code; score=21; signals=`document`, `documento`, `wa_from`, `wa_id`, `whatsapp`)
  - `db.py` (code; score=20; signals=`delivery`, `entrega`, `telefono`, `wa_from`, `whatsapp`)
