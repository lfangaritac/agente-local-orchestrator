#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

CORE_FILES = {
    "AGENT_RULES.md": """# AGENT_RULES.md

## Propósito

Define las reglas generales de operación de los agentes del proyecto.

## Reglas base

1. Git, código real, pruebas, logs y documentación actualizada son la fuente verificable de verdad.
2. Continue actúa como copiloto operativo en VS Code.
3. OpenCode o el agente coder local actúa como ejecutor técnico cuando la tarea supera una edición menor.
4. Replit actúa como entorno de ejecución, validación, supervisión, despliegue o revisión avanzada.
5. Ningún agente debe exponer, registrar o versionar secrets reales.
6. Una tarea operativa debe tener un solo ejecutor principal.
7. Toda modificación relevante debe poder explicarse, probarse y versionarse.
""",

    "PROJECT_CONTEXT.md": """# PROJECT_CONTEXT.md

## Propósito

Contexto operativo persistente del proyecto.

Este archivo debe resumir la información mínima que Continue, OpenCode, Replit Agent o cualquier modelo de apoyo necesitan para trabajar correctamente sobre este repositorio.

## Proyecto

- Nombre:
- Objetivo:
- Tipo de aplicación:
- Stack principal:
- Entorno local:
- Entorno Replit:
- Repositorio GitHub:

## Arquitectura

Describir aquí los componentes principales del proyecto.

## Servicios externos

Registrar servicios como Azure, Resend, OpenAI, Voiceflow, bases de datos, almacenamiento, APIs de terceros u otros.

## Comandos relevantes

- Ejecutar proyecto:
- Ejecutar pruebas:
- Validar entorno: python scripts/check_env.py

## Reglas críticas

- No versionar secrets.
- Validar cambios localmente cuando aplique.
- Validar en Replit cuando el comportamiento dependa del entorno remoto.
- Actualizar documentación mínima cuando cambien arquitectura, comandos, dependencias o integraciones.
""",

    "REPLIT_HANDOFF.md": """# REPLIT_HANDOFF.md

## Propósito

Formato mínimo para preparar entregas hacia Replit o Replit Agent.

## Contexto del handoff

- Proyecto:
- Rama:
- Fecha:
- Objetivo:
- Problema o tarea:
- Archivos relevantes:
- Cambios recientes:
- Comandos ejecutados:
- Resultado esperado:

## Qué se necesita de Replit

- Validar ejecución remota:
- Revisar error del entorno:
- Probar deployment:
- Revisar arquitectura:
- Ejecutar debugging:
- Revisar integración externa:
- Otro:

## Servicios involucrados

- Servicio:
- Variables requeridas:
- Endpoint o prueba:
- Riesgo:

## Evidencia

- Logs:
- Errores:
- Pruebas:
- Pendientes:
""",

    "SECURITY_POLICY.md": """# SECURITY_POLICY.md

## Propósito

Política mínima de seguridad para operación local, agentes, Replit y servicios externos.

## Reglas obligatorias

1. No versionar secrets reales.
2. No imprimir valores sensibles en logs.
3. No subir .env, llaves privadas, certificados privados ni connection strings.
4. No ejecutar comandos destructivos sin autorización explícita.
5. No modificar deployments activos sin validación.
6. No compartir credenciales entre proyectos.
7. No usar agentes para acceder a recursos externos sin necesidad justificada.
8. Mantener separación entre entorno local, Replit y producción.

## Archivos sensibles que deben excluirse

- .env
- .env.*
- *.pem
- *.key
- *.p12
- *.sqlite
- *.db
- .venv/
- __pycache__/

## Secrets

Los valores reales deben vivir en Replit Secrets, variables de entorno locales seguras, gestor de secretos autorizado o configuración privada no versionada.
""",

    "MODEL_ROUTING.md": """# MODEL_ROUTING.md

## Propósito

Define cómo seleccionar modelo, agente o entorno según la fase del ciclo de trabajo.

## Regla general

Usar el recurso más eficiente que resuelva la tarea con calidad suficiente, sin escalar innecesariamente a Replit o modelos premium.

## Routing base

| Tipo de tarea | Herramienta sugerida | Observación |
|---|---|---|
| Explicación puntual | Continue | Usar contexto del proyecto |
| Edición menor | Continue | Validar diff |
| Revisión de código | Continue / modelo local coder | Según complejidad |
| Cambio multiarchivo | OpenCode / agente coder local | Generar diff y pruebas |
| Debugging de entorno Replit | Replit | Cuando dependa del entorno remoto |
| Deployment | Replit | Validar con secrets reales |
| Arquitectura crítica | Replit / modelo premium | Escalar si el impacto es alto |
| Seguridad sensible | modelo premium / revisión humana | No depender solo de modelo local |
| Documentación operativa | Continue | Mantener concisa y útil |

## Criterio de escalamiento

Escalar cuando el modelo local no tenga suficiente calidad, la tarea tenga alto impacto, se requiera entorno Replit real, se requiera validación de deployment o se requiera análisis de seguridad o arquitectura avanzada.
""",

    "PROJECT_ACTIVATION_PROTOCOL.md": """# PROJECT_ACTIVATION_PROTOCOL.md

## Propósito

Protocolo operativo mínimo para activar el sistema de agentes en un proyecto.

## Ciclo esperado

VS Code local -> Continue -> OpenCode o agente coder local -> Git/GitHub -> Replit -> pruebas, logs, documentación y handoff.

## Activación mínima

1. Crear núcleo documental.
2. Identificar stack.
3. Identificar secrets requeridos.
4. Crear SECRETS_MANIFEST.md.
5. Crear scripts/check_env.py.
6. Validar entorno.
7. Versionar cambios.
8. Probar en Replit cuando aplique.

## Criterio de éxito

El proyecto queda activado cuando puede ejecutarse el ciclo: definir tarea -> revisar contexto -> elegir agente/modelo -> ejecutar -> probar -> versionar -> validar en Replit.
""",

    "CONTINUE_USAGE_PROTOCOL.md": """# CONTINUE_USAGE_PROTOCOL.md

## Propósito

Guía operativa mínima para usar Continue dentro de VS Code.

## Archivos que Continue debe considerar

- AGENT_RULES.md
- PROJECT_CONTEXT.md
- MODEL_ROUTING.md
- SECURITY_POLICY.md
- REPLIT_HANDOFF.md
- PROJECT_ACTIVATION_PROTOCOL.md
- SECRETS_MANIFEST.md

## Prompts sugeridos

### Revisar contexto

Revisa AGENT_RULES.md, PROJECT_CONTEXT.md, MODEL_ROUTING.md y SECURITY_POLICY.md. Luego resume qué debes tener en cuenta antes de modificar este proyecto.

### Elegir modelo/agente

Según MODEL_ROUTING.md, clasifica esta tarea y dime si conviene resolverla con Continue, OpenCode, Replit o un modelo premium.

### Preparar tarea para OpenCode

Prepara una tarea estructurada para OpenCode con objetivo, alcance, archivos relevantes, restricciones, pruebas esperadas y formato de handoff.

### Preparar handoff para Replit

Usando REPLIT_HANDOFF.md, prepara un handoff compacto para Replit con el contexto mínimo necesario, cambios recientes, pruebas y pregunta concreta.

## Límites

Continue no debe inventar secrets, asumir comandos no verificados, hacer cambios multiarchivo complejos sin plan, modificar seguridad o despliegue sin revisión ni sustituir pruebas reales.
"""
}

