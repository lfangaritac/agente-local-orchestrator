"""test_opencode_cli_model_resolution.py

Tests read-only para la capa logical_model -> cli_model en run_opencode_from_handoff.py.

Objetivo:
- Validar mapping aprobado.
- Validar bloqueo cuando no hay mapping aprobado.
- Validar que no se degrade a modelos free por defecto.

Uso:
  python .\scripts\test_opencode_cli_model_resolution.py
"""

from __future__ import annotations

import os

from run_opencode_from_handoff import resolve_cli_model


def _setenv(name: str, value: str | None) -> None:
    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value


def main() -> None:
    available = [
        "opencode/qwen3.6-plus",
        "opencode/kimi-k2.6",
        "opencode/qwen3.5-plus",
        "opencode/deepseek-v4-flash-free",
        "opencode/nemotron-3-super-free",
        "opencode/big-pickle",
    ]

    # 1) Mapping aprobado
    ok, cli, err = resolve_cli_model(logical_model="opencode-go/qwen3.6-plus", available_models=available)
    if not ok or cli != "opencode/qwen3.6-plus":
        raise AssertionError(f"Mapping aprobado falló: ok={ok}, cli={cli!r}, err={err!r}")

    # 2) Bloqueo por falta de mapping aprobado (deepseek v4 flash)
    ok, cli, err = resolve_cli_model(logical_model="opencode-go/deepseek-v4-flash", available_models=available)
    if ok:
        raise AssertionError(f"Debió bloquear opencode-go/deepseek-v4-flash y no degradar. cli={cli!r}")
    if "No hay mapping" not in err and "Bloqueado" not in err:
        raise AssertionError(f"Mensaje de bloqueo inesperado: {err!r}")

    # 3) Bloqueo por falta de mapping aprobado (deepseek v4 pro)
    ok, cli, err = resolve_cli_model(logical_model="opencode-go/deepseek-v4-pro", available_models=available)
    if ok:
        raise AssertionError(f"Debió bloquear opencode-go/deepseek-v4-pro y no degradar. cli={cli!r}")

    # 4) Bloqueo de modelos free por defecto (smoke test requiere override explícito)
    _setenv("OPENCODE_ALLOW_FREE_SMOKE_TEST", None)
    ok, cli, err = resolve_cli_model(logical_model="opencode/deepseek-v4-flash-free", available_models=available)
    if ok:
        raise AssertionError("Modelos *-free deben estar bloqueados por defecto (sin OPENCODE_ALLOW_FREE_SMOKE_TEST).")

    # 5) Permitido explícito de modelos free (solo smoke test)
    _setenv("OPENCODE_ALLOW_FREE_SMOKE_TEST", "1")
    ok, cli, err = resolve_cli_model(logical_model="opencode/deepseek-v4-flash-free", available_models=available)
    if not ok:
        raise AssertionError(f"Con OPENCODE_ALLOW_FREE_SMOKE_TEST=1 debería permitir. err={err!r}")

    # 6) big-pickle bloqueado por defecto
    _setenv("OPENCODE_ALLOW_BIG_PICKLE", None)
    ok, cli, err = resolve_cli_model(logical_model="opencode/big-pickle", available_models=available)
    if ok:
        raise AssertionError("opencode/big-pickle debe estar bloqueado por defecto (sin OPENCODE_ALLOW_BIG_PICKLE).")

    # 7) big-pickle permitido explícito
    _setenv("OPENCODE_ALLOW_BIG_PICKLE", "1")
    ok, cli, err = resolve_cli_model(logical_model="opencode/big-pickle", available_models=available)
    if not ok:
        raise AssertionError(f"Con OPENCODE_ALLOW_BIG_PICKLE=1 debería permitir. err={err!r}")

    print("ok")


if __name__ == "__main__":
    main()
