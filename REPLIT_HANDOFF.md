<!-- START: REPLIT_HANDOFF_GO_ZEN_PREMIUM_V0_2 -->

---

## Actualización v0.2 — Handoff desde OpenCode con Go + Zen + Premium

Esta sección actualiza el protocolo de handoff hacia Replit conforme a la arquitectura definida en `AGENT_ORCHESTRATION.md`, `MODEL_ROUTING.md`, `AGENT_RULES.md` y `CONTINUE_USAGE_PROTOCOL.md`.

Replit no debe recibir instrucciones genéricas ni contexto excesivo. Debe recibir un handoff compacto, verificable y seguro, construido a partir del trabajo previo realizado por Continue, OpenCode Go, Zen continuidad, Zen económico o Zen premium.

### 1. Rol de Replit

Replit se usará como capa de validación remota, entorno real y ejecución controlada cuando la tarea requiera:

- validar en runtime Replit;
- revisar preview;
- probar build o servidor remoto;
- usar secrets reales sin exponerlos;
- validar variables de entorno reales;
- ejecutar pruebas de integración;
- revisar deployment;
- diagnosticar errores que solo ocurren en Replit;
- validar configuración específica de Replit.

### 2. Cuándo escalar a Replit

Debe prepararse handoff a Replit cuando exista cualquiera de estos escenarios:

1. La tarea requiere entorno real.
2. La validación local no es suficiente.
3. Se requiere revisar deployment.
4. Se requiere probar runtime remoto.
5. Hay variables de entorno reales involucradas.
6. Hay secrets reales involucrados.
7. Hay integración externa que solo puede probarse en Replit.
8. Hay diferencias entre local y Replit.
9. OpenCode necesita que Replit confirme build, preview o ejecución.
10. El usuario solicita validación en Replit.

### 3. Relación con Go, Zen y Premium

El handoff a Replit debe conservar la trazabilidad del flujo previo.

Si la tarea pasó por Go, Zen o Premium, el handoff debe incluir:

- solicitud original;
- agente utilizado;
- modelo utilizado;
- resultado de primera línea;
- motivo de escalamiento, si existió;
- resultado premium, si existió;
- archivos relevantes;
- cambios realizados;
- comandos sugeridos;
- validaciones pendientes;
- riesgos residuales.

Regla:

    Replit no debe empezar desde cero si ya existe análisis previo.
    El resultado de Go, Zen o Premium debe servir como insumo del handoff.

### 4. Información que debe incluir un handoff

Todo handoff a Replit debe incluir, como mínimo:

- contexto de la tarea;
- objetivo concreto;
- alcance;
- archivos relevantes;
- archivos modificados, si aplica;
- comandos sugeridos;
- validaciones esperadas;
- restricciones;
- riesgos conocidos;
- criterios de éxito;
- acciones prohibidas;
- salida esperada.

Formato recomendado:

    Handoff a Replit:
    1. Contexto:
    2. Objetivo:
    3. Alcance:
    4. Trabajo previo realizado:
    5. Archivos relevantes:
    6. Cambios realizados:
    7. Comandos seguros sugeridos:
    8. Variables/secrets requeridos:
    9. Validaciones pendientes:
    10. Riesgos:
    11. No hacer:
    12. Criterios de éxito:
    13. Resultado esperado:

### 5. Tratamiento de secrets y variables

El handoff puede mencionar nombres de variables de entorno, pero nunca valores.

Permitido:

    DATABASE_URL
    OPENAI_API_KEY
    SESSION_SECRET
    JWT_SECRET
    GITHUB_TOKEN

Prohibido:

    Imprimir valores reales.
    Copiar secrets al handoff.
    Pegar contenido de .env.
    Exponer tokens.
    Recomendar versionar .env.

Regla:

    Replit puede validar que un secret existe, pero no debe imprimir su valor.

### 6. Comandos en handoff

Los comandos sugeridos deben ser seguros, explícitos y no destructivos.

Comandos permitidos como sugerencia, según el contexto:

- `git status`
- `npm run build`
- `npm run dev`
- `npm test`
- `python scripts/check_env.py`
- `python scripts/activate_agent_system.py --auto`
- comandos de lectura o diagnóstico no destructivos.

Comandos que requieren autorización explícita:

- migraciones;
- deployment;
- eliminación de archivos;
- reset de git;
- cambios de ramas;
- push;
- instalación masiva de dependencias;
- modificación de secrets;
- scripts que escriban en base de datos.

### 7. Handoff cuando hubo escalamiento premium

Si el caso fue revisado con modelo premium, el handoff debe incluir:

- motivo del escalamiento premium;
- modelo premium utilizado;
- decisión o recomendación premium;
- riesgos confirmados;
- cambios aprobados;
- puntos que Replit debe validar;
- puntos que Replit no debe modificar.

Regla:

    Replit debe validar la recomendación premium, no reemplazarla sin justificarlo.

### 8. Handoff cuando Go fue suficiente

Si Go fue suficiente y no hubo escalamiento, el handoff debe indicarlo.

