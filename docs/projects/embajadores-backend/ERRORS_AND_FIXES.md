# ERRORS_AND_FIXES - embajadores-backend

Registro compacto de errores tecnicos reutilizables.

| error_id | date | symptom | root_cause | fix_summary | refs | prevention |
|---|---|---|---|---|---|---|
| ERR-0001 | 2026-05-26 | `git clone` inicial quedo con solo `.git` visible por timeout. | Timeout del comando de clonacion antes de materializar worktree. | Se verifico repo parcial y se ejecuto `git checkout HEAD -- .` sobre estado limpio para poblar archivos. | local clone setup | Si clone timeoutea, verificar `git status`, `git rev-parse HEAD`, `git ls-tree HEAD` antes de borrar o reclonar. |

