"""
run_opencode_from_handoff.py

Invoca OpenCode en modo no interactivo a partir de un paquete de handoff.

Objetivo:
- Tomar el último handoff Markdown o uno indicado por --run-id.
- Invocar opencode.cmd run con agente/modelo seleccionados.
- Capturar salida JSONL de OpenCode.
- Extraer eventos tipo text.
- Registrar resultado limpio en agent_outputs.
- Guardar salida cruda en raw_outputs para no contaminar RUN_SUMMARY.md.
- Actualizar TRACE.md y RUN_SUMMARY.md.
- Mostrar el flujo actualizado al usuario.

Este script sí invoca OpenCode real, pero no solicita edición ni ejecución de comandos dentro del prompt base.
"""

from __future__ import annotations

from pathlib import Path
import argparse
import datetime
import json
import subprocess
import sys
import os

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def safe_print(value: object = "") -> None:
    text = str(value)
    try:
        print(text)
    except UnicodeEncodeError:
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))


ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "docs" / "agent_queue" / "inbox"
RUNS = ROOT / "docs" / "agent_runs"


def run_command(command: list[str]) -> tuple[int, str, str]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.returncode, completed.stdout, completed.stderr


def latest_handoff_md() -> Path | None:
    files = sorted(INBOX.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def handoff_for_run(run_id: str) -> Path | None:
    path = INBOX / f"{run_id}.md"
    return path if path.exists() else None


def load_package_for_handoff(handoff_path: Path) -> dict:
    json_path = handoff_path.with_suffix(".json")
    if not json_path.exists():
        return {}
    return json.loads(json_path.read_text(encoding="utf-8"))


def parse_opencode_jsonl(stdout: str) -> dict:
    events = []
    text_parts = []
    session_id = None
    tokens = None
    cost = None

    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue

        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            events.append({
                "type": "raw",
                "raw": line,
            })
            continue

        events.append(event)

        if event.get("sessionID"):
            session_id = event.get("sessionID")

        if event.get("type") == "text":
            part = event.get("part", {})
            text = part.get("text")
            if text:
                text_parts.append(text)

        if event.get("type") == "step_finish":
            part = event.get("part", {})
            tokens = part.get("tokens")
            cost = part.get("cost")

    return {
        "session_id": session_id,
        "text": "\n".join(text_parts).strip(),
        "events_count": len(events),
        "tokens": tokens,
        "cost": cost,
        "events": events,
    }


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2), encoding="utf-8")


def append_trace(run_id: str, agent: str, status: str, summary: str, model: str, handoff_path: Path) -> None:
    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    trace_path = run_dir / "TRACE.md"
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")

    with trace_path.open("a", encoding="utf-8") as f:
        f.write(f"\n## {timestamp} — {agent}\n\n")
        f.write(f"- status: `{status}`\n")
        f.write(f"- model: `{model}`\n")
        f.write(f"- handoff: `{handoff_path.relative_to(ROOT)}`\n")
        f.write(f"- summary: {summary}\n")


def load_agent_result_files(outputs_dir: Path) -> list[dict]:
    results = []
    if not outputs_dir.exists():
        return results

    for path in sorted(outputs_dir.glob("*.json")):
        if path.name.endswith("_raw.json"):
            continue

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {
                "agent": path.stem,
                "status": "unreadable",
                "summary": f"No se pudo leer {path.name}",
                "timestamp": "",
            }

        if not isinstance(data, dict):
            continue

        if not data.get("agent") and not data.get("summary") and not data.get("status"):
            continue

        results.append(data)

    return results


