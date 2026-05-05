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

Debe registrarse TODO:

- solicitudes
- planes
- validaciones
- errores
- pruebas
- diffs
- decisiones
- feedback de Replit
- ajustes
- aprendizajes

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

