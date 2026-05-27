from __future__ import annotations

import tempfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_generic_auth_jwt_tag_without_project_hardcode() -> None:
    from scripts.project_context_indexer import Project, build_semantic_tags

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "routes").mkdir()
        (root / "routes" / "auth.py").write_text(
            """
from flask import Blueprint
auth_bp = Blueprint("auth", __name__)
@auth_bp.route('/api/login', methods=['POST'])
def login():
    token = create_jwt_token({"role": "admin"})
    return {"token": token}
""",
            encoding="utf-8",
        )
        tags = build_semantic_tags(Project(project_id="tmp", local_path=str(root)))
        assert "auth.jwt" in tags


def test_no_index_when_no_relevant_signals() -> None:
    from scripts.project_context_indexer import Project, build_semantic_tags

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "README.md").write_text("Small notes about a generic static page.", encoding="utf-8")
        tags = build_semantic_tags(Project(project_id="tmp", local_path=str(root)))
        assert tags == {}


def test_render_is_reference_based_no_dumps() -> None:
    from scripts.project_context_indexer import Project, build_semantic_tags, render_index

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "services").mkdir()
        (root / "services" / "db.py").write_text(
            "MYSQL_URL='x'\nSELECT_USERS = 'SELECT * FROM usuarios'\n",
            encoding="utf-8",
        )
        tags = build_semantic_tags(Project(project_id="tmp", local_path=str(root)))
        rendered = render_index("tmp", tags)
        assert "services/db.py" in rendered
        assert "SELECT * FROM usuarios" not in rendered
        assert all(len(line) < 260 for line in rendered.splitlines())


def main() -> None:
    test_generic_auth_jwt_tag_without_project_hardcode()
    test_no_index_when_no_relevant_signals()
    test_render_is_reference_based_no_dumps()
    print("[PASS] project_context_indexer tags genericos, evita ruido y no genera dumps")


if __name__ == "__main__":
    main()
