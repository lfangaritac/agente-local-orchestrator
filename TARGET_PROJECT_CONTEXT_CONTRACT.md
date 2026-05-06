# TARGET_PROJECT_CONTEXT_CONTRACT.md

## 1. Propósito

Definir el contrato de contexto multi-proyecto del orquestador local `C:\Agente`.

Este contrato establece cómo el orquestador debe indagar, descubrir, registrar, indexar, contrastar, centralizar de forma funcional, referenciar y sincronizar el contexto documental, técnico, operativo y embebido de cada proyecto objetivo habilitado.

El contrato aplica a proyectos creados localmente, importados desde carpetas existentes, clonados desde GitHub, iniciados desde Replit, sincronizados desde Replit, nuevos, existentes con documentación previa, y existentes con documentación dispersa o embebida en código.

## 2. Principio central

`C:\Agente` no es un proyecto de aplicación ordinario. `C:\Agente` es el orquestador local maestro encargado de gobernar agentes, modelos, reglas, routing, documentación transversal, memoria operativa, registros, handoffs, alertas, lecciones aprendidas y sincronización multi-proyecto.

Cada proyecto objetivo conserva su propio contexto vivo. El orquestador no debe reemplazarlo ni reducirlo a un único archivo simplificado.

El orquestador debe indagar el contexto del proyecto objetivo, descubrir documentación explícita, descubrir contexto embebido en código, contrastar documentación contra código, registrar fuentes relevantes, indexar contexto consultable, centralizar síntesis funcionales, referenciar archivos fuente, mantener trazabilidad, actualizar sincronización, activar alertas críticas, y alimentar lecciones aprendidas transversales cuando corresponda.

## 3. Distinción obligatoria entre orquestador y proyecto objetivo

Todo análisis debe distinguir entre el proyecto orquestador y el proyecto objetivo.

El proyecto orquestador corresponde a `C:\Agente` / `agente-local-orchestrator`.

Contiene:

- reglas transversales;
- protocolos de activación;
- reglas de Continue;
- reglas de OpenCode;
- routing de modelos;
- documentación de arquitectura de agentes;
- registro de proyectos;
- alertas globales;
- lecciones aprendidas transversales;
- handoffs agregados;
- protocolos de sincronización;
- criterios de escalamiento;
- documentación del sistema de orquestación.

El proyecto objetivo corresponde al repositorio, carpeta, workspace o aplicación que está siendo analizado, desarrollado, corregido, documentado o sincronizado por el orquestador.

Puede ser:

- un proyecto Replit;
- un proyecto local;
- un repositorio GitHub;
- una carpeta importada;
- un proyecto nuevo;
- un proyecto existente con documentación previa.

El proyecto objetivo contiene:

- código fuente;
- documentación propia;
- configuraciones;
- tests;
- scripts;
- comentarios;
- decisiones;
- handoffs;
- errores históricos;
- reglas de negocio;
- arquitectura real;
- dependencias;
- endpoints;
- componentes;
- modelos de datos;
- prompts o flujos propios;
- notas técnicas;
- documentación generada por otros agentes.

## 4. Regla de no confusión de identidad

Los agentes no deben inventar ni asumir el nombre del proyecto objetivo.

Si el proyecto objetivo no está confirmado, deben declarar:

`Proyecto objetivo no confirmado.`

Si detectan nombres posibles en archivos, carpetas o documentación, deben clasificarlos como:

`posible alias no confirmado`

No deben convertir un alias, carpeta, comentario, nombre de prueba o referencia parcial en identidad formal del proyecto.

## 5. Contexto distribuido e índice centralizado

La arquitectura adopta un modelo híbrido:

`fuentes distribuidas originales + índices centralizados consultables + síntesis curadas por capas + referencias trazables`

Esto significa que:

- la documentación original del proyecto objetivo no se elimina;
- los comentarios útiles permanecen en el código;
- los README, docs, schemas, tests y configuraciones siguen siendo fuentes primarias;
- el orquestador genera índices y síntesis para recuperación eficiente;
- toda síntesis debe conservar referencia a sus fuentes;
- ningún índice debe ocultar que existen fuentes adicionales no procesadas;
- ningún `PROJECT_CONTEXT.md` debe entenderse como reemplazo total del conocimiento distribuido.

