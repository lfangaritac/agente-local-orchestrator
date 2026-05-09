<!-- START: MODEL_ROUTING_ESCALATION_SCHEMA_V0_3 -->

---

## Actualización v0.3 — Routing con paquete canónico de escalamiento

Esta sección alinea `MODEL_ROUTING.md` con el schema canónico definido en `AGENT_ORCHESTRATION.md`.

A partir de esta versión, todo escalamiento desde Go hacia Zen continuidad, Zen económico, Zen premium o Replit debe usar el paquete canónico anidado.

**Schema canónico (fuente de verdad):** `AGENT_ORCHESTRATION.md` → `ESCALATION_PACKAGE_CANONICAL_SCHEMA_V0_3`.

Este documento (`MODEL_ROUTING.md`) define **reglas y matrices de routing**; evita duplicar el schema completo para reducir deriva. El formato vigente usa `first_line_output.*`.

### 1. Regla de routing con paquete canónico

El routing no debe enviar directamente una respuesta suelta de Go al modelo escalado.

Debe enviar un paquete estructurado con:

- metadata de orquestación;
- validación de contexto;
- salida normalizada de primera línea;
- motivo de escalamiento;
- pregunta específica para el modelo escalado;
- salida esperada;
- restricciones;
- acciones prohibidas.

### 2. Uso por tipo de escalamiento

#### Go → Zen continuidad

Usar cuando Go se agota.

    escalation_type = zen_continuity
    trigger = go_exhausted

El modelo Zen debe continuar la tarea, no tratarla como revisión premium.

#### Go → Zen económico

Usar cuando Go fue insuficiente, pero la tarea no justifica premium.

    escalation_type = zen_economic
    trigger = low_quality | second_opinion | medium_high_volume

#### Go → Zen premium

Usar cuando exista solicitud del usuario, riesgo, complejidad, volumen alto sensible o revisión crítica.

    escalation_type = zen_premium
    trigger = user_request | architectural_change | security | critical_debugging | high_sensitive_volume | final_sensitive_review

#### Go / Zen → Replit

Usar cuando se requiera entorno real, secrets reales, deployment, runtime o validación remota.

    escalation_type = replit_handoff
    trigger = real_environment_validation | deployment | runtime | secrets_required

### 3. Regla de suficiencia y routing

La decisión de routing debe ocurrir después de `evaluate_sufficiency()`.

Si Go es suficiente:

    return first_line_result

Si Go no es suficiente:

    normalizar salida Go
    construir paquete canónico
    validar paquete
    enviar según routing

### 4. Compatibilidad con campos planos previos

Cuando documentos anteriores hagan referencia a:

- `first_line_summary`
- `first_line_findings`
- `first_line_plan`

deben entenderse como equivalentes internos de:

- `first_line_output.summary`
- `first_line_output.findings`
- `first_line_output.plan`

La estructura oficial será la anidada bajo `first_line_output`.

### 5. Regla de modelos

El modelo escalado debe recibir el paquete completo.

No debe recibir únicamente:

- un resumen informal;
- una pregunta aislada;
- el resultado bruto de Go;
- un diff sin contexto;
- una instrucción sin motivo de escalamiento.

### 6. Regla de selección premium

La existencia de un paquete de escalamiento no implica usar siempre premium.

El routing debe seguir aplicando:

    Go -> Zen continuidad -> Zen económico -> Zen premium -> Replit

Premium se activa únicamente cuando exista activador válido conforme a este documento y a `AGENT_RULES.md`.

<!-- END: MODEL_ROUTING_ESCALATION_SCHEMA_V0_3 -->

# MODEL_ROUTING.md

## Proposito

Definir como se seleccionan agentes y modelos dentro del orquestador local, segun tipo de tarea, riesgo, contexto requerido y necesidad de validacion local o remota.

Este documento es una baseline operativa provisional basada en pruebas reales realizadas con OpenCode, Ollama, Continue y Replit.

