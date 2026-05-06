# DOCUMENTATION_CODE_ALIGNMENT_PROTOCOL.md

## 1. Propósito

Definir el proceso obligatorio de contrastación entre documentación y código real dentro de cada proyecto objetivo habilitado en el orquestador local `C:\Agente`.

Este protocolo busca evitar que Continue, OpenCode, Replit o modelos de escalamiento trabajen sobre documentación obsoleta, incompleta, aspiracional, contradictoria o desconectada del estado real del código.

## 2. Principio central

La documentación y el código son fuentes de contexto complementarias.

La documentación explica intención, decisiones, reglas, arquitectura, casos de uso y operación.

El código revela implementación real, comportamiento efectivo, dependencias, estructura, restricciones técnicas, validaciones y decisiones implícitas.

Ninguna de las dos fuentes debe asumirse como verdad absoluta sin contraste cuando la tarea dependa de precisión técnica, funcional, arquitectónica o de seguridad.

## 3. Cuándo aplicar la contrastación

La contrastación documentación-código debe aplicarse:

- al habilitar un proyecto objetivo;
- antes de cambios relevantes;
- antes de planificación arquitectónica;
- antes de refactor transversal;
- antes de debugging complejo;
- antes de cambios de seguridad;
- antes de cambios de autenticación o permisos;
- antes de cambios en base de datos;
- antes de cambios en endpoints;
- antes de escalamiento premium;
- antes de handoff a Replit;
- después de cambios estructurales;
- cuando se detecta documentación antigua;
- cuando se detecta código importante no documentado;
- cuando una instrucción del usuario depende de reglas de negocio;
- cuando hay contradicción entre agentes;
- cuando Continue u OpenCode detectan contexto incompleto;
- cuando hay riesgo de repetir errores previos.

## 4. Niveles de contrastación

### 4.1 Nivel A — Validación documental básica

Se revisa si la documentación existe, está ubicada, tiene fecha o indicios de vigencia y menciona componentes presentes en el proyecto.

Aplica a tareas de baja complejidad.

### 4.2 Nivel B — Contraste estructural

Se compara documentación contra estructura real del repositorio.

Debe revisar:

- carpetas;
- entrypoints;
- scripts;
- configuración;
- rutas principales;
- módulos;
- dependencias;
- archivos críticos.

Aplica a tareas de complejidad media.

### 4.3 Nivel C — Contraste funcional

Se compara documentación contra comportamiento implementado.

Debe revisar:

- endpoints;
- componentes;
- servicios;
- controladores;
- modelos de datos;
- validaciones;
- flujos funcionales;
- tests;
- errores;
- integraciones.

Aplica a tareas de complejidad media-alta o alta.

### 4.4 Nivel D — Contraste profundo o crítico

Se realiza análisis multiarchivo, trazado de flujos, revisión de dependencias, análisis de seguridad, debugging, revisión de diffs o validación de arquitectura.

Aplica a tareas críticas, sensibles, premium, de producción o de alto impacto.

## 5. Fuentes documentales a revisar

Según el proyecto, deben considerarse:

- `README.md`;
- `PROJECT_CONTEXT.md`;
- archivos en `/docs`;
- ADRs;
- handoffs;
- test reports;
- decisiones;
- documentación de arquitectura;
- documentación funcional;
- documentación de API;
- documentación de casos de uso;
- instrucciones de agentes;
- prompts;
- archivos de reglas;
- documentación de Replit;
- documentación de seguridad;
- documentación de base de datos;
- notas de despliegue;
- notas de configuración;
- documentación histórica.

## 6. Fuentes de código y configuración a revisar

Según el proyecto, deben considerarse:

- estructura de carpetas;
- entrypoints;
- `package.json`;
- `requirements.txt`;
- `pyproject.toml`;
- `tsconfig.json`;
- `vite.config.*`;
- `drizzle.config.*`;
- `.replit`;
- `Dockerfile`;
- scripts;
- componentes;
- servicios;
- controladores;
- rutas;
- endpoints;
- modelos;
- schemas;
- migraciones;
- seeds;
- tests;
- fixtures;
- middlewares;
- validaciones;
- archivos compartidos;
- configuración de build;
- configuración de deployment;
- integraciones externas.

