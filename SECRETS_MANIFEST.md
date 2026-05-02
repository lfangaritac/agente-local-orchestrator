# SECRETS_MANIFEST.md

## Propósito

Inventario de variables de entorno y secrets del orquestador local.

Este repositorio base no debe almacenar secrets reales ni exigir variables de proyectos específicos por defecto.

Las credenciales de cada proyecto activado —por ejemplo Azure, Resend, OpenAI, Voiceflow, bases de datos o servicios externos— deben documentarse y validarse dentro del repositorio específico de ese proyecto.

## Variables opcionales del orquestador local

| Variable | Servicio | Requerida | Entorno | Prueba de validación | Observaciones |
|---|---|---:|---|---|---|
| OPENAI_API_KEY | OpenAI | No | local | `python scripts/check_env.py` | Solo si se usa OpenAI desde el orquestador |
| ANTHROPIC_API_KEY | Anthropic | No | local | `python scripts/check_env.py` | Solo si se usa Anthropic desde el orquestador |
| GITHUB_TOKEN | GitHub | No | local | operación GitHub controlada | No usar si basta con Git autenticado |
| REPLIT_API_TOKEN | Replit | No | local | operación Replit controlada | Solo si se automatizan acciones vía API |
| OLLAMA_HOST | Ollama | No | local | prueba de conexión local | Solo si se usa Ollama en host distinto al default |

## Reglas

- No incluir valores reales.
- No versionar `.env`.
- No copiar secrets de proyectos cliente a este repositorio base.
- No imprimir valores sensibles en logs.
- Las variables de cada proyecto deben documentarse en el `SECRETS_MANIFEST.md` del proyecto correspondiente.