## Principio central

El valor del sistema no depende de usar siempre el modelo mas fuerte.

Depende de usar el agente correcto, con el modelo correcto, en la fase correcta, con contexto suficiente, verificacion tecnica y trazabilidad.

<!-- START: ROUTING_GO_ZEN_PREMIUM_V0_2 -->

---

## Actualización v0.2 — Routing Go + Zen + Premium

Esta sección actualiza la baseline operativa del routing de modelos e incorpora la arquitectura definida en `AGENT_ORCHESTRATION.md`.

La ruta estándar será:

    Go -> Zen continuidad -> Zen económico -> Zen premium -> Replit

### 1. Principio actualizado

El sistema no debe usar siempre el modelo más fuerte. Debe usar el modelo suficiente, seguro y costo-eficiente para cada fase.

Regla central:

    Go primero.
    Zen continuidad si Go se agota.
    Zen económico si se requiere contraste o continuidad no premium.
    Zen premium si el usuario lo solicita o si el riesgo, complejidad o volumen lo exige.
    Replit si se requiere entorno real, secrets, deployment o validación remota.

### 2. OpenCode Go como primera línea

OpenCode Go será la primera línea para:

- clasificación de tareas;
- validación de contexto;
- planificación simple o media;
- ejecución controlada de código;
- cambios pequeños;
- debugging moderado;
- revisión normal de diffs;
- documentación técnica no crítica;
- handoffs no críticos.

Modelos Go definidos:

- Builder principal: `opencode-go/kimi-k2.6`
- Small model / tareas rápidas: `opencode-go/deepseek-v4-flash`
- Validador de contexto: `opencode-go/qwen3.6-plus`
- Debugger moderado: `opencode-go/deepseek-v4-pro`
- Auxiliar liviano: `opencode-go/qwen3.5-plus`

### 3. Zen como continuidad de Go

Zen no debe entenderse solo como escalamiento premium.

Cuando Go alcance límites de uso, Zen podrá continuar la tarea como capa pay-as-you-go usando el mismo modelo o un equivalente funcional.

Equivalencias base:

- `opencode-go/kimi-k2.6` -> `opencode/kimi-k2.6`
- `opencode-go/qwen3.6-plus` -> `opencode/qwen3.6-plus`
- `opencode-go/qwen3.5-plus` -> `opencode/qwen3.5-plus`
- `opencode-go/deepseek-v4-flash` -> `opencode/qwen3.5-plus` o `opencode/minimax-m2.7`
- `opencode-go/deepseek-v4-pro` -> `opencode/kimi-k2.6`, `opencode/qwen3.6-plus` o `opencode/glm-5`

Zen continuidad se usa cuando:

- Go alcanza límite de ventana;
- Go alcanza límite semanal;
- Go alcanza límite mensual;
- se necesita terminar una tarea iniciada;
- se requiere continuidad inmediata sin esperar renovación de Go.

### 4. Zen económico

Zen económico se usará cuando:

- Go produjo una respuesta débil;
- se requiere segundo criterio;
- hay volumen medio o alto sin sensibilidad crítica;
- se quiere comparar modelos;
- se requiere un modelo abierto no disponible en Go;
- Go se agotó, pero la tarea no justifica premium.

Modelos sugeridos:

- `opencode/kimi-k2.6`
- `opencode/qwen3.6-plus`
- `opencode/qwen3.5-plus`
- `opencode/glm-5`
- `opencode/glm-5.1`
- `opencode/gemini-3-flash`
- `opencode/minimax-m2.7`

### 5. Zen premium

Zen premium se activa por:

1. Solicitud expresa del usuario.
2. Seguridad, auth, permisos, secrets o datos personales.
3. Debugging complejo o persistente.
4. Cambio arquitectónico.
5. Refactor transversal.
6. Migraciones o persistencia crítica.
7. Deployment, CI/CD, Replit o entorno real.
8. Alto volumen de información con necesidad de juicio técnico.
9. Falla de Go o Zen económico después de intentos razonables.
10. Revisión final sensible antes de merge o handoff.
11. Costo de equivocarse superior al costo de escalar.

