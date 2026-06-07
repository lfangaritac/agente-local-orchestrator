# PROJECT_RESUME — riskmanagement360

Vista compacta para retomar el proyecto sin depender del chat ni de `.orchestrator_state/`.

Reglas:
- No pegar artefactos voluminosos (TRACE/RUN_SUMMARY/raw_outputs).
- Operar por referencias: run_id + rutas + conteos + previews cortos.
- Evidencia pesada es operacional y no se versiona por defecto (ver `.gitignore` y `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md`).

## 1) Qué es este proyecto

- (1–3 líneas)

## 2) Dónde está el repo (local/remoto)

- repo_url: (referencia; no secrets)
- local_path: (si aplica; puede vivir en PROJECT_REGISTRY.md)
- branch: (última conocida)
- last_commit: (hash corto + mensaje)

## 3) Estado actual conocido

- status_classification: `unknown|listo|parcialmente_listo|no_listo`
- last_synced: (ver `SYNC_STATUS.md`)

## 4) Frontera actual

- Ver: `CURRENT_FRONTIER.md`

## 5) Última decisión relevante

- decision_ref: (ruta a `docs/decisions/**` o resumen 1 línea + referencia)

## 6) Riesgos/alertas aplicables

- Global: `docs/alerts/GLOBAL_CRITICAL_ALERTS.md`
- Local: `CRITICAL_ALERTS.md`

## 7) Handoffs / runs / returns relevantes

- Handoffs: `HANDOFF_LOG.md`
- Runs: `docs/context/RUN_INDEX.md` + (entradas locales en `CONTEXT_INDEX.md`)
- Returns: `docs/returns/RETURN_INDEX.md` (y archivos referenciados)

## 8) Errores/fixes reutilizables

- Ver: `ERRORS_AND_FIXES.md`

## 9) Qué consultar antes de actuar

- `PROJECT_PROFILE.md`
- `CURRENT_FRONTIER.md`
- `CRITICAL_ALERTS.md`
- `LESSONS_LOCAL.md`
- `CONTEXT_INDEX.md` + `DOCUMENTATION_AUDIT.md` + `CODE_CONTEXT_MAP.md`

## 10) Qué no repetir

- (errores recurrentes + referencia a fixes/lecciones; 3–7 bullets)
