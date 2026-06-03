# SEMANTIC_TAG_INDEX - embajadores-backend

Canonical semantic index for context retrieval. Generated from project docs/code by references only.

Rules:
- Do not paste dumps or logs here.
- Keep sources as paths/references; preserve original docs as source of truth.
- Update only when a change affects reusable project context.

## Tags

### admin.portal
- criticality: `recommended_for_plan`
- freshness: `requires_review`
- signals: `admin`, `aliados`, `frontend`, `portal`, `react`, `reportes`, `usuarios`, `vite`
- sources:
  - `replit.md` (doc; score=32; signals=`admin`, `aliados`, `frontend`, `portal`, `react`, `usuarios`, `vite`)
  - `docs/retos-sync/07_plan_habilitacion.md` (doc; score=22; signals=`admin`, `frontend`, `portal`, `react`)
  - `docs/retos-sync/02_brechas_y_riesgos.md` (doc; score=21; signals=`admin`, `aliados`, `frontend`, `portal`)
  - `docs/TECHNICAL_DOCUMENTATION.md` (doc; score=20; signals=`admin`, `aliados`, `react`, `reportes`, `usuarios`)
  - `auth_web.py` (code; score=20; signals=`admin`, `aliados`, `portal`, `usuarios`)
  - `app.py` (code; score=17; signals=`aliados`, `portal`, `react`, `usuarios`)
  - `routes/admin_usuarios_routes.py` (code; score=17; signals=`admin`, `aliados`, `frontend`, `usuarios`)
  - `routes/auth_special_routes.py` (code; score=17; signals=`admin`, `frontend`, `reportes`, `usuarios`)

### ai.agentic_reports
- criticality: `recommended_for_plan`
- freshness: `requires_review`
- signals: `agentic`, `consulta`, `intent`, `openai`, `query`, `report_spec`, `sql`
- sources:
  - `docs/TECHNICAL_DOCUMENTATION.md` (doc; score=37; signals=`agentic`, `consulta`, `intent`, `openai`, `query`, `report_spec`, `sql`)
  - `services/agentic_query_service.py` (code; score=37; signals=`agentic`, `consulta`, `intent`, `openai`, `query`, `report_spec`, `sql`)
  - `routes/special_queries_routes.py` (code; score=34; signals=`agentic`, `consulta`, `intent`, `openai`, `query`, `report_spec`)
  - `services/query_intent_service.py` (code; score=31; signals=`agentic`, `consulta`, `intent`, `openai`, `query`)
  - `services/query_execution_service.py` (code; score=28; signals=`agentic`, `consulta`, `openai`, `query`)
  - `.agents/skills/voiceflow-project-rules/SKILL.md` (doc; score=27; signals=`consulta`, `intent`, `openai`, `query`, `report_spec`)
  - `replit.md` (doc; score=24; signals=`consulta`, `openai`, `query`, `sql`)
  - `docs/retos-sync/01_inventario_backend_actual.md` (doc; score=21; signals=`agentic`, `consulta`, `query`)

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
  - `docs/TECHNICAL_DOCUMENTATION.md` (doc; score=27; signals=`azure`, `db`, `insert`, `mysql`, `sql`, `tabla`, `table`)
  - `auth_web.py` (code; score=27; signals=`db`, `insert`, `mysql`, `select`, `sql`, `tabla`, `table`)
  - `routes/futbol_routes.py` (code; score=27; signals=`db`, `insert`, `mysql`, `select`, `sql`, `tabla`, `table`)

### faq.questions
- criticality: `recommended_for_plan`
- freshness: `requires_review`
- signals: `faq`, `pregunta`, `preguntas`, `preguntas_escritas`, `respuesta_pregunta`
- sources:
  - `.agents/skills/voiceflow-project-rules/SKILL.md` (doc; score=18; signals=`faq`, `pregunta`, `preguntas`)
  - `embajadores_adapter.py` (code; score=18; signals=`faq`, `pregunta`, `preguntas`)
  - `repositories/special_queries_repository.py` (code; score=18; signals=`faq`, `pregunta`, `preguntas`)
  - `repositories/special_reports_repository.py` (code; score=18; signals=`faq`, `pregunta`, `preguntas`)
  - `docs/TECHNICAL_DOCUMENTATION.md` (doc; score=14; signals=`pregunta`, `preguntas`, `preguntas_escritas`)
  - `app.py` (code; score=14; signals=`pregunta`, `preguntas`, `respuesta_pregunta`)
  - `services/voiceflow_normalizer.py` (code; score=14; signals=`faq`, `pregunta`, `respuesta_pregunta`)
  - `README.md` (doc; score=11; signals=`pregunta`, `preguntas`)

