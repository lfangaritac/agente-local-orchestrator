# GLOBAL_LESSONS_LEARNED.md

## 1. Propósito

Consolidar lecciones aprendidas transversales del orquestador local `C:\Agente`.

Este documento registra aprendizajes derivados de la operación cotidiana de Continue, OpenCode, Replit, modelos Go, Zen, modelos premium y proyectos objetivo.

No debe almacenar preferencias específicas de un proyecto, salvo que representen una regla, protocolo, patrón, anti-patrón o buena práctica reutilizable para el orquestador.

---

## 2. Regla general

Una lección debe registrarse como transversal solo si:

- aplica a múltiples proyectos;
- mejora reglas de orquestación;
- mejora routing de modelos;
- previene errores repetibles;
- fortalece seguridad;
- mejora handoffs;
- mejora sincronización de contexto;
- mejora coordinación entre agentes;
- reduce ambigüedad;
- mejora calidad técnica;
- está alineada con buenas prácticas.

No debe registrarse como transversal si:

- solo refleja una preferencia local;
- solo aplica a un proyecto;
- no fue validada;
- contradice reglas de seguridad;
- depende de una condición temporal;
- no mejora el modelo de orquestación.

---

## 3. Formato de lecciones

Cada lección debe registrar:

- `lesson_id`
- `title`
- `scope`
- `source`
- `problem`
- `lesson`
- `recommended_rule_or_change`
- `applies_to`
- `status`
- `last_verified`

---

## 4. Lecciones transversales activas

### LESSON-GLOBAL-001 — Gemini en Continue requiere reglas fuertes y contexto explícito

- `lesson_id`: LESSON-GLOBAL-001
- `title`: Gemini en Continue requiere reglas fuertes y contexto explícito
- `scope`: global
- `source`: pruebas Continue + Gemini → OpenCode
- `problem`: Gemini funcionó técnicamente en Continue, pero produjo handoffs genéricos e inferencias incorrectas cuando no recibió contexto visible, reglas estrictas o fuentes obligatorias.
- `lesson`: Gemini puede aportar valor como copiloto contextual, pero no debe operar sin reglas locales, fuentes explícitas y estructura obligatoria de handoff.
- `recommended_rule_or_change`: mantener reglas en `.continue/rules`, prompts en `.continue/prompts` y exigir declaración de archivos revisados, escenario, riesgo, volumen, agente OpenCode y modelo/línea sugerida.
- `applies_to`: Continue, Gemini, handoffs, context validation
- `status`: active
- `last_verified`: 2026-05-05

---

### LESSON-GLOBAL-002 — OpenCode debe validar handoffs de Continue antes de actuar

- `lesson_id`: LESSON-GLOBAL-002
- `title`: OpenCode debe validar handoffs de Continue antes de actuar
- `scope`: global
- `source`: pruebas Continue → OpenCode
- `problem`: El primer handoff de Continue fue insuficiente y contenía errores de contexto. OpenCode detectó falta de archivos clave, agente genérico, modelo no específico y ambigüedad de alcance.
- `lesson`: OpenCode no debe ejecutar ni planificar cambios con base en un handoff sin validarlo previamente.
- `recommended_rule_or_change`: mantener una fase obligatoria `context-validator` o `model-evaluator` antes de ejecución cuando el handoff provenga de Continue y sea de complejidad media o superior.
- `applies_to`: OpenCode, Continue, mini-orchestration, handoffs
- `status`: active
- `last_verified`: 2026-05-05

---

### LESSON-GLOBAL-003 — La visibilidad parcial de archivos debe tratarse como falla de contexto

- `lesson_id`: LESSON-GLOBAL-003
- `title`: La visibilidad parcial de archivos debe tratarse como falla de contexto
- `scope`: global
- `source`: pruebas donde Continue no veía `AGENT_ORCHESTRATION.md` en raíz
- `problem`: Continue afirmó que un archivo no existía porque no era visible desde su contexto, aunque OpenCode verificó que sí existía.
- `lesson`: La no visibilidad desde un agente no equivale a inexistencia del archivo.
- `recommended_rule_or_change`: si un archivo obligatorio no es visible, el agente debe declarar falla de contexto, revisar rutas alternativas o solicitar verificación por OpenCode antes de emitir handoff final.
- `applies_to`: Continue, OpenCode, context contract, project enablement
- `status`: active
- `last_verified`: 2026-05-05

