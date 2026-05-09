---
name: Handoff to OpenCode
description: Thin wrapper: prepara un handoff Continue→OpenCode remitiendo al formato canónico (sin duplicarlo)
invokable: true
---

Actúa como Continue en rol de copiloto contextual.

No inventes contexto ni afirmes “archivos revisados” si no los revisaste.
No copies/pegues artefactos voluminosos: `raw_outputs/**`, `TRACE.md`, `RUN_SUMMARY.md`, logs ni handoffs completos.

Referencia (fuente canónica del formato completo):
- `.continue/rules/continue-opencode-handoff.md`

Referencia para routing/modelo:
- `MODEL_ROUTING.md`

Referencia para modo Plan/Build y umbrales de autorización:
- `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md` (sección 25)

Entrega (mínimo obligatorio, en este orden):
1) Objetivo.
2) Modo (Plan/Build) y alcance autorizado.
3) Escenario.
4) Archivos revisados.
5) Archivos no revisados relevantes (y por qué).
6) Reglas aplicables.
7) Restricciones.
8) Riesgos.
9) Validaciones esperadas (qué evidencia devolverá OpenCode).
10) Próxima acción recomendada.

Luego, genera el handoff final usando **exactamente** el formato de `.continue/rules/continue-opencode-handoff.md` (sin añadir plantillas alternativas).