## 6. Contexto explícito del proyecto objetivo

Se considera contexto explícito todo contenido documental producido intencionalmente para describir el proyecto, sus decisiones, operación, arquitectura o reglas.

Esto incluye:

- README;
- archivos Markdown;
- documentación en `/docs`;
- ADRs;
- handoffs;
- test reports;
- instrucciones de agentes;
- prompts;
- archivos de reglas;
- documentación de APIs;
- comentarios de configuración;
- notas de despliegue;
- documentación de Replit;
- documentación de seguridad;
- documentación de base de datos;
- documentación funcional;
- documentación de casos de uso;
- documentación de arquitectura;
- reportes de errores;
- decisiones registradas.

## 7. Contexto embebido del proyecto objetivo

Se considera contexto embebido toda información relevante que no aparece necesariamente como documento formal, pero que está presente en el código o estructura de la solución.

Esto incluye:

- comentarios en código;
- nombres de funciones;
- nombres de clases;
- nombres de componentes;
- nombres de rutas;
- nombres de carpetas;
- TODO;
- FIXME;
- comentarios de migraciones;
- seeds;
- fixtures;
- schemas;
- tests;
- scripts;
- mensajes de error;
- constantes;
- validaciones;
- nombres de variables significativos;
- convenciones repetidas;
- prompts dentro del código;
- configuraciones;
- reglas de negocio implementadas pero no documentadas;
- dependencias que revelan capacidades o arquitectura.

El contexto embebido no debe tratarse como verdad absoluta. Debe ser contrastado contra código, documentación y comportamiento.

## 8. Niveles de acceso al código

El sistema reconoce tres niveles de acceso al código.

### 8.1 Nivel 1 — Contexto documental

Incluye lectura de documentación, reglas, handoffs, README, decisiones y reportes.

### 8.2 Nivel 2 — Contraste documentación-código

Incluye revisión de estructura, entrypoints, rutas, endpoints, scripts, configuraciones, dependencias y archivos clave para confirmar si la documentación refleja el estado real.

### 8.3 Nivel 3 — Análisis profundo de código

Incluye lectura multiarchivo, seguimiento de flujos, revisión de dependencias, validaciones, tests, errores, diffs, arquitectura, modelos de datos, componentes y relaciones técnicas.

Continue y OpenCode pueden acceder a nivel 3 cuando sea necesario, pero con responsabilidades distintas.

## 9. Rol de Continue con acceso nivel 3

Continue puede acceder a nivel 3 al código cuando sea necesario para construir contexto específico, contrastar documentación, detectar inconsistencias o preparar handoffs sólidos.

Continue puede:

- leer código;
- revisar estructura del repositorio;
- identificar archivos relevantes;
- contrastar documentación contra implementación;
- identificar comentarios útiles;
- detectar contexto embebido;
- construir mapas de contexto;
- detectar riesgos de desalineación;
- preparar handoffs;
- proponer agente OpenCode;
- sugerir línea/modelo según routing.

Continue no debe:

- actuar como ejecutor principal;
- modificar archivos sin instrucción explícita;
- ejecutar comandos sin autorización;
- resolver cambios complejos como autoridad final;
- reemplazar validación técnica de OpenCode;
- inventar contexto;
- asumir identidad del proyecto objetivo;
- declarar inexistencia de archivos sin verificación confiable.

## 10. Rol de OpenCode con acceso nivel 3

OpenCode puede acceder a nivel 3 para validación técnica, planificación, edición, debugging, revisión de diffs, pruebas y ejecución controlada.

OpenCode debe:

- validar handoffs de Continue;
- verificar contexto contra archivos reales;
- confirmar existencia de fuentes;
- clasificar escenario, riesgo y volumen;
- seleccionar agente especializado;
- seleccionar modelo o línea;
- decidir si el handoff es suficiente;
- planificar o ejecutar según autorización;
- generar diffs;
- ejecutar validaciones permitidas;
- preparar paquetes de escalamiento;
- devolver feedback estructurado a Continue cuando el contexto sea insuficiente.

OpenCode no debe:

- asumir que Continue tiene razón;
- ejecutar con handoff insuficiente;
- ignorar alertas críticas;
- modificar archivos sensibles sin autorización;
- exponer secrets;
- escalar por comodidad;
- omitir incertidumbre técnica.

