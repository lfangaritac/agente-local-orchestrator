<!-- START: ESCALATION_PACKAGE_CANONICAL_SCHEMA_V0_3 -->

---

## Actualización v0.3 — Schema canónico y generación automática del paquete de escalamiento

Esta sección resuelve los hallazgos de la prueba controlada `classifier → context-validator → planner → escalamiento simulado a Zen premium`.

La prueba confirmó que la arquitectura es funcional, pero requiere tres precisiones antes de implementación real:

1. Definir un schema canónico único del paquete de escalamiento.
2. Documentar el mecanismo de extracción automática desde salidas Go.
3. Precisar el punto exacto de inserción dentro del mini-orquestador.

### 1. Decisión canónica

Se adopta como canónico el schema anidado del paquete de escalamiento.

Razones:

- Separa la metadata de orquestación de la salida del modelo de primera línea.
- Evita contaminar el objeto raíz con campos operativos.
- Conserva trazabilidad completa del resultado de Go.
- Facilita que Zen premium valide, corrija, complete o profundice sin reiniciar desde cero.
- Permite agregar metadatos futuros sin romper la estructura principal.

A partir de esta versión, `first_line_output` será el contenedor oficial de la salida normalizada del modelo de primera línea.

### 2. Schema canónico

Formato oficial:

    {
      "escalation_type": "zen_continuity | zen_economic | zen_premium | replit_handoff",
      "trigger": "",
      "original_user_request": "",
      "scenario": "",
      "risk_level": "low | medium | medium-high | high | critical",
      "information_volume": "low | medium | high | high_sensitive",
      "first_line_agent": "",
      "first_line_model": "",
      "context_validation": {
        "files_reviewed": [],
        "rules_applied": [],
        "constraints": [],
        "assumptions": [],
        "risks": []
      },
      "first_line_output": {
        "summary": "",
        "findings": [],
        "plan": [],
        "files_reviewed": [],
        "files_modified": [],
        "commands_suggested": [],
        "commands_executed": [],
        "risks_detected": [],
        "open_questions": [],
        "confidence": "low | medium | high"
      },
      "reason_for_escalation": "",
      "specific_question_for_escalated_model": "",
      "expected_output": "",
      "constraints": [],
      "security_notes": [],
      "do_not_do": []
    }

### 3. Campos mínimos obligatorios

Todo paquete de escalamiento debe contener:

- `escalation_type`
- `trigger`
- `original_user_request`
- `scenario`
- `risk_level`
- `information_volume`
- `first_line_agent`
- `first_line_model`
- `first_line_output.summary`
- `first_line_output.findings`
- `first_line_output.plan`
- `reason_for_escalation`
- `specific_question_for_escalated_model`
- `expected_output`
- `constraints`
- `do_not_do`

Si un campo no puede completarse automáticamente, debe quedar como `unknown` o como lista vacía. No se debe inventar información.

### 4. Extracción automática desde salidas Go

La generación del paquete debe realizarse mediante una función lógica de normalización:

    normalize_first_line_output()

Entradas mínimas:

- solicitud original del usuario;
- clasificación de tarea;
- resultado del context-validator, si existe;
- resultado del agente Go de primera línea;
- evaluación de suficiencia;
- motivo de escalamiento.

Salidas:

- `first_line_output` normalizado;
- paquete canónico de escalamiento;
- lista de campos incompletos, si aplica.

Reglas de extracción:

- `summary`: extraer de resumen, conclusión, objetivo entendido o diagnóstico principal.
- `findings`: extraer de hallazgos, observaciones, riesgos, inconsistencias o evidencias.
- `plan`: extraer de pasos, plan de ejecución, recomendaciones o próximos pasos.
- `files_reviewed`: extraer de archivos o fuentes declaradas como revisadas.
- `files_modified`: extraer de cambios realizados o diff; en solo lectura debe ser lista vacía.
- `commands_suggested`: comandos recomendados, no ejecutados.
- `commands_executed`: comandos realmente ejecutados.
- `risks_detected`: riesgos, restricciones, incertidumbres o advertencias.
- `open_questions`: dudas, decisiones pendientes o información faltante.
- `confidence`: `high`, `medium` o `low` según suficiencia, trazabilidad y calidad del resultado.

### 5. Punto exacto de inserción

La generación automática del paquete debe ocurrir después de `evaluate_sufficiency()` y antes de invocar Zen continuidad, Zen económico, Zen premium o Replit.

Flujo actualizado:

    first_line_result
            ↓
    evaluate_sufficiency()
            ↓
    si suficiente:
        retornar resultado Go
    si no suficiente:
        normalize_first_line_output()
            ↓
        build_escalation_package()
            ↓
        validate_escalation_package()
            ↓
        enviar a Zen continuidad / Zen económico / Zen premium / Replit

