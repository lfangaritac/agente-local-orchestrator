<!-- START: AGENT_RULES_CONTEXT_GOVERNANCE_V0_4 -->

---

## Actualización v0.4 — Gobierno de contexto multi-proyecto y mini-orquestación bidireccional

Esta sección incorpora reglas operativas obligatorias para que OpenCode, Continue y demás agentes trabajen bajo el contrato de contexto multi-proyecto.

### 1. Consulta obligatoria de contrato, alertas y lecciones

Antes de tareas de complejidad media, alta o crítica, los agentes deben consultar:

- `TARGET_PROJECT_CONTEXT_CONTRACT.md`
- `PROJECT_REGISTRY.md`
- `docs/protocols/PROJECT_ENABLEMENT_PROTOCOL.md`
- `docs/protocols/CONTEXT_SYNC_PROTOCOL.md`
- `docs/protocols/DOCUMENTATION_CODE_ALIGNMENT_PROTOCOL.md`
- `docs/alerts/GLOBAL_CRITICAL_ALERTS.md`
- `docs/lessons/GLOBAL_LESSONS_LEARNED.md`

Si la tarea se refiere a un proyecto objetivo, también deben consultar o solicitar:

- perfil del proyecto objetivo;
- índice de contexto;
- mapa de código;
- auditoría documentación-código;
- alertas locales;
- lecciones locales;
- estado de sincronización.

### 2. Identificación del proyecto objetivo

Ningún agente debe actuar sobre un proyecto objetivo sin identificarlo o declarar que no está confirmado.

Si el proyecto objetivo no está confirmado, el agente debe operar en modo diagnóstico.

No debe inventarse el nombre del proyecto objetivo.

### 3. Indagación contextual

El orquestador y los agentes deben indagar:

- documentación explícita;
- contexto embebido;
- código relevante;
- comentarios;
- estructura;
- scripts;
- configuración;
- tests;
- rutas;
- endpoints;
- modelos;
- dependencias;
- decisiones;
- alertas;
- lecciones.

### 4. Continue con nivel 3 contextual

Continue puede acceder a nivel 3 al código cuando sea necesario para construir contexto preciso, contrastar documentación o preparar handoffs.

Continue no debe actuar como ejecutor principal ni reemplazar a OpenCode en validación técnica, ejecución, debugging o revisión de diffs.

### 5. OpenCode con nivel 3 operativo

OpenCode debe usar nivel 3 cuando sea necesario para validar técnicamente, planificar, ejecutar, depurar, revisar diffs, probar o preparar escalamiento.

OpenCode no debe asumir que el handoff de Continue es suficiente sin validación.

### 6. Mini-orquestación bidireccional

Para complejidad media o superior, los agentes deben permitir retroalimentación bidireccional:

`Continue contextualiza → OpenCode valida → Continue refina → OpenCode actúa`

No debe existir conversación indefinida entre agentes.

Si después de los ciclos permitidos persisten contradicciones o insuficiencia contextual, debe pedirse decisión humana o escalar según routing.

### 7. Prevención de colusión y condescendencia

Los agentes deben evitar:

- condescendencia;
- colusión;
- validación acrítica de otro agente;
- confirmación automática de premisas del usuario;
- suavización de alertas críticas;
- omisión de incertidumbre;
- invención de contexto.

Deben promover contradicción técnica fundada, verificación cruzada, trazabilidad y roles diferenciados.

### 8. Bloqueo por contexto incompleto

Si el contexto necesario está incompleto, el agente debe operar en modo diagnóstico y no en modo ejecución.

Debe bloquear ejecución si:

- no identifica proyecto objetivo;
- falta contexto obligatorio;
- faltan alertas críticas;
- hay contradicción documentación-código no resuelta;
- se requiere código y no se revisó código;
- se requiere premium y no existe paquete canónico;
- hay riesgo de secrets.

### 9. Alertas y lecciones

Si una tarea revela una alerta crítica o lección transversal, el agente debe proponer actualización de:

- `docs/alerts/GLOBAL_CRITICAL_ALERTS.md`
- `docs/lessons/GLOBAL_LESSONS_LEARNED.md`