### football.challenge
- criticality: `recommended_for_plan`
- freshness: `requires_review`
- signals: `futbol`, `jornada`, `premios`, `pronostico`, `puntajes`, `ranking`, `recalcular`
- sources:
  - `replit.md` (doc; score=37; signals=`futbol`, `jornada`, `premios`, `pronostico`, `puntajes`, `ranking`, `recalcular`)
  - `routes/futbol_routes.py` (code; score=37; signals=`futbol`, `jornada`, `premios`, `pronostico`, `puntajes`, `ranking`, `recalcular`)
  - `.agents/skills/voiceflow-project-rules/SKILL.md` (doc; score=31; signals=`futbol`, `jornada`, `premios`, `pronostico`, `ranking`)
  - `README.md` (doc; score=21; signals=`futbol`, `jornada`, `pronostico`)
  - `tests/test_futbol_endpoints.py` (test; score=21; signals=`futbol`, `jornada`, `pronostico`)
  - `routes/admin_usuarios_routes.py` (code; score=14; signals=`futbol`, `pronostico`)
  - `docs/TECHNICAL_DOCUMENTATION.md` (doc; score=7; signals=`futbol`)
  - `docs/retos-sync/01_inventario_backend_actual.md` (doc; score=7; signals=`futbol`)

### mrp.content
- criticality: `recommended_for_plan`
- freshness: `requires_review`
- signals: `aliado`, `contenido`, `modulo`, `moduloid`, `mrp`, `mrp_aliado`, `recurso`, `recursoid`, `upload`
- sources:
  - `docs/TECHNICAL_DOCUMENTATION.md` (doc; score=34; signals=`aliado`, `contenido`, `modulo`, `moduloid`, `mrp`, `mrp_aliado`, `recurso`, `recursoid`, `upload`)
  - `routes/admin_mrp_routes.py` (code; score=31; signals=`aliado`, `contenido`, `modulo`, `moduloid`, `mrp`, `mrp_aliado`, `recurso`, `recursoid`)
  - `replit.md` (doc; score=28; signals=`aliado`, `contenido`, `modulo`, `moduloid`, `mrp`, `mrp_aliado`, `recurso`)
  - `routes/futbol_routes.py` (code; score=24; signals=`aliado`, `contenido`, `modulo`, `moduloid`, `mrp`, `mrp_aliado`)
  - `routes/mrp_upload_routes.py` (code; score=22; signals=`aliado`, `modulo`, `mrp`, `recurso`, `upload`)
  - `repositories/special_queries_repository.py` (code; score=22; signals=`aliado`, `contenido`, `modulo`, `mrp`, `recurso`)
  - `repositories/special_reports_repository.py` (code; score=22; signals=`aliado`, `contenido`, `modulo`, `mrp`, `recurso`)
  - `.agents/skills/voiceflow-project-rules/SKILL.md` (doc; score=21; signals=`aliado`, `contenido`, `modulo`, `moduloid`, `recurso`, `recursoid`)

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

### retos.sync
- criticality: `recommended_for_plan`
- freshness: `requires_review`
- signals: `fechacorte`, `retoidexterno`, `retos-sync`, `retos_cargas_audit`, `retos_ciclos`, `retos_ganadores`, `retos_seguimiento`, `sftp`
- sources:
  - `docs/retos-sync/04_modelo_canonico_datos.md` (doc; score=40; signals=`fechacorte`, `retoidexterno`, `retos-sync`, `retos_cargas_audit`, `retos_ciclos`, `retos_ganadores`, `retos_seguimiento`, `sftp`)
  - `docs/retos-sync/07_plan_habilitacion.md` (doc; score=40; signals=`fechacorte`, `retoidexterno`, `retos-sync`, `retos_cargas_audit`, `retos_ciclos`, `retos_ganadores`, `retos_seguimiento`, `sftp`)
  - `docs/retos-sync/05_endpoints_servicios_propuestos.md` (doc; score=34; signals=`fechacorte`, `retoidexterno`, `retos-sync`, `retos_cargas_audit`, `retos_ciclos`, `retos_seguimiento`)
  - `docs/retos-sync/02_brechas_y_riesgos.md` (doc; score=33; signals=`fechacorte`, `retoidexterno`, `retos-sync`, `retos_cargas_audit`, `retos_ganadores`, `retos_seguimiento`, `sftp`)
  - `docs/retos-sync/03_alternativas_integracion.md` (doc; score=33; signals=`fechacorte`, `retoidexterno`, `retos-sync`, `retos_cargas_audit`, `retos_ganadores`, `retos_seguimiento`, `sftp`)
  - `docs/retos-sync/propuesta_tecnica_integracion_retos.md` (doc; score=27; signals=`fechacorte`, `retoidexterno`, `retos-sync`, `retos_seguimiento`, `sftp`)
  - `docs/retos-sync/01_inventario_backend_actual.md` (doc; score=20; signals=`fechacorte`, `retoidexterno`, `retos-sync`, `sftp`)
  - `docs/retos-sync/06_preguntas_para_puntos_colombia.md` (doc; score=10; signals=`retos-sync`, `sftp`)

