# DEVELOPMENT_CHECKS.md

## Proposito

Definir las verificaciones minimas que debe ejecutar o reportar cualquier agente antes de considerar completa una tarea de codificacion.

Este documento aplica especialmente a OpenCode como agente local de codificacion, pero tambien orienta a Continue, Codex en VS Code (cuando el usuario autorice modo integrado de codificacion), Replit Agent y cualquier modelo de apoyo.


## Regla principal

Ningun cambio de codigo se considera completo si no incluye evidencia de verificacion.

La evidencia minima debe incluir:

- archivos modificados;
- comandos ejecutados;
- resultado de cada comando;
- errores encontrados;
- correcciones aplicadas;
- git diff revisado;
- git status final;
- pruebas pendientes, si existen.

## Flujo obligatorio para tareas de codificacion

1. Revisar alcance autorizado.
2. Revisar contexto del proyecto.
3. Identificar archivos relevantes.
4. Proponer plan breve antes de modificar.
5. Modificar archivos solo si existe autorizacion.
6. Ejecutar verificaciones disponibles.
7. Corregir errores detectados.
8. Repetir verificaciones necesarias.
9. Revisar git diff.
10. Revisar git status.
11. Entregar reporte de cambios.
12. Preparar handoff a Replit si se requiere validacion remota.

## Comandos comunes por tipo de proyecto

### Node, React, Vite o Express

Usar cuando existan en package.json:

- npm install
- npm run check
- npm run build
- npm test
- npm run dev, solo si se requiere validacion local de ejecucion

### Python

Usar cuando apliquen:

- python scripts/check_env.py
- python -m compileall .
- pytest
- ruff check .
- mypy .

### Proyecto hibrido o Replit

Usar segun stack detectado:

- python scripts/check_env.py
- npm run check
- npm run build
- git diff
- git status
- validacion en Replit si depende de runtime, preview, secrets o deployment.

## Si no existen pruebas

Si el proyecto no tiene pruebas automatizadas o comandos claros, el agente debe reportar:

- No se encontraron pruebas automatizadas configuradas.
- Verificaciones disponibles ejecutadas.
- Riesgos de validar manualmente.
- Recomendacion de prueba minima futura.

El agente no debe inventar pruebas ni declarar exito total sin evidencia.

## Restricciones

El agente no debe:

- ejecutar migraciones sin autorizacion;
- ejecutar deployment sin autorizacion;
- modificar secrets;
- imprimir valores sensibles;
- versionar archivos .env;
- modificar .replit sin autorizacion;
- cambiar schema sin plan y aprobacion;
- hacer refactor no solicitado.

## Criterio de cierre

Una tarea de codificacion queda lista para revision cuando existe:

- diff revisado;
- verificaciones ejecutadas o justificacion de ausencia;
- reporte de cambios;
- git status limpio o cambios claramente pendientes de commit;
- indicacion de si requiere validacion en Replit.
