# CONTEXT_SYNC_PROTOCOL.md

## 1. Propósito

Definir cómo el orquestador local `C:\Agente` mantiene actualizado el contexto de cada proyecto objetivo después de su habilitación inicial.

Este protocolo asegura que la documentación, los índices, las alertas, las lecciones aprendidas, los handoffs, el mapa de código y el estado de sincronización sigan reflejando el estado real del proyecto objetivo a medida que evoluciona.

## 2. Principio central

El contexto de un proyecto objetivo no es estático.

Debe sincronizarse de forma continua cuando ocurran cambios relevantes en documentación, código, arquitectura, dependencias, reglas, errores, pruebas, decisiones, handoffs, ramas, commits, Replit, GitHub o modelos/agentes utilizados.

El orquestador debe evitar que Continue, OpenCode, Replit o modelos premium operen sobre contexto obsoleto, incompleto o no contrastado.

## 3. Alcance

Este protocolo aplica a:

- proyectos locales;
- proyectos Replit;
- proyectos GitHub;
- proyectos existentes;
- proyectos nuevos;
- proyectos importados;
- proyectos sincronizados en varios entornos;
- proyectos con documentación explícita;
- proyectos con contexto embebido en código;
- proyectos con documentación generada por agentes.

## 4. Archivos sujetos a sincronización

Por cada proyecto objetivo, deben mantenerse actualizados, cuando existan:

- `docs/projects/<project-id>/PROJECT_PROFILE.md`;
- `docs/projects/<project-id>/PROJECT_RESUME.md`;
- `docs/projects/<project-id>/CURRENT_FRONTIER.md`;
- `docs/projects/<project-id>/ERRORS_AND_FIXES.md`;
- `docs/projects/<project-id>/CONTEXT_INDEX.md`;
- `docs/projects/<project-id>/CODE_CONTEXT_MAP.md`;
- `docs/projects/<project-id>/DOCUMENTATION_AUDIT.md`;
- `docs/projects/<project-id>/CRITICAL_ALERTS.md`;
- `docs/projects/<project-id>/LESSONS_LOCAL.md`;
- `docs/projects/<project-id>/SYNC_STATUS.md`;
- `docs/projects/<project-id>/HANDOFF_LOG.md`.

También pueden actualizarse dentro del proyecto objetivo:

- `PROJECT_CONTEXT.md`;
- `docs/context/*`;
- `docs/decisions/*`;
- `docs/handoffs/*`;
- `docs/test_reports/*`;
- `docs/critical_alerts/*`;
- documentación técnica propia del proyecto.

## 5. Eventos que disparan sincronización

Debe evaluarse sincronización cuando ocurra cualquiera de estos eventos:

- habilitación inicial del proyecto;
- cambio de rama;
- pull o actualización remota;
- commit relevante;
- push relevante;
- cambio de estructura de carpetas;
- cambio de dependencias;
- cambio de scripts;
- cambio de configuración;
- cambio de endpoints;
- cambio de modelos de datos;
- cambio de migraciones;
- cambio de autenticación;
- cambio de seguridad;
- cambio de variables de entorno requeridas;
- generación de handoff;
- recepción de feedback de otro agente;
- resultado de prueba;
- error corregido;
- debugging relevante;
- escalamiento a Zen;
- escalamiento a modelo premium;
- handoff a Replit;
- validación en Replit;
- deployment;
- cierre de tarea importante;
- identificación de alerta crítica;
- identificación de lección aprendida;
- detección de documentación obsoleta;
- detección de código importante no documentado.

## 6. Tipos de sincronización

### 6.1 Sincronización ligera

Aplica cuando hay cambios menores, documentación simple o validaciones sin impacto estructural.

Debe actualizar, si corresponde:

- `SYNC_STATUS.md`;
- `HANDOFF_LOG.md`;
- reportes de prueba;
- fecha de última revisión.

### 6.2 Sincronización contextual

Aplica cuando cambia o se descubre contexto relevante.

Debe actualizar:

- `CONTEXT_INDEX.md`;
- `DOCUMENTATION_AUDIT.md`;
- `SYNC_STATUS.md`;
- referencias a fuentes;
- estado de vigencia.

