# CONTEXT_INDEX - analisis-impacto-privacidad

Indice de contexto por referencias.

## Documentacion encontrada

- `replit.md`: documentacion maestra funcional/tecnica, modulos, arquitectura, endpoints, IA y decisiones.
- `docs/DOCUMENTACION_TECNICA.md`: documentacion tecnica integral de arquitectura, stack, DB, backend, IA, frontend, API, flujos y deuda tecnica.
- `docs/test_reports/baseline_validacion_local_aip_20260504.md`: baseline local de validaciones.
- `docs/test_reports/opencode_diagnostico_typescript_aip_20260504.md`: diagnostico OpenCode de errores TypeScript.
- `client/src/DOCUMENTACION_TECNICA.md`: copia/variante embebida de documentacion tecnica.
- `client/src/INSTRUCCION_*_RESUMEN.md`: notas de instrucciones previas del cliente/UI.

## Decisiones relevantes

- Arquitectura de puerto unico: Express sirve API y frontend; Vite se integra en desarrollo.
- Sin autenticacion activa segun documentacion tecnica: tabla `users` existe, pero no hay rutas activas de auth.
- CSS Tailwind precompilado en `client/src/index.css`; nuevas utilidades deben agregarse manualmente.
- No remediar TypeScript masivamente sin plan por bloques.
- No ejecutar `db:push` ni Drizzle migrations sin autorizacion explicita.

## Runs / evidencia

- `git ls-remote`: HEAD remoto `9c5ed1815aeb861ab81e417cd9a89cb50d1d50ee`.
- `git clone`: repo local `C:\Users\murfe\source\repos\Analisis_impacto_privacidad`.
- `git status -sb`: `## main...origin/main`.