## 11. Mini-orquestación bidireccional Continue ↔ OpenCode

La coordinación entre agentes no debe ser únicamente unidireccional.

El flujo base es:

`Continue contextualiza → OpenCode valida suficiencia → OpenCode devuelve hallazgos, correcciones o preguntas → Continue refina contexto o handoff → OpenCode planifica, ejecuta o escala.`

Para complejidad baja, puede bastar con:

`Continue → OpenCode`

Para complejidad media, debe existir al menos un ciclo:

`Continue → OpenCode → Continue → OpenCode`

Este ciclo aplica si OpenCode detecta falta de contexto, errores factuales o ambigüedad relevante.

Para complejidad alta, puede existir un máximo de dos ciclos antes de decisión humana o escalamiento.

Para complejidad crítica, debe intervenir:

`OpenCode + Zen premium + aprobación humana`

Continue organiza contexto, pero no decide ejecución crítica.

## 12. Responsabilidades de decisión

Continue decide:

- qué contexto logró reunir;
- qué fuentes revisó;
- qué fuentes no revisó;
- qué código contrastó;
- qué información falta;
- qué handoff propone;
- qué agente OpenCode sugiere;
- qué modelo/línea sugiere según routing.

OpenCode decide:

- si el handoff es suficiente;
- si hay errores factuales;
- si debe bloquearse la ejecución;
- qué agente especializado corresponde;
- qué modelo/línea usar;
- si Go basta;
- si se requiere Zen continuidad;
- si se requiere Zen económico;
- si se requiere Zen premium;
- si se requiere Replit;
- si debe devolver feedback a Continue.

El usuario decide:

- autorizaciones sensibles;
- costos premium;
- cambios destructivos;
- cambios de producción;
- despliegues;
- decisiones estratégicas;
- exposición o uso de secrets reales;
- acciones con impacto material.

## 13. Reglas preventivas de interacción entre agentes

Los agentes deben evitar:

- condescendencia;
- confirmación de premisas del usuario sin validación;
- colusión;
- asumir que otro agente tiene razón;
- inventar contexto;
- suavizar alertas críticas;
- omitir incertidumbre;
- escalar por comodidad;
- ejecutar sin suficiencia contextual;
- declarar archivos como inexistentes sin verificación;
- confundir Go con el lenguaje Go cuando el contexto se refiere a OpenCode Go;
- confundir Zen con una red, bus, framework o arquitectura técnica no documentada;
- inventar proyectos objetivo;
- mezclar reglas transversales con reglas específicas sin aclaración.

Los agentes deben promover:

- contradicción técnica fundada;
- colaboración con roles claros;
- trazabilidad;
- verificación cruzada;
- identificación de incertidumbre;
- foco en la instrucción del usuario;
- separación entre contexto, planificación, ejecución y revisión;
- consulta de alertas críticas;
- uso de lecciones aprendidas transversales;
- minimización de costo sin sacrificar calidad;
- escalamiento justificado;
- documentación de hallazgos relevantes.

## 14. Regla de visibilidad, existencia y falla de contexto

Si un archivo obligatorio no es visible para un agente, el agente no debe afirmar automáticamente que no existe.

Debe distinguir entre:

- visible;
- no visible desde este agente;
- visible en ruta alternativa;
- pendiente de verificación por otro agente;
- verificado como inexistente por herramienta confiable.

Si un archivo obligatorio para la tarea no es visible, debe tratarse como una falla de contexto.

Una falla de contexto puede resolverse mediante:

- revisión de ruta alternativa;
- consulta de índice;
- solicitud de reindexación;
- derivación a OpenCode;
- verificación de filesystem;
- aclaración humana.

No debe emitirse un handoff final si falta una fuente obligatoria y no se declara la limitación.

## 15. Alertas críticas

Cada proyecto objetivo debe contar con un archivo o sección de alertas críticas. El orquestador debe contar con alertas globales en:

`docs/alerts/GLOBAL_CRITICAL_ALERTS.md`

Las alertas críticas deben consultarse antes de tareas de complejidad media, alta o crítica.

Deben registrar:

- errores graves ya ocurridos;
- prohibiciones;
- restricciones de seguridad;
- decisiones irreversibles;
- patrones de código peligrosos;
- configuraciones que no deben tocarse;
- comandos prohibidos;
- dependencias sensibles;
- bugs recurrentes;
- riesgos de producción;
- aprendizajes críticos;
- instrucciones que siempre deben consultarse.

## 16. Lecciones aprendidas transversales

El orquestador debe mantener lecciones aprendidas transversales en:

`docs/lessons/GLOBAL_LESSONS_LEARNED.md`

Estas lecciones no deben ser preferencias específicas de un proyecto, salvo que representen reglas, protocolos, patrones o anti-patrones reutilizables.

Deben registrar:

- patrones de interacción agente-agente;
- errores frecuentes de Continue;
- errores frecuentes de OpenCode;
- cuándo escalar a premium;
- cuándo no escalar;
- reglas de seguridad refinadas;
- mejores formatos de handoff;
- mejores prácticas de documentación;
- patrones de debugging;
- anti-patrones de ejecución;
- aprendizajes sobre modelos;
- mejoras al routing;
- oportunidades de automatización.

Al cierre de tareas relevantes, los agentes deben evaluar:

- si la interacción revela una lección transversal;
- si corrige una regla del orquestador;
- si mejora el routing;
- si previene un error futuro;
- si debe agregarse como alerta crítica o lección aprendida.

## 17. Centralización funcional del contexto

La centralización debe ser funcional, no sustitutiva.

El orquestador puede crear, por cada proyecto objetivo, archivos como:

- `PROJECT_PROFILE.md`;
- `CONTEXT_INDEX.md`;
- `CODE_CONTEXT_MAP.md`;
- `DOCUMENTATION_AUDIT.md`;
- `CRITICAL_ALERTS.md`;
- `LESSONS_LOCAL.md`;
- `SYNC_STATUS.md`;
- `HANDOFF_LOG.md`.

Estos archivos no reemplazan automáticamente las fuentes originales.

Cada entrada relevante debe conservar:

- `source_path`;
- `context_type`;
- `summary`;
- `confidence`;
- `last_verified`;
- `validated_against_code`;
- `status`;
- `applies_to`.

## 18. Contrastación documentación-código

La contrastación debe aplicarse:

- al habilitar un proyecto;
- antes de cambios relevantes;
- después de cambios estructurales;
- antes de escalamiento premium;
- antes de handoff a Replit;
- cuando hay dudas entre documentación y comportamiento;
- cuando se detecta documentación antigua;
- cuando una tarea depende de reglas de negocio no verificadas.

Debe responder:

- si la documentación describe lo que el código hace;
- si el código implementa lo que la documentación afirma;
- qué está vigente;
- qué está obsoleto;
- qué está no documentado;
- qué comentarios del código contienen contexto útil;
- qué decisiones están implícitas pero no formalizadas.

## 19. Automatización transparente para el usuario

El objetivo final es que el usuario pueda permanecer en un solo punto de interacción.

El usuario no debería:

- copiar manualmente handoffs entre Continue y OpenCode;
- seleccionar manualmente modelos;
- decidir manualmente qué agente usar;
- recordar qué alertas consultar;
- transferir contexto entre herramientas.

El sistema debe tender a un flujo donde:

- el usuario solicita una tarea;
- el orquestador identifica el proyecto objetivo;
- consulta registro, contexto, alertas y lecciones;
- Continue prepara contexto;
- OpenCode valida suficiencia;
- Continue refina si aplica;
- OpenCode selecciona agente/modelo;
- OpenCode ejecuta o escala;
- el resultado se documenta;
- los índices/lecciones se actualizan.

El usuario interviene para:

- autorizar acciones sensibles;
- autorizar costos;
- aprobar cambios destructivos;
- confirmar ambigüedades;
- validar decisiones estratégicas.

## 20. Regla superior

Ningún agente debe actuar sobre un proyecto objetivo sin:

- identificar el proyecto objetivo;
- indagar su contexto documental;
- indagar su contexto embebido;
- contrastar lo relevante contra el código;
- consultar alertas críticas aplicables;
- revisar lecciones transversales pertinentes;
- declarar suficiencia contextual;
- respetar roles de mini-orquestación;
- justificar agente/modelo sugerido;
- registrar hallazgos relevantes.