Modelos premium sugeridos:

- Planificación arquitectónica: `opencode/claude-opus-4-7`
- Planificación media premium: `opencode/claude-sonnet-4-6`
- Ejecución premium balanceada: `opencode/claude-sonnet-4-6` o `opencode/gpt-5.4`
- Debugging complejo: `opencode/gpt-5.5`
- Seguridad: `opencode/gpt-5.5`
- Diff sensible: `opencode/gpt-5.5`
- Documentación premium: `opencode/claude-sonnet-4-6`

### 6. Solicitud expresa del usuario

Cuando el usuario pida escalar a premium, no se debe forzar el paso previo por Go para esa fase.

Ejemplos:

- Revisión premium de diff normal -> `opencode/gpt-5.4`
- Revisión premium de diff sensible -> `opencode/gpt-5.5`
- Debugging con el modelo más fuerte -> `opencode/gpt-5.5`
- Planificación premium de arquitectura -> `opencode/claude-opus-4-7`
- Revisión premium de seguridad -> `opencode/gpt-5.5`
- Documentación premium -> `opencode/claude-sonnet-4-6`

Regla:

    Solicitud premium no significa siempre usar el modelo más caro.
    Significa usar el modelo premium adecuado para el escenario.

### 7. Routing por volumen

Volumen bajo:

- 1 a 3 archivos pequeños;
- sin documentación extensa;
- sin impacto transversal;
- sin seguridad.

Modelo sugerido: Go.

Volumen medio:

- 4 a 8 archivos;
- código más documentación;
- dependencias moderadas;
- riesgo controlado.

Modelo sugerido: Go fuerte o Zen continuidad.

Volumen alto:

- más de 8 archivos;
- documentación extensa;
- handoffs previos;
- arquitectura más código más reglas;
- necesidad de razonamiento transversal.

Modelos sugeridos:

- `opencode/gemini-3-flash`
- `opencode/qwen3.6-plus`
- `opencode/claude-sonnet-4-6`
- `opencode/gpt-5.4`

Volumen alto sensible:

- mucho contexto;
- seguridad;
- auth;
- DB;
- datos personales;
- deployment;
- producción.

Modelos sugeridos:

- `opencode/gpt-5.5`
- `opencode/claude-opus-4-7`

### 8. Routing resumido por escenario

| Escenario | Go default | Zen continuidad | Premium |
|---|---|---|---|
| Clasificación | `opencode-go/deepseek-v4-flash` | `opencode/qwen3.5-plus` | `opencode/gpt-5.4` |
| Validación de contexto | `opencode-go/qwen3.6-plus` | `opencode/qwen3.6-plus` / `opencode/gemini-3-flash` | `opencode/claude-sonnet-4-6` / `opencode/gpt-5.4` |
| Plan simple/media | `opencode-go/kimi-k2.6` | `opencode/kimi-k2.6` | `opencode/claude-sonnet-4-6` |
| Plan arquitectónico | `opencode-go/kimi-k2.6` preliminar | `opencode/kimi-k2.6` / `opencode/glm-5` | `opencode/claude-opus-4-7` / `opencode/gpt-5.5` |
| Código controlado | `opencode-go/kimi-k2.6` | `opencode/kimi-k2.6` | `opencode/claude-sonnet-4-6` / `opencode/gpt-5.4` |
| Cambios pequeños | `opencode-go/deepseek-v4-flash` | `opencode/qwen3.5-plus` | `opencode/gpt-5.4` solo si se pide |
| Debugging moderado | `opencode-go/deepseek-v4-pro` | `opencode/kimi-k2.6` / `opencode/qwen3.6-plus` | `opencode/gpt-5.4` / `opencode/gpt-5.5` |
| Debugging crítico | `opencode-go/deepseek-v4-pro` preliminar | `opencode/kimi-k2.6` | `opencode/gpt-5.5` / `opencode/claude-opus-4-7` |
| Diff normal | `opencode-go/qwen3.6-plus` | `opencode/qwen3.6-plus` | `opencode/gpt-5.4` / `opencode/gpt-5.5` si sensible |
| Seguridad | `opencode-go/qwen3.6-plus` pre-review | `opencode/qwen3.6-plus` pre-review | `opencode/gpt-5.5` / `opencode/claude-opus-4-7` |
| Handoff Replit | `opencode-go/qwen3.6-plus` | `opencode/qwen3.6-plus` | `opencode/gpt-5.4` / `opencode/gpt-5.5` |
| Documentación | `opencode-go/qwen3.6-plus` | `opencode/qwen3.6-plus` / `opencode/gemini-3-flash` | `opencode/claude-sonnet-4-6` |