SENSITIVE_GITIGNORE_LINES = [
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.sqlite",
    "*.db",
    ".venv/",
    "__pycache__/",
]

ENV_PATTERNS = [
    re.compile(r"os\.getenv\([\"']([A-Z0-9_]+)[\"']"),
    re.compile(r"os\.environ\.get\([\"']([A-Z0-9_]+)[\"']"),
    re.compile(r"os\.environ\[[\"']([A-Z0-9_]+)[\"']\]"),
    re.compile(r"process\.env\.([A-Z0-9_]+)"),
    re.compile(r"process\.env\[[\"']([A-Z0-9_]+)[\"']\]"),
    re.compile(r"getenv\([\"']([A-Z0-9_]+)[\"']\)"),
]

IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".next",
    "dist",
    "build",
    ".cache",
    ".pytest_cache",
}

TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".env",
    ".example",
    ".md",
    ".sh",
    ".bash",
    ".zsh",
}


def run_command(args):
    try:
        result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)
        output = (result.stdout or "") + (result.stderr or "")
        return result.returncode == 0, output.strip()
    except FileNotFoundError:
        return False, f"Command not found: {args[0]}"


def path_exists(path):
    return (ROOT / path).exists()


def is_replit_environment():
    indicators = ["REPL_ID", "REPL_SLUG", "REPL_OWNER", "REPLIT_DB_URL"]
    return any(os.getenv(name) for name in indicators) or path_exists(".replit")