Formato:

    Trabajo previo:
    - Agente: [nombre]
    - Modelo: [modelo Go]
    - Resultado: suficiente
    - Motivo: [breve explicación]

Esto permite que Replit se enfoque en validar ejecución, no en repetir análisis.

### 9. Handoff cuando Go no fue suficiente

Si Go no fue suficiente, el handoff debe incluir la razón.

Ejemplos:

- respuesta genérica;
- falta de contexto;
- bug persistente;
- riesgo de seguridad;
- volumen alto;
- solicitud del usuario;
- necesidad de entorno real;
- necesidad de premium;
- validación local insuficiente.

### 10. No hacer en Replit

Todo handoff debe incluir una sección “No hacer” cuando aplique.

Ejemplos:

- no imprimir secrets;
- no modificar `.env`;
- no versionar credenciales;
- no hacer deployment sin autorización;
- no ejecutar migraciones sin autorización;
- no cambiar arquitectura fuera de alcance;
- no reemplazar lógica funcional sin validar;
- no hacer cambios masivos no solicitados;
- no tocar ramas o git remoto sin instrucción explícita.

### 11. Criterios de éxito

Todo handoff debe indicar criterios de éxito.

Ejemplos:

- build exitoso;
- servidor inicia sin errores;
- preview carga correctamente;
- endpoint responde;
- tests pasan;
- variables requeridas presentes;
- no hay secrets expuestos;
- git status limpio o con cambios esperados;
- comportamiento funcional validado.

### 12. Resultado esperado de Replit

La respuesta de Replit debe indicar:

- qué revisó;
- qué comandos ejecutó;
- qué encontró;
- qué cambió, si cambió algo;
- qué validaciones pasaron;
- qué validaciones fallaron;
- riesgos pendientes;
- si requiere acción del usuario;
- si requiere volver a OpenCode.

### 13. External diagnostic returns

Procedimiento mínimo para procesar retornos de diagnóstico (sin volver a consumir Replit):

1) Verificar que el retorno incluya confirmación explícita: "No modifiqué archivos".
2) Verificar comandos ejecutados (solo lectura) y estado Git (rama, remotes, último commit, working tree).
3) Confirmar que el retorno NO contiene: secrets/tokens/credenciales, valores de env, join links u otros links sensibles.
4) Clasificar estado del proyecto: `listo` / `parcialmente_listo` / `no_listo`.
5) Extraer blockers y riesgos (priorizar `critical`, luego `medium`, luego `low`).
6) Decidir escalamiento (según umbral existente): `no_escalate` / `replit_needed` / `premium_needed`.
7) Definir una sola `next_frontier` (p.ej. `pause_pilot`, `local_analysis`, `plan_only`). Semántica: `next_frontier` se emite como cierre/continuidad/bloqueo justificado (no como microfase ni detención prematura).
8) No usar Replit para remediación amplia si el problema puede analizarse localmente (Plan) antes de cualquier ejecución.
9) Registrar el retorno de forma compacta usando el template:
   `templates/returns/external_diagnostic_return.md` (sin copiar chats completos).

<!-- END: REPLIT_HANDOFF_GO_ZEN_PREMIUM_V0_2 -->

# REPLIT_HANDOFF.md

---

## 1. PROPÃ“SITO

Definir cÃ³mo interactuar con Replit como agente hÃ­brido dentro del sistema.

El objetivo es:

- maximizar valor de validaciÃ³n
- minimizar consumo de tokens
- evitar respuestas redundantes
- obtener feedback tÃ©cnico preciso

---

## 2. PRINCIPIO FUNDAMENTAL

Replit NO es un generador principal.

### 2.1 Canal de transferencia de intención hacia el orquestador (vía chat de Replit Agent)

Si el usuario escribe en el chat de Replit Agent: **"resolver con Orquestador"** (o equivalente: "pasar esto al Orquestador", "que lo maneje el Orquestador"), Replit debe comportarse como **canal de transferencia de intención** hacia el orquestador (Continue/MCP), no como ejecutor automático.

Comportamiento esperado:
- No ejecutar cambios funcionales.
- No iniciar dinámica propia de remediación/diagnóstico amplio salvo solicitud explícita.
- Generar un bloque de handoff para Continue/Orquestador.

Advertencia:
- Esta ruta **sí** usa el chat de Replit Agent (puede implicar activación/costo del agente).

Handoff mínimo recomendado (pegable en Continue):
- mode: `orchestrator_transfer`
- channel: `replit_agent_chat`
- instruction: (texto original)
- declaración: "ruta por chat; Replit Agent estuvo activo"
- declaración: "no ejecuté cambios funcionales"
- siguiente acción: abrir Continue y usar `run_general_instruction_flow` / `plan_general_instruction`

### 2.2 Transferencia de intención hacia el orquestador (vía Shell / sin Replit Agent)

Para evitar activar Replit Agent solo para transferir intención, usar la vía Shell.

Si el proyecto tiene aplicado el sistema del orquestador (vía `scripts/apply_to_project.py`), debe existir el wrapper:

- `./orquestador "<instrucción>"`

Ejemplos:
- `./orquestador "Avanza con este proyecto hasta la siguiente frontera segura"`
- `./orquestador "volver a replit"`
- `./orquestador --help`

Esta ruta:
- **No ejecuta Replit Agent**.
- No modifica código funcional.
- Solo genera un handoff compacto (MD+JSON) en `docs/handoffs/` del proyecto.

Handoff mínimo garantizado por Shell bridge:
- mode: `orchestrator_transfer`
- channel: `shell_bridge`
- timestamp
- instruction
- declaración: "No se ejecutó Replit Agent"
- declaración: "No se modificaron archivos funcionales"
- destino: Continue/Orquestador

### 2.3 Volver manualmente a Replit Agent (ambas rutas)

- Desde chat: el usuario debe ser explícito (p.ej. "que lo ejecute Replit Agent" / "usar Replit Agent para validar").
- Desde Shell: `./orquestador "volver a replit"` o `./orquestador --return-to-replit` (genera intent=`return_to_replit`).

Replit es:



- validador de planes
- revisor tÃ©cnico
- verificador de calidad

---

## 3. TIPOS DE INTERACCIÃ“N

---

### 3.1 ValidaciÃ³n de plan

Uso:

- antes de ejecutar cambios
- en tareas complejas
- en decisiones arquitectÃ³nicas

Entrada a Replit:

- contexto filtrado
- plan estructurado

Salida esperada:

- âœ” validaciÃ³n (si es correcto)
- âš  observaciones puntuales (si aplica)

Formato esperado:

- respuestas cortas
- sin reescritura completa
- sin redundancia

---

### 3.2 RevisiÃ³n de implementaciÃ³n

Uso:

- despuÃ©s de ejecutar cambios
- antes de cerrar tarea

Entrada:

- resumen de cambios
- diffs relevantes
- objetivo inicial

Salida esperada:

- validaciÃ³n de coherencia
- detecciÃ³n de problemas
- sugerencias puntuales

---

### 3.3 ValidaciÃ³n arquitectÃ³nica

Uso:

- cambios estructurales
- decisiones de diseÃ±o
- integraciones complejas

Entrada:

- contexto estructurado
- propuesta de arquitectura

Salida esperada:

- evaluaciÃ³n crÃ­tica
- riesgos
- recomendaciones

---

## 4. FORMATO DE HANDOFF

---

### 4.1 Estructura de entrada

Siempre enviar:

- objetivo
- contexto relevante (NO completo)
- plan o cambios realizados

Ejemplo:


Objetivo:
[descripciÃ³n clara]

Contexto relevante:
[solo lo necesario]

Plan / Cambios:
[resumen estructurado]


---

### 4.2 Reglas de contenido

NO enviar:

- historial completo
- documentaciÃ³n innecesaria
- contexto redundante

SÃ enviar:

- informaciÃ³n precisa
- contexto filtrado
- datos estructurados

---

## 5. EXPECTATIVA DE RESPUESTA

---

### 5.1 Respuesta ideal

- breve
- tÃ©cnica
- directa
- sin redundancia

---

### 5.2 Tipos de respuesta

1. ValidaciÃ³n:

âœ” "El enfoque es correcto."

2. ValidaciÃ³n con mejora:

âœ” "El enfoque es correcto, pero considera..."

3. CorrecciÃ³n:

âš  "Hay un problema en..."

---

### 5.3 Respuesta NO deseada

- reescritura completa del cÃ³digo
- explicaciones extensas
- respuestas genÃ©ricas
- duplicaciÃ³n del plan

---

## 6. CRITERIOS PARA USAR REPLIT

---

### 6.1 CUÃNDO usarlo

- tareas complejas
- impacto arquitectÃ³nico
- incertidumbre tÃ©cnica
- validaciÃ³n final

---

### 6.2 CUÃNDO NO usarlo

- tareas simples
- cambios menores
- debugging bÃ¡sico
- generaciÃ³n trivial

---

## 7. OPTIMIZACIÃ“N DE COSTO

---

### 7.1 Minimizar uso

Regla:

1. resolver localmente
2. validar solo si aporta valor

---

### 7.2 Minimizar tokens

El agente local debe:

- resumir
- estructurar
- filtrar

ANTES de enviar

---

## 8. INTEGRACIÃ“N EN EL FLUJO

---

Flujo:

1. Continue genera plan
2. OpenCode valida tÃ©cnicamente
3. (Opcional) Replit valida plan
4. OpenCode ejecuta
5. Replit valida resultado
6. Continue documenta

---

## 9. PRINCIPIO CLAVE

Replit NO agrega valor por volumen de respuesta.

Agrega valor por:

- precisiÃ³n
- criterio
- capacidad de detectar errores

---

## 10. EVOLUCIÃ“N

Este documento debe:

- ajustarse con experiencia real
- optimizar prompts
- reducir consumo de tokens
- mejorar calidad de validaciÃ³n
