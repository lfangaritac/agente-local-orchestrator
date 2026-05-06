# PROJECT_ENABLEMENT_PROTOCOL.md

## 1. Propósito

Definir el protocolo operativo para habilitar proyectos objetivo dentro del orquestador local `C:\Agente`.

Este protocolo convierte el contrato de contexto multi-proyecto en un procedimiento aplicable a proyectos nuevos, existentes, locales, Replit, GitHub, importados o sincronizados.

La habilitación de un proyecto objetivo no consiste únicamente en copiar reglas o documentación. Consiste en indagar, registrar, indexar, contrastar, referenciar, sincronizar y gobernar el contexto completo del proyecto para que Continue, OpenCode, Replit y los modelos de escalamiento puedan operar con contexto suficiente, trazable y actualizado.

## 2. Principio central

Ningún proyecto objetivo debe considerarse habilitado en el orquestador si no cuenta, como mínimo, con:

- identificación formal;
- registro en `PROJECT_REGISTRY.md`;
- ruta local o ubicación confirmada;
- origen del proyecto;
- stack detectado;
- documentación explícita identificada;
- contexto embebido preliminar identificado;
- mapa inicial de código;
- alertas críticas iniciales;
- estado de sincronización;
- reglas de acceso para Continue y OpenCode;
- criterios de actualización continua;
- relación con Replit/GitHub si aplica.

## 3. Modos de habilitación

El protocolo aplica a estos modos:

### 3.1 Local primero

Proyecto creado o gestionado inicialmente en entorno local.

### 3.2 Replit primero

Proyecto iniciado, ejecutado o validado inicialmente desde Replit.

### 3.3 GitHub primero

Proyecto clonado o sincronizado desde repositorio remoto.

### 3.4 Proyecto existente

Proyecto con código, documentación y decisiones previas.

### 3.5 Proyecto nuevo

Proyecto iniciado desde cero bajo gobierno del orquestador.

### 3.6 Carpeta importada

Proyecto incorporado manualmente desde una carpeta local existente.

### 3.7 Proyecto sincronizado

Proyecto que ya existe en más de un entorno, por ejemplo local + GitHub + Replit.

## 4. Fases del protocolo ENABLE_TARGET_PROJECT

La habilitación debe ejecutarse en fases.

## 5. Fase 1 — Identificación del proyecto objetivo

El orquestador debe determinar:

- nombre canónico del proyecto;
- alias permitidos;
- origen del proyecto;
- ruta local;
- repositorio remoto;
- relación con Replit;
- relación con GitHub;
- rama activa;
- estado Git;
- stack preliminar;
- responsable o usuario principal;
- estado de habilitación.

Si el nombre del proyecto no está confirmado, debe registrarse como:

`Proyecto objetivo no confirmado`

Si se detectan nombres posibles en archivos, carpetas o documentación, deben registrarse como:

`posible alias no confirmado`

No se debe inventar identidad del proyecto.

## 6. Fase 2 — Registro inicial en PROJECT_REGISTRY.md

Todo proyecto habilitado debe registrarse en `PROJECT_REGISTRY.md`.

Campos mínimos:

- `project_id`
- `nombre_canonico`
- `alias_permitidos`
- `ruta_local`
- `repositorio_remoto`
- `origen`
- `stack_detectado`
- `documentacion_principal`
- `codigo_fuente_relevante`
- `estado_sincronizacion`
- `alertas_criticas`
- `lecciones_locales`
- `ultimo_analisis`
- `responsable`
- `continue_access_level`
- `opencode_access_level`
- `replit_relation`
- `github_relation`
- `status`

El registro no debe contener secrets, tokens, credenciales ni valores reales de variables de entorno.

## 7. Fase 3 — Creación de estructura documental del proyecto en el orquestador

Por cada proyecto objetivo debe crearse una carpeta:

`docs/projects/<project-id>/`

Con estos archivos mínimos:

- `PROJECT_PROFILE.md`
- `CONTEXT_INDEX.md`
- `CODE_CONTEXT_MAP.md`
- `DOCUMENTATION_AUDIT.md`
- `CRITICAL_ALERTS.md`
- `LESSONS_LOCAL.md`
- `SYNC_STATUS.md`
- `HANDOFF_LOG.md`

Estos archivos son índices, perfiles y síntesis curadas. No reemplazan automáticamente las fuentes originales del proyecto objetivo.

## 8. Fase 4 — Indagación de documentación explícita

El orquestador debe buscar y registrar documentación explícita en el proyecto objetivo.

Fuentes típicas:

- `README.md`
- `PROJECT_CONTEXT.md`
- `/docs`
- ADRs;
- handoffs;
- test reports;
- decisiones;
- prompts;
- instrucciones de agentes;
- documentación API;
- documentación funcional;
- documentación técnica;
- notas Replit;
- notas de despliegue;
- documentación de seguridad;
- documentación de base de datos;
- documentación de casos de uso;
- documentación de arquitectura.

