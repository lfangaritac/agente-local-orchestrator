"""
get_run_status.py

Devuelve un resumen compacto y JSON-friendly de un run del orquestador.

Objetivo:
- Evitar que Continue use terminal para leer archivos manualmente.
- Evitar respuestas extensas de show_latest_run.
- Confirmar si existe salida de OpenCode en agent_outputs/raw_outputs/TRACE/RUN_SUMMARY.
"""

from __future__ import annotations

from pathlib import Path
import argparse
import json
import re


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "docs" / "agent_runs"
INBOX = ROOT / "docs" / "agent_queue" / "inbox"


def latest_run_id() -> str | None:
    runs = sorted([p for p in RUNS.iterdir() if p.is_dir()], key=lambda p: p.stat().st_mtime, reverse=True) if RUNS.exists() else []
    return runs[0].name if runs else None


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def json_files(path: Path) -> list[str]:
    if not path.exists():
        return []
    return sorted([p.name for p in path.glob("*.json")])


def extract_agents_from_trace(trace: str) -> list[str]:
    agents = []
    for match in re.finditer(r"^##\s+.+?—\s+(.+?)\s*$", trace, flags=re.MULTILINE):
        agents.append(match.group(1).strip())
    return agents


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    run_id = args.run_id or latest_run_id()

    if not run_id:
        print(json.dumps({
            "ok": False,
            "status": "not_found",
            "error": "No hay runs disponibles.",
        }, ensure_ascii=True, indent=2))
        return

    run_dir = RUNS / run_id
    inbox_json = INBOX / f"{run_id}.json"
    inbox_md = INBOX / f"{run_id}.md"
    summary_path = run_dir / "RUN_SUMMARY.md"
    trace_path = run_dir / "TRACE.md"
    agent_outputs_dir = run_dir / "agent_outputs"
    raw_outputs_dir = run_dir / "raw_outputs"
    background_dir = run_dir / "background"

    trace = read_text(trace_path)
    summary = read_text(summary_path)

    agent_outputs = json_files(agent_outputs_dir)
    raw_outputs = json_files(raw_outputs_dir)
    background_meta = sorted([p.name for p in background_dir.glob("*_meta.json")]) if background_dir.exists() else []
    background_stdout = sorted([p.name for p in background_dir.glob("*_stdout.log")]) if background_dir.exists() else []
    background_stderr = sorted([p.name for p in background_dir.glob("*_stderr.log")]) if background_dir.exists() else []

    agents = extract_agents_from_trace(trace)

    opencode_outputs = [name for name in agent_outputs if "_opencode" in name]
    opencode_raw_outputs = [name for name in raw_outputs if "_opencode_raw" in name]

    result = {
        "ok": run_dir.exists(),
        "status": "ok" if run_dir.exists() else "not_found",
        "run_id": run_id,
        "paths": {
            "run_dir": str(run_dir),
            "handoff_json_exists": inbox_json.exists(),
            "handoff_md_exists": inbox_md.exists(),
            "run_summary_exists": summary_path.exists(),
            "trace_exists": trace_path.exists(),
            "agent_outputs_dir_exists": agent_outputs_dir.exists(),
            "raw_outputs_dir_exists": raw_outputs_dir.exists(),
            "background_dir_exists": background_dir.exists(),
        },
        "counts": {
            "agent_outputs": len(agent_outputs),
            "raw_outputs": len(raw_outputs),
            "opencode_outputs": len(opencode_outputs),
            "opencode_raw_outputs": len(opencode_raw_outputs),
            "background_meta": len(background_meta),
            "background_stdout": len(background_stdout),
            "background_stderr": len(background_stderr),
        },
        "agents_in_trace": agents,
        "has_orchestrator_diagnostic": "orchestrator-diagnostic-flow" in agents,
        "has_opencode_context_validator": "context-validator" in agents and len(opencode_outputs) > 0,
        "opencode_registered": len(opencode_outputs) > 0 and len(opencode_raw_outputs) > 0,
        "files": {
            "agent_outputs": agent_outputs,
            "raw_outputs": raw_outputs,
            "background_meta": background_meta,
            "background_stdout": background_stdout,
            "background_stderr": background_stderr,
        },
        "summary_preview": summary[:800].replace("\n", " "),
        "trace_preview": trace[:800].replace("\n", " "),
    }

    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