### 9. Escalamiento con transferencia de insumos

Cuando un modelo de primera línea escala a Zen o premium, su resultado no debe descartarse.

Debe convertirse en insumo estructurado para el siguiente modelo.

Paquete **canónico** de escalamiento (schema):

- Fuente de verdad: `AGENT_ORCHESTRATION.md` → `ESCALATION_PACKAGE_CANONICAL_SCHEMA_V0_3`.
- Formato vigente: **anidado** con `first_line_output.*` (no plano).

Campos mínimos (resumen; no schema completo):
- `escalation_type`, `trigger`, `original_user_request`, `scenario`, `risk_level`, `information_volume`
- `first_line_agent`, `first_line_model`
- `first_line_output`: `summary`, `findings`, `plan`, `files_reviewed`, `files_modified`, `commands_suggested`, `commands_executed`, `risks_detected`, `open_questions`, `confidence`
- `reason_for_escalation`, `specific_question_for_escalated_model`, `expected_output`, `constraints`, `do_not_do`

Compatibilidad legacy (no preferido):
- `first_line_summary` → `first_line_output.summary`
- `first_line_findings` → `first_line_output.findings`
- `first_line_plan` → `first_line_output.plan`

Regla:

    El modelo escalado debe validar, corregir, completar o profundizar el resultado previo.
    No debe reiniciar la tarea desde cero sin aprovechar el insumo de primera línea.

### 10. Criterios de suficiencia de Go

Go es suficiente si:

- entiende correctamente la tarea;
- respeta restricciones;
- identifica archivos relevantes;
- no inventa contexto;
- no solicita secrets;
- propone plan acotado;
- toca pocos archivos;
- justifica cambios;
- identifica riesgos razonables;
- produce salida accionable;
- no hay seguridad ni criticidad.

Go no es suficiente si:

- responde genérico;
- contradice reglas;
- omite riesgos evidentes;
- propone cambios masivos innecesarios;
- no entiende arquitectura;
- falla dos veces en bug;
- no explica el diff;
- no identifica archivos clave;
- hay seguridad, auth, datos o deployment;
- el usuario pidió premium.

Ver detalle completo de agentes, estados, paquetes y mini-orquestador en `AGENT_ORCHESTRATION.md`.

<!-- END: ROUTING_GO_ZEN_PREMIUM_V0_2 -->
## Roles de agentes

### Continue

Continue opera como copiloto IDE e integrador de contexto.

Responsabilidades principales:

- asistir al usuario dentro de VS Code;
- revisar documentacion y codigo relevante;
- consolidar ventana de contexto;
- preparar o revisar handoffs;
- explicar diffs y decisiones;
- apoyar revisiones ligeras;
- no actuar como unico ejecutor de cambios complejos.

Continue puede incluir codigo en su contexto, pero no se debe asumir cobertura total automatica del repositorio.

Regla: Continue debe declarar que fuentes o archivos reviso cuando consolide contexto para una tarea relevante.

### OpenCode

OpenCode opera como agente local especializado de codificacion.

