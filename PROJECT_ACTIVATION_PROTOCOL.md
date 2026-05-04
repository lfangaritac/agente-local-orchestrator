# PROJECT_ACTIVATION_PROTOCOL.md

## Propósito

Protocolo operativo mínimo para activar el sistema de agentes en un proyecto.

## Ciclo esperado

VS Code local -> Continue -> OpenCode o agente coder local -> Git/GitHub -> Replit -> pruebas, logs, documentación y handoff.

## Activación mínima

1. Crear núcleo documental.
2. Identificar stack.
3. Identificar secrets requeridos.
4. Crear SECRETS_MANIFEST.md.
5. Crear scripts/check_env.py.
6. Validar entorno.
7. Versionar cambios.
8. Probar en Replit cuando aplique.

## Criterio de éxito

El proyecto queda activado cuando puede ejecutarse el ciclo: definir tarea -> revisar contexto -> elegir agente/modelo -> ejecutar -> probar -> versionar -> validar en Replit.

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

El sistema operativo de agentes debe quedar versionado en el repositorio del proyecto destino, y cada entorno debe terminar con git status limpio antes de continuar.