---

### LESSON-GLOBAL-004 — No permitir inferencias técnicas no documentadas sobre Go o Zen

- `lesson_id`: LESSON-GLOBAL-004
- `title`: No permitir inferencias técnicas no documentadas sobre Go o Zen
- `scope`: global
- `source`: prueba Continue donde Gemini inventó "Zero Entropy Network", "Zen bus" y microservicios en Go
- `problem`: El modelo interpretó Go como lenguaje de programación y Zen como arquitectura técnica, aunque en el orquestador Go y Zen son líneas/proveedores de modelos OpenCode.
- `lesson`: Los términos operativos del orquestador deben protegerse contra asociaciones externas no documentadas.
- `recommended_rule_or_change`: consultar `MODEL_ROUTING.md`, `AGENT_ORCHESTRATION.md` y `GLOBAL_CRITICAL_ALERTS.md` antes de interpretar Go, Zen, Premium o Replit en tareas de agentes.
- `applies_to`: Continue, OpenCode, model routing, handoffs
- `status`: active
- `last_verified`: 2026-05-05

---

### LESSON-GLOBAL-005 — La mini-orquestación debe ser bidireccional en complejidad media o superior

- `lesson_id`: LESSON-GLOBAL-005
- `title`: La mini-orquestación debe ser bidireccional en complejidad media o superior
- `scope`: global
- `source`: diseño de coordinación Continue ↔ OpenCode
- `problem`: Un flujo unidireccional Continue → OpenCode puede propagar errores de contexto si OpenCode no devuelve feedback y Continue no refina el handoff.
- `lesson`: Para tareas medias o superiores, debe existir al menos un ciclo de feedback entre Continue y OpenCode cuando se detecten errores, ambigüedad o insuficiencia contextual.
- `recommended_rule_or_change`: aplicar `Continue contextualiza → OpenCode valida → Continue refina → OpenCode actúa` con límite de ciclos y responsabilidades claras.
- `applies_to`: Continue, OpenCode, mini-orchestration, project tasks
- `status`: active
- `last_verified`: 2026-05-05

---

### LESSON-GLOBAL-006 — Continue también debe poder acceder a nivel 3 al código

- `lesson_id`: LESSON-GLOBAL-006
- `title`: Continue también debe poder acceder a nivel 3 al código
- `scope`: global
- `source`: revisión del contrato de contexto multi-proyecto
- `problem`: Limitar el análisis profundo de código solo a OpenCode reduce la calidad del contexto que Continue puede preparar.
- `lesson`: Continue debe poder leer código a nivel profundo cuando sea necesario para construir contexto, contrastar documentación, detectar inconsistencias o preparar handoffs sólidos.
- `recommended_rule_or_change`: permitir acceso nivel 3 a Continue para comprensión contextual, manteniendo a OpenCode como responsable de validación técnica, ejecución, debugging y diffs.
- `applies_to`: Continue, OpenCode, context contract, target projects
- `status`: active
- `last_verified`: 2026-05-05

---

### LESSON-GLOBAL-007 — El contexto del proyecto objetivo no debe reducirse a un único archivo

- `lesson_id`: LESSON-GLOBAL-007
- `title`: El contexto del proyecto objetivo no debe reducirse a un único archivo
- `scope`: global
- `source`: diseño del contrato de contexto multi-proyecto
- `problem`: Proyectos existentes pueden contener documentación formal, comentarios, configuración, scripts, tests y decisiones embebidas que se perderían si se consolida todo de forma simplificada en un único `PROJECT_CONTEXT.md`.
- `lesson`: El orquestador debe centralizar índices y síntesis, pero conservar referencias a fuentes distribuidas originales.
- `recommended_rule_or_change`: aplicar modelo híbrido de fuentes distribuidas + índices centralizados + síntesis curadas + referencias trazables.
- `applies_to`: project enablement, context sync, documentation-code alignment
- `status`: active
- `last_verified`: 2026-05-05

---

### LESSON-GLOBAL-008 — La contrastación documentación-código debe ser inicial y recurrente

