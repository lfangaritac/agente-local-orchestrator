# PROJECT_RESUME - analisis-impacto-privacidad

## Resumen operativo

La Plataforma AIP guia al usuario en la documentacion del ciclo de vida de datos personales y genera salidas legales/tecnicas: autorizaciones, acuerdos, diagnosticos de terceros, conceptos de riesgo e informes AIP.

## Modulos funcionales relevantes

- Ciclo de vida: contexto, recoleccion, almacenamiento, relacionamiento, procesamiento y disposicion.
- Debida diligencia: politicas de terceros y riesgos.
- Riesgos: flujo guiado de 9 pasos con perspectiva dual Titular/Organizacion.
- Coberturas: autorizaciones, acuerdos e informes.
- Registro de casos AIP multi-iniciativa.
- Asistente IA por seccion, creacion de tarjetas y generacion documental.

## Arquitectura

- `client/src/App.tsx` centraliza estado global y navegacion por secciones.
- `client/src/components/section-view.tsx` es un componente critico de gran tamano para tarjetas/secciones.
- `server/index.ts` arranca Express.
- `server/routes.ts` registra rutas API.
- `server/storage.ts` maneja persistencia.
- `server/ai.ts` concentra prompts y llamadas OpenAI.
- `server/docx-generator.ts` genera documentos/informes.
- `shared/schema.ts` define schema Drizzle/PostgreSQL.

## Baseline conocido

- Validacion historica `2026-05-04`: `npm run build` OK.
- Validacion historica `2026-05-04`: `npm run check` falla con 146 errores TypeScript en 18 archivos.
- No ejecutar remediacion TS masiva sin plan por bloques.