No debe actualizar automáticamente reglas globales sin autorización cuando el cambio tenga impacto transversal significativo.

### 10. Automatización futura

El objetivo final es que el usuario permanezca en un solo punto de interacción.

El sistema debe tender a automatizar:

- identificación del proyecto objetivo;
- consulta de registro;
- consulta de alertas;
- consulta de lecciones;
- selección de agente;
- selección de modelo;
- transferencia de handoffs;
- validación de suficiencia;
- generación de paquetes de escalamiento;
- documentación de resultados.

Hasta que esa automatización exista, los agentes deben dejar claro qué paso manual sustituye una transferencia automática pendiente.

<!-- END: AGENT_RULES_CONTEXT_GOVERNANCE_V0_4 -->

<!-- START: AGENT_RULES_ESCALATION_SCHEMA_V0_3 -->

---

## Actualización v0.3 — Reglas obligatorias del paquete canónico de escalamiento

Esta sección convierte el paquete canónico de escalamiento en una regla operativa obligatoria para todos los agentes.

### 1. Regla canónica

Todo escalamiento desde Go hacia Zen continuidad, Zen económico, Zen premium o Replit debe usar el paquete canónico definido en `AGENT_ORCHESTRATION.md`.

No se permite escalar únicamente con:

- una respuesta suelta;
- una conclusión informal;
- una pregunta aislada;
- un diff sin contexto;
- una instrucción sin motivo de escalamiento.

### 2. Regla de normalización

Antes de escalar, el mini-orquestador debe normalizar la salida de Go dentro de:

    first_line_output

Ese objeto debe contener:

- summary;
- findings;
- plan;
- files_reviewed;
- files_modified;
- commands_suggested;
- commands_executed;
- risks_detected;
- open_questions;
- confidence.

### 3. Regla de extracción automática

La extracción debe ser automática siempre que exista resultado de Go.

Si un campo no puede extraerse, debe quedar como `unknown` o lista vacía.

No se debe inventar información para completar campos faltantes.

### 4. Regla de validación previa

Antes de escalar, el paquete debe validarse.

La validación debe revisar:

- campos mínimos obligatorios;
- ausencia de secrets;
- motivo de escalamiento;
- pregunta específica para el modelo escalado;
- salida esperada;
- restricciones;
- acciones prohibidas.

Si la validación falla, debe pedirse revisión humana antes de continuar.

### 5. Regla de no reinicio

Todo modelo escalado debe recibir esta instrucción:

    No empieces desde cero. Usa el paquete de escalamiento como insumo principal. Valida, corrige, completa o profundiza el resultado previo.

### 6. Regla de seguridad

El paquete de escalamiento nunca debe contener:

- `.env`;
- `.env.*`;
- secrets;
- tokens;
- credenciales;
- llaves privadas;
- dumps de base de datos;
- datos personales reales;
- logs con PII;
- valores reales de variables de entorno.

### 7. Regla de trazabilidad

El paquete debe permitir reconstruir:

- qué pidió el usuario;
- qué agente actuó primero;
- qué modelo se usó;
- qué archivos se revisaron;
- qué se encontró;
- por qué se escaló;
- qué se espera del modelo escalado.

<!-- END: AGENT_RULES_ESCALATION_SCHEMA_V0_3 -->

<!-- START: AGENT_RULES_GO_ZEN_PREMIUM_V0_2 -->

---

## Actualización v0.2 — Reglas operativas Go + Zen + Premium

Esta sección incorpora reglas obligatorias para la arquitectura definida en `AGENT_ORCHESTRATION.md` y `MODEL_ROUTING.md`.

La ruta estándar será:

    Go -> Zen continuidad -> Zen económico -> Zen premium -> Replit

### 1. Primera línea: OpenCode Go

OpenCode Go será la primera línea operativa para tareas ordinarias de desarrollo.

Debe usarse por defecto para:

- clasificación de tareas;
- validación de contexto;
- planificación simple o media;
- ejecución controlada de código;
- cambios pequeños;
- debugging moderado;
- revisión normal de diffs;
- documentación técnica no crítica;
- handoffs no críticos.