- `lesson_id`: LESSON-GLOBAL-008
- `title`: La contrastación documentación-código debe ser inicial y recurrente
- `scope`: global
- `source`: diseño de `DOCUMENTATION_CODE_ALIGNMENT_PROTOCOL.md`
- `problem`: La documentación puede estar obsoleta, ser aspiracional o no reflejar el estado real del código.
- `lesson`: La documentación relevante debe contrastarse contra código, configuración, tests o comportamiento real al habilitar un proyecto y cuando la tarea lo requiera.
- `recommended_rule_or_change`: aplicar contrastación antes de cambios relevantes, escalamiento premium, handoff a Replit, debugging complejo y tareas que dependan de reglas de negocio.
- `applies_to`: Continue, OpenCode, project enablement, context sync
- `status`: active
- `last_verified`: 2026-05-05

---

### LESSON-GLOBAL-009 — El usuario no debe operar manualmente la coordinación entre agentes

- `lesson_id`: LESSON-GLOBAL-009
- `title`: El usuario no debe operar manualmente la coordinación entre agentes
- `scope`: global
- `source`: pruebas manuales Continue ↔ OpenCode
- `problem`: Copiar y pegar handoffs entre Continue y OpenCode es útil para pruebas, pero no debe ser el estado final del sistema.
- `lesson`: La experiencia final debe permitir que el usuario converse en un solo punto de entrada, mientras el orquestador selecciona agentes, modelos y transferencias internamente.
- `recommended_rule_or_change`: diseñar automatización futura para transferencia de handoffs, selección de agente/modelo, consulta de alertas, actualización de índices y solicitud de autorización solo cuando aplique.
- `applies_to`: automation, Continue, OpenCode, model routing
- `status`: active
- `last_verified`: 2026-05-05

---

### LESSON-GLOBAL-010 — Las alertas críticas deben entrar antes que el razonamiento de tarea

- `lesson_id`: LESSON-GLOBAL-010
- `title`: Las alertas críticas deben entrar antes que el razonamiento de tarea
- `scope`: global
- `source`: discusión sobre errores repetidos fuera de ventana de contexto
- `problem`: Algunos errores críticos quedan documentados en reportes pero no entran en la ventana de contexto de interacciones futuras.
- `lesson`: Las alertas críticas deben consultarse antes de tareas medias, altas o críticas para prevenir repetición de errores.
- `recommended_rule_or_change`: consultar `docs/alerts/GLOBAL_CRITICAL_ALERTS.md` y alertas locales del proyecto antes de análisis, handoff, planificación o ejecución relevante.
- `applies_to`: Continue, OpenCode, premium models, project tasks
- `status`: active
- `last_verified`: 2026-05-05

---

## 5. Regla de actualización

Este documento debe actualizarse cuando:

- se detecte una lección aplicable a más de un proyecto;
- se corrija un error recurrente del orquestador;
- se mejore el routing de modelos;
- se identifique un patrón o anti-patrón de agentes;
- se optimice la coordinación Continue ↔ OpenCode;
- se detecte una mejor práctica transversal;
- una alerta crítica derive en aprendizaje reutilizable;
- una experiencia local revele una mejora global del sistema.

Cada actualización debe registrarse en Git y, si aplica, reflejarse también en reglas, protocolos o alertas.

---

### LESSON-GLOBAL-011 — Las reglas no automatizan sin capa ejecutable

- `lesson_id`: LESSON-GLOBAL-011
- `title`: Las reglas no automatizan sin capa ejecutable
- `scope`: global
- `source`: diseño de automatización Continue ↔ OpenCode
- `problem`: Documentar que los agentes deben interactuar automáticamente no produce automatización real. Sin una capa ejecutable, el usuario sigue copiando handoffs, seleccionando modelos y trasladando contexto manualmente.
- `lesson`: Las reglas definen comportamiento esperado, pero la automatización requiere una capa operativa que conecte contexto, agentes, modelos, handoffs, alertas, lecciones, autorización humana y trazabilidad.
- `recommended_rule_or_change`: construir progresivamente una capa semiautomática, luego MCP local y posteriormente integración con OpenCode, manteniendo visibilidad del proceso para el usuario.
- `applies_to`: automation, Continue, OpenCode, MCP, model routing, handoffs
- `status`: active
- `last_verified`: 2026-05-05
