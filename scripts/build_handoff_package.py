"""
build_handoff_package.py

Construye un paquete básico de handoff semiautomático.

Este script no invoca agentes ni modelos. Solo genera un archivo Markdown/JSON
para ser consumido por Continue, OpenCode o una futura capa MCP.

Puede incorporar automáticamente fuentes, alertas y lecciones desde el preflight.
"""

from __future__ import annotations

from pathlib import Path
import argparse
import datetime
import json
import subprocess
import sys
import uuid


ROOT = Path(__file__).resolve().parents[1]
QUEUE_INBOX = ROOT / "docs" / "agent_queue" / "inbox"
RUNS = ROOT / "docs" / "agent_runs"


def run_preflight() -> dict:
    script = ROOT / "scripts" / "orchestrator_preflight.py"
    completed = subprocess.run(
        [sys.executable, str(script)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return json.loads(completed.stdout)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", default="orchestrator")
    parser.add_argument("--source-agent", default="user")
    parser.add_argument("--target-agent", default="context-validator")
    parser.add_argument("--scenario", default="context-validation")
    parser.add_argument("--risk", default="medium")
    parser.add_argument("--volume", default="medium")
    parser.add_argument("--objective", required=True)
    parser.add_argument("--skip-preflight", action="store_true")
    args = parser.parse_args()

    run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]
    preflight = {} if args.skip_preflight else run_preflight()

    package = {
        "run_id": run_id,
        "step_id": "01",
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "project_id": args.project_id,
        "source_agent": args.source_agent,
        "target_agent": args.target_agent,
        "scenario": args.scenario,
        "risk_level": args.risk,
        "information_volume": args.volume,
        "objective": args.objective,
        "context_sources": preflight.get("context_sources", []),
        "alerts_checked": preflight.get("alerts_checked", []),
        "lessons_checked": preflight.get("lessons_checked", []),
        "preflight_status": preflight.get("status", "skipped"),
        "missing_files": preflight.get("missing_files", []),
        "status": "created",
    }

    QUEUE_INBOX.mkdir(parents=True, exist_ok=True)
    RUNS.mkdir(parents=True, exist_ok=True)

    json_path = QUEUE_INBOX / f"{run_id}.json"
    md_path = QUEUE_INBOX / f"{run_id}.md"

    json_path.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")

    md_path.write_text(
        "# Handoff Package\n\n"
        f"- run_id: `{run_id}`\n"
        f"- project_id: `{args.project_id}`\n"
        f"- source_agent: `{args.source_agent}`\n"
        f"- target_agent: `{args.target_agent}`\n"
        f"- scenario: `{args.scenario}`\n"
        f"- risk_level: `{args.risk}`\n"
        f"- information_volume: `{args.volume}`\n"
        f"- preflight_status: `{package['preflight_status']}`\n\n"
        "## Objective\n\n"
        f"{args.objective}\n\n"
        "## Context Sources\n\n"
        + "\n".join(f"- `{item}`" for item in package["context_sources"])
        + "\n\n## Alerts Checked\n\n"
        + "\n".join(f"- `{item}`" for item in package["alerts_checked"])
        + "\n\n## Lessons Checked\n\n"
        + "\n".join(f"- `{item}`" for item in package["lessons_checked"])
        + "\n\n## Missing Files\n\n"
        + ("\n".join(f"- `{item}`" for item in package["missing_files"]) if package["missing_files"] else "- Ninguno")
        + "\n\n## Status\n\ncreated\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "status": "created",
        "run_id": run_id,
        "json_path": str(json_path),
        "md_path": str(md_path),
        "preflight_status": package["preflight_status"],
        "context_sources_count": len(package["context_sources"]),
        "alerts_checked_count": len(package["alerts_checked"]),
        "lessons_checked_count": len(package["lessons_checked"]),
    }, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()

