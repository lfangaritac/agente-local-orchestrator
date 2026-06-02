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

## ALERT-EMB-006 - `.env.example` contiene valores aparentemente reales

- severity: `critical`
- scope: `security`
- trigger: cualquier lectura, handoff, diff, revision publica, commit, escalamiento, prompt externo o documentacion que toque `.env.example`.
- do_not_do: no copiar, citar, pegar, resumir valores, enviar a modelos externos ni tratar `.env.example` como plantilla saneada.
- required_check: rotar/revocar credenciales afectadas si aplican, reemplazar por placeholders antes de difundir, y revisar historial Git si se va a sanear el repositorio.
- source: retoma local 2026-05-26; lectura controlada de `.env.example` sin reproducir valores.

## ALERT-EMB-007 - Secrets expuestos durante sesion local

- severity: `critical`
- scope: `security`
- trigger: cualquier uso futuro de Meta, Voiceflow, DB, Pinecone, Azure Storage, GitHub PAT o variables copiadas durante la sesion 2026-05-28.
- do_not_do: no reutilizar tokens/passwords/connection strings pegados en chat, buffers del editor o scripts temporales; no commitear scripts con valores reales.
- required_check: rotar/revocar credenciales expuestas antes de operacion productiva; mantener scripts de entorno como plantillas sin valores reales o usar gestores de secrets.
- source: sesion local 2026-05-28; archivo temporal `scripts/set_embajadores_env_template.ps1` eliminado del orquestador tras cumplir su finalidad.

## ALERT-EMB-008 - Script de envio WhatsApp programado tiene side effects externos

- severity: `critical`
- scope: `operations`
- trigger: `_scripts/envio_10_30_bogota.py` o cualquier envio con templates `lanzamiento_reto_solo_texto` y `opcion2`.
- do_not_do: no ejecutar el script sin destinatarios confirmados, horario confirmado, autorizacion humana, secrets Meta seguros y verificacion de que `opcion2` se envia como imagen inline.
- required_check: revisar destinatarios, templates, `IMAGE_URL`, zona horaria `America/Bogota`, logs y tasa de envio; confirmar que no es una prueba contra usuarios reales no autorizados.
- source: pull `ffb8f3c`; `_scripts/envio_10_30_bogota.py`.
