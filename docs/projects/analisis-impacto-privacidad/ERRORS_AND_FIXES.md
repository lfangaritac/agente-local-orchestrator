# ERRORS_AND_FIXES - analisis-impacto-privacidad

## Errores / deuda conocidos

### TypeScript baseline - 146 errores

- source: `docs/test_reports/baseline_validacion_local_aip_20260504.md`
- source: `docs/test_reports/opencode_diagnostico_typescript_aip_20260504.md`
- status: vigente hasta nueva validacion.
- summary: `npm run check` falla con 146 errores TypeScript en 18 archivos; `npm run build` habia pasado en la validacion historica.
- familias:
  - tipos duplicados o divergentes entre `App.tsx`, `section-view.tsx` y componentes relacionados.
  - propiedades faltantes en modelos de recoleccion, relacionamiento, almacenamiento, procesamiento y disposicion.
  - errores de iteracion de `Set` asociados a configuracion TypeScript.
  - imports/modulos faltantes o inconsistentes.
  - props UI incompatibles.
  - errores puntuales en rutas e integraciones de servidor.
- recomendacion historica: primera microtarea segura es revisar `tsconfig.json` (`target: ES2020`, `downlevelIteration: true`) para reducir TS2802.
- prohibicion operativa: no aplicar casts masivos ni unificacion forzada de interfaces sin plan.

### NPM audit historico

- source: `docs/test_reports/baseline_validacion_local_aip_20260504.md`
- status: pendiente de revalidacion.
- summary: `npm audit` reporto 13 vulnerabilidades (1 baja, 3 moderadas, 9 altas); no se ejecuto `npm audit fix`.