def write_run_summary(run_id: str) -> None:
    run_dir = RUNS / run_id
    outputs_dir = run_dir / "agent_outputs"
    results = load_agent_result_files(outputs_dir)

    summary_path = run_dir / "RUN_SUMMARY.md"

    lines = [
        "# RUN_SUMMARY",
        "",
        f"- run_id: `{run_id}`",
        f"- updated_at: `{datetime.datetime.now().isoformat(timespec='seconds')}`",
        f"- total_agent_outputs: `{len(results)}`",
        "",
        "## Estado general",
        "",
    ]

    if not results:
        lines.append("Sin resultados de agentes registrados todavía.")
    else:
        last_status = results[-1].get("status", "unknown")
        lines.append(f"Último estado registrado: `{last_status}`")

    lines.extend([
        "",
        "## Resultados por agente",
        "",
    ])

    for idx, item in enumerate(results, start=1):
        lines.extend([
            f"### {idx}. {item.get('agent', 'unknown')}",
            "",
            f"- timestamp: `{item.get('timestamp', '')}`",
            f"- status: `{item.get('status', 'unknown')}`",
            f"- model: `{item.get('model', '')}`",
            f"- summary: {item.get('summary', '')}",
            "",
        ])

    lines.extend([
        "## Transparencia del proceso",
        "",
        "Este resumen permite revisar qué agente intervino, qué modelo se usó, qué estado reportó y cuál fue el aporte registrado.",
        "",
        "Para mayor detalle, revisar `TRACE.md` y los archivos en `agent_outputs/`.",
        "",
    ])

    summary_path.write_text("\n".join(lines), encoding="utf-8")


def _normalize_rel(path: str) -> str:
    return path.strip().replace("\\", "/")


def _is_disallowed_allowed_file(path: str) -> bool:
    p = _normalize_rel(path).lower()
    disallowed_prefixes = [
        ".env",
        "secrets",
        "docs/agent_runs/",
        "docs/agent_queue/",
        "raw_outputs",
        "deployment",
        "deploy",
        "migrations",
        "infra",
        "infrastructure",
    ]
    return any(p == pref or p.startswith(pref) for pref in disallowed_prefixes)


def _is_exact_relative_path(path: str) -> bool:
    s = _normalize_rel(path)
    if not s:
        return False
    if s.startswith("/") or ":" in s.split("/")[0]:
        return False
    if ".." in s.split("/"):
        return False
    if any(ch in s for ch in ["*", "?", "[", "]"]):
        return False
    return True


