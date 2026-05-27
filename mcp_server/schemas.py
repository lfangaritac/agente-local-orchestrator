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
        "name": "semantic_context_gate",
        "description": "Gate read-only que infiere senales desde una instruccion y devuelve referencias compactas de contexto relevante del proyecto.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "project_id registrado en PROJECT_REGISTRY.md.",
                },
                "instruction": {
                    "type": "string",
                    "description": "Instruccion original del usuario.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximo de referencias a devolver.",
                    "default": 8,
                },
            },
            "required": ["project_id", "instruction"],
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
        "description": "Ejecuta el flujo diagnóstico semiautomático. Puede invocar OpenCode real si with_opencode=True.",
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
    }
,
    {
        "name": "create_and_dispatch_opencode_handoff",
        "description": "Crea un paquete de handoff, lo persiste en docs/agent_queue/inbox, inicializa TRACE.md y RUN_SUMMARY.md, y despacha OpenCode en segundo plano si está autorizado.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "default": "orchestrator",
                },
                "objective": {
                    "type": "string",
                    "description": "Objetivo del handoff.",
                },
                "handoff_body": {
                    "type": "string",
                    "description": "Cuerpo del handoff con detalles.",
                    "default": "",
                },
                "target_agent": {
                    "type": "string",
                    "description": "Agente destino, ej: builder, debugger, context-validator.",
                },
                "model": {
                    "type": "string",
                    "description": "Modelo sugerido, ej: opencode-go/kimi-k2.6",
                },
                "risk_level": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "default": "medium",
                },
                "scenario": {
                    "type": "string",
                    "default": "implementation",
                },
                "allowed_files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Archivos permitidos para el alcance.",
                    "default": [],
                },
                "validation_commands": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Comandos de validación sugeridos.",
                    "default": [],
                },
                "requires_authorization": {
                    "type": "boolean",
                    "description": "Si requiere autorización humana antes de despachar.",
                    "default": False,
                },
                "authorization_granted": {
                    "type": "boolean",
                    "description": "Si la autorización humana ya fue concedida.",
                    "default": False,
                },
                "auto_approve_permissions": {
                    "type": "boolean",
                    "description": "Habilita auto-aprobación de permisos de OpenCode (usa internamente --dangerously-skip-permissions). Default false. Solo para Build low-risk con allowed_files acotado.",
                    "default": False,
                },
                "build_authorized": {
                    "type": "boolean",
                    "description": "Marcador explícito: el usuario autorizó modo Build para esta ejecución (requerido si auto_approve_permissions=true).",
                    "default": False,
                },
                "user_authorized_build": {
                    "type": "boolean",
                    "description": "Señal explícita adicional: el usuario autorizó Build real con permisos autoaprobados (requerido si auto_approve_permissions=true).",
                    "default": False,
                },
            },
            "required": ["project_id", "objective", "target_agent", "model", "risk_level", "scenario"],
            "additionalProperties": False,
        },
    },
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
            "additionalProperties": False
        }
    },
    {
        "name": "check_opencode_run_status",
        "description": "Verifica de forma compacta si un run ya tiene salida de OpenCode registrada en agent_outputs, raw_outputs, TRACE.md y RUN_SUMMARY.md.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "Run ID que se desea verificar."
                }
            },
            "required": ["run_id"],
            "additionalProperties": False
        }
    },
    {
        "name": "run_health_check",
        "description": "Health check compacto de un run (missing/partial/healthy/failed/stale) sin abrir raw_outputs ni TRACE/RUN_SUMMARY completos.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "Run ID a chequear (requerido)."
                },
                "stale_minutes": {
                    "type": "integer",
                    "description": "Umbral en minutos para marcar stale cuando hay background meta sin outputs (default 15).",
                    "default": 15
                }
            },
            "required": ["run_id"],
            "additionalProperties": False
        }
    },
        {
        "name": "verify_master_files",
        "description": "Verifica físicamente la existencia e integridad SHA-256 de los archivos maestros críticos del orquestador.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "description": "Modo de salida. En MCP el default es compact-first.",
                    "enum": ["compact", "full"],
                    "default": "compact"
                },
                "paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Rutas relativas a ROOT para verificar. Si se omite, usa la lista maestra completa.",
                    "default": []
                }
            },
            "additionalProperties": False
        }
    },
    {
        "name": "operational_status",
        "description": "Diagnóstico operativo compact-first del orquestador (estado git, quick checks, master files, último run). Read-only.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "include_git_status": {
                    "type": "boolean",
                    "description": "Incluye resumen de git status --porcelain.",
                    "default": True,
                },
                "run_quick_checks": {
                    "type": "boolean",
                    "description": "Ejecuta scripts/run_local_checks.py --mode quick.",
                    "default": False,
                },
                "verify_master_files": {
                    "type": "boolean",
                    "description": "Verifica archivos maestros críticos.",
                    "default": True,
                },
            },
            "additionalProperties": False,
                },
    },
    {
        "name": "resolve_target_project",

        "description": "Resuelve el proyecto objetivo (por project_id/alias o por workspace_path) y devuelve un preflight compacto read-only para operar con instrucciones generales.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_query": {
                    "type": "string",
                    "description": "project_id, alias o nombre canónico a resolver desde PROJECT_REGISTRY.md.",
                    "default": "",
                },
                "workspace_path": {
                    "type": "string",
                    "description": "Ruta local del workspace/repo actual para inferencia best-effort (read-only).",
                    "default": "",
                },
                "projects_root": {
                    "type": "string",
                    "description": "Raíz local donde se esperan clones (solo para sugerir/ubicar suggested_local_path; read-only).",
                },
                "include_git": {
                    "type": "boolean",
                    "description": "Si true, intenta incluir un probe Git compacto cuando exista repo local.",
                    "default": True,
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "enable_target_project",
        "description": "Plan-first → Apply confirmado para habilitar proyectos nuevos/no registrados: valida inputs, detecta colisiones, propone/actualiza PROJECT_REGISTRY.md y crea scaffold en docs/projects/<project-id>/ (sin sobrescribir).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["plan", "apply"],
                    "default": "plan"
                },
                "confirm": {
                    "type": "boolean",
                    "description": "Confirmación explícita requerida para Apply.",
                    "default": False
                },
                "project_id": {
                    "type": "string",
                    "description": "ID canónico (a-z0-9._-; recomendado kebab-case)."
                },
                "nombre_canónico": {
                    "type": "string",
                    "description": "Nombre canónico (opcional).",
                    "default": ""
                },
                "aliases": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Aliases permitidos (opcional).",
                    "default": []
                },
                "repo_url": {
                    "type": "string",
                    "description": "URL del repo remoto (opcional).",
                    "default": ""
                },
                "local_path": {
                    "type": "string",
                    "description": "Ruta local del repo/workspace (opcional; no clona).",
                    "default": ""
                },
                "workspace_path": {
                    "type": "string",
                    "description": "Alias de local_path (opcional).",
                    "default": ""
                },
                "environment_type": {
                    "type": "string",
                    "description": "Tipo de entorno (local, replit-git, etc).",
                    "default": ""
                },
                "origen": {
                    "type": "string",
                    "description": "Origen (local|replit|github|importado|nuevo|unknown).",
                    "default": ""
                },
                "set_active_project": {
                    "type": "boolean",
                    "description": "Si true, fija active_project (sesión) tras Apply.",
                    "default": False
                },
                "test_mode": {
                    "type": "boolean",
                    "description": "Solo para tests internos: permite overrides dentro de .orchestrator_state/.",
                    "default": False
                },
                "registry_path": {
                    "type": "string",
                    "description": "(test_mode) Ruta a registry alterno dentro de .orchestrator_state/.",
                    "default": ""
                                },
                "docs_projects_root": {

                    "type": "string",
                    "description": "(test_mode) Root alterno para docs/projects dentro de .orchestrator_state/.",
                    "default": ""
                }
            },
            "additionalProperties": False
        }
    },
    {
        "name": "plan_general_instruction",

        "description": "Wrapper read-only que traduce una instrucción general en un plan compacto + siguiente frontera segura (encadena operational_status + resolve_target_project + select_agent_model).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "instruction": {
                    "type": "string",
                    "description": "Instrucción general del usuario (p.ej. 'Diagnostica este proyecto', 'Avanza hasta la siguiente frontera segura').",
                },
                "project_query": {
                    "type": "string",
                    "description": "project_id/alias/nombre del proyecto objetivo. Si se omite, usar workspace_path.",
                    "default": "",
                },
                "workspace_path": {
                    "type": "string",
                    "description": "Ruta local del workspace/repo actual para inferencia best-effort (read-only).",
                    "default": "",
                },
                "projects_root": {
                    "type": "string",
                    "description": "Raíz local donde se esperan clones (solo para sugerir/ubicar suggested_local_path; read-only).",
                },
                "include_git": {
                    "type": "boolean",
                    "description": "Si true, intenta incluir un probe Git compacto cuando exista repo local.",
                    "default": True,
                },
                "include_orchestrator_status": {
                    "type": "boolean",
                    "description": "Si true, ejecuta operational_status del orquestador para bloquear avances con git/master-files en mal estado.",
                    "default": True,
                },
                "include_preflight": {
                    "type": "boolean",
                    "description": "Si true, ejecuta orchestrator_preflight para verificar fuentes transversales mínimas.",
                    "default": True,
                },
                "include_semantic_context_gate": {
                    "type": "boolean",
                    "description": "Si true, ejecuta Semantic Context Gate read-only antes de sugerir edicion o dispatch.",
                    "default": True,
                },
            },
            "required": ["instruction"],
            "additionalProperties": False,
        },
    },
    {
        "name": "ingest_orchestrator_transfer",
        "description": "Ingiere el último handoff orchestrator_transfer_*.json (Shell bridge) y lo convierte en un Plan interno sin copy/paste (Plan-only; no activa Replit ni Build).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "handoff_json_path": {
                    "type": "string",
                    "description": "Ruta explícita al handoff JSON. Si se provee, se usa directamente.",
                    "default": "",
                },
                "handoff_dir": {
                    "type": "string",
                    "description": "Directorio donde buscar orchestrator_transfer_*.json. Default: <workspace_path>/docs/handoffs.",
                    "default": "",
                },
                "workspace_path": {
                    "type": "string",
                    "description": "Ruta local del workspace del proyecto donde se generó el handoff (read-only).",
                    "default": "",
                },
                "project_query": {
                    "type": "string",
                    "description": "project_id/alias/nombre del proyecto objetivo (si el handoff no lo trae).",
                    "default": "",
                },
                "allowed_channels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Canales permitidos (default: shell_bridge, replit_agent_chat).",
                },
                "max_candidates": {
                    "type": "integer",
                    "description": "Máximo de candidatos a considerar en handoff_dir (default 50).",
                    "default": 50,
                },
                "set_active_project": {
                    "type": "boolean",
                    "description": "Si true, fija active_project (sesión) cuando el proyecto esté confirmado.",
                    "default": True,
                },
                "include_git": {
                    "type": "boolean",
                    "description": "Si true, incluye probe Git (read-only) al resolver el proyecto.",
                    "default": True,
                },
                "include_orchestrator_status": {
                    "type": "boolean",
                    "description": "Si true, incluye operational_status del orquestador en el plan.",
                    "default": True,
                },
                "include_preflight": {
                    "type": "boolean",
                    "description": "Si true, incluye orchestrator_preflight en el plan.",
                    "default": True,
                },
                "include_semantic_context_gate": {
                    "type": "boolean",
                    "description": "Si true, incluye Semantic Context Gate en el plan.",
                    "default": True,
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "run_general_instruction_flow",
        "description": "Cierra el loop: instrucción general → plan → dispatch controlado (si es seguro) → seguimiento compact-first.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "instruction": {
                    "type": "string",
                    "description": "Instrucción general del usuario.",
                },
                "mode": {
                    "type": "string",
                    "description": "plan (no side-effects) o dispatch_if_safe (dispatch OpenCode Go solo si no requiere autorización).",
                    "enum": ["plan", "dispatch_if_safe"],
                    "default": "plan",
                },
                "project_query": {
                    "type": "string",
                    "description": "project_id/alias/nombre del proyecto objetivo. Si se omite, usar workspace_path.",
                    "default": "",
                },
                "workspace_path": {
                    "type": "string",
                    "description": "Ruta local del workspace/repo actual para inferencia best-effort (read-only).",
                    "default": "",
                },
                "projects_root": {
                    "type": "string",
                    "description": "Raíz local donde se esperan clones (solo para sugerir/ubicar suggested_local_path; read-only).",
                },
                "include_git": {
                    "type": "boolean",
                    "description": "Si true, intenta incluir un probe Git compacto cuando exista repo local.",
                    "default": True,
                },
                "include_orchestrator_status": {
                    "type": "boolean",
                    "description": "Si true, ejecuta operational_status del orquestador (read-only).",
                    "default": True,
                },
                "include_preflight": {
                    "type": "boolean",
                    "description": "Si true, ejecuta orchestrator_preflight.",
                    "default": True,
                },
                "include_semantic_context_gate": {
                    "type": "boolean",
                    "description": "Si true, ejecuta Semantic Context Gate read-only antes de sugerir edicion o dispatch.",
                    "default": True,
                },
                "authorize_onboarding_scaffold_write": {
                    "type": "boolean",
                    "description": "Autorización explícita para que run_general_instruction_flow cree el scaffold mínimo en docs/projects/<project-id>/ cuando el plan devuelva status=onboarding_required.",
                    "default": False,
                },
            },
            "required": ["instruction"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_active_project",
        "description": "Devuelve el proyecto activo (sesión) si existe. Vive en .orchestrator_state/ (gitignored).",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "set_active_project",
        "description": "Establece el proyecto activo (sesión) para soportar 'retomar'/'volver'. Escribe solo en .orchestrator_state/ (gitignored).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "project_id del proyecto activo."},
                "note": {"type": "string", "description": "Nota opcional (p.ej. por qué se activó).", "default": ""}
            },
            "required": ["project_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "sync_active_last_event_to_project_docs",
        "description": "Sincroniza referencias compactas desde .orchestrator_state/active_project.json:last_event hacia docs/projects/<project-id>/{PROJECT_RESUME.md,CURRENT_FRONTIER.md}. Dry-run por defecto; apply requiere autorización explícita.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "project_id opcional; si se omite, usa active_project.project_id.",
                    "default": "",
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "Si true, no escribe; reporta qué cambiaría. Default true.",
                    "default": True,
                },
                "apply": {
                    "type": "boolean",
                    "description": "Si true, escribe los bloques AUTO:last_event_refs (requiere dry_run=false).",
                    "default": False,
                },
                "update_files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Archivos a sincronizar: PROJECT_RESUME y/o CURRENT_FRONTIER.",
                    "default": ["PROJECT_RESUME", "CURRENT_FRONTIER"],
                },
                "allow_orchestrator": {
                    "type": "boolean",
                    "description": "Permite project_id=orchestrator (default false; no aplicable salvo justificación expresa).",
                    "default": False,
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "init_project_onboarding_scaffold",
        "description": "Crea (si falta) el scaffold documental mínimo en docs/projects/<project-id>/ (sin sobrescribir).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "project_id del proyecto a onboardear."},
                "dry_run": {"type": "boolean", "description": "Si true, solo reporta qué crearía.", "default": False}
            },
            "required": ["project_id"],
            "additionalProperties": False,
        },
    },
]


