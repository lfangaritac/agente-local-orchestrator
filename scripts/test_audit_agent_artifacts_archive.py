"""test_audit_agent_artifacts_archive.py

Pruebas unitarias para:
- archive_run()
- verify_archive()

Objetivo:
- Validar creación de archive y manifest.
- Validar verificación de integridad (SHA256, conteo).
- No tocar evidencia real.

Ejecución sugerida:
  python .\\scripts\\test_audit_agent_artifacts_archive.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


def _patch_module_paths(audit_mod, root: Path) -> None:
    audit_mod.ROOT = root
    audit_mod.RUNS_DIR = root / "docs" / "agent_runs"
    audit_mod.INBOX_DIR = root / "docs" / "agent_queue" / "inbox"
    audit_mod.RUN_INDEX = root / "docs" / "context" / "RUN_INDEX.md"


def main() -> None:
    # Asegura que `scripts/` esté en sys.path para poder importar `audit_agent_artifacts.py`
    scripts_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(scripts_dir))

    import audit_agent_artifacts as audit

    with tempfile.TemporaryDirectory(prefix="audit-archive-") as td:
        root = Path(td)
        _patch_module_paths(audit, root)

        # Setup dummy run
        run_id = "run_test_001"
        run_dir = root / "docs" / "agent_runs" / run_id
        run_dir.mkdir(parents=True)
        (run_dir / "TRACE.md").write_text("trace content", encoding="utf-8")
        
        archive_dir = root / "archives"
        archive_dir.mkdir()

        print("--- Caso 1: archive_run OK ---")
        res = audit.archive_run(run_id, str(archive_dir))
        assert res["ok"] is True
        assert res["status"] == "archived"
        zip_path = Path(str(res["archive_path"])) # res["archive_path"] puede ser relativo a ROOT
        if not zip_path.is_absolute():
             zip_path = root / zip_path
        
        manifest_path = Path(str(res["manifest_path"]))
        if not manifest_path.is_absolute():
             manifest_path = root / manifest_path

        assert zip_path.exists()
        assert manifest_path.exists()
        print(f"Archive OK: {zip_path.name}")

        print("\n--- Caso 2: verify_archive OK ---")
        v = audit.verify_archive(str(zip_path))
        assert v["ok"] is True
        assert v["sha256_matches"] is True
        assert v["included_files_count_matches"] is True
        print("Verification OK")

        print("\n--- Caso 3: verify_archive Hash Mismatch ---")
        # Modificar el ZIP (añadir basura al final)
        with open(zip_path, "ab") as f:
            f.write(b"corrupt")
        
        v2 = audit.verify_archive(str(zip_path))
        assert v2["ok"] is False
        assert v2["sha256_matches"] is False
        assert any("Mismatch de SHA256" in e for e in v2["errors"])
        print("Hash mismatch detected OK")

        print("\n--- Caso 4: verify_archive Missing Manifest ---")
        manifest_path.unlink()
        v3 = audit.verify_archive(str(zip_path))
        assert v3["ok"] is False
        assert v3["manifest_exists"] is False
        print("Missing manifest detected OK")

        print("\n--- Caso 5: verify_archive File Count Mismatch ---")
        # Re-archivar para limpiar
        res4 = audit.archive_run(run_id, str(archive_dir))
        zip_path4 = root / res4["archive_path"]
        manifest_path4 = root / res4["manifest_path"]
        
        # Corromper manifest (cambiar count)
        mdata = json.loads(manifest_path4.read_text(encoding="utf-8"))
        mdata["archive"]["included_files_count"] = 999
        manifest_path4.write_text(json.dumps(mdata), encoding="utf-8")
        
        v4 = audit.verify_archive(str(zip_path4))
        assert v4["ok"] is False
        assert v4["included_files_count_matches"] is False
        print("File count mismatch detected OK")

    print("\n[OK] Todas las pruebas de archive/verify pasaron.")


if __name__ == "__main__":
    main()