def _git_diff_name_only() -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except Exception:
        return []

    if completed.returncode != 0:
        return []

    return [_normalize_rel(ln) for ln in (completed.stdout or "").splitlines() if ln.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--agent", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--format", default="json")
    parser.add_argument(
        "--prompt",
        default=(
            "Lee el archivo de handoff adjunto. Actúa en modo diagnóstico. "
            "No modifiques archivos. No ejecutes comandos. "
            "Responde con un JSON corto con estas claves: status, agent, model, file_read, summary, next_action."
        ),
    )

    # Guardrail: este flag habilita auto-aprobación de permisos en OpenCode.
    # Está apagado por defecto y solo debe usarse con package guardraileado.
    parser.add_argument("--auto-approve-permissions", action="store_true")

    args = parser.parse_args()

    if args.run_id:
        handoff_path = handoff_for_run(args.run_id)
    else:
        handoff_path = latest_handoff_md()

    if not handoff_path:
        safe_print("ERROR: No se encontró handoff Markdown en docs/agent_queue/inbox.")
        sys.exit(1)

    package = load_package_for_handoff(handoff_path)
    run_id = package.get("run_id", handoff_path.stem)

    agent = args.agent or package.get("target_agent") or "context-validator"
    model = args.model or "opencode-go/qwen3.6-plus"

    # Auto-approve de permisos: solo cuando es explícito (flag) + package compatible.
    auto_approve_permissions = bool(args.auto_approve_permissions)

    if auto_approve_permissions:
        # Requisitos mínimos (defensa en profundidad):
        # - Debe estar explícitamente marcado como Build autorizado.
        # - risk_level debe ser low.
        # - allowed_files debe estar definido y ser una lista no vacía de rutas exactas.
        if package.get("auto_approve_permissions") is not True:
            safe_print("ERROR: auto_approve_permissions fue solicitado pero el paquete no lo habilita.")
            sys.exit(2)

        if package.get("build_authorized") is not True:
            safe_print("ERROR: auto_approve_permissions requiere build_authorized=true en el paquete.")
            sys.exit(2)

        if str(package.get("risk_level") or "").lower().strip() != "low":
            safe_print("ERROR: auto_approve_permissions solo permitido con risk_level=low.")
            sys.exit(2)

        allowed_files = package.get("allowed_files")
        if not isinstance(allowed_files, list) or not allowed_files:
            safe_print("ERROR: auto_approve_permissions requiere allowed_files no vacío en el paquete.")
            sys.exit(2)

        for f in allowed_files:
            if not isinstance(f, str) or not _is_exact_relative_path(f):
                safe_print(f"ERROR: allowed_files inválido para auto_approve_permissions (debe ser ruta exacta relativa): {f!r}")
                sys.exit(2)
            if _is_disallowed_allowed_file(f):
                safe_print(f"ERROR: allowed_files contiene ruta sensible/bloqueada para auto_approve_permissions: {f!r}")
                sys.exit(2)

    command = [
        "opencode.cmd",
        "run",
    ]

    if auto_approve_permissions:
        # Nota: flag explícitamente peligroso de OpenCode.
        command.append("--dangerously-skip-permissions")

    command.extend([
        "--agent",
        agent,
        "--model",
        model,
        "--file",
        str(handoff_path),
        "--format",
        args.format,
        args.prompt,
    ])

    safe_print("=== Invocando OpenCode ===")
    safe_print(" ".join(command[:-1]) + " <prompt>")

    code, stdout, stderr = run_command(command)

    if stderr:
        safe_print("=== STDERR ===")
        safe_print(stderr)

    if stdout:
        safe_print("=== STDOUT ===")
        safe_print(stdout)

    if code != 0:
        safe_print(f"ERROR: opencode.cmd run falló con código {code}")
        sys.exit(code)

    parsed = parse_opencode_jsonl(stdout)
    text = parsed.get("text", "")

    status = "diagnostic"
    summary = text[:700].replace("\n", " ").strip() if text else "OpenCode respondió sin texto extraíble."

    # Post-check (guardrail): si se habilitó auto-approve, verificar que el diff solo toque allowed_files.
    changed_files: list[str] = []
    out_of_scope: list[str] = []

    if auto_approve_permissions:
        changed_files = _git_diff_name_only()
        allowed_set = { _normalize_rel(str(p)) for p in (package.get("allowed_files") or []) }

        for p in changed_files:
            if p not in allowed_set:
                out_of_scope.append(p)

        if out_of_scope:
            status = "error"
            summary = (
                "ERROR: OpenCode produjo cambios fuera de allowed_files. "
                f"Fuera de alcance: {out_of_scope[:10]}"
            )
        elif changed_files:
            status = "build_applied"
        else:
            status = "no_changes"

    run_dir = RUNS / run_id
    outputs_dir = run_dir / "agent_outputs"
    raw_outputs_dir = run_dir / "raw_outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    raw_outputs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    safe_timestamp = timestamp.replace(":", "-")

    result = {
        "run_id": run_id,
        "timestamp": timestamp,
        "agent": agent,
        "model": model,
        "status": status,
        "handoff_path": str(handoff_path.relative_to(ROOT)),
        "summary": summary,
        "opencode_session_id": parsed.get("session_id"),
        "events_count": parsed.get("events_count"),
        "tokens": parsed.get("tokens"),
        "cost": parsed.get("cost"),
        "text": text,
        "auto_approve_permissions": auto_approve_permissions,
        "allowed_files": package.get("allowed_files"),
        "changed_files": changed_files[:50],
        "out_of_scope_changes": out_of_scope[:50],
    }

    result_path = outputs_dir / f"{safe_timestamp}_{agent}_opencode.json"
    write_json(result_path, result)

    raw_path = raw_outputs_dir / f"{safe_timestamp}_{agent}_opencode_raw.json"
    write_json(raw_path, parsed)

    append_trace(run_id, agent, status, summary, model, handoff_path)
    write_run_summary(run_id)

    safe_print("=== Resultado registrado ===")
    safe_print(json.dumps({
        "status": "recorded",
        "run_id": run_id,
        "agent": agent,
        "model": model,
        "result_path": str(result_path),
        "raw_path": str(raw_path),
        "summary": summary,
    }, ensure_ascii=True, indent=2))

    safe_print("=== Visualización actualizada ===")
    show_code, show_out, show_err = run_command([
        sys.executable,
        "scripts/show_latest_run.py",
        "--run-id",
        run_id,
    ])

    if show_out:
        safe_print(show_out)
    if show_err:
        safe_print(show_err)

    if show_code != 0:
        print(f"ADVERTENCIA: show_latest_run.py terminó con código {show_code}")


if __name__ == "__main__":
    main()