Responsabilidades principales:

- leer archivos reales del repositorio;
- diagnosticar problemas tecnicos;
- proponer planes de cambio;
- ejecutar cambios locales solo con autorizacion;
- revisar git diff y git status;
- ejecutar verificaciones definidas en DEVELOPMENT_CHECKS.md;
- generar reporte tecnico o handoff cuando aplique.

OpenCode no necesita operar dentro de VS Code. Debe operar sobre el repositorio y dejar evidencia verificable.

### Replit Agent

Replit Agent opera como agente remoto de validacion, preview, runtime y entorno Replit.

Responsabilidades principales:

- validar ejecucion en Replit;
- revisar preview;
- diagnosticar errores de runtime remoto;
- validar build, deployment o configuracion Replit;
- revisar cambios sincronizados por GitHub cuando el entorno Replit aporte valor.

Replit Agent no debe usarse para tareas triviales si la validacion local es suficiente.

### ChatGPT / supervisor metodologico

ChatGPT acompana la configuracion, clasifica decisiones, mantiene foco operativo y ayuda a consolidar documentacion maestra.

No sustituye los artefactos del repo ni la evidencia de Git, pruebas o logs.

## Modelos disponibles y resultado de pruebas

### OpenCode hosted

Modelos probados:

- opencode/minimax-m2.5-free;
- opencode/nemotron-3-super-free;
- opencode/hy3-preview-free;
- opencode/big-pickle;
- opencode/gpt-5-nano.

Resultado provisional:

1. opencode/minimax-m2.5-free
   - Mejor balance observado para diagnostico corto.
   - Preciso, concreto y alineado con la logica del orquestador.

2. opencode/nemotron-3-super-free
   - Buen entendimiento operativo.
   - Util para proponer wrappers, logs, validaciones externas y riesgos.

3. opencode/hy3-preview-free
   - Prudente, seguro y conservador.
   - Util para revision de bajo riesgo y mejoras documentales.

4. opencode/big-pickle
   - Buena lectura real de archivos.
   - Puede proponer soluciones sobredimensionadas.
   - Usar como fallback o contraste enfocado.

5. opencode/gpt-5-nano
   - Rapido y estructurado.
   - En prueba invento capacidades actuales de check_env.py.
   - Usar para tareas rapidas no criticas, no como diagnostico preciso principal.

### Ollama local

Modelos instalados:

- qwen2.5-coder:7b;
- deepseek-coder:6.7b;
- mistral:7b.

Resultado provisional:

1. qwen2.5-coder:7b
   - Mejor candidato local para codificacion.
   - Fuera de OpenCode fue correcto pero superficial.
   - Dentro de OpenCode intento emitir accion de edicion pese a instruccion de no modificar.
   - No usar todavia como modelo principal de diagnostico sin cambios.

2. deepseek-coder:6.7b
   - Respaldo local de codigo.
   - En prueba inicial fue poco util y pidio mas informacion.

3. mistral:7b
   - Modelo general local.
   - Usar para redaccion, explicacion, resumen o apoyo conceptual.
   - No es coder principal.

## Routing por tipo de tarea

| Tipo de tarea | Agente principal | Modelo recomendado | Observaciones |
|---|---|---|---|
| Diagnostico sin cambios | OpenCode | opencode/minimax-m2.5-free | Debe leer archivos reales y no modificar. |
| Diagnostico alterno | OpenCode | opencode/nemotron-3-super-free | Usar para segunda opinion tecnica. |
| Revision prudente | OpenCode | opencode/hy3-preview-free | Bueno para tareas conservadoras. |
| Contexto IDE | Continue | qwen2.5-coder:7b via Ollama, si esta configurado | Continue integra contexto, no ejecuta cambios grandes. |
| Redaccion tecnica local | Continue/Ollama | mistral:7b | Para documentacion y explicacion. |
| Codificacion local autorizada | OpenCode | candidato: ollama/qwen2.5-coder:7b | Solo con autorizacion explicita y DEVELOPMENT_CHECKS.md. |
| Fallback OpenCode | OpenCode | opencode/big-pickle | Para contraste o tareas enfocadas. |
| Validacion remota | Replit Agent | modelo Replit disponible | Preview, runtime, build, deployment. |
| Alta criticidad | Replit Agent + premium | segun caso | Seguridad, schema, deployment, arquitectura. |

