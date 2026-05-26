# SECURITY_POLICY.md

---

## 1. PROPÓSITO

Definir reglas de seguridad para el sistema de agentes híbridos:

- Continue (orquestador)
- OpenCode (ejecutor)
- Replit (validador híbrido)
- Modelos premium (escalamiento)

El objetivo es:

- proteger datos
- evitar ejecuciones riesgosas
- garantizar trazabilidad
- controlar acceso a recursos

---

## 2. PRINCIPIO FUNDAMENTAL

El sistema opera bajo:

> **mínimo privilegio + control explícito + trazabilidad completa**

---

## 3. NIVELES DE ACCESO

---

### 3.1 Acceso local

Incluye:

- archivos del proyecto
- scripts
- ejecución de código
- sistema operativo

Riesgos:

- eliminación de archivos
- ejecución maliciosa
- modificación no controlada

---

### 3.2 Acceso externo (Replit / APIs)

Incluye:

- envío de contexto
- validación externa
- ejecución remota (potencial)

Riesgos:

- fuga de información
- exposición de código
- dependencia externa

---

### 3.3 Acceso sensible

Incluye:

- credenciales
- tokens
- APIs
- configuraciones críticas

Riesgo crítico:

- compromiso total del sistema

---

## 4. REGLAS GENERALES

---

### 4.1 Nunca exponer secretos

Prohibido enviar a:

- Replit
- modelos premium
- logs externos

Datos como:

- API keys
- passwords
- tokens
- credenciales

---

### 4.2 Sanitización obligatoria

Antes de cualquier envío externo:

- eliminar datos sensibles
- anonimizar información
- filtrar contexto

---

### 4.3 Confirmación para acciones críticas

Requieren validación explícita del usuario:

- eliminar archivos
- modificar múltiples archivos
- ejecutar scripts peligrosos
- instalar dependencias globales

---

## 5. CONTROL DE EJECUCIÓN (OPENCODE)

---

### 5.1 Acciones permitidas

- lectura de archivos
- escritura controlada
- ejecución de código validado
- pruebas locales

---

### 5.2 Acciones restringidas

Requieren validación:

- acceso a red
- ejecución de comandos del sistema
- manipulación masiva de archivos

---

### 5.3 Acciones prohibidas

- borrar sistema completo
- modificar configuraciones críticas del OS
- acceder a rutas fuera del proyecto

---

### 5.4 Codex en VS Code (modo integrado)

Si el usuario autoriza explícitamente que Codex asuma contexto + codificación (edición/validación) en una misma sesión, Codex debe operar con las mismas restricciones de seguridad del sistema:

- no tocar ni exponer secrets/tokens/credenciales;
- no versionar `.env`;
- no ejecutar acciones destructivas sin autorización;
- no hacer migraciones ni deployment sin autorización;
- respetar el alcance autorizado y detenerse ante umbrales.

---


## 6. CONTROL DE CONTEXTO

---

### 6.1 Regla de exposición

Nunca enviar contexto completo a:

- Replit
- modelos premium

Solo enviar:

- contexto filtrado
- información relevante
- datos mínimos necesarios

---

### 6.2 Clasificación de información

- Pública → libre uso
- Técnica → filtrada
- Sensible → restringida
- Crítica → nunca sale

---

## 7. SEGURIDAD EN ESCALAMIENTO

---

### 7.1 Escalamiento a Replit

Debe cumplir:

- contexto reducido
- sin secretos
- objetivo claro

---

### 7.2 Escalamiento a modelos premium

Requiere:

- validación del usuario
- justificación técnica
- filtrado de contexto

---

## 8. AISLAMIENTO

---

### 8.1 Entornos separados

- desarrollo local
- pruebas
- producción

Nunca mezclar:

- datos reales con pruebas
- credenciales en código

---

### 8.2 Archivos sensibles

Deben estar en:

- .env (no versionado)
- variables de entorno

---

## 9. AUDITORÍA Y TRAZABILIDAD

---

### 9.1 Registro obligatorio

Cada acción relevante debe registrar:

- instrucción recibida
- plan generado
- acción ejecutada
- resultado
- validación

---

### 9.2 Logs

Deben incluir:

- errores
- decisiones
- cambios

---

### 9.3 No registrar

Nunca incluir en logs:

- contraseñas
- tokens
- datos sensibles

---

## 10. CONTROL HUMANO

---

### 10.1 Usuario como autoridad final

El usuario puede:

- aprobar acciones
- rechazar ejecuciones
- forzar escalamiento

---

### 10.2 Confirmación obligatoria

Para:

- cambios críticos
- operaciones destructivas
- acceso externo sensible

---

## 11. FALLBACK Y CONTENCIÓN

---

### 11.1 En caso de error

El sistema debe:

- detener ejecución
- no escalar automáticamente
- solicitar validación

---

### 11.2 En caso de duda

Regla:

> NO ejecutar → consultar

---

## 12. PRINCIPIOS DE SEGURIDAD

---

1. Menos acceso = más control  
2. Menos contexto externo = menos riesgo  
3. Más validación = menos errores  
4. Más trazabilidad = más confianza  

---

## 13. EVOLUCIÓN

Este documento debe:

- ajustarse con experiencia real
- incorporar nuevos riesgos
- adaptarse a nuevas herramientas
- fortalecerse continuamente

---