### 6.3 Sincronización técnica

Aplica cuando cambia el código, arquitectura, rutas, dependencias, scripts, endpoints, modelos o tests.

Debe actualizar:

- `CODE_CONTEXT_MAP.md`;
- `DOCUMENTATION_AUDIT.md`;
- `CONTEXT_INDEX.md`;
- `SYNC_STATUS.md`.

### 6.4 Sincronización crítica

Aplica cuando se detectan riesgos, errores graves, restricciones, comandos prohibidos, configuraciones sensibles o lecciones de alto impacto.

Debe actualizar:

- `CRITICAL_ALERTS.md`;
- `docs/alerts/GLOBAL_CRITICAL_ALERTS.md`, si aplica transversalmente;
- `LESSONS_LOCAL.md`;
- `docs/lessons/GLOBAL_LESSONS_LEARNED.md`, si aplica transversalmente;
- `SYNC_STATUS.md`.

### 6.5 Sincronización de escalamiento

Aplica cuando hay Go → Zen continuidad, Zen económico, Zen premium o Replit.

Debe actualizar:

- `HANDOFF_LOG.md`;
- paquete de escalamiento;
- `SYNC_STATUS.md`;
- reporte de decisión;
- alertas si surgieron riesgos;
- lecciones si el caso genera aprendizaje transversal.

## 7. Responsabilidades por agente

### 7.1 Continue

Continue debe:

- detectar si la tarea requiere sincronización contextual;
- revisar documentación y código cuando sea necesario para contexto;
- identificar fuentes revisadas y no revisadas;
- detectar documentación posiblemente obsoleta;
- detectar contexto embebido relevante;
- proponer actualizaciones a índices;
- preparar handoffs con estado de contexto;
- no afirmar vigencia sin contraste suficiente.

### 7.2 OpenCode

OpenCode debe:

- validar el estado real del repositorio;
- confirmar si los índices reflejan el código;
- detectar cambios técnicos relevantes;
- actualizar o proponer actualización de mapas técnicos;
- registrar pruebas, diffs y resultados;
- bloquear ejecución si el contexto crítico está desactualizado;
- preparar paquetes de escalamiento cuando corresponda.

### 7.3 Replit

Replit debe aportar validación de entorno real cuando aplique:

- runtime;
- preview;
- deployment;
- secrets reales;
- variables de entorno;
- integración externa;
- comportamiento remoto.

### 7.4 Usuario

El usuario debe autorizar:

- sincronizaciones que impliquen cambios sensibles;
- exposición de contexto a modelos premium;
- cambios destructivos;
- deployment;
- uso de costos premium;
- decisiones estratégicas.

## 8. Preflight de sincronización

Antes de tareas de complejidad media, alta o crítica, debe verificarse:

- proyecto objetivo identificado;
- `PROJECT_REGISTRY.md` actualizado;
- `SYNC_STATUS.md` existente;
- fecha de última sincronización;
- rama activa;
- último commit revisado;
- alertas críticas consultadas;
- lecciones relevantes consultadas;
- contexto documental revisado;
- contexto de código revisado si aplica;
- documentación-código contrastados si la tarea depende de ello.

Si este preflight falla, el agente debe operar en modo diagnóstico, no en modo ejecución.

## 9. Estado de sincronización

`SYNC_STATUS.md` debe incluir:

- project_id;
- ruta local;
- repositorio remoto;
- rama activa;
- último commit revisado;
- última sincronización;
- tipo de sincronización;
- agente que sincronizó;
- archivos actualizados;
- archivos pendientes;
- contexto explícito revisado;
- contexto embebido revisado;
- código contrastado;
- alertas consultadas;
- lecciones consultadas;
- riesgos de desincronización;
- próximos pasos.

## 10. Regla de documentación distribuida

La sincronización no debe eliminar ni reemplazar fuentes originales del proyecto objetivo.

Debe crear índices y síntesis trazables.

Cada entrada relevante debe conservar:

- source_path;
- context_type;
- summary;
- confidence;
- last_verified;
- validated_against_code;
- status;
- applies_to.

## 11. Regla de vigencia

Toda información sincronizada debe clasificarse como:

- vigente;
- incierta;
- obsoleta;
- pendiente de verificación;
- deprecated;
- inferida;
- validada contra código.

No se debe presentar información inferida como verdad confirmada.

## 12. Regla de alertas críticas

Cuando se detecte una alerta crítica, el agente debe decidir si corresponde a:

- alerta local del proyecto;
- alerta global del orquestador;
- ambas.

Debe registrarse con:

- alert_id;
- severity;
- scope;
- trigger;
- description;
- do_not_do;
- required_check;
- source;
- last_verified;
- applies_to.

## 13. Regla de lecciones aprendidas

Cuando una interacción revele una lección, el agente debe clasificarla como:

- local del proyecto;
- transversal del orquestador;
- no persistente.

Solo debe escalarse a lección transversal si:

- aplica a más de un proyecto;
- mejora reglas de orquestación;
- mejora routing;
- previene errores recurrentes;
- representa buena práctica general;
- no depende de una preferencia específica del proyecto.

## 14. Sincronización después de handoff

Todo handoff relevante debe registrar:

- agente emisor;
- agente receptor;
- objetivo;
- archivos revisados;
- contexto usado;
- suficiencia contextual;
- errores detectados;
- feedback recibido;
- modelo usado;
- decisión;
- resultado;
- pendientes.

Si OpenCode devuelve feedback a Continue, ese feedback debe alimentar el siguiente handoff o quedar registrado como limitación.

## 15. Sincronización después de pruebas

Después de pruebas relevantes debe registrarse:

- comando o validación;
- agente que ejecutó;
- resultado;
- errores;
- causa raíz si se conoce;
- archivos afectados;
- decisiones;
- si generó alerta crítica;
- si generó lección aprendida;
- próximos pasos.

## 16. Sincronización después de debugging

Después de debugging relevante debe registrarse:

- síntoma;
- diagnóstico;
- causa raíz;
- solución aplicada o recomendada;
- archivos revisados;
- archivos modificados;
- pruebas realizadas;
- riesgos;
- prevención futura;
- alerta o lección si aplica.

## 17. Sincronización antes de escalamiento premium

Antes de escalar a Zen premium o modelo premium debe verificarse:

- contexto actualizado;
- alertas críticas consultadas;
- lecciones relevantes consultadas;
- paquete canónico de escalamiento generado;
- ausencia de secrets;
- motivo de escalamiento;
- salida esperada;
- autorización del usuario si hay costo o sensibilidad.

## 18. Sincronización antes de Replit

Antes de handoff a Replit debe verificarse:

- entorno local revisado;
- contexto del proyecto actualizado;
- variables requeridas identificadas solo por nombre;
- secrets no expuestos;
- comandos seguros definidos;
- criterios de éxito;
- acciones prohibidas;
- riesgos residuales;
- motivo de validación remota.

## 19. Bloqueo por contexto desactualizado

El agente debe bloquear ejecución y operar en modo diagnóstico si:

- no identifica proyecto objetivo;
- no existe registro;
- faltan alertas críticas;
- el estado de sincronización es desconocido;
- la documentación clave está obsoleta;
- hay contradicción no resuelta entre documentación y código;
- el handoff no declara fuentes;
- se requiere código pero no se revisó código;
- se requiere premium pero no existe paquete canónico;
- hay riesgo de secrets.

## 20. Automatización futura

Este protocolo debe evolucionar hacia automatización transparente:

- detección automática de eventos de sincronización;
- actualización automática de índices;
- generación automática de handoffs;
- selección automática de agente/modelo;
- creación automática de paquetes de escalamiento;
- consulta automática de alertas y lecciones;
- solicitud de autorización solo cuando aplique;
- documentación automática de resultados relevantes.

## 21. Regla superior

El contexto sincronizado debe ser suficiente, trazable, vigente y proporcional a la tarea.

Si el contexto no cumple esas condiciones, el sistema debe operar en modo diagnóstico y no en modo ejecución.
