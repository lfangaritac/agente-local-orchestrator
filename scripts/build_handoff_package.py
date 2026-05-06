"""
build_handoff_package.py

Construye un paquete básico de handoff semiautomático.

Este script no invoca agentes ni modelos. Solo genera un archivo Markdown/JSON
para ser consumido por Continue, OpenCode o una futura capa MCP.
"""

from __future__ import annotations

from pathlib import Path
import argparse
import datetime
import json
import uuid


ROOT = Path(__file__).resolve().parents[1]
QUEUE_INBOX = ROOT / "docs" / "agent_queue" / "inbox"
RUNS = ROOT / "docs" / "agent_runs"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", default="orchestrator")
    parser.add_argument("--source-agent", default="user")
    parser.add_argument("--target-agent", default="context-validator")
    parser.add_argument("--scenario", default="context-validation")
    parser.add_argument("--risk", default="medium")
    parser.add_argument("--volume", default="medium")
    parser.add_argument("--objective", required=True)
    args = parser.parse_args()

    run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]

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
        "context_sources": [],
        "alerts_checked": [],
        "lessons_checked": [],
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
        f"- information_volume: `{args.volume}`\n\n"
        "## Objective\n\n"
        f"{args.objective}\n\n"
        "## Status\n\n"
        "created\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "status": "created",
        "run_id": run_id,
        "json_path": str(json_path),
        "md_path": str(md_path),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