def has_git_repo():
    return path_exists(".git")


def get_git_remote():
    ok, output = run_command(["git", "remote", "-v"])
    if not ok or not output:
        return ""
    return output


def detect_stack():
    detected = []

    if path_exists("requirements.txt") or path_exists("pyproject.toml") or any(ROOT.glob("*.py")):
        detected.append("Python")

    if path_exists("app.py") or path_exists("main.py"):
        detected.append("Possible Flask/FastAPI/Python entrypoint")

    if path_exists("package.json"):
        detected.append("Node/JavaScript")

    if path_exists("vite.config.js") or path_exists("vite.config.ts"):
        detected.append("Vite")

    if path_exists("next.config.js") or path_exists("next.config.ts"):
        detected.append("Next.js")

    if path_exists("Dockerfile"):
        detected.append("Docker")

    if path_exists(".replit"):
        detected.append("Replit")

    return detected or ["Unknown"]


def ensure_directory(path, created):
    target = ROOT / path
    if not target.exists():
        target.mkdir(parents=True, exist_ok=True)
        created.append(path)


def write_file_if_missing(path, content, created, skipped):
    target = ROOT / path
    if target.exists():
        skipped.append(path)
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    created.append(path)


def update_gitignore(created, updated):
    gitignore = ROOT / ".gitignore"
    existing = ""

    if gitignore.exists():
        existing = gitignore.read_text(encoding="utf-8", errors="ignore")

    existing_lines = existing.splitlines()
    lines_to_add = [line for line in SENSITIVE_GITIGNORE_LINES if line not in existing_lines]

    if not gitignore.exists():
        gitignore.write_text("\n".join(SENSITIVE_GITIGNORE_LINES) + "\n", encoding="utf-8")
        created.append(".gitignore")
        return

    if lines_to_add:
        with gitignore.open("a", encoding="utf-8") as f:
            f.write("\n# Sensitive/local files\n")
            for line in lines_to_add:
                f.write(f"{line}\n")
        updated.append(".gitignore")


def should_scan_file(path):
    if any(part in IGNORE_DIRS for part in path.parts):
        return False
    if path.is_dir():
        return False
    return path.suffix.lower() in TEXT_EXTENSIONS


def detect_env_vars():
    found = set()

    for path in ROOT.rglob("*"):
        if not should_scan_file(path):
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for pattern in ENV_PATTERNS:
            for match in pattern.findall(text):
                found.add(match)

    return found


def classify_secret_service(var_name):
    upper = var_name.upper()

    if "AZURE" in upper or "BLOB" in upper or "STORAGE" in upper:
        return "Azure"
    if "OPENAI" in upper or "GPT" in upper:
        return "OpenAI"
    if "RESEND" in upper:
        return "Resend"
    if "VOICEFLOW" in upper or upper.startswith("VF_"):
        return "Voiceflow"
    if "DB" in upper or "DATABASE" in upper or "MYSQL" in upper or "POSTGRES" in upper:
        return "Database"
    if "SECRET" in upper or "TOKEN" in upper or "KEY" in upper:
        return "External service"
    return "Project"