## Mini-orquestacion de contexto

Para tareas medianas o complejas, el contexto no debe depender de un solo agente.

Flujo recomendado:

1. Usuario formula tarea.
2. Se clasifica alcance y riesgo.
3. OpenCode genera lectura tecnica del repo.
4. Continue integra la ventana final de contexto.
5. Se decide agente principal.
6. Se prepara handoff si aplica.

OpenCode debe aportar:

- archivos relevantes;
- funciones, rutas o componentes relacionados;
- dependencias;
- comandos de verificacion disponibles;
- riesgos tecnicos;
- archivos sensibles o que no deben tocarse;
- dudas o vacios de contexto.

Continue debe consolidar:

- objetivo de la tarea;
- alcance autorizado;
- archivos revisados;
- contexto documental relevante;
- riesgos;
- comandos de verificacion;
- agente recomendado;
- si debe intervenir Replit Agent;
- si se requiere aprobacion humana.

No siempre se requiere mini-orquestacion de contexto. Activarla cuando exista:

- cambio multiarchivo;
- backend/frontend conectados;
- integracion local/Replit;
- ambiguedad funcional;
- riesgo de secrets;
- migraciones;
- deployment;
- errores de runtime;
- necesidad de handoff a Replit.

## Doble planificacion

Para tareas de riesgo medio o alto, OpenCode puede generar dos planes alternativos antes de ejecutar.

Modelos sugeridos:

- Plan A: opencode/minimax-m2.5-free;
- Plan B: opencode/nemotron-3-super-free;
- Contraste opcional: opencode/hy3-preview-free.

Continue debe revisar los planes y producir un curso de accion unificado.

El plan unificado debe incluir:

- puntos coincidentes;
- divergencias;
- riesgos;
- archivos a modificar;
- archivos a no tocar;
- comandos de verificacion;
- necesidad de Replit;
- necesidad de autorizacion humana.

Regla: no se ejecutan cambios hasta que el usuario autorice el plan.

## Tareas de codificacion

Toda tarea de codificacion queda gobernada por DEVELOPMENT_CHECKS.md.

Reglas obligatorias:

- OpenCode solo modifica archivos con autorizacion explicita;
- debe ejecutar verificaciones disponibles;
- debe revisar git diff;
- debe revisar git status;
- debe reportar comandos ejecutados y resultados;
- no debe declarar exito sin evidencia;
- si no hay pruebas, debe reportarlo;
- si requiere preview o runtime remoto, debe preparar handoff a Replit.

## Escalamiento

Escalar a Replit Agent, modelo premium o revision humana cuando exista:

- baja confianza en el modelo local;
- cambios de schema o migraciones;
- deployment;
- manejo de secrets;
- errores persistentes;
- impacto multiarchivo alto;
- seguridad;
- arquitectura;
- conflicto entre recomendaciones de agentes;
- necesidad de preview o runtime en Replit.

## Restricciones

El sistema no debe:

- enviar la misma tarea a varios modelos sin proposito;
- generar analisis redundante;
- usar Replit para tareas triviales;
- usar premium sin justificacion;
- cargar contexto innecesario;
- modificar archivos sin autorizacion;
- ejecutar migraciones sin autorizacion;
- imprimir secrets;
- versionar archivos .env.

## Principio final

Contexto primero, agente correcto despues, ejecucion controlada al final.

La arquitectura debe favorecer contexto depurado, plan verificable, cambios trazables, pruebas documentadas y sincronizacion por GitHub.


