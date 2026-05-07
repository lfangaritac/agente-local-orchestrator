"""
schemas.py

Esquemas de herramientas MCP del orquestador local.

Fase v0.1:
- Solo diagnóstico.
- Sin comandos arbitrarios.
- Sin edición de código.
- Sin secrets.
- Sin deployment.
- Sin migraciones.
"""

from __future__ import annotations


TOOL_SCHEMAS = [
    {
        "name": "orchestrator_preflight",
        "description": "Ejecuta el preflight transversal del orquestador y devuelve fuentes, alertas, lecciones y estado del contexto.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "select_agent_model",
        "description": "Selecciona de forma diagnóstica agente/modelo según escenario, riesgo y volumen.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "scenario": {
                    "type": "string",
                    "description": "Escenario de routing. Ejemplo: context-validation, planning, architecture, debugging, security, handoff.",
                    "default": "context-validation",
                },
                "risk": {
                    "type": "string",
                    "description": "Nivel de riesgo.",
                    "enum": ["low", "medium", "high", "critical"],
                    "default": "medium",
                },
                "volume": {
                    "type": "string",
                    "description": "Volumen de información.",
                    "enum": ["low", "medium", "high"],
                    "default": "medium",
                },
                "user_premium": {
                    "type": "boolean",
                    "description": "Indica si el usuario pidió explícitamente premium.",
                    "default": False,
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "build_handoff_package",
        "description": "Crea un paquete de handoff con fuentes, alertas y lecciones incorporadas desde el preflight.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "default": "orchestrator",
                },
                "source_agent": {
                    "type": "string",
                    "default": "continue",
                },
                "target_agent": {
                    "type": "string",
                    "default": "context-validator",
                },
                "scenario": {
                    "type": "string",
                    "default": "context-validation",
                },
                "risk": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "default": "medium",
                },
                "volume": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "default": "high",
                },
                "objective": {
                    "type": "string",
                    "description": "Objetivo del handoff.",
                },
            },
            "required": ["objective"],
            "additionalProperties": False,
        },
    },
    {
        "name": "run_diagnostic_flow",
        "description": "Ejecuta el flujo diagnóstico semiautomático. Puede invocar OpenCode real si with_opencode=true.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "default": "orchestrator",
                },
                "scenario": {
                    "type": "string",
                    "default": "context-validation",
                },
                "risk": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "default": "medium",
                },
                "volume": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "default": "high",
                },
                "objective": {
                    "type": "string",
                    "default": "Flujo diagnóstico MCP v0.1.",
                },
                "with_opencode": {
                    "type": "boolean",
                    "description": "Invoca OpenCode real en modo diagnóstico controlado.",
                    "default": False,
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "show_latest_run",
        "description": "Muestra el último flujo o un run específico con RUN_SUMMARY y TRACE.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "Run ID opcional. Si se omite, muestra el último run.",
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "run_opencode_from_handoff",
        "description": "Invoca OpenCode real desde un handoff existente en modo diagnóstico controlado.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "Run ID del handoff existente.",
                },
                "agent": {
                    "type": "string",
                    "default": "context-validator",
                },
                "model": {
                    "type": "string",
                    "default": "opencode-go/qwen3.6-plus",
                },
                "prompt": {
                    "type": "string",
                    "description": "Prompt diagnóstico para OpenCode. No debe pedir edición ni ejecución de comandos.",
                },
            },
            "required": ["run_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "start_opencode_from_handoff_async",
        "description": "Lanza OpenCode real desde un handoff existente en segundo plano y devuelve inmediatamente estado started.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "Run ID del handoff existente."
                },
                "agent": {
                    "type": "string",
                    "default": "context-validator"
                },
                "model": {
                    "type": "string",
                    "default": "opencode-go/qwen3.6-plus"
                },
                "prompt": {
                    "type": "string",
                    "description": "Prompt diagnóstico para OpenCode. No debe pedir edición ni ejecución de comandos."
                }
            },
            "required": ["run_id"],
            "additionalProperties": False
        }
    },
    {
        "name": "get_run_status",
        "description": "Devuelve un resumen compacto de un run, incluyendo si OpenCode registró salida en agent_outputs, raw_outputs, TRACE.md y RUN_SUMMARY.md.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "Run ID opcional. Si se omite, usa el run más reciente."
                }
            },
            "additionalProperties": false
        }
    }
]