### 6. Pseudocódigo actualizado

    def orchestrate_task(task):
        classification = run_agent("classifier", task)

        routing = determine_routing(
            scenario=classification.scenario,
            risk=classification.risk_level,
            volume=classification.information_volume,
            user_requested_premium=classification.user_requested_premium,
            go_available=check_go_availability()
        )

        context_result = None

        if routing.requires_context_validation:
            context_result = run_agent(
                "context-validator",
                build_context_prompt(task, classification)
            )

        first_line_result = run_agent(
            routing.go_agent,
            build_first_line_prompt(
                task=task,
                classification=classification,
                context_result=context_result
            )
        )

        sufficiency = evaluate_sufficiency(
            task=task,
            classification=classification,
            first_line_result=first_line_result
        )

        if sufficiency.is_sufficient and not routing.user_requested_premium:
            return first_line_result

        normalized_output = normalize_first_line_output(
            task=task,
            classification=classification,
            context_result=context_result,
            first_line_result=first_line_result,
            sufficiency=sufficiency
        )

        escalation_package = build_escalation_package(
            task=task,
            classification=classification,
            context_result=context_result,
            normalized_output=normalized_output,
            sufficiency=sufficiency,
            routing=routing
        )

        validation = validate_escalation_package(escalation_package)

        if not validation.is_valid:
            return request_human_review(
                reason="Escalation package incomplete",
                missing_fields=validation.missing_fields,
                package=escalation_package
            )

        if routing.go_exhausted:
            return run_agent(routing.zen_continuity_agent, escalation_package)

        if routing.requires_premium or routing.user_requested_premium:
            return run_agent(routing.premium_agent, escalation_package)

        return run_agent(routing.zen_economic_agent, escalation_package)

### 7. Validación previa del paquete

Antes de escalar, debe ejecutarse:

    validate_escalation_package()

Debe verificar:

- campos mínimos obligatorios;
- ausencia de secrets o credenciales;
- existencia de solicitud original;
- existencia de motivo de escalamiento;
- existencia de pregunta específica para el modelo escalado;
- consistencia entre `scenario`, `risk_level` y `escalation_type`;
- claridad de `expected_output`.

Si falla la validación, debe solicitar revisión humana antes de escalar.

### 8. Regla de no reinicio

Todo prompt hacia Zen premium debe incluir:

    Tu tarea no es empezar desde cero. Debes usar el paquete de escalamiento como insumo principal, validar el análisis previo, corregir errores, completar omisiones y profundizar donde sea necesario.

### 9. Prevalencia documental

Esta sección prevalece sobre versiones anteriores del paquete de escalamiento cuando exista inconsistencia.

Documentos que deben alinearse:

- `MODEL_ROUTING.md`
- `AGENT_RULES.md`
- `REPLIT_HANDOFF.md`
- `CONTINUE_USAGE_PROTOCOL.md`
- `docs/test_reports/*`

<!-- END: ESCALATION_PACKAGE_CANONICAL_SCHEMA_V0_3 -->

# AGENT_ORCHESTRATION.md

## 1. Propósito

Este documento define la arquitectura de orquestación de agentes para el entorno local de desarrollo asistido por IA, integrando OpenCode, OpenCode Go, OpenCode Zen, Continue, Gemini API gratuita, modelos premium vía Zen y escalamiento hacia Replit cuando corresponda.

La finalidad es establecer un sistema operativo de agentes que permita:

- Usar modelos económicos como primera línea.
- Mantener continuidad cuando Go se agote.
- Escalar a modelos premium solo cuando exista justificación.
- Usar el resultado de modelos de primera línea como insumo para modelos superiores.
- Evitar que cada escalamiento reinicie el análisis desde cero.
- Controlar costos.
- Preservar seguridad.
- Mantener trazabilidad técnica.
- Generar handoffs útiles para Replit, Continue o revisión humana.

---

## 2. Principio rector

La arquitectura no debe operar bajo el patrón:

    Modelo económico intenta -> si falla, modelo premium empieza desde cero.

Debe operar bajo el patrón:

    Modelo de primera línea analiza -> genera salida estructurada -> mini-orquestador evalúa -> modelo Zen o premium valida, corrige, completa o profundiza.

La regla general será:

    Go primero.
    Zen continuidad si Go se agota.
    Zen premium si el usuario lo pide o si el caso lo exige.

---

## 3. Capas de modelos

### 3.1 Línea 1 — OpenCode Go

OpenCode Go será la primera línea operativa de uso cotidiano.

Se usará para:

- Clasificación de tareas.
- Validación preliminar de contexto.
- Planificación simple o media.
- Ejecución controlada de código.
- Cambios pequeños.
- Debugging moderado.
- Revisión normal de diffs.
- Generación de handoffs no críticos.
- Documentación técnica no sensible.
- Evaluación inicial de modelos.

Modelos Go definidos:

    Builder principal:
    opencode-go/kimi-k2.6

    Small model / tareas rápidas:
    opencode-go/deepseek-v4-flash

    Validador de contexto:
    opencode-go/qwen3.6-plus

    Debugger moderado:
    opencode-go/deepseek-v4-pro

    Auxiliar liviano:
    opencode-go/qwen3.5-plus

