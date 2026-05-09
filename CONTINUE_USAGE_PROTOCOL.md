<!-- START: CONTINUE_GEMINI_CONTEXT_V0_2 -->

---

## Actualización v0.2 — Continue + Gemini como copiloto contextual

Esta sección actualiza el rol de Continue dentro de la arquitectura definida en `AGENT_ORCHESTRATION.md`, `MODEL_ROUTING.md` y `AGENT_RULES.md`.

Continue operará como copiloto contextual dentro del IDE, apoyado preferentemente por Gemini API gratuita para tareas de lectura amplia, análisis documental y preparación de contexto.

Continue no será el ejecutor principal de cambios críticos. Su valor principal será ayudar a comprender, organizar, validar y preparar contexto para OpenCode, Zen, Replit o revisión humana.

### 1. Rol principal de Continue

Continue debe operar como:

- copiloto IDE;
- lector y organizador de contexto;
- analista preliminar de documentación y código;
- preparador de paquetes de contexto;
- revisor preliminar de coherencia;
- apoyo para handoffs;
- asistente para explicación de diffs y decisiones.

Continue puede revisar archivos del repositorio, documentación técnica y fragmentos de código, pero debe declarar qué fuentes o archivos revisó cuando entregue un análisis relevante.

### 2. Modelo recomendado

El modelo principal recomendado para Continue será:

    gemini-3-flash-preview

Modelo auxiliar para tareas livianas:

    gemini-3.1-flash-lite-preview

Uso esperado de Gemini en Continue:

- lectura amplia de documentación;
- análisis de coherencia;
- preparación de contexto;
- explicación técnica;
- revisión preliminar;
- identificación de contradicciones;
- apoyo en handoffs;
- resumen de reglas relevantes.

### 3. Contexto amplio, no contexto indiscriminado

La capacidad de contexto amplio no autoriza a cargar información innecesaria.

Regla:

    Contexto amplio sí.
    Contexto indiscriminado no.

Continue debe priorizar contexto curado, suficiente y trazable.

Orden recomendado del contexto:

1. Reglas permanentes del proyecto.
2. `PROJECT_CONTEXT.md`.
3. `AGENT_RULES.md`.
4. `MODEL_ROUTING.md`.
5. `AGENT_ORCHESTRATION.md`.
6. `SECURITY_POLICY.md`.
7. `REPLIT_HANDOFF.md`.
8. Handoff o tarea actual.
9. Archivos relevantes.
10. Pregunta o instrucción final concreta.

### 4. Buenas prácticas de prompt para contexto largo

Cuando se use Gemini con contexto amplio, la instrucción final debe quedar al final del prompt.

Estructura recomendada:

    [Reglas permanentes]
    [Contexto del proyecto]
    [Documentación relevante]
    [Archivos relevantes]
    [Evidencia de la tarea]
    [Pregunta final concreta]

Regla:

    La pregunta final debe ser específica, accionable y alineada con el resultado esperado.

### 5. Qué puede hacer Continue

Continue puede:

- analizar documentación;
- comparar instrucciones;
- revisar coherencia entre archivos;
- preparar contexto para OpenCode;
- ayudar a clasificar tareas;
- sugerir qué agente debe intervenir;
- explicar riesgos preliminares;
- revisar handoffs;
- sugerir comandos seguros sin ejecutarlos automáticamente;
- ayudar a resumir aprendizajes.

### 6. Qué no debe hacer Continue

Continue no debe actuar como único ejecutor para:

- cambios críticos de código;
- cambios multiarchivo sensibles;
- seguridad;
- auth;
- secrets;
- migraciones;
- deployment;
- operaciones destructivas;
- modificaciones productivas;
- cambios en variables de entorno reales;
- ejecución de comandos peligrosos.

Regla:

    Para ejecución, debugging operativo, revisión de diffs, seguridad o handoff a Replit, debe intervenir OpenCode según `AGENT_ORCHESTRATION.md` y `MODEL_ROUTING.md`.

