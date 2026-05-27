# SEMANTIC_CONTEXT_GATE_PROTOCOL.md

## Proposito

Evitar que una tarea dependa de la memoria o disciplina del agente para revisar contexto relevante.

El Semantic Context Gate es un paso read-only previo a Plan profundo o Build que convierte la instruccion del usuario en senales de busqueda y devuelve un paquete compacto de referencias. No carga todo el proyecto: encuentra documentos y reglas probablemente relevantes por coincidencia semantica ligera, rutas, identificadores y palabras de dominio.

## Cuando aplica

Aplicar antes de:

- cambios de codigo o documentacion de proyecto;
- diagnosticos sobre bugs, regresiones, incidentes o diffs;
- instrucciones con identidad, seguridad, datos, integraciones externas, runtime real, DB, migraciones, deploy o Replit;
- cualquier tarea donde una regla local del proyecto pueda cambiar la interpretacion de la instruccion.

No es necesario para respuestas conversacionales simples sin accion sobre repositorios.

## Entrada minima

- `project_id`.
- instruccion original del usuario.
- opcional: archivos cambiados, diff resumido, rutas mencionadas o modulo sospechoso.

## Algoritmo

1. Inferir senales desde la instruccion:
   - terminos relevantes;
   - identificadores (`wa_from`, `userId`, `identity_context`, nombres de endpoints, tablas, rutas);
   - nombres de archivos, modulos, carpetas o dominios;
   - verbos de accion que aumenten riesgo (`corrige`, `implementa`, `push`, `migra`, `deploy`, `diagnostica`).

2. Construir el corpus compacto:
   - índice semántico canónico del proyecto: `docs/projects/<project_id>/SEMANTIC_TAG_INDEX.md`;
   - indices locales del orquestador para el proyecto: `docs/projects/<project_id>/*.md`;
   - documentacion principal registrada en `PROJECT_REGISTRY.md`;
   - `README.md`, `replit.md`, `docs/**/*.md`, `.agents/**/*.md` del repo objetivo cuando exista ruta local;
   - excluir secrets, `.env`, artefactos voluminosos, logs y salidas generadas.

3. Puntuar referencias:
   - primero bloques de `SEMANTIC_TAG_INDEX.md` que coincidan con señales de la instrucción;
   - boost por coincidencia en ruta/nombre de archivo;
   - boost por identificadores exactos;
   - conteo de terminos en contenido;
   - snippets cortos con lineas relevantes, no documentos completos.

4. Emitir decision:
   - `ok`: hay fuentes suficientes para seguir;
   - `needs_context_review`: hay fuentes candidatas, deben leerse antes de editar;
   - `blocked_missing_context`: la tarea implica Build o riesgo medio+ y no se encontro contexto suficiente.

5. Antes de editar:
   - leer las referencias top del gate;
   - declarar fuentes usadas en el cierre;
   - si aparece una regla local contradictoria, esta prevalece sobre inferencias generales.

## Presupuesto de contexto

El gate debe ser compacto por defecto:

- maximo recomendado: 8 referencias;
- snippets cortos, no volcados;
- ampliar profundidad solo si las fuentes top indican riesgo o ambiguedad real.

## Herramienta local

Implementacion inicial:

```powershell
python scripts\semantic_context_gate.py --project embajadores-backend --instruction "corrige envio por wa_from userId" --output text
```

Salida esperada: estado, terminos inferidos, referencias top, snippets y decision de suficiencia.

El índice semántico se construye/actualiza con:

```powershell
python scripts\project_context_indexer.py --project embajadores-backend --apply
```

`--apply` es explícito: sin ese flag, la herramienta solo reporta si habría cambios.

## Regla operativa

Este gate no reemplaza el juicio del agente; lo fuerza a buscar contexto relevante antes de actuar. Si el gate no encuentra fuentes y la tarea no es trivial, el agente debe detener Build o ampliar lectura read-only antes de modificar archivos.