---

### 3.2 Línea 1B — OpenCode Zen como continuidad

Zen no debe entenderse únicamente como escalamiento premium.

Zen también opera como continuidad pay-as-you-go cuando OpenCode Go llega a sus límites de uso.

En este modo, Zen debe intentar usar:

1. El mismo modelo de Go, si está disponible en Zen.
2. Un modelo equivalente funcional, si el modelo exacto no está disponible.
3. Un modelo económico alternativo antes de usar premium.

Equivalencias base:

    opencode-go/kimi-k2.6
    -> opencode/kimi-k2.6

    opencode-go/qwen3.6-plus
    -> opencode/qwen3.6-plus

    opencode-go/qwen3.5-plus
    -> opencode/qwen3.5-plus

    opencode-go/deepseek-v4-flash
    -> opencode/qwen3.5-plus
    -> opencode/minimax-m2.7

    opencode-go/deepseek-v4-pro
    -> opencode/kimi-k2.6
    -> opencode/qwen3.6-plus
    -> opencode/glm-5

Zen continuidad se usará cuando:

- Go alcance límite de ventana.
- Go alcance límite semanal.
- Go alcance límite mensual.
- Se necesite terminar una tarea ya iniciada.
- Se requiera continuidad inmediata sin esperar renovación de Go.

---

### 3.3 Línea 2 — OpenCode Zen premium

Zen premium se usará cuando exista un activador explícito.

Activadores de premium:

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

Modelos premium definidos:

    Planificación arquitectónica:
    opencode/claude-opus-4-7

    Planificación media premium:
    opencode/claude-sonnet-4-6

    Debugging complejo:
    opencode/gpt-5.5

    Seguridad:
    opencode/gpt-5.5

    Diff sensible:
    opencode/gpt-5.5

    Ejecución premium balanceada:
    opencode/claude-sonnet-4-6
    opencode/gpt-5.4

    Documentación premium:
    opencode/claude-sonnet-4-6

---

## 4. Rol de Continue + Gemini

Continue con Gemini API gratuita actuará como copiloto contextual, no como ejecutor principal.

Uso de Continue + Gemini:

- Lectura amplia de documentación.
- Análisis de coherencia.
- Validación preliminar de arquitectura.
- Preparación de contexto.
- Revisión de handoffs.
- Explicación técnica.
- Apoyo documental.

No debe usarse como ejecutor principal para:

- Cambios críticos de código.
- Cambios multiarchivo sensibles.
- Seguridad.
- Auth.
- Secrets.
- Migraciones.
- Deployment.
- Operaciones destructivas.

---

## 5. Rol de Replit

Replit se conserva como capa de validación remota y entorno real.

Escalar a Replit cuando:

- Se requiera validar en entorno Replit.
- Existan secrets reales.
- Haya deployment.
- Se requieran pruebas de integración.
- Haya migraciones o variables de entorno reales.
- Sea necesaria revisión avanzada de build, entorno o despliegue.

OpenCode debe preparar un handoff compacto, verificable y seguro para Replit.

---

## 6. Mini-orquestador

### 6.1 Propósito

El mini-orquestador coordina el flujo entre agentes, modelos, escalamiento y resultados.

No es solo un selector de modelo. Debe cumplir estas funciones:

1. Clasificar la tarea.
2. Determinar escenario, riesgo y volumen.
3. Seleccionar agente.
4. Seleccionar modelo Go inicial.
5. Ejecutar primera línea.
6. Evaluar suficiencia del resultado.
7. Construir paquete de escalamiento si aplica.
8. Seleccionar Zen continuidad, Zen económico o Zen premium.
9. Garantizar que el resultado de primera línea sea insumo del modelo escalado.
10. Registrar decisión, justificación y resultado.

---

## 7. Flujo operativo general

    Usuario solicita tarea
            ↓
    classifier
            ↓
    mini-orquestador determina:
    - escenario
    - riesgo
    - volumen
    - agente
    - modelo Go
    - necesidad de contexto previo
            ↓
    context-validator si aplica
            ↓
    planner / builder / debugger / reviewer
            ↓
    evaluación de suficiencia
            ↓
    si Go basta:
        entregar resultado o pasar a siguiente fase
    si Go no basta:
        construir paquete de escalamiento
            ↓
    Zen continuidad, Zen económico o Zen premium
            ↓
    resultado escalado
            ↓
    diff-reviewer / security-reviewer si aplica
            ↓
    handoff / documentación si aplica
            ↓
    cierre

---

## 7.1 Plan/Build, aprobaciones y orquestación de fondo

Esta arquitectura asume dos modos operativos:

- **Plan**: análisis/diagnóstico/diseño/revisión/handoff, sin modificar archivos ni ejecutar comandos.
- **Build**: ejecución autorizada por el usuario dentro de un alcance definido, coordinando Continue → MCP → OpenCode con trazabilidad.

