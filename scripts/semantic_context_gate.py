"""Read-only semantic context gate for project instructions.

The gate builds a compact context pack from project docs and local indexes.
It is intentionally lightweight: no embeddings, no network, no writes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "PROJECT_REGISTRY.md"

STOPWORDS = {
    "analiza",
    "analizar",
    "cada",
    "como",
    "contexto",
    "cual",
    "cuales",
    "cuando",
    "desde",
    "donde",
    "este",
    "esta",
    "esto",
    "hacer",
    "hasta",
    "instruccion",
    "para",
    "pero",
    "porque",
    "proyecto",
    "realiza",
    "realizar",
    "sobre",
    "todo",
    "todos",
    "and",
    "for",
    "from",
    "that",
    "the",
    "this",
    "with",
}

BUILD_TERMS = {
    "ajusta",
    "ajustar",
    "aplica",
    "aplicar",
    "commit",
    "corrige",
    "corregir",
    "edita",
    "editar",
    "implementa",
    "implementar",
    "modifica",
    "modificar",
    "push",
}

DOC_GLOBS = ("*.md", "docs/**/*.md", ".agents/**/*.md")

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "raw_outputs",
    "agent_runs",
    "agent_queue",
    "handoffs",
    "logs",
    "attached_assets",
}


@dataclass
class Project:
    project_id: str
    local_path: str = ""
    ruta_local: str = ""
    documentacion_principal: str = ""


@dataclass
class Match:
    path: str
    score: int
    matched_terms: list[str]
    snippets: list[str]


def parse_registry(path: Path) -> dict[str, Project]:
    if not path.exists():
        return {}

    projects: dict[str, Project] = {}
    current: dict[str, str] = {}

    def flush() -> None:
        nonlocal current
        pid = current.get("project_id", "").strip()
        if pid:
            projects[pid] = Project(
                project_id=pid,
                local_path=current.get("local_path", "").strip(),
                ruta_local=current.get("ruta_local", "").strip(),
                documentacion_principal=current.get("documentacion_principal", "").strip(),
            )
        current = {}

    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line:
            flush()
            continue
        if ":" not in line or line.startswith("#") or line.startswith("<!--"):
            continue
        key, value = line.split(":", 1)
        current[key.strip()] = value.strip()
    flush()
    return projects


def split_identifier(value: str) -> list[str]:
    parts = re.split(r"[^A-Za-z0-9_./:-]+", value)
    out: list[str] = []
    for part in parts:
        if not part:
            continue
        out.append(part)
        out.extend(re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|\d+", part))
        if "_" in part:
            out.extend(part.split("_"))
    return out


def infer_terms(instruction: str) -> list[str]:
    terms: list[str] = []
    seen: set[str] = set()
    for raw in split_identifier(instruction):
        term = raw.strip().strip(".,;:!?()[]{}\"'").lower()
        if len(term) < 3 or term in STOPWORDS:
            continue
        if term not in seen:
            seen.add(term)
            terms.append(term)
    return terms[:80]


def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in path.parts)


def iter_markdown_files(base: Path) -> Iterable[Path]:
    if not base.exists():
        return
    for pattern in DOC_GLOBS:
        for path in base.glob(pattern):
            if path.is_file() and not is_excluded(path):
                yield path


def candidate_files(project: Project) -> list[Path]:
    candidates: dict[str, Path] = {}

    if project.project_id == "orchestrator":
        for pattern in ("*.md", "docs/protocols/**/*.md", "docs/context/**/*.md", ".continue/**/*.md"):
            for path in ROOT.glob(pattern):
                if path.is_file() and not is_excluded(path):
                    candidates[str(path.resolve()).lower()] = path
        return sorted(candidates.values(), key=lambda p: str(p).lower())

    project_index_dir = ROOT / "docs" / "projects" / project.project_id
    for path in iter_markdown_files(project_index_dir):
        candidates[str(path.resolve()).lower()] = path

    target_root_value = project.local_path or project.ruta_local
    if target_root_value and target_root_value.lower() != "null":
        target_root = Path(target_root_value)
        for path in iter_markdown_files(target_root):
            candidates[str(path.resolve()).lower()] = path

        for ref in project.documentacion_principal.split(","):
            ref = ref.strip()
            if not ref:
                continue
            path = target_root / ref
            if path.exists() and path.is_file() and not is_excluded(path):
                candidates[str(path.resolve()).lower()] = path

    return sorted(candidates.values(), key=lambda p: str(p).lower())


def line_snippets(text: str, terms: list[str], max_snippets: int = 3) -> list[str]:
    snippets: list[str] = []
    lowered_terms = [term.lower() for term in terms]
    for idx, line in enumerate(text.splitlines(), start=1):
        low = line.lower()
        if any(term in low for term in lowered_terms):
            clean = re.sub(r"\s+", " ", line).strip()
            if len(clean) > 180:
                clean = clean[:177] + "..."
            snippets.append(f"L{idx}: {clean}")
            if len(snippets) >= max_snippets:
                break
    return snippets


def score_file(path: Path, terms: list[str]) -> Match | None:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")[:250_000]
    except OSError:
        return None

    content = text.lower()
    path_text = str(path).lower()
    matched: list[str] = []
    score = 0

    for term in terms:
        content_hits = content.count(term)
        path_hits = path_text.count(term)
        if content_hits or path_hits:
            matched.append(term)
            score += min(content_hits, 20)
            score += path_hits * 12
            if "_" in term or "/" in term or "-" in term:
                score += content_hits * 2

    if not matched:
        return None

    lower_path = path_text.replace("\\", "/")
    if "/docs/projects/" in lower_path:
        score += 8
    if "/.agents/skills/" in lower_path:
        score += 12
    if lower_path.endswith("technical_documentation.md"):
        score += 8
    if lower_path.endswith("replit.md"):
        score += 5

    return Match(
        path=str(path),
        score=score,
        matched_terms=matched[:20],
        snippets=line_snippets(text, matched),
    )


def build_report(project_id: str, instruction: str, max_results: int) -> dict:
    if project_id == "orchestrator":
        project = Project(
            project_id="orchestrator",
            local_path=str(ROOT),
            documentacion_principal=(
                "AGENT_RULES.md, CONTINUE_USAGE_PROTOCOL.md, PROJECT_REGISTRY.md, "
                "docs/protocols/AGENT_AUTOMATION_PROTOCOL.md, docs/context/ACTION_INDEX.md"
            ),
        )
    else:
        project = parse_registry(REGISTRY).get(project_id)
    terms = infer_terms(instruction)
    if not project:
        return {
            "status": "blocked_missing_project",
            "project_id": project_id,
            "instruction": instruction,
            "terms": terms,
            "matches": [],
            "message": f"Project not found in {REGISTRY}",
        }

    matches = [
        match
        for path in candidate_files(project)
        if (match := score_file(path, terms)) is not None
    ]
    matches.sort(key=lambda item: item.score, reverse=True)
    top = matches[:max_results]

    buildish = any(term in BUILD_TERMS for term in terms)
    if top:
        status = "needs_context_review" if buildish else "ok"
    else:
        status = "blocked_missing_context" if buildish else "no_context_found"

    return {
        "status": status,
        "project_id": project_id,
        "instruction": instruction,
        "terms": terms,
        "match_count": len(matches),
        "matches": [asdict(match) for match in top],
    }


def print_text(report: dict) -> None:
    def safe_print(value: str = "") -> None:
        encoding = sys.stdout.encoding or "utf-8"
        print(value.encode(encoding, errors="replace").decode(encoding))

    safe_print(f"status: {report['status']}")
    safe_print(f"project_id: {report['project_id']}")
    safe_print("terms: " + ", ".join(report.get("terms", [])[:30]))
    safe_print(f"match_count: {report.get('match_count', 0)}")
    for idx, match in enumerate(report.get("matches", []), start=1):
        safe_print()
        safe_print(f"{idx}. {match['path']}")
        safe_print(f"   score: {match['score']}")
        safe_print("   matched_terms: " + ", ".join(match["matched_terms"]))
        for snippet in match.get("snippets", []):
            safe_print(f"   {snippet}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the semantic context gate.")
    parser.add_argument("--project", required=True, help="project_id from PROJECT_REGISTRY.md")
    parser.add_argument("--instruction", required=True, help="User instruction to analyze")
    parser.add_argument("--max-results", type=int, default=8)
    parser.add_argument("--output", choices=("json", "text"), default="text")
    args = parser.parse_args()

    report = build_report(args.project, args.instruction, args.max_results)
    if args.output == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_text(report)
    return 0 if not report["status"].startswith("blocked") else 2


if __name__ == "__main__":
    raise SystemExit(main())
