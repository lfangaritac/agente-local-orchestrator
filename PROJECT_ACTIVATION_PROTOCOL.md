# PROJECT_ACTIVATION_PROTOCOL.md

## Proposito

Protocolo operativo minimo para activar el sistema de agentes en un proyecto.

Este documento define las rutas soportadas para iniciar, sincronizar y operar proyectos entre VS Code/local, GitHub y Replit.

## Ciclo esperado

VS Code local -> Continue -> OpenCode o agente coder local -> Git/GitHub -> Replit -> pruebas -> logs -> documentacion -> handoff.

## Activacion minima

1. Crear nucleo documental.
2. Identificar stack.
3. Identificar secrets requeridos.
4. Crear o ajustar SECRETS_MANIFEST.md.
5. Crear o ajustar scripts/check_env.py.
6. Validar entorno.
7. Versionar cambios.
8. Probar en Replit cuando aplique.

## Criterio de exito

El proyecto queda activado cuando puede ejecutarse el ciclo:

definir tarea -> revisar contexto -> elegir agente/modelo -> ejecutar -> probar -> versionar -> validar en Replit.

## Cierre de habilitacion operativa minima

Registrar y documentar un proyecto no equivale automaticamente a dejarlo listo para trabajo funcional real.

- Proyecto registrado: existe identidad confirmada, ruta local/remota conocida y entrada en el registro del orquestador.
- Proyecto documentado: existe scaffold o contexto minimo con stack, estructura, riesgos, comandos, restricciones y fuentes relevantes.
- Proyecto operativo para trabajo funcional controlado: ademas de lo anterior, existe evidencia suficiente para ejecutar cambios acotados con validaciones seguras y umbrales claros.

Un proyecto solo debe declararse operativo cuando haya evidencia razonable de:

- registro del proyecto en el orquestador;
- scaffold/contexto documental minimo creado o actualizado;
- repositorio objetivo identificado y estado Git conocido;
- riesgos iniciales detectados;
- entrypoints o mecanismo de arranque revisados para side effects cuando aplique;
- comandos seguros y comandos bloqueados identificados;
- baseline minima de validacion definida, o ausencia de baseline justificada;
- pruebas seguras identificadas si existen;
- exclusiones documentadas;
- clasificacion inicial de tareas por riesgo;
- declaracion final: listo, no listo o listo parcialmente, con proxima frontera.

La habilitacion no debe perseguir cobertura total ni perfeccion. Debe cerrar cuando exista una baseline minima suficiente para empezar trabajo funcional real con control, o cuando quede documentado por que el proyecto aun no esta listo.

Despues de declarar un proyecto listo para trabajo funcional controlado, las instrucciones futuras deben orientarse a necesidades reales del usuario, no a preparacion generica indefinida.

Clasificacion transversal de tareas:

- VERDE: documentacion, helpers puros, normalizadores, validaciones locales, tests aislados y cambios sin DB real ni servicios externos.
- AMARILLA: endpoints o rutas con mocks, test_client o equivalente con aislamiento, logica funcional puntual con datos fake, cambios controlados que requieren baseline antes/despues y ajustes de payload/copy sin invocar servicios reales.
- ROJA: DB real, migraciones, servicios externos reales, secrets, auth sensible, envios masivos, scripts operativos, deployment, infraestructura y cambios que puedan afectar datos reales.

Formato breve de declaracion final:

- Estado de habilitacion operativa: listo / no listo / listo parcialmente.
- Listo para tareas VERDES: si/no.
- Listo para tareas AMARILLAS con baseline/mocks: si/no.
- Tareas ROJAS requieren autorizacion especial: si.
- Baseline segura recomendada:
- Comandos bloqueados:
- Proxima frontera:

## Rutas operativas soportadas

El orquestador reconoce dos rutas principales de activacion de proyectos:

### Ruta local-first

Usar cuando el proyecto nace o se trabaja inicialmente en VS Code/local.

Flujo: local -> GitHub -> Replit -> GitHub -> local.

### Ruta replit-first

Usar cuando el proyecto nace o se prototipa inicialmente en Replit.

Flujo: Replit -> GitHub -> local -> GitHub.

### Regla operativa

En ambos casos, GitHub funciona como punto de sincronizacion verificable entre local y Replit.

El sistema operativo de agentes debe quedar versionado en el repositorio del proyecto destino.

Cada entorno debe terminar con git status limpio antes de continuar.

## Escenario validado: local-first

Flujo validado: Proyecto local -> GitHub -> Replit -> GitHub -> local.

Resultado operativo:
- Proyecto minimo creado en local.
- Sistema operativo de agentes aplicado desde el orquestador.
- Commit local inicial realizado.
- Repositorio privado creado en GitHub.
- Push desde local hacia GitHub realizado.
- Repl vacio creado en Replit.
- Repositorio llevado al workspace de Replit.
- Archivo .replit agregado y versionado desde Replit.
- Push desde Replit hacia GitHub realizado.
- Pull local exitoso con cambios creados desde Replit.
- Git limpio en ambos extremos.

Conclusion: el escenario local-first queda validado como ruta viable para iniciar proyectos desde VS Code/local, versionarlos en GitHub y operarlos posteriormente desde Replit.

## Escenario validado: replit-first

Flujo validado: Replit -> GitHub -> local -> GitHub.

Resultado operativo:
- Proyecto minimo creado directamente en Replit.
- Git inicializado en Replit.
- Commit inicial realizado desde Replit.
- Repositorio privado creado en GitHub.
- Push desde Replit hacia GitHub realizado.
- Repositorio clonado en local.
- Sistema operativo de agentes aplicado desde el orquestador local.
- Activador ejecutado correctamente en local.
- check_env.py validado correctamente.
- Commit local con sistema de agentes realizado.
- Push desde local hacia GitHub realizado.
- Git limpio al finalizar.

Conclusion: el escenario replit-first queda validado como ruta viable para iniciar proyectos desde Replit, versionarlos en GitHub, traerlos a VS Code/local y activar posteriormente el sistema operativo de agentes.

## Nota sobre proyectos destino

Cuando el orquestador se aplica a un proyecto externo, scripts/check_env.py se copia como plantilla inicial.

Cada proyecto destino debe ajustar ese archivo segun sus propias variables reales, stack e integraciones, y debe actualizar SECRETS_MANIFEST.md sin incluir valores sensibles.