Reglas clave:

- OpenCode es el agente técnico natural para codificación, modificación técnica, validación y pruebas (no es “escalamiento”).
- Zen/modelos premium/Replit sí son mecanismos de escalamiento o ampliación de capacidad, y requieren los umbrales de aprobación correspondientes.
- Cuando la existencia de archivos maestros sea relevante, debe prevalecer `verify_master_files` vía MCP sobre la visibilidad del IDE.

Definición completa de aprobaciones, roles, transparencia progresiva y condición de cierre:

- `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md` → **PLAN_BUILD_APPROVAL_AND_BACKGROUND_ORCHESTRATION_POLICY**

---

## 8. Estados del flujo

Cada tarea debe poder ubicarse en uno de estos estados:

    PENDING_CLASSIFICATION
    CLASSIFIED
    CONTEXT_VALIDATED
    FIRST_LINE_EXECUTED
    FIRST_LINE_SUFFICIENT
    ESCALATION_REQUIRED
    ESCALATION_PACKAGE_CREATED
    ZEN_CONTINUITY_EXECUTED
    ZEN_ECONOMIC_EXECUTED
    PREMIUM_EXECUTED
    DIFF_REVIEWED
    SECURITY_REVIEWED
    HANDOFF_CREATED
    DOCUMENTED
    COMPLETED
    BLOCKED

---

## 9. Objeto estándar de orquestación

Toda tarea debe representarse internamente con una estructura equivalente a la siguiente:

    {
      "task_id": "auto-generated",
      "user_request": "",
      "scenario": "",
      "risk_level": "low | medium | high | critical",
      "information_volume": "low | medium | high | high_sensitive",
      "agent": "",
      "first_line_model": "",
      "zen_continuity_model": "",
      "premium_model": "",
      "tools_allowed": {
        "read": true,
        "write": false,
        "bash": false
      },
      "requires_human_approval": true,
      "requires_escalation": false,
      "escalation_reason": "",
      "first_line_result": null,
      "escalation_package": null,
      "final_result": null,
      "security_flags": [],
      "files_in_scope": [],
      "files_modified": [],
      "commands_suggested": [],
      "commands_executed": [],
      "documentation_required": false
    }

---

## 10. Escenarios reconocidos

El mini-orquestador debe reconocer los siguientes escenarios:

1. Clasificación de tarea.
2. Validación de contexto.
3. Planificación simple/media.
4. Planificación arquitectónica/compleja.
5. Ejecución de código controlada.
6. Cambios pequeños/localizados.
7. Debugging moderado.
8. Debugging complejo/crítico.
9. Revisión normal de diff.
10. Revisión de seguridad.
11. Handoff a Replit.
12. Documentación técnica.
13. Evaluación de modelos.

---

## 11. Criterios de volumen de información

### 11.1 Volumen bajo

- 1 a 3 archivos pequeños.
- Sin documentación extensa.
- Sin impacto transversal.
- Sin seguridad.

Modelo sugerido: Go.

### 11.2 Volumen medio

- 4 a 8 archivos.
- Código + documentación.
- Dependencias moderadas.
- Riesgo controlado.

Modelo sugerido: Go fuerte o Zen continuidad.

### 11.3 Volumen alto

- Más de 8 archivos.
- Documentación extensa.
- Handoffs previos.
- Arquitectura + código.
- Decisiones técnicas.

Modelo sugerido: Zen económico de contexto o premium balanceado.

Modelos sugeridos:

    opencode/gemini-3-flash
    opencode/qwen3.6-plus
    opencode/claude-sonnet-4-6
    opencode/gpt-5.4

### 11.4 Volumen alto sensible

- Mucho contexto.
- Seguridad.
- Auth.
- DB.
- Datos personales.
- Deployment.
- Producción.

Modelo sugerido: Premium.

Modelos sugeridos:

    opencode/gpt-5.5
    opencode/claude-opus-4-7

---

## 12. Criterios de riesgo

### 12.1 Riesgo bajo

- Texto.
- Documentación.
- Cambio menor.
- Typo.
- Ajuste visual localizado.
- Explicación.

### 12.2 Riesgo medio

- Cambio de lógica.
- Varios archivos.
- Pruebas.
- Configuración no sensible.
- Debugging moderado.

### 12.3 Riesgo alto

- Auth.
- Permisos.
- Datos.
- Base de datos.
- Integraciones.
- Rutas críticas.
- Build.
- Cambios transversales.

### 12.4 Riesgo crítico

- Secrets.
- Producción.
- Deployment.
- Migraciones.
- Seguridad.
- Datos personales.
- Exposición externa.

Regla:

    Riesgo alto o crítico exige revisión premium final, aunque el análisis inicial pueda iniciar con Go.

---

## 13. Agentes oficiales

### 13.1 classifier

Rol:

Clasificar la tarea, riesgo, volumen, escenario y agente recomendado.