def infer_required_vars(env_vars):
    required_keywords = ["DB_", "DATABASE", "MYSQL", "POSTGRES"]
    return {
        var for var in env_vars
        if any(keyword in var.upper() for keyword in required_keywords)
    }


def build_secret_manifest(env_vars):
    if not env_vars:
        rows = "| PENDING_ENV_VAR | Pendiente | Por definir | local/replit | Por definir | Completar manualmente |"
    else:
        required = infer_required_vars(env_vars)
        row_lines = []
        for var in sorted(env_vars):
            service = classify_secret_service(var)
            required_text = "Sí" if var in required else "Según proyecto"
            test = "scripts/check_env.py" if var in required else "Prueba funcional asociada"
            row_lines.append(
                f"| {var} | {service} | {required_text} | local/replit | {test} | No incluir valor real |"
            )
        rows = "\n".join(row_lines)

    return f"""# SECRETS_MANIFEST.md

## Propósito

Inventario de variables de entorno y secrets requeridos por el proyecto.

Este archivo no debe contener valores reales.

## Variables detectadas o requeridas

| Variable | Servicio | Requerida | Entorno | Prueba de validación | Observaciones |
|---|---|---:|---|---|---|
{rows}

## Reglas

- No incluir valores reales.
- Configurar secrets reales en Replit Secrets, entorno local seguro o gestor autorizado.
- Mantener este archivo actualizado cuando se agreguen nuevas integraciones.
"""


def build_check_env(env_vars):
    required = sorted(infer_required_vars(env_vars))
    optional = sorted(env_vars - set(required))

    if not required and not optional:
        required = ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD"]
        optional = ["OPENAI_API_KEY", "RESEND_API_KEY", "AZURE_STORAGE_CONNECTION_STRING"]

    required_vars = "".join(f'    "{name}",\n' for name in required)
    optional_vars = "".join(f'    "{name}",\n' for name in optional)

    return f'''#!/usr/bin/env python3
"""
check_env.py

Valida que las variables de entorno requeridas estén presentes.
No imprime valores reales.
"""

from __future__ import annotations

import os
import sys


REQUIRED_VARS = [
{required_vars}
]

OPTIONAL_VARS = [
{optional_vars}
]


def main() -> None:
    missing = [name for name in REQUIRED_VARS if not os.getenv(name)]

    if missing:
        print("Missing required environment variables:")
        for name in missing:
            print(f"- {{name}}")
        sys.exit(1)

    print("Required environment variables are present.")

    configured_optional = [name for name in OPTIONAL_VARS if os.getenv(name)]
    if configured_optional:
        print("Configured optional variables:")
        for name in configured_optional:
            print(f"- {{name}}")


if __name__ == "__main__":
    main()
'''


def create_activation_report(mode, is_replit, git_repo, git_remote, stack, env_vars, created, updated, skipped):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_path = f"docs/test_reports/activation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    env_vars_text = "\n".join(f"- {var}" for var in sorted(env_vars)) if env_vars else "- No environment variables detected automatically"
    stack_text = "\n".join(f"- {item}" for item in stack)
    created_text = "\n".join(f"- {item}" for item in created) if created else "- Nothing created"
    updated_text = "\n".join(f"- {item}" for item in updated) if updated else "- Nothing updated"
    skipped_text = "\n".join(f"- {item}" for item in skipped) if skipped else "- Nothing skipped"

    content = f"""# Activation Report

## Metadata

- Date: {timestamp}
- Mode: {mode}
- Working directory: `{ROOT}`

## Environment detected

- Replit environment: {"yes" if is_replit else "no"}
- Git repository: {"yes" if git_repo else "no"}
- Git remote configured: {"yes" if bool(git_remote) else "no"}

## Git remote

{git_remote or "No remote detected"}

## Stack detected

{stack_text}

## Environment variables referenced in code

{env_vars_text}

## Created

{created_text}

## Updated

{updated_text}

## Skipped because file already existed

{skipped_text}

## Pending manual actions

1. Review PROJECT_CONTEXT.md.
2. Review SECRETS_MANIFEST.md.
3. Configure real secrets in the correct environment.
4. Run: python scripts/check_env.py
5. Run the project locally or in Replit.
6. Commit changes manually:

git add .
git commit -m "Activar sistema operativo de agentes"
git push
git status
"""

    target = ROOT / report_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return report_path


