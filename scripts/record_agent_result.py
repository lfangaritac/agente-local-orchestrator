"""
record_agent_result.py

Registra manual o semiautomáticamente el resultado de un agente.

Uso:
python scripts/record_agent_result.py --run-id <run_id> --agent opencode --status diagnostic --summary "..."
"""

from __future__ import annotations

from pathlib import Path
import argparse
import datetime
import json


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "docs" / "agent_runs"
OUTBOX = ROOT / "docs" / "agent_queue" / "outbox"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--agent", required=True)
    parser.add_argument("--status", default="diagnostic")
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()

    run_dir = RUNS / args.run_id
    outputs_dir = run_dir / "agent_outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    OUTBOX.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    result = {
        "run_id": args.run_id,
        "timestamp": timestamp,
        "agent": args.agent,
        "status": args.status,
        "summary": args.summary,
    }

    result_path = outputs_dir / f"{timestamp.replace(':', '-')}_{args.agent}.json"
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    trace_path = run_dir / "TRACE.md"
    with trace_path.open("a", encoding="utf-8") as f:
        f.write(f"\n## {timestamp} — {args.agent}\n\n")
        f.write(f"- status: `{args.status}`\n")
        f.write(f"- summary: {args.summary}\n")

    print(json.dumps({
        "status": "recorded",
        "result_path": str(result_path),
        "trace_path": str(trace_path),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
