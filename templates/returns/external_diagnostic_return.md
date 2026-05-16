# External diagnostic return (template)

> Uso: formato mínimo para registrar retornos de diagnóstico desde agentes externos (p.ej. Replit Agent) **sin volver a consumir el agente externo**.
>
> Reglas:
> - No incluir secrets/tokens/credenciales.
> - No incluir join links ni URLs sensibles.
> - No pegar chats completos; solo síntesis + evidencia mínima.
> - En modo diagnóstico, el agente externo debe confirmar explícitamente: "No modifiqué archivos".

---

## Header (mínimo)

target_project:
  project_id: <project-id>
  name: <canonical-name>
  environment_type: <replit-git|replit|local|github|imported>
  repo_url: <https://github.com/org/repo>
  workspace_path: <remote path or null>

external_agent:
  name: <replit_agent|other>
  mode: diagnostico_sin_cambios
  immutable_confirmed: <true|false>
  immutable_statement: "<No modifiqué archivos>"

sensitive_data_check:
  contains_join_links: <true|false>
  contains_secrets_or_tokens: <true|false>
  contains_env_values: <true|false>
  notes: "<si hay riesgo, describir sin exponer valores>"

---

## Commands executed (solo lectura)

commands_executed:
  - "git status"
  - "git remote -v"
  - "git log -1 --oneline"
  - "<other read-only command>"

---

## Git state (resumen)

git_state:
  branch: <main>
  remotes:
    - "origin <url-redacted-if-needed>"
  last_commit: "<hash> — <subject>"
  working_tree:
    status: <clean|dirty>
    notes: "<e.g. untracked file(s) present>"

---

## Stack detected (resumen)

stack_detected:
  frontend: <React|Next|none|unknown>
  backend: <Express|FastAPI|none|unknown>
  language: <TypeScript|Python|mixed|unknown>
  database: <PostgreSQL|none|unknown>
  orm_or_migrations: <Drizzle|Prisma|Alembic|unknown>
  package_manager: <npm|pnpm|yarn|uv|poetry|unknown>

---

## Checks run + results

checks_run:
  - name: "<npm run check>"
    result: <pass|fail|not_run>
    summary: "<compact summary; no logs completos>"

results_summary: "<1-3 frases>"

---

## Blockers / risks / recommendations

status_classification: <listo|parcialmente_listo|no_listo>

blockers:
  - "<blocker 1>"
  - "<blocker 2>"

risks:
  critical:
    - "<e.g. no ejecutar migraciones/db push>"
  medium:
    - "<e.g. build/typecheck failing; scope unclear>"
  low:
    - "<e.g. untracked session artifact>"

recommendations:
  - "<next safe step (plan-only)>"

---

## Escalation decision + next frontier

escalation_decision: <no_escalate|replit_needed|premium_needed>
escalation_reason: "<1-2 frases>"

next_frontier: <pause_pilot|local_analysis|plan_only|other>
next_frontier_reason: "<1-2 frases>"

evidence_notes:
  - "<what evidence was used to decide: commands + key results>"