Regla:

    No usar modelos premium como default.
    Usar Go salvo que exista activador claro de continuidad, escalamiento o solicitud directa del usuario.

### 2. Continuidad con Zen

Zen no debe entenderse solo como escalamiento premium.

Cuando Go alcance límites de uso, Zen podrá continuar la misma tarea como capa pay-as-you-go.

Regla:

    Si Go se agota, no escalar automáticamente a premium.
    Primero usar Zen con el mismo modelo o con un equivalente funcional.

Equivalencias base:

- `opencode-go/kimi-k2.6` -> `opencode/kimi-k2.6`
- `opencode-go/qwen3.6-plus` -> `opencode/qwen3.6-plus`
- `opencode-go/qwen3.5-plus` -> `opencode/qwen3.5-plus`
- `opencode-go/deepseek-v4-flash` -> `opencode/qwen3.5-plus` o `opencode/minimax-m2.7`
- `opencode-go/deepseek-v4-pro` -> `opencode/kimi-k2.6`, `opencode/qwen3.6-plus` o `opencode/glm-5`

### 3. Escalamiento premium

Zen premium se usará únicamente cuando exista un activador válido.

Activadores válidos:

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

Regla:

    Escalamiento premium no significa usar siempre el modelo más caro.
    Debe usarse el modelo premium adecuado para el escenario.

### 4. Solicitud directa del usuario

Cuando el usuario solicite explícitamente usar premium, el sistema no debe forzar el paso previo por Go para esa fase.

Ejemplos:

- “Usa premium para revisar este diff.”
- “Usa el modelo más fuerte para este bug.”
- “Haz planificación premium de arquitectura.”
- “Revisión premium de seguridad.”
- “Documenta esto con premium.”

Regla:

    La solicitud del usuario activa premium para la fase correspondiente.
    El modelo se selecciona según escenario, riesgo y volumen.

### 5. Transferencia de insumos al escalar

Cuando una tarea escala desde Go hacia Zen o premium, el resultado del modelo de primera línea no debe descartarse.

Debe convertirse en insumo estructurado para el modelo siguiente.

El paquete mínimo de escalamiento debe incluir:

- solicitud original del usuario;
- escenario;
- nivel de riesgo;
- volumen de información;
- agente de primera línea;
- modelo de primera línea;
- resumen del resultado inicial;
- hallazgos;
- plan preliminar, si existe;
- archivos revisados;
- archivos modificados, si aplica;
- comandos sugeridos;
- riesgos detectados;
- preguntas abiertas;
- confianza estimada;
- motivo del escalamiento;
- pregunta específica para el modelo escalado;
- salida esperada;
- restricciones;
- acciones prohibidas.

Regla:

    El modelo escalado debe validar, corregir, completar o profundizar el resultado previo.
    No debe reiniciar la tarea desde cero sin aprovechar el insumo de primera línea.

### 6. Seguridad

Ningún agente debe solicitar, imprimir, copiar, versionar o exponer:

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

Regla:

    Los modelos externos solo pueden recibir código fuente sin secrets, documentación técnica no sensible, logs depurados, errores anonimizados, diffs revisables y handoffs sin credenciales.

### 7. Permisos

La regla por defecto para OpenCode será:

    edit: ask
    bash: ask

Los agentes de planificación, clasificación, validación, revisión y seguridad deben operar sin escritura por defecto.

Los agentes de ejecución pueden escribir o ejecutar comandos únicamente con aprobación humana.

Regla:

    Ningún agente debe ejecutar comandos destructivos, migraciones, deployment, eliminación de archivos, cambios masivos o modificaciones de entorno sin autorización explícita.

### 8. Replit

Replit se usará cuando la tarea requiera:

- entorno real;
- secrets reales;
- deployment;
- runtime remoto;
- preview;
- pruebas de integración;
- variables de entorno reales;
- validación de build o configuración Replit.

Antes de escalar a Replit, OpenCode debe preparar un handoff claro, compacto y verificable.

### 9. Documentación

No se debe documentar todo automáticamente.

Debe documentarse cuando exista:

- decisión técnica relevante;
- cambio de routing;
- cambio de modelo default;
- error corregido importante;
- aprendizaje de prueba;
- riesgo de seguridad;
- handoff a Replit;
- descarte de alternativa técnica;
- cambio de arquitectura;
- cambio de protocolo operativo.

