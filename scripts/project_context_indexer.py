"""Build a compact Semantic Tag Index for a registered project.

The indexer is read-only against the target project. It writes only the
orchestrator-owned docs/projects/<project-id>/SEMANTIC_TAG_INDEX.md when
--apply is explicitly provided.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from semantic_context_gate import Project, parse_registry


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "PROJECT_REGISTRY.md"
TARGET_READ_LIMIT = 120_000
MAX_SOURCES_PER_TAG = 8

DOC_PATTERNS = ("README*.md", "replit.md", "docs/**/*.md", ".agents/skills/**/*.md")
CODE_PATTERNS = (
    "*.py",
    "routes/**/*.py",
    "services/**/*.py",
    "decorators/**/*.py",
    "repositories/**/*.py",
    "utils/**/*.py",
    "tests/**/*.py",
    "frontend/src/**/*.{ts,tsx,js,jsx,md}",
    ".replit",
    "requirements*.txt",
    "package.json",
    "pyproject.toml",
)
EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    "raw_outputs",
    "agent_runs",
    "agent_queue",
    "handoffs",
    "logs",
    "attached_assets",
}

TAG_RULES: dict[str, dict[str, set[str]]] = {
    "voiceflow.identity": {
        "required_any": {"voiceflow", "vf", "verificar_registro"},
        "signals": {"userid", "user_id", "wa_id", "wa_from", "identity_context", "tipoid", "numeroid", "verificar_registro"},
    },
    "whatsapp.delivery": {
        "required_any": {"whatsapp", "wa_from", "wa_id"},
        "signals": {"send", "enviar", "delivery", "entrega", "telefono", "reporte", "document", "documento", "wa_from"},
    },
    "reports.special_users": {
        "required_any": {"reporte", "report", "informes", "especial", "special"},
        "signals": {"usuarioespecialid", "usuarios_especiales", "special_users", "permitewhatsapp", "especial", "reportes"},
    },
    "training.flow": {
        "required_any": {"formacion", "modulo", "recurso", "pregunta"},
        "signals": {"siguiente_elemento", "registrar_evento", "validar_respuesta", "avance", "finalizado", "porcentaje"},
    },
    "faq.questions": {
        "required_any": {"faq", "preguntas", "pregunta"},
        "signals": {"faq", "preguntas", "respuesta_pregunta", "faq_siguiente", "preguntas_escritas"},
    },
    "football.challenge": {
        "required_any": {"futbol", "jornada", "pronostico", "ranking"},
        "signals": {"futbol", "jornada", "pronostico", "ranking", "premios", "recalcular", "puntajes"},
    },
    "retos.sync": {
        "required_any": {"retos-sync", "retoidexterno", "retos_ciclos", "retos_seguimiento", "puntos colombia"},
        "signals": {"retos-sync", "retoidexterno", "retos_cargas_audit", "retos_ciclos", "retos_seguimiento", "retos_ganadores", "api push", "sftp", "azure blob", "puntos colombia", "fecha_corte", "fechacorte"},
    },
    "mrp.content": {
        "required_any": {"mrp", "modulo", "recurso", "aliado"},
        "signals": {"mrp", "mrp_aliado", "moduloid", "recursoid", "contenido", "upload", "migracion"},
    },
    "voiceflow.sync": {
        "required_any": {"voiceflow", "vf", "snapshot", "api-steps"},
        "signals": {"sync", "snapshot", "api_steps", "diagnostics", "diff", "project-published", "normalizer"},
    },
    "ai.agentic_reports": {
        "required_any": {"agentic", "openai", "consulta", "query"},
        "signals": {"agentic", "openai", "query", "consulta", "intent", "sql", "report_spec"},
    },
    "admin.portal": {
        "required_any": {"frontend", "react", "vite", "portal", "admin"},
        "signals": {"admin", "portal", "usuarios", "aliados", "analytics", "reportes", "comunicaciones"},
    },
    "db.mysql": {
        "required_any": {"mysql", "sql", "db", "database"},
        "signals": {"mysql", "azure", "migration", "migracion", "insert", "select", "table", "tabla"},
    },
    "auth.jwt": {
        "required_any": {"auth", "jwt", "token", "login"},
        "signals": {"jwt", "token", "authorization", "require_auth", "login", "permisos", "claims"},
    },
    "frontend.risk_module": {
        "required_any": {"frontend", "react", "vite"},
        "signals": {"risk_module", "aip", "privacy_risk", "riesgo_privacidad"},
    },
    "privacy.aip.risks": {
        "required_any": {"privacy", "privacidad", "aip", "pii", "datos_personales"},
        "signals": {"privacy", "privacidad", "aip", "pii", "datos_personales", "riesgo_privacidad"},
    },
    "replit.deployment": {
        "required_any": {"replit", "deployment", "deploy", "gunicorn"},
        "signals": {"replit", "deployment", "deploy", "gunicorn", "autoscale", "secrets", "workflow"},
    },
    "opencode.dispatch": {
        "required_any": {"opencode", "handoff", "dispatch"},
        "signals": {"opencode", "handoff", "dispatch", "run_id", "agent_queue"},
    },
}


@dataclass
class SourceHit:
    path: str
    kind: str
    score: int
    signals: set[str] = field(default_factory=set)


def _is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in path.parts)


def _kind(path: Path) -> str:
    suffix = path.suffix.lower()
    text = str(path).replace("\\", "/").lower()
    if "/tests/" in text or text.startswith("tests/"):
        return "test"
    if suffix == ".md":
        return "doc"
    if suffix == ".py":
        return "code"
    return "config"


def _iter_files(root: Path) -> Iterable[Path]:
    seen: set[str] = set()
    for pattern in (*DOC_PATTERNS, *CODE_PATTERNS):
        for path in root.glob(pattern):
            if not path.is_file() or _is_excluded(path):
                continue
            key = str(path.resolve()).lower()
            if key in seen:
                continue
            seen.add(key)
            yield path


def _tokens_for(path: Path, text: str) -> set[str]:
    raw = f"{path} {text[:TARGET_READ_LIMIT]}".lower()
    tokens = set(re.findall(r"[a-z0-9_./:-]{3,}", raw))
    for endpoint in re.findall(r"route\(\s*['\"]([^'\"]+)", raw):
        tokens.add(endpoint.strip("/").replace("/", "."))
    for table in re.findall(r"\b(?:from|into|update|join)\s+([a-z0-9_]+)", raw):
        tokens.add(table)
    return tokens


def _score_tag(tokens: set[str], rule: dict[str, set[str]]) -> tuple[int, set[str]]:
    required = rule["required_any"]
    signals = rule["signals"]
    required_hits = {term for term in required if any(term in token for token in tokens)}
    signal_hits = {term for term in signals if any(term in token for token in tokens)}
    if not required_hits or not signal_hits:
        return 0, set()
    score = len(required_hits) * 4 + len(signal_hits) * 3
    return score, required_hits | signal_hits


def _criticality(tag: str) -> str:
    if tag in {"voiceflow.identity", "auth.jwt", "reports.special_users", "privacy.aip.risks"}:
        return "critical_before_build"
    if tag in {"training.flow", "football.challenge", "mrp.content", "ai.agentic_reports"}:
        return "recommended_for_plan"
    if tag.startswith("db.") or tag.startswith("replit."):
        return "critical_before_build"
    return "recommended_for_plan"


def build_semantic_tags(project: Project) -> dict[str, list[SourceHit]]:
    target_root_value = project.local_path or project.ruta_local
    if not target_root_value or target_root_value.lower() == "null":
        return {}

    target_root = Path(target_root_value)
    if not target_root.exists():
        return {}

    tags: dict[str, list[SourceHit]] = {tag: [] for tag in TAG_RULES}
    for path in _iter_files(target_root):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")[:TARGET_READ_LIMIT]
        except OSError:
            continue
        tokens = _tokens_for(path.relative_to(target_root), text)
        for tag, rule in TAG_RULES.items():
            score, signals = _score_tag(tokens, rule)
            if score:
                tags[tag].append(
                    SourceHit(
                        path=str(path.relative_to(target_root)).replace("\\", "/"),
                        kind=_kind(path.relative_to(target_root)),
                        score=score,
                        signals=signals,
                    )
                )

    return {
        tag: sorted(hits, key=lambda hit: hit.score, reverse=True)[:MAX_SOURCES_PER_TAG]
        for tag, hits in tags.items()
        if hits
    }


def render_index(project_id: str, tags: dict[str, list[SourceHit]]) -> str:
    lines = [
        f"# SEMANTIC_TAG_INDEX - {project_id}",
        "",
        "Canonical semantic index for context retrieval. Generated from project docs/code by references only.",
        "",
        "Rules:",
        "- Do not paste dumps or logs here.",
        "- Keep sources as paths/references; preserve original docs as source of truth.",
        "- Update only when a change affects reusable project context.",
        "",
        "## Tags",
        "",
    ]
    for tag in sorted(tags):
        hits = tags[tag]
        signals = sorted({signal for hit in hits for signal in hit.signals})[:24]
        lines.extend(
            [
                f"### {tag}",
                f"- criticality: `{_criticality(tag)}`",
                "- freshness: `requires_review`",
                "- signals: " + ", ".join(f"`{signal}`" for signal in signals),
                "- sources:",
            ]
        )
        for hit in hits:
            sig = ", ".join(f"`{signal}`" for signal in sorted(hit.signals)[:10])
            lines.append(f"  - `{hit.path}` ({hit.kind}; score={hit.score}; signals={sig})")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def index_path(project_id: str) -> Path:
    return ROOT / "docs" / "projects" / project_id / "SEMANTIC_TAG_INDEX.md"


def build_report(project_id: str, apply: bool = False) -> dict:
    project = parse_registry(REGISTRY).get(project_id)
    if not project:
        return {"ok": False, "status": "missing_project", "project_id": project_id, "tags": []}

    tags = build_semantic_tags(project)
    if not tags:
        return {"ok": True, "status": "no_relevant_signals", "project_id": project_id, "tags": []}

    rendered = render_index(project_id, tags)
    path = index_path(project_id)
    existing = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
    changed = existing != rendered

    if apply and changed:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")

    return {
        "ok": True,
        "status": "updated" if apply and changed else "ready",
        "project_id": project_id,
        "path": str(path),
        "changed": changed,
        "applied": bool(apply and changed),
        "tag_count": len(tags),
        "tags": sorted(tags.keys()),
        "source_count": sum(len(v) for v in tags.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build/update a project Semantic Tag Index.")
    parser.add_argument("--project", required=True, help="project_id from PROJECT_REGISTRY.md")
    parser.add_argument("--apply", action="store_true", help="Write SEMANTIC_TAG_INDEX.md if changed")
    parser.add_argument("--output", choices=("json", "text"), default="text")
    args = parser.parse_args()

    report = build_report(args.project, apply=args.apply)
    if args.output == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"status: {report['status']}")
        print(f"project_id: {report['project_id']}")
        print(f"tag_count: {report.get('tag_count', 0)}")
        print("tags: " + ", ".join(report.get("tags", [])))
        if report.get("path"):
            print(f"path: {report['path']}")
        print(f"changed: {report.get('changed', False)}")
        print(f"applied: {report.get('applied', False)}")
    return 0 if report.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
