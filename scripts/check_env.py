#!/usr/bin/env python3
"""
check_env.py

Valida que las variables de entorno requeridas estén presentes.
No imprime valores reales.
"""

from __future__ import annotations

import os
import sys


REQUIRED_VARS = [
    "DB_HOST",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",

]

OPTIONAL_VARS = [
    "OPENAI_API_KEY",
    "RESEND_API_KEY",
    "AZURE_STORAGE_CONNECTION_STRING",

]


def main() -> None:
    missing = [name for name in REQUIRED_VARS if not os.getenv(name)]

    if missing:
        print("Missing required environment variables:")
        for name in missing:
            print(f"- {name}")
        sys.exit(1)

    print("Required environment variables are present.")

    configured_optional = [name for name in OPTIONAL_VARS if os.getenv(name)]
    if configured_optional:
        print("Configured optional variables:")
        for name in configured_optional:
            print(f"- {name}")


if __name__ == "__main__":
    main()