Modelos:

    Go:
    opencode-go/deepseek-v4-flash

    Go alternativa:
    opencode-go/qwen3.5-plus

    Zen continuidad:
    opencode/qwen3.5-plus

    Premium por solicitud:
    opencode/gpt-5.4

Permisos:

    {
      "write": false,
      "bash": false
    }

Salida esperada:

    Clasificación:
    - Tipo de tarea:
    - Escenario:
    - Riesgo:
    - Volumen:
    - Agente recomendado:
    - Modelo recomendado:
    - Escalamiento requerido:
    - Motivo:
    - Restricciones:

---

### 13.2 context-validator

Rol:

Validar reglas, alcance, documentación, archivos relevantes y restricciones antes de ejecutar.

Modelos:

    Go:
    opencode-go/qwen3.6-plus

    Go alternativa:
    opencode-go/deepseek-v4-pro

    Zen continuidad:
    opencode/qwen3.6-plus

    Zen volumen:
    opencode/gemini-3-flash

    Premium:
    opencode/claude-sonnet-4-6
    opencode/gpt-5.4

Permisos:

    {
      "write": false,
      "bash": false
    }

Salida esperada:

    Validación de contexto:
    1. Contexto leído.
    2. Archivos relevantes.
    3. Reglas aplicables.
    4. Riesgos.
    5. Supuestos.
    6. Alcance recomendado.
    7. Agente siguiente.
    8. Necesidad de escalamiento.

---

### 13.3 planner

Rol:

Planificar cambios simples o medianos sin editar archivos.

Modelos:

    Go:
    opencode-go/kimi-k2.6

    Go alternativa:
    opencode-go/deepseek-v4-pro

    Zen continuidad:
    opencode/kimi-k2.6

    Zen económico:
    opencode/qwen3.6-plus
    opencode/glm-5

    Premium:
    opencode/claude-sonnet-4-6

Permisos:

    {
      "write": false,
      "bash": false
    }

Salida esperada:

    Plan de ejecución:
    1. Objetivo.
    2. Archivos a tocar.
    3. Pasos propuestos.
    4. Comandos seguros sugeridos.
    5. Riesgos.
    6. Criterios de éxito.
    7. Criterios para escalar.

---

### 13.4 architect-planner

Rol:

Planificar cambios complejos, arquitectónicos o transversales.

Modelos:

    Go preliminar:
    opencode-go/kimi-k2.6

    Zen continuidad:
    opencode/kimi-k2.6
    opencode/glm-5

    Premium default:
    opencode/claude-opus-4-7

    Premium alternativo:
    opencode/gpt-5.5

Permisos:

    {
      "write": false,
      "bash": false
    }

Salida esperada:

    Plan arquitectónico:
    1. Diagnóstico.
    2. Decisión recomendada.
    3. Alternativas descartadas.
    4. Impactos.
    5. Riesgos.
    6. Secuencia de implementación.
    7. Estrategia de validación.
    8. Estrategia de rollback.
    9. Recomendación de agente ejecutor.

---

### 13.5 builder

Rol:

Ejecutar cambios controlados de código con aprobación humana.

Modelos:

    Go:
    opencode-go/kimi-k2.6

    Go alternativa:
    opencode-go/deepseek-v4-pro

    Zen continuidad:
    opencode/kimi-k2.6

    Zen económico:
    opencode/qwen3.6-plus

    Premium por solicitud:
    opencode/claude-sonnet-4-6
    opencode/gpt-5.4

    Premium crítico:
    opencode/gpt-5.5
    opencode/claude-opus-4-7

Permisos:

    {
      "write": true,
      "bash": true,
      "edit": "ask",
      "bash_permission": "ask"
    }

Restricciones:

- No tocar archivos fuera de alcance.
- No modificar .env.
- No hacer migraciones sin autorización.
- No hacer deployment.
- No reformatear todo el proyecto.
- No eliminar validaciones sin justificación.
- No crear documentación innecesaria.

Salida esperada:

    Ejecución:
    1. Archivos modificados.
    2. Cambios realizados.
    3. Motivo técnico.
    4. Pruebas sugeridas o ejecutadas.
    5. Riesgos residuales.
    6. Diff listo para revisión.

---

### 13.6 light-builder

Rol:

Ejecutar cambios pequeños, localizados y de bajo riesgo.

Modelos:

    Go:
    opencode-go/deepseek-v4-flash

    Go alternativa:
    opencode-go/qwen3.5-plus

    Zen continuidad:
    opencode/qwen3.5-plus
    opencode/minimax-m2.7

    Premium por solicitud:
    opencode/gpt-5.4

Permisos:

    {
      "write": true,
      "bash": true,
      "edit": "ask",
      "bash_permission": "ask"
    }

Salida esperada:

    Cambio menor:
    - Archivo modificado.
    - Cambio aplicado.
    - Validación mínima.
    - Riesgo residual.

---

### 13.7 debugger

Rol:

Analizar errores moderados, logs depurados, fallos de pruebas y bugs no críticos.