## 7. Contexto embebido a detectar

Durante la contrastación, los agentes deben buscar contexto embebido en:

- comentarios;
- TODO;
- FIXME;
- nombres de funciones;
- nombres de clases;
- nombres de componentes;
- nombres de rutas;
- nombres de carpetas;
- constantes;
- mensajes de error;
- validaciones;
- nombres de variables significativos;
- prompts dentro del código;
- convenciones repetidas;
- dependencias;
- pruebas;
- seeds;
- schemas;
- migraciones.

El contexto embebido debe registrarse como evidencia, inferencia o alerta, según su nivel de confirmación.

## 8. Preguntas obligatorias de contrastación

Todo proceso de contrastación debe responder, según aplique:

- ¿La documentación describe archivos que existen?
- ¿Los archivos documentados siguen vigentes?
- ¿Los endpoints documentados existen?
- ¿Los scripts documentados siguen vigentes?
- ¿La arquitectura documentada coincide con la estructura real?
- ¿Los modelos de datos documentados coinciden con schemas o migraciones?
- ¿Las variables de entorno documentadas coinciden con manifiestos o configuración?
- ¿Las reglas de negocio documentadas están implementadas?
- ¿Hay código relevante no documentado?
- ¿Hay documentación que describe comportamiento inexistente?
- ¿Hay comentarios en código que contradicen documentación formal?
- ¿Hay tests que revelan comportamiento no documentado?
- ¿Hay decisiones implícitas que deben documentarse?
- ¿Hay documentación obsoleta que pueda inducir errores?
- ¿Hay alertas críticas relacionadas?
- ¿Hay lecciones aprendidas aplicables?

## 9. Clasificación de hallazgos

Cada hallazgo debe clasificarse como:

- alineado;
- parcialmente alineado;
- desalineado;
- obsoleto;
- no documentado;
- documentado pero no implementado;
- implementado pero no documentado;
- inferido;
- pendiente de verificación;
- crítico.

## 10. Metadata mínima por hallazgo

Cada hallazgo relevante debe registrar:

- `finding_id`;
- `source_document`;
- `source_code`;
- `summary`;
- `classification`;
- `confidence`;
- `impact`;
- `risk_level`;
- `recommended_action`;
- `requires_human_review`;
- `requires_opencode_validation`;
- `requires_continue_refinement`;
- `requires_premium_review`;
- `last_verified`.

## 11. Resultado esperado

La contrastación debe producir o actualizar:

- `DOCUMENTATION_AUDIT.md`;
- `CONTEXT_INDEX.md`;
- `CODE_CONTEXT_MAP.md`;
- `CRITICAL_ALERTS.md`, si aplica;
- `LESSONS_LOCAL.md`, si aplica;
- `SYNC_STATUS.md`;
- reporte de prueba o análisis, si aplica.

## 12. Rol de Continue

Continue puede realizar contrastación documental y de código hasta nivel 3 cuando sea necesario para construir contexto preciso.

Continue debe:

- revisar documentación;
- revisar código cuando sea necesario;
- identificar fuentes revisadas;
- identificar fuentes no revisadas;
- detectar contradicciones;
- detectar contexto embebido;
- preparar síntesis;
- proponer actualización de índices;
- preparar handoff para OpenCode;
- declarar incertidumbre;
- no actuar como autoridad final de implementación.

Continue no debe:

- inventar alineación;
- asumir que documentación está vigente;
- declarar inexistencia sin verificación;
- ejecutar cambios críticos;
- reemplazar la validación técnica de OpenCode.

## 13. Rol de OpenCode

OpenCode debe validar técnicamente la contrastación cuando haya impacto operativo, código, ejecución, debugging, arquitectura, seguridad, diffs o cambios.

OpenCode debe:

- verificar archivos reales;
- revisar código en profundidad;
- validar o corregir hallazgos de Continue;
- identificar riesgos técnicos;
- preparar plan de acción;
- ejecutar cambios solo con autorización;
- generar diffs;
- ejecutar pruebas permitidas;
- preparar paquete de escalamiento si corresponde.

OpenCode no debe:

- aceptar sin verificación una contrastación de Continue;
- ejecutar con hallazgos críticos pendientes;
- ignorar alertas críticas;
- exponer secrets;
- modificar documentación o código sensible sin autorización.

## 14. Regla de discrepancia

Si documentación y código se contradicen, el agente no debe elegir automáticamente una fuente.

Debe clasificar la discrepancia y determinar:

- si el código refleja el comportamiento vigente;
- si la documentación refleja una intención no implementada;
- si ambos están desactualizados;
- si falta revisión humana;
- si se requiere prueba;
- si se requiere validación de Replit;
- si se requiere escalamiento premium.

## 15. Regla de código sin documentación

Si se detecta código relevante sin documentación, debe registrarse como hallazgo.

Debe evaluarse si requiere:

- actualización de `CONTEXT_INDEX.md`;
- actualización de `CODE_CONTEXT_MAP.md`;
- documentación funcional;
- documentación técnica;
- alerta crítica;
- lección local;
- lección transversal.

## 16. Regla de documentación obsoleta

Si se detecta documentación obsoleta, debe clasificarse como:

- obsoleta confirmada;
- posiblemente obsoleta;
- contradictoria;
- pendiente de verificación.

No debe eliminarse sin autorización.

Debe registrarse su riesgo y recomendar acción.

## 17. Regla de comentarios en código

Los comentarios en código pueden contener contexto valioso, pero deben tratarse con cautela.

Deben clasificarse como:

- vigente;
- útil pero no verificado;
- contradictorio;
- obsoleto;
- crítico;
- pendiente de revisión.

Los comentarios que documenten restricciones, prohibiciones, errores graves o decisiones sensibles deben considerarse candidatos para `CRITICAL_ALERTS.md`.

## 18. Regla de alertas críticas

Si la contrastación detecta una restricción, prohibición, error recurrente, riesgo de producción, comando peligroso, dependencia sensible o patrón de fallo, debe evaluarse si corresponde actualizar:

- `docs/projects/<project-id>/CRITICAL_ALERTS.md`;
- `docs/alerts/GLOBAL_CRITICAL_ALERTS.md`.

## 19. Regla de lecciones aprendidas

Si la contrastación revela una mejora reutilizable para el orquestador, debe evaluarse si corresponde actualizar:

- `docs/projects/<project-id>/LESSONS_LOCAL.md`;
- `docs/lessons/GLOBAL_LESSONS_LEARNED.md`.

Solo debe elevarse a global si la lección es transversal y alineada con buenas prácticas.

## 20. Preflight obligatorio

Antes de iniciar contrastación nivel C o D, debe verificarse:

- proyecto objetivo identificado;
- nivel de acceso permitido;
- alertas críticas consultadas;
- lecciones relevantes consultadas;
- archivos principales ubicados;
- rama activa conocida;
- estado de sincronización conocido;
- restricciones de seguridad;
- necesidad o no de autorización humana.

## 21. Bloqueo por insuficiencia

El agente debe detenerse o actuar en modo diagnóstico si:

- no identifica el proyecto objetivo;
- no puede acceder a fuentes mínimas;
- no puede revisar código necesario;
- no puede determinar vigencia;
- hay contradicción crítica;
- hay riesgo de secrets;
- la tarea exige nivel D y no hay autorización;
- el handoff carece de fuentes.

## 22. Salida mínima de un reporte de contrastación

Todo reporte de contrastación debe incluir:

- objetivo;
- proyecto objetivo;
- nivel de contrastación;
- documentación revisada;
- código revisado;
- contexto embebido identificado;
- hallazgos;
- discrepancias;
- riesgos;
- alertas propuestas;
- lecciones propuestas;
- recomendaciones;
- siguiente agente recomendado;
- modelo/línea sugerida;
- si requiere escalamiento;
- estado de suficiencia contextual.

## 23. Relación con sincronización

Todo hallazgo relevante debe alimentar `CONTEXT_SYNC_PROTOCOL.md`.

La contrastación no termina al producir un reporte. Debe actualizar el estado de contexto del proyecto.

## 24. Regla superior

Ningún proyecto objetivo debe considerarse suficientemente comprendido si su documentación relevante no ha sido contrastada, en la medida necesaria, contra código, configuración, tests o comportamiento real.
