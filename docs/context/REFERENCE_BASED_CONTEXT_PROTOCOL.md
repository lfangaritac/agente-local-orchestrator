# REFERENCE_BASED_CONTEXT_PROTOCOL

## 1. Principio central

Contexto persistente no equivale a contexto cargado.

Este protocolo define una operación por **referencias**:

- No cargar todo el contexto del repositorio por defecto.
- No guardar “todo” como contenido en el chat ni en handoffs por defecto.
- Registrar **acciones relevantes** como referencias estructuradas (metadatos + rutas + run_id).
- Recuperar selectivamente contexto aplicable por tarea y por necesidad.
- Usar evidencia por **rutas** / **run_id** / **conteos** / **previews**, no por pegado completo.

Regla superior: **cobertura por capas**, no por volumen.

---

## 2. Modelo de acción relevante

Cuenta como *acción relevante* cualquier evento que cambie el estado operativo o afecte decisiones futuras, por ejemplo:

- decisión de gobierno (política, canonicidad, restricciones);
- cambio de código (cuando aplique, y siempre referenciado);
- creación o modificación de herramienta MCP (o su documentación);
- run de diagnóstico / validación (con `run_id`);
- error recurrente (timeout, truncamiento, loops de contexto);
- validación crítica (seguridad, secretos, integridad de archivos maestros);
- cambio de política (Plan/Build, compact-first, contexto mínimo);
- riesgo detectado (secrets, premium triggers, Replit triggers);
- autorización humana (con alcance y umbrales);
- escalamiento (OpenCode, Zen, premium, Replit);
- bloqueo técnico (falta de contexto, fallas MCP, falta de permisos);
- aprendizaje consolidado (lección operativa que evita repetir errores).

---

## 3. Metadatos mínimos para una acción relevante

Toda acción relevante debe registrarse como referencia liviana con:

- `action_id` (o `run_id` si aplica)
- `date` (ISO-8601)
- `type` (ver lista sugerida abajo)
- `objective` (1 línea)
- `status` (planned | in_progress | done | blocked | superseded)
- `owner` (Continue | OpenCode | MCP | user)
- `mode` (Plan | Build)
- `related_paths` (rutas; sin contenido)
- `evidence_refs` (rutas a artefactos: RUN_SUMMARY/TRACE/agent_outputs/raw_outputs; sin pegado)
- `decision` (si aplica; 1–3 líneas)
- `next_action` (1 línea)
- `importance` (low | medium | high | critical)
- `base_context` (yes | no)  
  - **yes**: entra en el *context pack* base por defecto.
  - **no**: solo se recupera bajo demanda.

Tipos sugeridos (`type`):
- `policy`
- `routing_decision`
- `run`
- `mcp_tooling`
- `context_mitigation`
- `risk`
- `authorization`
- `escalation`
- `blocker`
- `lesson`

---

## 4. Qué NO debe guardarse/cargarse completo por defecto

Por defecto (Nivel 0/1) **NO** se debe guardar ni cargar completo:

- `raw_outputs/**` completos
- `TRACE.md` completo
- `RUN_SUMMARY.md` completo
- logs completos (`*_stdout.log`, `*_stderr.log`)
- handoffs completos (`docs/agent_queue/inbox/*.md`)
- output completo de terminal
- dumps JSON extensos
- diffs completos
- duplicados documentales (preferir documento canónico + referencia)
- contenidos temporales de prueba (salvo referencia)

---

## 5. Context Pack por tarea (estructura mínima)

Todo prompt/instrucción debe construir un *context pack* mínimo antes de pedir acción a un agente:

- **Objetivo actual:**
- **Modo:** Plan | Build
- **Alcance autorizado:**
- **Restricciones aplicables:** (secrets, premium, Replit, no tocar X)
- **Reglas canónicas relevantes:** (solo referencias a docs/secciones)
- **Decisiones previas relevantes:** (IDs + 1 línea)
- **Acciones / runs relacionados:** (`run_id` + estado + conteos)
- **Archivos consultables/modificables:** (lista de rutas)
- **Evidencia mínima:** (previews cortos; no logs completos)
- **Exclusiones explícitas:** (qué no traer al contexto)
- **Siguiente paso único:**

---

## 6. Niveles de contexto

