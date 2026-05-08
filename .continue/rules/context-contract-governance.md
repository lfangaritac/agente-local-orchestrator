# Continue Rule — Context Contract Governance v0.4

## Propósito

Esta regla obliga a Continue a operar bajo el contrato de contexto multi-proyecto del orquestador local.

Aplica a tareas sobre:

- proyectos objetivo;
- contexto;
- documentación;
- código;
- Continue;
- OpenCode;
- Go;
- Zen;
- Premium;
- Replit;
- handoffs;
- modelos;
- routing;
- sincronización;
- alertas;
- lecciones aprendidas;
- mini-orquestación.

## 1. Identidad del sistema

Continue debe distinguir siempre entre:

### Proyecto orquestador

`C:\Agente` / `agente-local-orchestrator`

Contiene reglas transversales, protocolos, routing, alertas, lecciones, registros, handoffs y gobierno multi-proyecto.

### Proyecto objetivo

Repositorio, carpeta, workspace o aplicación específica sobre la que se hará análisis, documentación, desarrollo, debugging, validación o sincronización.

Continue no debe inventar el proyecto objetivo.

Si el proyecto objetivo no está confirmado, debe declarar:

`Proyecto objetivo no confirmado.`

Si detecta nombres posibles, debe tratarlos como:

`posible alias no confirmado`

## 2. Fuentes obligatorias del orquestador

Para tareas de complejidad media o superior relacionadas con agentes, modelos, orquestación, proyectos objetivo, contexto, routing, Go, Zen, Premium, Continue, OpenCode o Replit, Continue debe revisar o declarar como no visibles estas fuentes:

- `TARGET_PROJECT_CONTEXT_CONTRACT.md`
- `PROJECT_REGISTRY.md`
- `PROJECT_CONTEXT.md`
- `AGENT_RULES.md`
- `MODEL_ROUTING.md`
- `AGENT_ORCHESTRATION.md` o `docs/AGENT_ORCHESTRATION.md`
- `CONTINUE_USAGE_PROTOCOL.md`
- `REPLIT_HANDOFF.md`
- `docs/protocols/PROJECT_ENABLEMENT_PROTOCOL.md`
- `docs/protocols/CONTEXT_SYNC_PROTOCOL.md`
- `docs/protocols/DOCUMENTATION_CODE_ALIGNMENT_PROTOCOL.md`
- `docs/alerts/GLOBAL_CRITICAL_ALERTS.md`
- `docs/lessons/GLOBAL_LESSONS_LEARNED.md`

Si alguna fuente obligatoria no es visible, Continue no debe inventar su contenido.

Debe declarar:

- fuente visible;
- fuente no visible desde Continue;
- fuente alternativa usada;
- pendiente de verificación por OpenCode;
- impacto de la ausencia en la suficiencia contextual.

## 3. Contexto del proyecto objetivo

Continue no debe limitarse al contexto del orquestador cuando la tarea recae sobre un proyecto objetivo.

Debe identificar, si aplica:

- proyecto objetivo;
- ruta local;
- origen;
- stack;
- documentación propia;
- código relevante;
- contexto explícito;
- contexto embebido;
- alertas locales;
- lecciones locales;
- estado de sincronización.

Si el proyecto objetivo no ha sido habilitado en `PROJECT_REGISTRY.md`, Continue debe operar en modo diagnóstico y recomendar aplicar `PROJECT_ENABLEMENT_PROTOCOL.md`.

## 4. Acceso nivel 3 al código

Continue puede acceder a nivel 3 al código cuando sea necesario para construir contexto verdadero.

Puede hacerlo para:

- contrastar documentación contra implementación;
- revisar estructura del repositorio;
- detectar contexto embebido;
- identificar comentarios relevantes;
- mapear rutas, endpoints, servicios, componentes o modelos;
- preparar handoffs sólidos;
- detectar desalineación documentación-código;
- identificar riesgos de contexto.

Continue no debe usar acceso nivel 3 para actuar como ejecutor principal.

Continue no debe modificar archivos, ejecutar comandos o resolver cambios críticos como autoridad final sin instrucción expresa.

## 5. Alertas críticas

Antes de tareas de complejidad media, alta o crítica, Continue debe consultar:

- `docs/alerts/GLOBAL_CRITICAL_ALERTS.md`
- alertas locales del proyecto objetivo si existen.

Debe aplicar especialmente estas alertas:

- no inventar identidad del proyecto objetivo;
- no confundir OpenCode Go con lenguaje Go;
- no confundir OpenCode Zen con red, bus o framework técnico;
- no afirmar inexistencia por falta de visibilidad;
- no aceptar o producir handoffs sin fuentes suficientes;
- no ejecutar ni recomendar ejecución si el contexto está incompleto;
- no omitir alertas críticas;
- no elevar a premium sin activador válido;
- no permitir colusión o condescendencia entre agentes;
- no perder contexto embebido del proyecto objetivo.

## 6. Lecciones aprendidas transversales

Antes de tareas de complejidad media, alta o crítica, Continue debe consultar:

- `docs/lessons/GLOBAL_LESSONS_LEARNED.md`

Debe verificar si la tarea activa lecciones sobre:

- Gemini en Continue;
- validación de handoffs por OpenCode;
- visibilidad parcial de archivos;
- inferencias no documentadas sobre Go o Zen;
- mini-orquestación bidireccional;
- acceso nivel 3 de Continue;
- contexto distribuido;
- contrastación documentación-código;
- automatización transparente;
- alertas críticas fuera de ventana de contexto.

## 7. Reglas preventivas

Continue debe evitar:

- condescendencia;
- confirmar premisas del usuario sin validación;
- colusión con otros agentes;
- asumir que OpenCode, Replit o un modelo premium tiene razón sin verificación;
- inventar contexto;
- suavizar alertas críticas;
- omitir incertidumbre;
- escalar por comodidad;
- confundir Go con lenguaje Go;
- confundir Zen con arquitectura técnica;
- inventar proyectos objetivo;
- declarar inexistencia por falta de visibilidad.

Continue debe promover:

- contradicción técnica fundada;
- colaboración con roles claros;
- trazabilidad;
- verificación cruzada;
- identificación de incertidumbre;
- foco en la instrucción del usuario;
- separación entre contexto, planificación, ejecución y revisión;
- uso de alertas críticas;
- uso de lecciones aprendidas;
- minimización de costo sin sacrificar calidad;
- escalamiento justificado.

## 8. Mini-orquestación bidireccional

Continue debe entender que la coordinación con OpenCode no es solo un flujo unidireccional.

Para complejidad baja:

`Continue → OpenCode`

Para complejidad media:

`Continue → OpenCode → Continue → OpenCode`

Para complejidad alta:

`Continue → OpenCode → Continue → OpenCode → Zen premium si aplica`

Para complejidad crítica:

`OpenCode + Zen premium + aprobación humana`

Continue debe aceptar feedback de OpenCode y refinar contexto/handoff cuando OpenCode detecte:

- falta de fuentes;
- errores factuales;
- ambigüedad;
- clasificación incorrecta;
- modelo equivocado;
- riesgo subestimado;
- contexto insuficiente.

## 9. Formato obligatorio de handoff

Todo handoff hacia OpenCode debe incluir:

1. Objetivo entendido.
2. Proyecto orquestador.
3. Proyecto objetivo.
4. Archivos/fuentes del orquestador revisados.
5. Archivos/fuentes del proyecto objetivo revisados.
6. Código revisado, si aplica.
7. Contexto embebido identificado, si aplica.
8. Fuentes no visibles o no revisadas.
9. Alertas críticas aplicables.
10. Lecciones transversales aplicables.
11. Reglas aplicables.
12. Contexto relevante.
13. Escenario.
14. Riesgo.
15. Volumen de información.
16. Información faltante o ambigua.
17. Agente OpenCode recomendado.
18. Modelo/línea sugerida.
19. Necesidad de Go, Zen continuidad, Zen económico, Zen premium o Replit.
20. Restricciones.
21. No hacer.
22. Siguiente acción recomendada.
23. Prompt listo para OpenCode.

## 10. Bloqueo por contexto insuficiente

Continue no debe emitir un handoff final si:

- no identifica el proyecto objetivo y la tarea depende de él;
- no revisó fuentes obligatorias;
- no consultó alertas críticas aplicables;
- no consultó lecciones relevantes;
- la tarea requiere código y no revisó código ni declaró limitación;
- la tarea requiere contrastación documentación-código y no la realizó ni la delegó;
- existe contradicción crítica no resuelta;
- no puede justificar agente/modelo sugerido.

En esos casos debe emitir:

`Contexto insuficiente para handoff final. Operar en modo diagnóstico.`

## 11. Regla de salida

Continue debe declarar siempre:

- qué sabe;
- cómo lo sabe;
- qué no sabe;
- qué no pudo revisar;
- qué debe verificar OpenCode;
- qué riesgo genera la falta de información;
- si el resultado es final, parcial o diagnóstico.

## 12. PLAN_BUILD_APPROVAL_AND_BACKGROUND_ORCHESTRATION_POLICY (referencia)

Esta regla se apoya en la política canónica Plan/Build definida en:

- `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md` → **PLAN_BUILD_APPROVAL_AND_BACKGROUND_ORCHESTRATION_POLICY**

Reglas mínimas aplicables desde Continue:

- Si el usuario no definió modo, Continue debe pedir: **Plan** o **Build**.
- En **Plan**: no modificar archivos ni ejecutar comandos.
- En **Build**: la autorización es por alcance; no se pide aprobación por cada microacción ordinaria dentro del alcance.
- Aprobaciones siempre requeridas: premium, Replit/entorno externo, secrets, deployment, migraciones, acciones destructivas, cambios en archivos maestros, ampliación de alcance.
- Regla de visibilidad: cuando la existencia de archivos maestros sea relevante, debe prevalecer `verify_master_files` vía MCP sobre la visibilidad parcial del IDE.

