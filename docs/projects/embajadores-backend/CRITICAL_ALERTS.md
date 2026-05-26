# CRITICAL_ALERTS - embajadores-backend

Alertas criticas locales iniciales.

## ALERT-EMB-001 - No exponer secrets ni valores de entorno

- severity: `critical`
- scope: `security`
- trigger: cualquier tarea con DB, WhatsApp, Voiceflow, Pinecone, OpenAI, Azure, Resend o Replit.
- do_not_do: no imprimir `.env`, tokens, connection strings, API keys, SAS tokens, JWT secrets ni credenciales.
- required_check: trabajar solo con nombres de variables y fuentes saneadas.
- source: `SECURITY_POLICY.md`, `README.md`, `docs/TECHNICAL_DOCUMENTATION.md`, codigo.

## ALERT-EMB-002 - No ejecutar migraciones ni scripts DB sin autorizacion

- severity: `critical`
- scope: `database`
- trigger: `_scripts/*migrar*`, `migration_*.sql`, `fix_*.sql`, `admin_script_dual_compatibility.sql`, endpoints admin masivos.
- do_not_do: no correr scripts de migracion, SQL, updates masivos o endpoints que escriban DB.
- required_check: dry-run si existe, backup/rollback y aprobacion humana.

## ALERT-EMB-003 - Cuidado con PII y reportes versionados

- severity: `high`
- scope: `data`
- trigger: archivos `.xlsx`, reportes, trazabilidad, usuarios, telefonos, logs de conversaciones.
- do_not_do: no copiar contenidos ni exponer datos personales en handoffs.
- required_check: registrar solo nombres/rutas y conteos; anonimizar ejemplos.

## ALERT-EMB-004 - No ejecutar workflow Replit `uv add` durante diagnostico

- severity: `medium`
- scope: `environment`
- trigger: `.replit` workflow `flask_server`.
- do_not_do: no ejecutar run/workflow Replit localmente sin autorizacion, porque puede modificar dependencias.
- required_check: usar primero validaciones de lectura/compilacion.

## ALERT-EMB-005 - Endpoints internos/envio masivo requieren bloqueo por defecto

- severity: `critical`
- scope: `operations`
- trigger: `/internal/broadcast-reto-trimestral`, envios WhatsApp, exportaciones masivas, endpoints admin.
- do_not_do: no invocar endpoints que envien mensajes, generen reportes, escriban DB o disparen procesos.
- required_check: autorizacion humana, entorno correcto y credenciales controladas.