Para cada fuente debe registrarse:

- ruta;
- tipo de documento;
- resumen;
- nivel de confianza;
- fecha de revisión;
- estado: vigente, incierto, obsoleto o pendiente;
- relación con código;
- necesidad de revisión humana.

## 9. Fase 5 — Indagación de contexto embebido

El orquestador debe analizar contexto no necesariamente formal pero relevante, incluyendo:

- comentarios en código;
- TODO;
- FIXME;
- nombres de rutas;
- nombres de servicios;
- nombres de componentes;
- nombres de funciones;
- nombres de variables significativas;
- constantes;
- mensajes de error;
- validaciones;
- schemas;
- migraciones;
- seeds;
- fixtures;
- tests;
- scripts;
- prompts dentro del código;
- convenciones repetidas;
- dependencias;
- configuraciones;
- estructura de carpetas;
- entrypoints;
- endpoints;
- modelos de datos.

El contexto embebido debe registrarse como inferencia o evidencia, no como verdad definitiva, salvo que sea validado contra código, pruebas o documentación vigente.

## 10. Fase 6 — Detección de stack y arquitectura

El orquestador debe identificar:

- lenguaje principal;
- frameworks;
- gestor de paquetes;
- scripts disponibles;
- entrypoints;
- estructura frontend/backend;
- servicios;
- base de datos;
- ORM o query layer;
- sistema de autenticación;
- variables de entorno requeridas;
- integraciones externas;
- sistema de build;
- sistema de testing;
- deployment;
- relación con Replit;
- relación con GitHub.

Fuentes típicas:

- `package.json`
- `requirements.txt`
- `pyproject.toml`
- `tsconfig.json`
- `vite.config.*`
- `drizzle.config.*`
- `.replit`
- `Dockerfile`
- `server/`
- `client/`
- `src/`
- `app/`
- `scripts/`
- `shared/`
- archivos de configuración.

## 11. Fase 7 — Mapa inicial de código

Debe generarse o actualizarse `CODE_CONTEXT_MAP.md`.

Debe incluir:

- estructura principal de carpetas;
- entrypoints;
- módulos críticos;
- rutas o endpoints;
- componentes principales;
- modelos de datos;
- servicios;
- configuraciones;
- scripts relevantes;
- tests;
- integraciones;
- archivos sensibles;
- zonas que requieren revisión de OpenCode;
- zonas que Continue puede revisar para contexto;
- zonas que no deben tocarse sin autorización.

## 12. Fase 8 — Contrastación documentación-código

Debe ejecutarse una contrastación inicial entre documentación y código.

Preguntas mínimas:

- ¿La documentación describe archivos que existen?
- ¿Los endpoints documentados existen?
- ¿Los scripts documentados siguen vigentes?
- ¿La arquitectura descrita coincide con carpetas reales?
- ¿Los modelos de datos documentados coinciden con schemas/migraciones?
- ¿Las variables documentadas coinciden con manifiestos o configuración?
- ¿Hay documentación antigua no vigente?
- ¿Hay código importante sin documentación?
- ¿Hay comentarios en código que contradicen documentación formal?
- ¿Hay decisiones implícitas que deberían documentarse?

Resultado esperado:

- documentación vigente;
- documentación obsoleta;
- documentación incierta;
- código sin documentación;
- riesgos de desalineación;
- recomendaciones de actualización.

## 13. Fase 9 — Alertas críticas iniciales

Debe crearse o actualizarse:

`docs/projects/<project-id>/CRITICAL_ALERTS.md`

Debe registrar:

- errores graves conocidos;
- comandos prohibidos;
- archivos que no deben modificarse;
- configuraciones sensibles;
- restricciones de seguridad;
- dependencias delicadas;
- rutas críticas;
- riesgos de producción;
- instrucciones que siempre deben consultarse;
- bugs recurrentes;
- decisiones irreversibles;
- patrones peligrosos.

Cada alerta debe incluir:

- `alert_id`
- `severity`
- `scope`
- `trigger`
- `description`
- `do_not_do`
- `required_check`
- `source`
- `last_verified`
- `applies_to`

## 14. Fase 10 — Lecciones locales del proyecto

Debe crearse o actualizarse:

`docs/projects/<project-id>/LESSONS_LOCAL.md`

Debe contener aprendizajes propios del proyecto objetivo.

No debe confundirse con `docs/lessons/GLOBAL_LESSONS_LEARNED.md`.

Una lección local puede escalarse a lección transversal si:

- aplica a múltiples proyectos;
- corrige una regla del orquestador;
- mejora routing;
- previene errores repetibles;
- representa una buena práctica general;
- no depende exclusivamente de preferencias o condiciones específicas del proyecto.

## 15. Fase 11 — Estado de sincronización

Debe crearse o actualizarse:

`docs/projects/<project-id>/SYNC_STATUS.md`

Debe indicar:

- fecha de habilitación;
- último análisis;
- última sincronización;
- rama activa;
- último commit revisado;
- origen del proyecto;
- estado local;
- estado remoto;
- relación con Replit;
- relación con GitHub;
- documentos actualizados;
- índices actualizados;
- pendientes;
- riesgos de desincronización.

## 16. Fase 12 — Reglas de acceso de Continue y OpenCode

El proyecto debe definir cómo acceden los agentes.

### Continue

Puede acceder a nivel 1, 2 o 3 según necesidad contextual.

Continue debe poder acceder a nivel 3 cuando sea necesario para:

- construir contexto aterrizado;
- contrastar documentación con código;
- detectar contexto embebido;
- preparar handoffs sólidos;
- identificar archivos relevantes;
- detectar riesgos de desalineación.

Continue no debe ejecutar ni modificar sin autorización expresa.

### OpenCode

Puede acceder a nivel 1, 2 o 3 según necesidad técnica.

OpenCode debe validar:

- suficiencia del handoff;
- contexto real del repositorio;
- archivos relevantes;
- riesgos;
- agente/modelo adecuado;
- necesidad de escalamiento.

OpenCode puede modificar, ejecutar o depurar únicamente bajo permisos y autorización correspondientes.

## 17. Fase 13 — Mini-orquestación inicial

Todo proyecto habilitado debe declarar cómo se coordinarán Continue y OpenCode.

Flujo base:

`Continue contextualiza → OpenCode valida → Continue refina si aplica → OpenCode planifica/ejecuta/escala`

Para complejidad media en adelante debe contemplarse retroalimentación bidireccional.

No debe existir conversación indefinida entre agentes.

Debe definirse:

- máximo de ciclos;
- agente responsable de contexto;
- agente responsable de ejecución;
- criterios de bloqueo;
- criterios de escalamiento;
- rol del usuario.

## 18. Fase 14 — Registro de handoffs

Debe crearse o actualizarse:

`docs/projects/<project-id>/HANDOFF_LOG.md`

Debe registrar:

- fecha;
- agente emisor;
- agente receptor;
- objetivo;
- archivos revisados;
- decisión;
- modelo utilizado;
- resultado;
- riesgos;
- pendientes;
- si hubo escalamiento;
- si hubo autorización humana.

## 19. Fase 15 — Criterio de habilitación completa

Un proyecto objetivo se considera habilitado cuando existen:

- registro en `PROJECT_REGISTRY.md`;
- carpeta en `docs/projects/<project-id>/`;
- `PROJECT_PROFILE.md`;
- `CONTEXT_INDEX.md`;
- `CODE_CONTEXT_MAP.md`;
- `DOCUMENTATION_AUDIT.md`;
- `CRITICAL_ALERTS.md`;
- `LESSONS_LOCAL.md`;
- `SYNC_STATUS.md`;
- `HANDOFF_LOG.md`;
- identificación de stack;
- documentación explícita indagada;
- contexto embebido preliminar indagado;
- contraste documentación-código inicial;
- reglas de acceso definidas;
- estado de sincronización registrado.

## 20. Reglas de seguridad

Durante la habilitación no se debe:

- imprimir secrets;
- copiar `.env`;
- versionar credenciales;
- exponer tokens;
- registrar valores reales de variables de entorno;
- copiar dumps de base de datos;
- procesar datos personales reales sin autorización;
- ejecutar migraciones;
- ejecutar deployment;
- cambiar ramas sin autorización;
- hacer push sin autorización;
- modificar configuración productiva sin aprobación.

Se pueden registrar nombres de variables de entorno, nunca sus valores.

## 21. Automatización futura

El protocolo debe evolucionar hacia una ejecución transparente para el usuario.

El usuario no debería:

- copiar handoffs entre Continue y OpenCode;
- seleccionar modelos manualmente;
- decidir agentes manualmente;
- recordar alertas;
- transferir contexto entre herramientas.

El sistema debe tender a:

- identificar proyecto objetivo;
- cargar registro;
- consultar índices;
- consultar alertas;
- consultar lecciones;
- activar Continue para contexto;
- activar OpenCode para validación;
- seleccionar agente/modelo;
- pedir autorización si aplica;
- ejecutar o escalar;
- documentar resultado;
- actualizar sincronización.

## 22. Salidas esperadas del protocolo

Al finalizar ENABLE_TARGET_PROJECT, debe existir un reporte de habilitación con:

- proyecto habilitado;
- modo de habilitación;
- ruta local;
- remoto;
- stack;
- documentación encontrada;
- contexto embebido encontrado;
- riesgos;
- alertas;
- brechas documentación-código;
- estado de sincronización;
- próximos pasos;
- agente recomendado para primera tarea;
- modelo/línea sugerida para primera validación.

## 23. Regla superior

No se debe iniciar trabajo operativo sobre un proyecto objetivo si el proyecto no ha sido habilitado o si no se ha declarado explícitamente que se trabajará bajo contexto incompleto.

Si el contexto está incompleto, los agentes deben actuar en modo diagnóstico, no en modo ejecución.
