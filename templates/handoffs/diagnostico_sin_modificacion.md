# Handoff Template — Diagnóstico sin modificación

## Objetivo

Realizar un diagnóstico controlado sobre una tarea, módulo, error o integración, sin modificar código ni configuración.

## Contexto

Describe brevemente:

- Proyecto:
- Entorno:
- Rama:
- Archivos relevantes:
- Problema o pregunta:
- Resultado esperado del diagnóstico:

## Alcance permitido

El agente puede:

- leer archivos;
- revisar logs;
- inspeccionar estructura;
- identificar riesgos;
- proponer hipótesis;
- sugerir pruebas;
- preparar un plan de cambio.

## Restricciones

El agente no debe:

- modificar código;
- modificar secrets;
- modificar `.env`;
- modificar `.replit`;
- ejecutar migraciones;
- ejecutar deployment;
- cambiar schema;
- ejecutar comandos destructivos;
- hacer refactor;
- aplicar cambios sin autorización.

## Resultado esperado

El agente debe entregar:

1. Estado general.
2. Hallazgos.
3. Archivos o bloques revisados.
4. Riesgos.
5. Cambio mínimo sugerido, si aplica.
6. Prueba recomendada.
7. Confirmación explícita de que no modificó nada.
8. Pregunta de autorización antes de cualquier cambio.