Modelos:

    Go:
    opencode-go/deepseek-v4-pro

    Go alternativa:
    opencode-go/kimi-k2.6

    Zen continuidad:
    opencode/kimi-k2.6
    opencode/qwen3.6-plus

    Premium por solicitud:
    opencode/gpt-5.4

    Premium si persiste:
    opencode/gpt-5.5

Permisos:

    {
      "write": false,
      "bash": true,
      "bash_permission": "ask"
    }

Salida esperada:

    Diagnóstico:
    1. Error observado.
    2. Hipótesis principal.
    3. Hipótesis alternativas.
    4. Archivos involucrados.
    5. Pruebas sugeridas.
    6. Corrección recomendada.
    7. Si requiere builder o escalamiento.

---

### 13.8 critical-debugger

Rol:

Diagnosticar errores complejos, persistentes o de alto impacto.

Modelos:

    Go preliminar:
    opencode-go/deepseek-v4-pro

    Zen continuidad:
    opencode/kimi-k2.6

    Premium default:
    opencode/gpt-5.5

    Premium alternativo:
    opencode/claude-opus-4-7

Permisos:

    {
      "write": false,
      "bash": true,
      "bash_permission": "ask"
    }

Salida esperada:

    Debugging crítico:
    1. Resumen del fallo.
    2. Cadena causal probable.
    3. Evidencias.
    4. Archivos críticos.
    5. Corrección recomendada.
    6. Riesgos.
    7. Plan de validación.
    8. Necesidad de handoff a Replit.

---

### 13.9 diff-reviewer

Rol:

Revisar diffs normales contra alcance, reglas, seguridad básica y coherencia.

Modelos:

    Go:
    opencode-go/qwen3.6-plus

    Go alternativa:
    opencode-go/deepseek-v4-pro

    Zen continuidad:
    opencode/qwen3.6-plus

    Zen económico:
    opencode/kimi-k2.6

    Premium por solicitud:
    opencode/gpt-5.4

    Premium sensible:
    opencode/gpt-5.5

Permisos:

    {
      "write": false,
      "bash": false
    }

Salida esperada:

    Revisión de diff:
    1. Cumple alcance: sí/no.
    2. Archivos modificados.
    3. Riesgos detectados.
    4. Cambios innecesarios.
    5. Posibles regresiones.
    6. Recomendación: aprobar / ajustar / escalar.

---

### 13.10 security-reviewer

Rol:

Revisar seguridad, secrets, auth, permisos, exposición de datos y comandos peligrosos.

Modelos:

    Go pre-revisión:
    opencode-go/qwen3.6-plus
    opencode-go/deepseek-v4-pro

    Zen continuidad pre-revisión:
    opencode/qwen3.6-plus

    Premium obligatorio:
    opencode/gpt-5.5

    Premium alternativo:
    opencode/claude-opus-4-7

Permisos:

    {
      "write": false,
      "bash": false
    }

Regla:

    La revisión final sensible de seguridad siempre requiere premium.

Salida esperada:

    Revisión de seguridad:
    1. Hallazgos.
    2. Severidad.
    3. Evidencia.
    4. Riesgo.
    5. Recomendación.
    6. Bloqueante: sí/no.
    7. Requiere revisión humana: sí/no.

---

### 13.11 handoff-writer

Rol:

Preparar handoffs claros para Replit, Continue, humano desarrollador u otro agente.

Modelos:

    Go:
    opencode-go/qwen3.6-plus

    Go alternativa:
    opencode-go/kimi-k2.6

    Zen continuidad:
    opencode/qwen3.6-plus

    Premium por solicitud:
    opencode/gpt-5.4

    Premium crítico:
    opencode/gpt-5.5
    opencode/claude-sonnet-4-6

Permisos:

    {
      "write": true,
      "bash": false,
      "edit": "ask"
    }

Salida esperada:

    Handoff:
    1. Contexto.
    2. Objetivo.
    3. Alcance.
    4. Restricciones.
    5. Archivos relevantes.
    6. Pasos sugeridos.
    7. Comandos seguros.
    8. No hacer.
    9. Criterios de éxito.
    10. Resultado esperado.

---

### 13.12 documentation-writer

Rol:

Documentar decisiones, aprendizajes, protocolos, resultados de pruebas y cambios relevantes.

Modelos:

    Go:
    opencode-go/qwen3.6-plus

    Go alternativa:
    opencode-go/qwen3.5-plus

    Zen continuidad:
    opencode/qwen3.6-plus

    Zen volumen alto:
    opencode/gemini-3-flash

    Premium por solicitud:
    opencode/claude-sonnet-4-6

    Premium crítico:
    opencode/gpt-5.5

Permisos:

    {
      "write": true,
      "bash": false,
      "edit": "ask"
    }

Regla:

    No documentar todo por defecto. Documentar solo decisiones, aprendizajes o cambios de valor persistente.

