# Reporte de prueba controlada — Flujo Go a Zen Premium v0.1

## Fecha

2026-05-05

## Objetivo

Validar documentalmente que la arquitectura del orquestador local permite conducir una tarea mediante el flujo:

classifier → context-validator → planner → escalamiento simulado a Zen premium

## Modelo usado

OpenCode Go — Kimi K2.6 (3x limits)

## Archivos revisados por OpenCode

- `AGENT_ORCHESTRATION.md`
- `MODEL_ROUTING.md`
- `AGENT_RULES.md`

## Resultado general

La prueba fue exitosa.

OpenCode actuó como mini-orquestador y produjo las fases esperadas:

1. Resultado del classifier.
2. Resultado del context-validator.
3. Resultado del planner.
4. Evaluación de suficiencia de Go.
5. Paquete simulado de escalamiento a Zen premium.
6. Prompt final para Zen premium.
7. Conclusión de la prueba.

## Validaciones positivas

La respuesta reconoció correctamente que:

- Go debe operar como primera línea.
- Zen continuidad debe considerarse antes de premium cuando aplique.
- Zen premium se justifica por solicitud, riesgo, volumen, complejidad o debugging crítico.
- El resultado de Go no debe descartarse.
- El resultado de Go debe convertirse en un paquete estructurado para el modelo premium.
- El modelo premium debe validar, corregir, completar o profundizar el resultado previo.
- El modelo premium no debe reiniciar desde cero.
- No se deben modificar archivos durante una prueba documental.

## Hallazgos

### 1. Divergencia de schema

Se identificó una divergencia entre dos documentos:

- `AGENT_ORCHESTRATION.md` define un paquete con salida de primera línea anidada bajo `first_line_output`.
- `MODEL_ROUTING.md` define un paquete más plano con campos como `first_line_summary`, `first_line_findings` y `first_line_plan`.

Esto puede generar ambigüedad en una implementación real.

### 2. Falta de mecanismo de extracción automática

La documentación todavía no define cómo el mini-orquestador debe extraer automáticamente campos desde respuestas variables de Go.

Ejemplos de campos que deben normalizarse:

- resumen;
- hallazgos;
- plan;
- archivos revisados;
- riesgos detectados;
- preguntas abiertas;
- confianza;
- motivo de escalamiento.

### 3. Punto de automatización

El pseudocódigo existente incluye `build_escalation_package()`, pero todavía debe aclararse si la generación será:

- manual;
- semiautomática;
- automática.

La recomendación de la prueba es que sea automática cuando `evaluate_sufficiency()` determine que Go no es suficiente o cuando exista activador premium.

## Conclusión

La arquitectura documentada es suficiente para guiar el flujo conceptual y operativo de orquestación.

Antes de avanzar hacia implementación real robusta, se recomienda una micro-actualización documental v0.3 para:

1. Definir un schema canónico único del paquete de escalamiento.
2. Documentar el mecanismo de extracción automática desde salidas Go.
3. Precisar el punto exacto de inserción dentro del mini-orquestador.
4. Actualizar `AGENT_ORCHESTRATION.md`, `MODEL_ROUTING.md` y `AGENT_RULES.md` para eliminar ambigüedad.

## Estado

Prueba superada con hallazgos documentales menores.
