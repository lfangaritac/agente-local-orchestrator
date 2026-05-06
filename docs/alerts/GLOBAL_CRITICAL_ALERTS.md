# GLOBAL_CRITICAL_ALERTS.md

## 1. Propósito

Consolidar alertas críticas transversales del orquestador local `C:\Agente`.

Estas alertas deben consultarse antes de tareas de complejidad media, alta o crítica, y siempre que una tarea involucre contexto multi-proyecto, Continue, OpenCode, Go, Zen, modelos premium, Replit, seguridad, ejecución, cambios de código, documentación maestra o sincronización de contexto.

Este documento no reemplaza las alertas locales de cada proyecto objetivo. Las complementa.

---

## 2. Regla general de uso

Antes de actuar, Continue, OpenCode o cualquier agente del sistema debe verificar si la tarea activa alguna alerta global.

Si una alerta aplica, el agente debe:

- mencionarla en su análisis o handoff;
- explicar cómo la va a mitigar;
- bloquear ejecución si la alerta exige bloqueo;
- pedir autorización humana si la alerta lo requiere;
- registrar si la alerta genera una lección aprendida.

---

## 3. Formato de alertas

Cada alerta debe registrar:

- `alert_id`
- `severity`
- `scope`
- `trigger`
- `description`
- `do_not_do`
- `required_check`
- `source`
- `last_verified`
- `applies_to`

---

## 4. Alertas globales activas

### ALERT-GLOBAL-001 — No inventar identidad del proyecto objetivo

- `alert_id`: ALERT-GLOBAL-001
- `severity`: high
- `scope`: global
- `trigger`: tareas sobre proyectos objetivo, habilitación, contexto, handoffs o análisis multi-proyecto
- `description`: Los agentes no deben inventar ni asumir la identidad del proyecto objetivo. Si el proyecto objetivo no está confirmado, deben declararlo como no confirmado. Alias, nombres de carpetas, textos de ejemplo o referencias parciales no constituyen identidad formal.
- `do_not_do`: no afirmar que el proyecto objetivo es AIP, Embajadores, Data Privacy, Replit App u otro nombre sin confirmación explícita o registro.
- `required_check`: revisar `PROJECT_REGISTRY.md` y el contexto explícito del usuario.
- `source`: pruebas Continue → OpenCode; `TARGET_PROJECT_CONTEXT_CONTRACT.md`
- `last_verified`: 2026-05-05
- `applies_to`: Continue, OpenCode, handoffs, project enablement, context sync

---

### ALERT-GLOBAL-002 — No confundir OpenCode Go con lenguaje Go

- `alert_id`: ALERT-GLOBAL-002
- `severity`: high
- `scope`: global
- `trigger`: menciones a Go, OpenCode Go, modelos Go, routing o primera línea
- `description`: En esta arquitectura, Go se refiere a OpenCode Go como línea/proveedor/modelos de primera línea, no al lenguaje de programación Go, salvo que el usuario lo indique expresamente.
- `do_not_do`: no proponer microservicios en Go, binarios Go, endpoints Go ni arquitectura basada en lenguaje Go si la instrucción se refiere a OpenCode Go.
- `required_check`: revisar `MODEL_ROUTING.md`, `AGENT_ORCHESTRATION.md` y `TARGET_PROJECT_CONTEXT_CONTRACT.md`.
- `source`: prueba Continue → OpenCode en la que Continue confundió Go con arquitectura técnica.
- `last_verified`: 2026-05-05
- `applies_to`: Continue, OpenCode, model routing, handoffs

---

### ALERT-GLOBAL-003 — No confundir OpenCode Zen con red, bus o framework técnico

