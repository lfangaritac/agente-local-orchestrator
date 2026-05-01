# MODEL_ROUTING.md

## 1. PROPÓSITO

Definir cómo el sistema selecciona modelos, agentes y capas de validación dentro de la arquitectura híbrida:

- Continue
- OpenCode
- modelos locales vía Ollama
- Replit
- modelos premium

El objetivo es maximizar calidad, reducir costo externo, evitar redundancia y mantener trazabilidad.

---

## 2. PRINCIPIO CENTRAL

El sistema no decide por preferencia de modelo.

Decide según:

- fase del ciclo operativo;
- complejidad;
- criticidad;
- impacto arquitectónico;
- necesidad de acceso a código real;
- necesidad de validación externa;
- costo/beneficio.

---

## 3. MODELOS DISPONIBLES

### 3.1 Qwen Coder

Modelo local principal para desarrollo diario.

Usar para:

- generación de código base;
- Flask, React, SQL, scripts;
- refactor menor;
- explicaciones técnicas;
- primer análisis de errores.

---

### 3.2 DeepSeek Coder

Modelo local de apoyo técnico.

Usar para:

- revisión de código;
- debugging más exigente;
- análisis de errores;
- validación técnica;
- comparación de alternativas de implementación.

---

### 3.3 Mistral

Modelo local generalista.

Usar para:

- análisis funcional;
- documentación;
- síntesis;
- estructuración de contexto;
- redacción de handoffs.

---

## 4. ROUTING POR FASE DEL CICLO

### 4.1 Construcción de contexto

Responsable principal:

- Continue

Modelo sugerido:

- Mistral o Qwen

Función:

- recorrer documentación viva;
- identificar información relevante;
- construir ventana depurada;
- evitar enviar contexto completo innecesariamente.

OpenCode no debe recibir todo el contexto inicial, sino un paquete técnico filtrado cuando sea necesario.

---

### 4.2 Planeación inicial

Responsable principal:

- Continue

Modelo sugerido:

- Mistral para análisis funcional;
- Qwen para planificación técnica simple;
- DeepSeek si hay complejidad técnica.

Salida esperada:

- interpretación de la solicitud;
- alcance;
- plan inicial;
- riesgos;
- archivos o componentes probablemente afectados.

---

### 4.3 Validación técnica interna

Responsable principal:

- OpenCode

Modelo sugerido:

- DeepSeek como principal;
- Qwen como apoyo.

Función:

- revisar factibilidad técnica contra el repositorio;
- identificar archivos afectados;
- validar dependencias;
- detectar riesgos de implementación.

OpenCode debe trabajar con:

- plan inicial;
- contexto técnico filtrado;
- archivos relevantes;
- estructura real del repositorio.

---

### 4.4 Concertación Continue + OpenCode

Responsables:

- Continue
- OpenCode

Objetivo:

- combinar criterio funcional y técnico;
- resolver inconsistencias;
- producir una única salida consolidada.

Regla:

- no se permite ejecutar con dos planes divergentes;
- debe existir un plan unificado antes de la ejecución.

---

### 4.5 Validación con Replit

Usar Replit cuando:

- exista impacto arquitectónico;
- haya incertidumbre;
- el cambio sea mediano o grande;
- se requiera validación del entorno Replit;
- el usuario lo solicite.

Replit debe recibir:

- objetivo;
- contexto filtrado;
- plan unificado;
- preguntas concretas.

Respuesta esperada:

- aprobación breve; o
- observaciones puntuales de valor.

No se busca una reescritura completa salvo que se solicite expresamente.

---

### 4.6 Ejecución

Responsable principal:

- OpenCode

Modelo sugerido:

- Qwen para implementación estándar;
- DeepSeek para implementación compleja.

Función:

- modificar archivos;
- generar diffs;
- ejecutar comandos autorizados;
- correr pruebas;
- reportar resultados.

---

### 4.7 Validación local

Responsables:

- OpenCode
- Continue

Modelo sugerido:

- DeepSeek para revisión técnica;
- Mistral para documentación y síntesis.

Validar:

- errores;
- pruebas;
- coherencia;
- impacto;
- cumplimiento del requerimiento.

---

### 4.8 Validación post-ejecución con Replit

Usar cuando:

- hubo cambios significativos;
- hubo cambios arquitectónicos;
- se requiere conformidad con entorno Replit;
- el usuario lo pide.

Enviar:

- objetivo inicial;
- resumen de cambios;
- diff relevante;
- pruebas ejecutadas;
- dudas concretas.

---

### 4.9 Documentación y memoria

Responsable principal:

- Continue

Modelo sugerido:

- Mistral

Actualizar:

- PROJECT_CONTEXT.md;
- handoffs;
- decisiones;
- errores;
- aprendizajes;
- próximos pasos.

---

## 5. ESCALAMIENTO PREMIUM

Activar modelos premium cuando:

- los modelos locales no ofrecen confianza suficiente;
- Replit identifica riesgo o insuficiencia;
- hay alta criticidad;
- la tarea requiere razonamiento profundo;
- el usuario lo solicita.

El usuario debe poder elegir la opción premium disponible.

El escalamiento debe registrar:

- motivo;
- contexto enviado;
- resultado;
- decisión adoptada.

---

## 6. REGLAS DE CONTEXTO

### 6.1 Continue

Puede acceder al contexto amplio del proyecto para:

- entender intención;
- sintetizar;
- construir ventanas depuradas;
- preparar handoffs.

### 6.2 OpenCode

No debe recibir contexto completo por defecto.

Debe recibir:

- contexto técnico filtrado;
- plan validado;
- archivos relevantes;
- instrucciones claras;
- criterios de prueba.

### 6.3 Replit y premium

Nunca deben recibir contexto completo sin filtrado.

Solo deben recibir:

- contexto mínimo suficiente;
- datos sanitizados;
- objetivo concreto;
- pregunta o validación específica.

---

## 7. REGLAS DE OPTIMIZACIÓN

El sistema debe evitar:

- enviar la misma tarea a varios modelos sin propósito;
- generar análisis redundantes;
- usar Replit para tareas triviales;
- usar premium sin justificación;
- cargar contexto innecesario.

El sistema debe priorizar:

- contexto depurado;
- validación puntual;
- ejecución controlada;
- documentación continua.

---

## 8. CRITERIOS RÁPIDOS DE SELECCIÓN

| Caso | Modelo / Agente recomendado |
|---|---|
| Código simple | Qwen |
| Código complejo | DeepSeek |
| Documentación | Mistral |
| Síntesis funcional | Mistral |
| Plan inicial | Continue + Qwen/Mistral |
| Validación técnica | OpenCode + DeepSeek |
| Ejecución local | OpenCode |
| Validación arquitectónica | Replit |
| Alta criticidad | Replit + Premium |
| Handoff a Replit | Mistral / Continue |

---

## 9. PRINCIPIO FINAL

El valor del sistema no depende de usar siempre el modelo más fuerte.

Depende de usar el modelo correcto, en la fase correcta, con el contexto correcto y con trazabilidad suficiente.

---