Salida esperada:

    Documento:
    1. Fecha.
    2. Contexto.
    3. Decisión o aprendizaje.
    4. Evidencia.
    5. Impacto.
    6. Regla actualizada.
    7. Próximos pasos.

---

### 13.13 model-evaluator

Rol:

Comparar modelos Go, Zen económico y Zen premium en tareas controladas.

Modelos evaluables:

    Go:
    opencode-go/kimi-k2.6
    opencode-go/qwen3.6-plus
    opencode-go/deepseek-v4-pro
    opencode-go/deepseek-v4-flash

    Zen económico:
    opencode/kimi-k2.6
    opencode/qwen3.6-plus
    opencode/qwen3.5-plus
    opencode/glm-5
    opencode/gemini-3-flash

    Zen premium:
    opencode/claude-sonnet-4-6
    opencode/claude-opus-4-7
    opencode/gpt-5.4
    opencode/gpt-5.5

Permisos:

    {
      "write": false,
      "bash": false
    }

Salida esperada:

    Evaluación:
    1. Tarea evaluada.
    2. Modelos comparados.
    3. Calidad de respuesta.
    4. Respeto de instrucciones.
    5. Riesgos.
    6. Costo relativo.
    7. Latencia percibida.
    8. Recomendación.

---

## 14. Matriz resumida de agentes

| Agente | Go default | Zen continuidad | Premium |
|---|---|---|---|
| classifier | DeepSeek V4 Flash | Qwen3.5 Plus | GPT-5.4 |
| context-validator | Qwen3.6 Plus | Qwen3.6 Plus / Gemini 3 Flash | Claude Sonnet / GPT-5.4 |
| planner | Kimi K2.6 | Kimi K2.6 | Claude Sonnet |
| architect-planner | Kimi preliminar | Kimi / GLM | Claude Opus / GPT-5.5 |
| builder | Kimi K2.6 | Kimi K2.6 | Claude Sonnet / GPT-5.4 |
| light-builder | DeepSeek V4 Flash | Qwen3.5 Plus | GPT-5.4 |
| debugger | DeepSeek V4 Pro | Kimi / Qwen | GPT-5.4 / GPT-5.5 |
| critical-debugger | DeepSeek preliminar | Kimi | GPT-5.5 / Claude Opus |
| diff-reviewer | Qwen3.6 Plus | Qwen3.6 Plus | GPT-5.4 / GPT-5.5 |
| security-reviewer | Qwen pre-review | Qwen pre-review | GPT-5.5 / Claude Opus |
| handoff-writer | Qwen3.6 Plus | Qwen3.6 Plus | GPT-5.4 / GPT-5.5 |
| documentation-writer | Qwen3.6 Plus | Gemini 3 Flash / Qwen | Claude Sonnet |
| model-evaluator | Variable | Variable | Variable |

---

## 15. Evaluación de suficiencia

Antes de escalar, salvo solicitud expresa del usuario o riesgo crítico, el mini-orquestador debe evaluar si el resultado de Go es suficiente.

### Go es suficiente si:

- Entiende correctamente la tarea.
- Respeta restricciones.
- Identifica archivos relevantes.
- No inventa contexto.
- No solicita secrets.
- Propone plan acotado.
- Toca pocos archivos.
- Justifica cambios.
- Identifica riesgos razonables.
- Produce salida accionable.
- No hay seguridad ni criticidad.

### Go no es suficiente si:

- Responde genérico.
- Contradice reglas.
- Omite riesgos evidentes.
- Propone cambios masivos innecesarios.
- No entiende arquitectura.
- Falla dos veces en bug.
- No explica el diff.
- No identifica archivos clave.
- Hay seguridad, auth, datos o deployment.
- El usuario pidió premium.

---

## 16. Paquete de escalamiento

Cuando se active escalamiento, la salida de primera línea debe convertirse en un paquete estructurado.

    {
      "escalation_type": "zen_continuity | zen_economic | zen_premium",
      "trigger": "",
      "original_user_request": "",
      "scenario": "",
      "risk_level": "",
      "information_volume": "",
      "first_line_agent": "",
      "first_line_model": "",
      "first_line_output": {
        "summary": "",
        "findings": [],
        "plan": [],
        "files_reviewed": [],
        "files_modified": [],
        "commands_suggested": [],
        "risks_detected": [],
        "open_questions": [],
        "confidence": "low | medium | high"
      },
      "reason_for_escalation": "",
      "specific_question_for_escalated_model": "",
      "expected_output": "",
      "constraints": [],
      "security_notes": [],
      "do_not_do": []
    }

---

## 17. Prompt estándar para Zen continuidad