- **Nivel 0 — Mínimo operativo:** objetivo + modo + alcance + restricciones + siguiente paso.
- **Nivel 1 — Referencias y metadatos (default):** IDs, rutas, conteos, estados, decisiones resumidas.
- **Nivel 2 — Fragmentos específicos:** extractos cortos (líneas/preview) de un artefacto concreto.
- **Nivel 3 — Lectura profunda autorizada:** múltiples fragmentos/secciones; análisis cruzado.
- **Nivel 4 — Carga completa excepcional:** solo con autorización explícita y justificación.

Autorización requerida:
- Nivel 0/1: implícito.
- Nivel 2: implícito si está dentro del alcance y es fragmento pequeño.
- Nivel 3/4: **solicitar autorización** indicando por qué es necesario y qué se va a leer.

---

## 7. Matriz de selección de contexto (guía rápida)

| Tipo de tarea | Nivel recomendado | Contexto a incluir | Evitar |
|---|---:|---|---|
| Diagnóstico | 0–1 | run_id, conteos, rutas, política vigente | TRACE/RUN_SUMMARY completos |
| Documentación/gobierno | 0–2 | secciones canónicas + refs | duplicar políticas |
| Cambio de código | 0–2 (3 si complejo) | archivos en scope + refs + plan | pegar diffs completos |
| Prueba MCP | 0–1 | tool + args + elapsed_ms + trunc flags | stdout masivo |
| Revisión de run | 1–2 | `run_health_check` (salud) + rutas + conteos + previews (y `get_run_status` si hace falta ampliación) | raw_outputs completos |
| Decisión de gobierno | 0–1 | decisión + motivo + refs | reimprimir todo |
| Escalamiento a OpenCode | 0–1 | handoff compacto + refs | handoff completo |
| Premium/Replit | 0–1 (+3 si crítico) | triggers + autorización + pregunta concreta | dumps |
| Retención/limpieza artefactos | 0–1 | qué se retiene y por qué | borrar sin autorización |

---

## 8. Relación con runs y handoffs

- Runs/handoffs son **evidencia**, no contexto base.
- Consultar por `run_id`.
- Por defecto (compact-first) usar:
  1) `run_health_check` (salud rápida del run: missing/partial/healthy/stale/failed)
  2) `check_opencode_run_status` (seguimiento específico de OpenCode)
  3) `get_run_status` (diagnóstico ampliado)
  4) `show_latest_run` solo como **fallback / preview-only** bajo solicitud explícita o necesidad justificada
- Solo cargar previews o fragmentos (Nivel 2) cuando exista una pregunta concreta.
- `raw_outputs/**` queda excluido por defecto.
- `TRACE.md` / `RUN_SUMMARY.md` se consultan por fragmentos y solo cuando aplique.

---

## 9. Relación con documentación maestra

- **Documento canónico:** fuente de verdad para un tema.
- **Documento referencial:** enlaza, resume en 1–3 líneas y apunta al canónico.

Reglas:
- Registrar en `docs/context/REFERENCE_MAP.md` qué documento es canónico por tema.
- Evitar duplicidades: si hay duplicado, registrar como *pendiente* hasta decisión canónica.
- Para tareas pequeñas, no cargar documentos largos: referenciar sección y extraer solo el fragmento aplicable.

---

## 10. Relación con agentes

- **Continue**
  - ensambla contexto referencial;
  - decide nivel de contexto necesario;
  - construye context packs Nivel 0/1.

- **OpenCode**
  - recibe handoffs compactos;
  - consulta archivos específicos;
  - devuelve evidencia estructurada sin volcar raw.

- **MCP**
  - provee referencias, estados, conteos, rutas y previews compactas;
  - no devuelve dumps extensos por defecto.

- **Usuario**
  - define intención, alcance y nivel de detalle;
  - autoriza elevación a Nivel 3/4 cuando corresponda.

---

## 11. Índices livianos (fuentes referenciales)

Este protocolo opera junto con:

- `docs/context/ACTION_INDEX.md`
- `docs/context/DECISION_INDEX.md`
- `docs/context/RUN_INDEX.md`
- `docs/context/REFERENCE_MAP.md`

Regla: estos índices no deben contener logs/dumps; solo referencias y metadatos.