### 7. Relación con OpenCode

Continue prepara y valida contexto.

OpenCode ejecuta, diagnostica, revisa diffs y coordina agentes especializados.

Flujo recomendado:

    Continue entiende y organiza contexto.
    OpenCode clasifica, valida, planifica o ejecuta.
    Zen continúa o escala cuando corresponda.
    Replit valida entorno real cuando aplique.

Continue puede preparar insumos para OpenCode, incluyendo:

- resumen de contexto;
- archivos relevantes;
- reglas aplicables;
- riesgos preliminares;
- preguntas abiertas;
- alcance sugerido;
- restricciones;
- handoff inicial.

### 8. Relación con Zen y premium

Continue no decide por sí solo usar modelos premium.

Puede recomendar escalamiento cuando identifique:

- volumen alto de información;
- contradicciones relevantes;
- riesgos de seguridad;
- falta de contexto suficiente;
- impacto arquitectónico;
- necesidad de validación con modelo más fuerte.

La decisión de escalamiento debe seguir `MODEL_ROUTING.md` y `AGENT_ORCHESTRATION.md`.

### 9. Seguridad y privacidad

Continue no debe incluir en prompts hacia modelos externos:

- `.env`;
- `.env.*`;
- secrets;
- tokens;
- credenciales;
- llaves privadas;
- dumps de base de datos;
- datos personales reales;
- logs con PII;
- archivos sensibles de cliente;
- credenciales Replit, GitHub, Azure, OpenAI, Google, Anthropic u otros proveedores.

Solo puede usar:

- código fuente sin secrets;
- documentación técnica no sensible;
- logs depurados;
- errores anonimizados;
- diffs revisables;
- handoffs sin credenciales;
- configuración estructural sin valores secretos.

### 10. Salida esperada de Continue

Cuando Continue realice análisis contextual, debe entregar preferentemente:

- objetivo entendido;
- fuentes o archivos revisados;
- reglas aplicables;
- contexto relevante;
- riesgos preliminares;
- agente sugerido;
- modelo o línea sugerida según routing;
- preguntas abiertas;
- siguiente acción recomendada.

Formato recomendado:

    Análisis contextual:
    - Objetivo:
    - Fuentes revisadas:
    - Reglas aplicables:
    - Riesgos:
    - Agente recomendado:
    - Modelo/línea sugerida:
    - Siguiente paso:

<!-- END: CONTINUE_GEMINI_CONTEXT_V0_2 -->

# CONTINUE_USAGE_PROTOCOL.md

## Propósito

Este documento define cómo usar Continue en VS Code dentro del orquestador local de agentes.

Continue debe operar como copiloto principal de análisis, revisión, edición menor, preparación de tareas para OpenCode y preparación de handoffs hacia Replit.

El objetivo es trabajar de forma eficiente, sin generar documentación innecesaria y sin perder trazabilidad.

---

## Rol de Continue

Continue cumple estas funciones:

1. Leer y usar el contexto del proyecto.
2. Ayudar a clasificar tareas.
3. Recomendar modelo, agente o entorno según `MODEL_ROUTING.md`.
4. Proponer cambios controlados.
5. Ejecutar ediciones menores cuando el riesgo sea bajo.
6. Preparar tareas estructuradas para OpenCode.
7. Preparar handoffs compactos para Replit.
8. Revisar diffs, errores, logs y resultados de pruebas.
9. Ayudar a actualizar documentación mínima cuando haya cambios reales.

Continue no debe actuar como ejecutor autónomo de cambios complejos sin plan.

---

## Modo operativo: Plan vs Build (gobierno)

Continue debe pedir o confirmar explícitamente con el usuario el modo operativo:

- **Plan**: análisis/diagnóstico/diseño/revisión/propuesta/handoff. No modifica archivos ni ejecuta comandos.
- **Build**: el usuario autoriza ejecución dentro de un alcance definido. En este modo, Continue puede coordinar orquestación “de fondo” (Continue → MCP → OpenCode) sin pedir aprobación por cada microacción ordinaria **dentro del alcance**.