Documentos relacionados:

- `MODEL_ROUTING.md`
- `AGENT_ORCHESTRATION.md`
- `AGENT_RULES.md`
- `PROJECT_CONTEXT.md`
- `CONTINUE_USAGE_PROTOCOL.md`
- `REPLIT_HANDOFF.md`
- `docs/test_reports/*`
- `docs/agent_handoffs/*`
- `docs/decisions/*`

<!-- END: AGENT_RULES_GO_ZEN_PREMIUM_V0_2 -->

# AGENT_RULES.md  
## Protocolo operativo del sistema hÃ­brido de agentes (Local + Replit + Premium)

---

## 1. PROPÃ“SITO DEL SISTEMA

Este sistema tiene como objetivo:

- Orquestar el desarrollo asistido por IA de forma controlada y trazable
- Maximizar el uso de capacidades locales
- Minimizar consumo de tokens externos
- Mantener memoria persistente del proyecto
- Integrar de forma eficiente:
  - Agente local de orquestaciÃ³n
  - Continue (copiloto)
  - OpenCode (ejecuciÃ³n tÃ©cnica)
  - Replit (agente hÃ­brido)
  - Modelos premium (criterio experto)

---

## 2. ROLES DEL SISTEMA

### 2.1 Agente de OrquestaciÃ³n Local

Es el nÃºcleo del sistema.

Responsabilidades:

- recorrer el contexto total del proyecto
- filtrar y construir contexto relevante
- generar planes
- coordinar interacciÃ³n entre agentes
- mantener documentaciÃ³n viva
- decidir cuÃ¡ndo escalar

---

### 2.2 Continue (Copiloto)

Responsable de:

- interacciÃ³n con el usuario
- interpretaciÃ³n de solicitudes
- generaciÃ³n de planes iniciales
- sÃ­ntesis de informaciÃ³n
- construcciÃ³n de respuesta unificada

---

### 2.3 OpenCode (Agente TÃ©cnico)

Responsable de:

- anÃ¡lisis tÃ©cnico del repositorio
- validaciÃ³n de planes contra cÃ³digo real
- ejecuciÃ³n de cambios
- generaciÃ³n de archivos
- ejecuciÃ³n de comandos

---

### 2.4 Replit (Agente HÃ­brido)

Cumple doble funciÃ³n:

#### a. ValidaciÃ³n continua

- valida planes
- confirma enfoque
- aporta mejoras si hay valor
- evita redundancia

#### b. EjecuciÃ³n avanzada

- debugging complejo
- pruebas en entorno real
- despliegue
- validaciÃ³n de arquitectura

---

### 2.5 Modelos Premium

Se usan para:

- razonamiento complejo
- arquitectura crÃ­tica
- decisiones de alto impacto
- validaciÃ³n cuando hay incertidumbre

---

## 3. PRINCIPIO DE CONTEXTO

El agente local mantiene acceso total al contexto del proyecto:

- cÃ³digo
- documentaciÃ³n
- decisiones
- errores
- pruebas
- diffs
- logs
- configuraciones

---

### 3.1 Regla clave

NO se envÃ­a todo el contexto.

Siempre:

1. recorrer contexto completo
2. identificar relevancia
3. filtrar ruido
4. estructurar informaciÃ³n
5. construir ventana depurada

---

## 4. PROTOCOLO DE CONCERTACIÃ“N INTER-AGENTE

Para tareas medianas o complejas:

### 4.1 Paso 1 â€“ Plan inicial

Continue genera:

- interpretaciÃ³n de la solicitud
- plan propuesto

---

### 4.2 Paso 2 â€“ ValidaciÃ³n tÃ©cnica

OpenCode en modo anÃ¡lisis:

- revisa plan contra cÃ³digo real
- identifica riesgos
- propone ajustes

---

### 4.3 Paso 3 â€“ SÃ­ntesis

Continue:

- integra plan + validaciÃ³n tÃ©cnica
- construye plan unificado

---

### 4.4 Regla clave

Debe existir una sola versiÃ³n final del plan.

