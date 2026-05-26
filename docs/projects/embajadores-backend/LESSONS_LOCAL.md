# LESSONS_LOCAL - embajadores-backend

Lecciones locales iniciales.

## LESSON-EMB-001 - README no basta para entender el sistema actual

- source: contraste `README.md` vs `replit.md`, `docs/TECHNICAL_DOCUMENTATION.md` y estructura real.
- lesson: usar `replit.md` y `docs/TECHNICAL_DOCUMENTATION.md` como fuentes principales de contexto; tratar `README.md` como quick start historico/parcial.

## LESSON-EMB-002 - Validaciones deben empezar por lectura y compilacion

- source: presencia de muchos servicios externos, scripts DB y endpoints con side effects.
- lesson: antes de ejecutar app, tests amplios o workflows, hacer `git status`, revision de env names, `py_compile` selectivo y auditoria de imports con side effects.

## LESSON-EMB-003 - Separar backend Flask legacy de portal admin moderno

- source: `app.py` concentra rutas legacy y `frontend/` contiene portal React/Vite.
- lesson: los cambios deben clasificar si afectan API legacy, blueprints nuevos, frontend admin o integraciones externas.

