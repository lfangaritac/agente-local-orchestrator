"""
select_agent_model.py

Selector semiautomático inicial de agente/modelo.

Objetivo:
- Recibir escenario, riesgo y volumen.
- Recomendar agente OpenCode y línea/modelo.
- No invocar modelos.
- No modificar archivos.

Uso:
python scripts/select_agent_model.py --scenario context-validation --risk medium --volume high
"""

from __future__ import annotations

import argparse
import json


ROUTING = {
    "context-validation": {
        "agent": "context-validator",
        "model": "opencode-go/qwen3.6-plus",
        "line": "Go",
    },
    "model-evaluation": {
        "agent": "model-evaluator",
        "model": "opencode-go/qwen3.6-plus",
        "line": "Go",
    },
    "planning": {
        "agent": "planner",
        "model": "opencode-go/kimi-k2.6",
        "line": "Go",
    },
    "architecture": {
        "agent": "architect-planner",
        "model": "opencode-go/kimi-k2.6",
        "line": "Go preliminary; consider Zen premium if risk/high complexity applies",
    },
    "debugging": {
        "agent": "debugger",
        "model": "opencode-go/deepseek-v4-pro",
        "line": "Go",
    },
    "security": {
        "agent": "security-reviewer",
        "model": "opencode/gpt-5.5",
        "line": "Zen premium with authorization",
    },
    "handoff": {
        "agent": "handoff-writer",
        "model": "opencode-go/qwen3.6-plus",
        "line": "Go",
    },
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--risk", default="medium")
    parser.add_argument("--volume", default="medium")
    parser.add_argument("--user-premium", action="store_true")
    args = parser.parse_args()

    key = args.scenario.strip().lower()
    recommendation = ROUTING.get(key, ROUTING["context-validation"]).copy()

    requires_authorization = False
    escalation_reason = None

    if args.user_premium:
        requires_authorization = True
        escalation_reason = "user_requested_premium"
        recommendation = {
            "agent": recommendation["agent"],
            "model": "premium_by_scenario",
            "line": "Zen premium",
        }

    if args.risk in {"high", "critical"}:
        requires_authorization = True
        escalation_reason = escalation_reason or "high_or_critical_risk"

    result = {
        "scenario": args.scenario,
        "risk": args.risk,
        "volume": args.volume,
        "recommended_agent": recommendation["agent"],
        "recommended_model": recommendation["model"],
        "recommended_line": recommendation["line"],
        "requires_authorization": requires_authorization,
        "escalation_reason": escalation_reason,
        "status": "diagnostic_recommendation",
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