Umbrales de aprobación (siempre requieren autorización humana, incluso en Build):

- escalar a modelo premium;
- usar Replit o entorno externo;
- acceder/modificar secrets;
- deployment, migraciones o acciones destructivas;
- mover/borrar/renombrar archivos maestros;
- ampliar alcance.

Política canónica:

- `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md` → **PLAN_BUILD_APPROVAL_AND_BACKGROUND_ORCHESTRATION_POLICY**

---

## Transparencia progresiva en chat

Cuando Continue coordine un flujo (Plan o Build), debe reportar primero:

- objetivo;
- etapa actual;
- acción central;
- resultado parcial;
- riesgos/bloqueos;
- si requiere decisión humana;
- próximo paso.

Y dejar como detalle técnico (si se solicita): archivos tocados, evidencia, `TRACE`, `RUN_SUMMARY`, `agent_outputs`, `raw_outputs`.

---

## Archivos de contexto que debe revisar

Antes de trabajar sobre un proyecto activado, Continue debe considerar estos archivos:

```text
AGENT_RULES.md
PROJECT_CONTEXT.md
MODEL_ROUTING.md
SECURITY_POLICY.md
REPLIT_HANDOFF.md
PROJECT_ACTIVATION_PROTOCOL.md
SECRETS_MANIFEST.md
QUICK_START.md
```

---

## CONTEXT_BUDGET_AND_MINIMAL_MODE_POLICY

### Objetivo
Reducir consumo de tokens/contexto en Continue priorizando **cobertura por capas** (inventario → rutas → preview → fragmento) y evitando cargar artefactos voluminosos.

### Reglas operativas

1) **Usar `run_id` + rutas + conteos, no contenido completo**
- Para runs/handoffs: reportar `run_id`, rutas, existencia, conteos y previews cortos.
- No pegar `TRACE.md`, `RUN_SUMMARY.md` o handoffs completos en el chat salvo solicitud explícita.

2) **Artefactos voluminosos: exclusión por defecto**
No deben entrar al contexto “normal” (ni copiarse al chat) estos artefactos:
- `docs/agent_runs/**`
- `docs/agent_queue/**`
- `**/raw_outputs/**`
- `**/TRACE.md`
- `**/RUN_SUMMARY.md`
- `**/*_stdout.log`
- `**/*_stderr.log`

3) **MCP: política compact-first**
- Preferir: `get_run_status` / `check_opencode_run_status`.
- Evitar: `show_latest_run` desde Continue (es verboso). Usarlo solo si el usuario pide detalle y **resumiendo** (preview-only).

4) **Evitar fuentes automáticas salvo necesidad**
- No usar *Active File* para handoffs, TRACE, RUN_SUMMARY o logs.
- No usar `@Terminal`, `@Git Diff`, `@Open` o “archivos abiertos” salvo necesidad específica.
  - Si se usan, extraer solo el fragmento mínimo relevante.

5) **Reglas Always Applied: versión mínima**
- Mantener reglas permanentes (Always Applied) en versión mínima.
- Preferir referencias a este protocolo en lugar de duplicar listas/formats extensos.

6) **Autorización antes de cargar contexto grande**
Antes de:
- pegar un documento largo,
- pegar un log,
- abrir/pegar secciones grandes de `TRACE.md` o `RUN_SUMMARY.md`,
Continue debe pedir autorización explícita y justificar por qué es necesario.

---

## Exclusiones configurables para Continue (best-effort)

Este repositorio incluye un archivo `.continueignore` con exclusiones para reducir contaminación de contexto.

Limitación: **no hay evidencia dentro del repo** de que la versión instalada de Continue lea `.continueignore`. Si no surte efecto, mantener esta política y configurar exclusiones/ignore en la configuración real de Continue (fuera del repo), según la versión instalada.