### training.flow
- criticality: `recommended_for_plan`
- freshness: `requires_review`
- signals: `avance`, `finalizado`, `formacion`, `modulo`, `porcentaje`, `pregunta`, `recurso`, `registrar_evento`, `siguiente_elemento`, `validar_respuesta`
- sources:
  - `docs/TECHNICAL_DOCUMENTATION.md` (doc; score=28; signals=`finalizado`, `formacion`, `modulo`, `pregunta`, `recurso`, `registrar_evento`, `siguiente_elemento`, `validar_respuesta`)
  - `app.py` (code; score=28; signals=`finalizado`, `formacion`, `modulo`, `pregunta`, `recurso`, `registrar_evento`, `siguiente_elemento`, `validar_respuesta`)
  - `.agents/skills/voiceflow-project-rules/SKILL.md` (doc; score=25; signals=`avance`, `formacion`, `modulo`, `pregunta`, `recurso`, `registrar_evento`, `siguiente_elemento`)
  - `svc.py` (code; score=25; signals=`finalizado`, `formacion`, `modulo`, `pregunta`, `recurso`, `registrar_evento`, `siguiente_elemento`)
  - `services/voiceflow_normalizer.py` (code; score=25; signals=`finalizado`, `formacion`, `modulo`, `pregunta`, `recurso`, `registrar_evento`, `siguiente_elemento`)
  - `replit.md` (doc; score=22; signals=`formacion`, `modulo`, `pregunta`, `recurso`, `registrar_evento`, `siguiente_elemento`)
  - `repositories/special_queries_repository.py` (code; score=22; signals=`finalizado`, `formacion`, `modulo`, `porcentaje`, `pregunta`, `recurso`)
  - `repositories/special_reports_repository.py` (code; score=22; signals=`finalizado`, `formacion`, `modulo`, `porcentaje`, `pregunta`, `recurso`)

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

### voiceflow.sync
- criticality: `recommended_for_plan`
- freshness: `requires_review`
- signals: `api-steps`, `api_steps`, `diagnostics`, `diff`, `normalizer`, `project-published`, `snapshot`, `sync`, `vf`, `voiceflow`
- sources:
  - `replit.md` (doc; score=37; signals=`api-steps`, `api_steps`, `diagnostics`, `diff`, `normalizer`, `project-published`, `snapshot`, `sync`, `vf`, `voiceflow`)
  - `routes/voiceflow_sync_routes.py` (code; score=34; signals=`api-steps`, `api_steps`, `diagnostics`, `diff`, `project-published`, `snapshot`, `sync`, `vf`, `voiceflow`)
  - `services/voiceflow_sync_service.py` (code; score=30; signals=`api_steps`, `diagnostics`, `diff`, `normalizer`, `snapshot`, `sync`, `vf`, `voiceflow`)
  - `tests/test_vf_sync.py` (test; score=30; signals=`api_steps`, `diagnostics`, `diff`, `normalizer`, `snapshot`, `sync`, `vf`, `voiceflow`)
  - `services/voiceflow_normalizer.py` (code; score=24; signals=`api_steps`, `diagnostics`, `normalizer`, `snapshot`, `vf`, `voiceflow`)
  - `README.md` (doc; score=20; signals=`diagnostics`, `diff`, `normalizer`, `sync`, `vf`, `voiceflow`)
  - `docs/TECHNICAL_DOCUMENTATION.md` (doc; score=14; signals=`diagnostics`, `sync`, `vf`, `voiceflow`)
  - `docs/retos-sync/05_endpoints_servicios_propuestos.md` (doc; score=11; signals=`sync`, `vf`, `voiceflow`)

### whatsapp.delivery
- criticality: `recommended_for_plan`
- freshness: `requires_review`
- signals: `delivery`, `document`, `documento`, `entrega`, `enviar`, `reporte`, `send`, `telefono`, `wa_from`, `wa_id`, `whatsapp`
- sources:
  - `docs/TECHNICAL_DOCUMENTATION.md` (doc; score=39; signals=`delivery`, `document`, `documento`, `entrega`, `enviar`, `reporte`, `send`, `telefono`, `wa_from`, `wa_id`)
  - `whatsapp_webhook.py` (code; score=39; signals=`delivery`, `document`, `documento`, `entrega`, `enviar`, `reporte`, `send`, `telefono`, `wa_from`, `wa_id`)
  - `routes/special_reports_routes.py` (code; score=35; signals=`delivery`, `document`, `documento`, `entrega`, `enviar`, `reporte`, `send`, `telefono`, `wa_from`, `whatsapp`)
  - `.agents/skills/voiceflow-project-rules/SKILL.md` (doc; score=33; signals=`document`, `documento`, `entrega`, `enviar`, `reporte`, `telefono`, `wa_from`, `wa_id`, `whatsapp`)
  - `replit.md` (doc; score=26; signals=`delivery`, `document`, `reporte`, `send`, `telefono`, `wa_from`, `whatsapp`)
  - `message_router.py` (code; score=23; signals=`delivery`, `entrega`, `enviar`, `send`, `wa_from`, `whatsapp`)
  - `decorators/require_auth_especial.py` (code; score=21; signals=`document`, `documento`, `wa_from`, `wa_id`, `whatsapp`)
  - `db.py` (code; score=20; signals=`delivery`, `entrega`, `telefono`, `wa_from`, `whatsapp`)