Usar cuando Go se agote y se requiera continuar sin escalar a premium.

    Actúa como continuidad operativa del agente de primera línea.

    El modelo Go alcanzó límites de uso o no está disponible.
    Debes continuar la tarea usando el mismo contexto y respetando el resultado previo.

    No trates este caso como escalamiento premium.
    Tu función es mantener continuidad operativa.

    Solicitud original:
    {{original_user_request}}

    Trabajo ya realizado por Go:
    {{first_line_result}}

    Siguiente paso requerido:
    {{next_step}}

    Restricciones:
    - Mantén el alcance.
    - No reinicies innecesariamente el análisis.
    - No propongas cambios más amplios.
    - No uses herramientas destructivas.
    - No expongas secrets.

    Salida esperada:
    {{expected_output}}

---

## 18. Prompt estándar para Zen premium

Usar cuando haya solicitud del usuario, complejidad, riesgo o revisión crítica.

    Actúa como agente premium especializado en {{scenario}}.

    Vas a recibir:
    1. Solicitud original del usuario.
    2. Clasificación de tarea.
    3. Validación de contexto, si existe.
    4. Resultado del modelo de primera línea.
    5. Motivo del escalamiento.

    Tu tarea no es empezar desde cero.

    Tu tarea es:
    - Validar el análisis previo.
    - Corregir errores.
    - Completar omisiones.
    - Profundizar donde sea necesario.
    - Decidir si el resultado previo es aceptable.
    - Producir una salida final accionable.

    Solicitud original:
    {{original_user_request}}

    Clasificación:
    {{classification}}

    Resultado de primera línea:
    {{first_line_result}}

    Motivo del escalamiento:
    {{reason_for_escalation}}

    Restricciones:
    - No inventes contexto.
    - No solicites ni expongas secrets.
    - No propongas cambios fuera de alcance.
    - No ejecutes acciones destructivas.
    - Si hay incertidumbre, identifícala.
    - Si el resultado de primera línea es correcto, puedes confirmarlo y fortalecerlo.

    Salida esperada:
    {{expected_output}}

---

## 19. Pseudocódigo del mini-orquestador

    def orchestrate_task(task):
        classification = run_agent("classifier", task)

        routing = determine_routing(
            scenario=classification.scenario,
            risk=classification.risk_level,
            volume=classification.information_volume,
            user_requested_premium=classification.user_requested_premium,
            go_available=check_go_availability()
        )

        if routing.user_requested_premium:
            escalation_package = build_direct_premium_package(
                task=task,
                classification=classification
            )
            return run_agent(routing.premium_agent, escalation_package)

        context_result = None

        if routing.requires_context_validation:
            context_result = run_agent(
                "context-validator",
                build_context_prompt(task, classification)
            )

        first_line_result = run_agent(
            routing.go_agent,
            build_first_line_prompt(
                task=task,
                classification=classification,
                context_result=context_result
            )
        )

        sufficiency = evaluate_sufficiency(
            task=task,
            classification=classification,
            first_line_result=first_line_result
        )

        if sufficiency.is_sufficient:
            return first_line_result

        escalation_package = build_escalation_package(
            task=task,
            classification=classification,
            context_result=context_result,
            first_line_result=first_line_result,
            sufficiency=sufficiency
        )

        if routing.go_exhausted:
            return run_agent(
                routing.zen_continuity_agent,
                escalation_package
            )

        if routing.requires_premium:
            return run_agent(
                routing.premium_agent,
                escalation_package
            )

        return run_agent(
            routing.zen_economic_agent,
            escalation_package
        )

---

## 20. Regla de documentación

El sistema no debe documentar todo automáticamente.

Debe documentar cuando exista:

- Decisión técnica relevante.
- Cambio de routing.
- Cambio de modelo default.
- Error corregido importante.
- Aprendizaje de prueba.
- Riesgo de seguridad.
- Handoff a Replit.
- Descarte de alternativa técnica.
- Cambio de arquitectura.

Documentos afectados posibles:

    MODEL_ROUTING.md
    AGENT_RULES.md
    PROJECT_CONTEXT.md
    CONTINUE_USAGE_PROTOCOL.md
    REPLIT_HANDOFF.md
    AGENT_ORCHESTRATION.md
    docs/test_reports/*
    docs/agent_handoffs/*
    docs/decisions/*

---

## 21. Decisión formal

Se adopta una arquitectura de orquestación para OpenCode basada en agentes especializados, routing por escenarios, niveles de modelo y volumen de información.

OpenCode Go será la primera línea operativa. OpenCode Zen funcionará como continuidad pay-as-you-go cuando Go se agote y como capa de escalamiento económico o premium cuando corresponda.

El escalamiento premium podrá activarse por:

- Solicitud del usuario.
- Complejidad.
- Riesgo.
- Volumen alto de información.
- Debugging persistente.
- Seguridad.
- Revisión sensible.
- Impacto productivo.

La mini-orquestación deberá garantizar que el resultado del modelo de primera línea no se descarte. En todo evento de escalamiento, el análisis, diagnóstico, plan, diff, riesgos y preguntas abiertas generados por Go deberán estructurarse como insumo para el modelo Zen o premium.

El modelo escalado deberá validar, corregir, completar o profundizar el resultado previo, no reiniciar la tarea sin aprovecharlo.