def print_summary(mode, is_replit, git_repo, git_remote, stack, env_vars, created, updated, skipped, report_path):
    print("\nAgent system activation completed.\n")

    print("Detected environment:")
    print(f"- Mode: {mode}")
    print(f"- Replit: {'yes' if is_replit else 'no'}")
    print(f"- Git repository: {'yes' if git_repo else 'no'}")
    print(f"- Git remote: {'configured' if git_remote else 'not detected'}")
    print(f"- Stack: {', '.join(stack)}")

    if env_vars:
        print("\nEnvironment variables referenced in code:")
        for var in sorted(env_vars):
            print(f"- {var}")
    else:
        print("\nEnvironment variables referenced in code: none detected automatically")

    if created:
        print("\nCreated:")
        for item in created:
            print(f"- {item}")

    if updated:
        print("\nUpdated:")
        for item in updated:
            print(f"- {item}")

    if skipped:
        print("\nSkipped because file already existed:")
        for item in skipped:
            print(f"- {item}")

    print(f"\nActivation report: {report_path}")

    print("\nNext recommended actions:")
    print("1. Review PROJECT_CONTEXT.md.")
    print("2. Review SECRETS_MANIFEST.md.")
    print("3. Configure real secrets in Replit or local environment.")
    print("4. Run: python scripts/check_env.py")
    print("5. Run the project.")
    print("6. Commit manually:")
    print("   git add .")
    print('   git commit -m "Activar sistema operativo de agentes"')
    print("   git push")
    print("   git status")


def activate(mode):
    created = []
    updated = []
    skipped = []

    is_replit = is_replit_environment()
    git_repo = has_git_repo()
    git_remote = get_git_remote() if git_repo else ""
    stack = detect_stack()
    env_vars = detect_env_vars()

    for directory in ["scripts", "docs/handoffs", "docs/decisions", "docs/test_reports"]:
        ensure_directory(directory, created)

    for path, content in CORE_FILES.items():
        write_file_if_missing(path, content, created, skipped)

    write_file_if_missing("SECRETS_MANIFEST.md", build_secret_manifest(env_vars), created, skipped)
    write_file_if_missing("scripts/check_env.py", build_check_env(env_vars), created, skipped)

    update_gitignore(created, updated)

    report_path = create_activation_report(
        mode=mode,
        is_replit=is_replit,
        git_repo=git_repo,
        git_remote=git_remote,
        stack=stack,
        env_vars=env_vars,
        created=created,
        updated=updated,
        skipped=skipped,
    )

    print_summary(
        mode=mode,
        is_replit=is_replit,
        git_repo=git_repo,
        git_remote=git_remote,
        stack=stack,
        env_vars=env_vars,
        created=created,
        updated=updated,
        skipped=skipped,
        report_path=report_path,
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Activate the agent operating system in a project.")
    parser.add_argument("--mode", choices=["new", "local-existing", "replit-existing"], help="Activation scenario.")
    parser.add_argument("--auto", action="store_true", help="Auto-detect activation scenario.")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.auto:
        if is_replit_environment():
            mode = "replit-existing"
        elif has_git_repo():
            mode = "local-existing"
        else:
            mode = "new"
    else:
        mode = args.mode or "local-existing"

    activate(mode)


if __name__ == "__main__":
    main()