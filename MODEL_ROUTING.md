# MODEL_ROUTING.md

## Proposito

Definir como se seleccionan agentes y modelos dentro del orquestador local, segun tipo de tarea, riesgo, contexto requerido y necesidad de validacion local o remota.

Este documento es una baseline operativa provisional basada en pruebas reales realizadas con OpenCode, Ollama, Continue y Replit.

## Principio central

El valor del sistema no depende de usar siempre el modelo mas fuerte.

Depende de usar el agente correcto, con el modelo correcto, en la fase correcta, con contexto suficiente, verificacion tecnica y trazabilidad.

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
