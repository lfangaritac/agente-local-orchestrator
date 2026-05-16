# RETURN_INDEX.md

## Propósito

Índice operativo de **retornos externos** normalizados (p.ej. Replit Agent) para trazabilidad por referencias.

Sirve para ubicar rápidamente, por proyecto:
- retornos externos recibidos;
- estado clasificado;
- decisión de escalamiento/no escalamiento;
- next_frontier;
- referencias a archivos canónicos (retorno + decisión).

## Reglas

- No pegar chats completos ni logs extensos.
- No incluir secrets/tokens/credenciales ni valores de env.
- No incluir join links ni URLs sensibles.
- Registrar solo metadatos + referencias a retornos sanitizados.
- Enlazar a la decisión derivada cuando exista.

## Returns (resumen)

| date | target_project | return_file | external_agent | status_classification | escalation_decision | linked_decision | next_frontier | notes |
|---|---|---|---|---|---|---|---|---|
| 2026-05-16 | data-privacy-management-d | `docs/returns/data-privacy-management-d/2026-05-16_replit_diagnostic_return.md` | replit_agent | parcialmente_listo | no_escalate | `docs/decisions/escalation/data-privacy-management-d/2026-05-16_no_escalate_replit.md` | pause_pilot_or_local_plan | Canal validado; piloto pausado por deuda TS amplia (~280 errores por imports versionados). |