No se permite ejecuciÃ³n sin sÃ­ntesis.

---

## 5. CICLO OPERATIVO ESTÃNDAR

### 5.1 Fase 1 â€“ Solicitud

Usuario define requerimiento

---

### 5.2 Fase 2 â€“ ConstrucciÃ³n de contexto

Agente local:

- recorre documentaciÃ³n
- selecciona informaciÃ³n relevante

---

### 5.3 Fase 3 â€“ PlanificaciÃ³n

- Continue propone plan
- OpenCode valida
- Continue sintetiza

---

### 5.4 Fase 4 â€“ ValidaciÃ³n con Replit (modo plan)

Replit:

- confirma enfoque
- aporta solo si agrega valor

---

### 5.5 Fase 5 â€“ EjecuciÃ³n

OpenCode:

- aplica cambios
- genera cÃ³digo
- ejecuta tareas

---

### 5.6 Fase 6 â€“ ValidaciÃ³n local

- pruebas
- revisiÃ³n tÃ©cnica
- anÃ¡lisis de resultados

---

### 5.7 Fase 7 â€“ DocumentaciÃ³n

Actualizar:

- PROJECT_CONTEXT.md
- decisiones
- errores
- resultados

---

### 5.8 Fase 8 â€“ ValidaciÃ³n con Replit (post-ejecuciÃ³n)

Replit:

- valida conformidad
- identifica mejoras

---

### 5.9 Fase 9 â€“ IteraciÃ³n

Si hay observaciones:

â†’ se reinicia el ciclo

---

## 6. ESCALAMIENTO A PREMIUM

Se activa cuando:

- capacidades locales son insuficientes
- Replit no resuelve el problema
- alta criticidad
- solicitud del usuario

---

### 6.1 Regla

El escalamiento debe ser:

- consciente
- justificado
- documentado

---

## 7. DOCUMENTACIÃ“N VIVA

Debe registrarse **lo relevante** (no “todo”):

- solicitudes (cuando cambian objetivo/alcance)
- planes (cuando habilitan ejecución o cambian ruta)
- validaciones (checks ejecutados o pendientes)
- errores (si afectan decisiones futuras)
- pruebas (resultado y evidencia mínima)
- diffs (referencia + resumen, no volcado completo)
- decisiones (incluye escalamiento/no-escalamiento y umbrales)
- feedback de Replit u otros agentes externos (retorno estructurado, sin secrets)
- ajustes (cuando cambian riesgo/alcance/arquitectura)
- aprendizajes (solo si son reutilizables)

Regla: preservar trazabilidad **sin documentar ruido operativo**. Preferir referencias compactas (IDs/rutas/run_id) sobre volcado de artefactos completos (ver `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md`).


---

### 7.1 Objetivo

Construir memoria progresiva que:

- mejore decisiones futuras
- reduzca errores
- optimice contexto

---

## 8. CONTROL DE CAMBIOS

Antes de ejecutar:

- identificar impacto
- definir alcance

DespuÃ©s:

- validar resultado
- documentar cambios
- preparar commit

---

## 9. GIT (OBLIGATORIO)

Todo cambio debe:

- ser versionado
- tener mensaje claro
- ser reversible

---

## 10. SEGURIDAD

El sistema NO debe:

- exponer credenciales
- ejecutar comandos riesgosos sin control
- acceder fuera del proyecto sin autorizaciÃ³n

---

## 11. PRINCIPIOS OPERATIVOS CLAVE

El sistema prioriza:

- coherencia sobre velocidad
- trazabilidad sobre automatizaciÃ³n
- calidad sobre rapidez
- control sobre delegaciÃ³n

---

## 12. CRITERIO DE FINALIZACIÃ“N

Una tarea se considera completa cuando:

- cumple requerimiento funcional
- pasa validaciones
- estÃ¡ documentada
- estÃ¡ versionada
- ha sido validada por Replit si aplica

---

## 13. EVOLUCIÃ“N

Este documento:

- debe evolucionar
- debe adaptarse al proyecto
- debe enriquecerse con la experiencia

Pero nunca debe comprometer:

- seguridad
- trazabilidad
- control del sistema