- `alert_id`: ALERT-GLOBAL-003
- `severity`: high
- `scope`: global
- `trigger`: menciones a Zen, OpenCode Zen, continuidad, escalamiento o premium
- `description`: En esta arquitectura, Zen se refiere a OpenCode Zen como capa pay-as-you-go, continuidad, escalamiento económico o premium. No es una red, bus de eventos, framework, orquestador técnico ni "Zero Entropy Network".
- `do_not_do`: no inventar conceptos como Zen bus, Zero Entropy Network, bus de eventos Zen o arquitectura Zen si no están documentados.
- `required_check`: revisar `MODEL_ROUTING.md`, `AGENT_ORCHESTRATION.md` y `AGENT_RULES.md`.
- `source`: prueba Continue → OpenCode en la que Continue inventó componentes técnicos no documentados.
- `last_verified`: 2026-05-05
- `applies_to`: Continue, OpenCode, Zen routing, handoffs, escalation

---

### ALERT-GLOBAL-004 — No afirmar inexistencia por falta de visibilidad

- `alert_id`: ALERT-GLOBAL-004
- `severity`: high
- `scope`: global
- `trigger`: cuando un agente no ve un archivo requerido
- `description`: Si un archivo obligatorio no es visible para un agente, el agente no debe afirmar automáticamente que no existe. Debe distinguir entre visible, no visible desde este agente, visible en ruta alternativa, pendiente de verificación por otro agente o verificado como inexistente por herramienta confiable.
- `do_not_do`: no decir "el archivo no existe" si solo no aparece en el contexto recuperado por Continue u otra herramienta.
- `required_check`: pedir verificación por OpenCode o herramienta de filesystem; revisar rutas alternativas e índices.
- `source`: OpenCode verificó que `AGENT_ORCHESTRATION.md` existía en raíz aunque Continue lo había reportado como no existente.
- `last_verified`: 2026-05-05
- `applies_to`: Continue, OpenCode, context validation, project enablement

---

### ALERT-GLOBAL-005 — No aceptar handoffs sin fuentes suficientes

- `alert_id`: ALERT-GLOBAL-005
- `severity`: high
- `scope`: global
- `trigger`: recepción de handoffs Continue → OpenCode o OpenCode → Continue
- `description`: Ningún handoff debe considerarse suficiente si no declara fuentes revisadas, fuentes no revisadas, reglas aplicables, escenario, riesgo, volumen, agente sugerido, modelo/línea sugerida, restricciones y siguiente acción.
- `do_not_do`: no ejecutar con handoffs genéricos, circulares, sin fuentes o sin agente especializado.
- `required_check`: validar contra `.continue/rules/continue-opencode-handoff.md`, `.continue/prompts/handoff-to-opencode.md`, `AGENT_RULES.md` y `MODEL_ROUTING.md`.
- `source`: pruebas de handoff Continue → OpenCode.
- `last_verified`: 2026-05-05
- `applies_to`: Continue, OpenCode, mini-orchestration, handoffs

---

### ALERT-GLOBAL-006 — No ejecutar si el contexto está incompleto

- `alert_id`: ALERT-GLOBAL-006
- `severity`: critical
- `scope`: global
- `trigger`: tareas de ejecución, edición, debugging, arquitectura, seguridad o cambios de código con contexto insuficiente
- `description`: Si el contexto requerido está incompleto, el agente debe operar en modo diagnóstico y no en modo ejecución.
- `do_not_do`: no modificar archivos, ejecutar comandos, proponer cambios productivos, escalar o hacer handoff operativo sin declarar suficiencia contextual.
- `required_check`: aplicar `TARGET_PROJECT_CONTEXT_CONTRACT.md`, `PROJECT_ENABLEMENT_PROTOCOL.md`, `CONTEXT_SYNC_PROTOCOL.md` y `DOCUMENTATION_CODE_ALIGNMENT_PROTOCOL.md`.
- `source`: definición del contrato multi-proyecto y protocolos de sincronización.
- `last_verified`: 2026-05-05
- `applies_to`: Continue, OpenCode, Replit, premium models, execution

---

### ALERT-GLOBAL-007 — No omitir alertas críticas en tareas medias, altas o críticas

- `alert_id`: ALERT-GLOBAL-007
- `severity`: high
- `scope`: global
- `trigger`: tareas de complejidad media, alta o crítica
- `description`: Antes de tareas medias, altas o críticas, los agentes deben consultar alertas globales y alertas locales del proyecto objetivo si existen.
- `do_not_do`: no iniciar análisis, handoff, planificación o ejecución sin revisar alertas aplicables.
- `required_check`: revisar `docs/alerts/GLOBAL_CRITICAL_ALERTS.md` y `docs/projects/<project-id>/CRITICAL_ALERTS.md`.
- `source`: `TARGET_PROJECT_CONTEXT_CONTRACT.md`
- `last_verified`: 2026-05-05
- `applies_to`: Continue, OpenCode, project tasks, escalations

---

### ALERT-GLOBAL-008 — No elevar a premium sin activador válido

- `alert_id`: ALERT-GLOBAL-008
- `severity`: medium
- `scope`: global
- `trigger`: recomendaciones de Zen premium, modelos premium o escalamiento
- `description`: El escalamiento premium debe justificarse por solicitud del usuario, seguridad, auth, permisos, secrets, datos personales, debugging complejo, arquitectura, refactor transversal, migraciones, deployment, volumen alto sensible, revisión final sensible o costo de equivocarse superior al costo de escalar.
- `do_not_do`: no escalar por comodidad, preferencia o falta de disciplina contextual.
- `required_check`: revisar `MODEL_ROUTING.md` y `AGENT_RULES.md`.
- `source`: arquitectura Go + Zen + Premium v0.2/v0.3.
- `last_verified`: 2026-05-05
- `applies_to`: Continue, OpenCode, model routing, Zen premium

---

### ALERT-GLOBAL-009 — No permitir colusión o condescendencia entre agentes

- `alert_id`: ALERT-GLOBAL-009
- `severity`: high
- `scope`: global
- `trigger`: interacciones Continue ↔ OpenCode, revisiones cruzadas o validaciones de handoff
- `description`: Los agentes no deben confirmar premisas del usuario ni aceptar respuestas de otro agente sin validación técnica. Deben promover contradicción técnica fundada, colaboración con roles claros, trazabilidad e identificación de incertidumbre.
- `do_not_do`: no validar por cortesía, no suavizar alertas, no omitir errores factuales, no reforzar una conclusión sin verificar fuentes.
- `required_check`: revisar fuentes, declarar incertidumbre, contrastar contra documentación y código cuando aplique.
- `source`: reglas preventivas del contrato de contexto multi-proyecto.
- `last_verified`: 2026-05-05
- `applies_to`: Continue, OpenCode, model-evaluator, context-validator, premium reviewers

---

### ALERT-GLOBAL-010 — No perder contexto embebido del proyecto objetivo

- `alert_id`: ALERT-GLOBAL-010
- `severity`: high
- `scope`: global
- `trigger`: habilitación, sincronización, documentación, análisis de proyecto existente o contrastación documentación-código
- `description`: Los proyectos existentes pueden contener contexto crítico en comentarios, estructura, scripts, tests, configuraciones, nombres de funciones, schemas, migraciones y código. Ese contexto debe indagarse, indexarse y contrastarse.
- `do_not_do`: no consolidar un `PROJECT_CONTEXT.md` único ignorando documentación distribuida o contexto embebido.
- `required_check`: aplicar `DOCUMENTATION_CODE_ALIGNMENT_PROTOCOL.md` y actualizar `CONTEXT_INDEX.md`/`CODE_CONTEXT_MAP.md`.
- `source`: contrato de contexto multi-proyecto.
- `last_verified`: 2026-05-05
- `applies_to`: project enablement, Continue, OpenCode, context sync

---

## 5. Regla de actualización

Este archivo debe actualizarse cuando:

- se detecte un error crítico repetible;
- un agente invente contexto;
- un handoff incorrecto pase validación;
- se identifique una prohibición transversal;
- se repita un patrón de fallo;
- un caso local revele una alerta aplicable a múltiples proyectos;
- un modelo premium, Continue u OpenCode incurra en errores prevenibles por contexto.

Todo cambio debe registrarse en Git y, si corresponde, alimentar `docs/lessons/GLOBAL_LESSONS_LEARNED.md`.
