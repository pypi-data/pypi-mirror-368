#!/usr/bin/env python3
"""Repo-wide smoke import for the Flow SDK.

Adds src/ to sys.path and attempts to import every module under the
top-level package 'flow'. Prints a summary and exits non-zero on failure.
"""

from __future__ import annotations

import importlib
import pkgutil
import sys
import traceback
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).parent
    src_path = repo_root / "src"
    if not src_path.exists():
        print(f"ERROR: src directory not found at {src_path}")
        return 2

    sys.path.insert(0, str(src_path))

    base_pkg_path = src_path / "flow"
    if not base_pkg_path.exists():
        print(f"ERROR: flow package not found under {src_path}")
        return 2

    print(f"Running smoke import for package 'flow' from {base_pkg_path}")

    failures: list[tuple[str, str]] = []
    successes: int = 0

    # Walk all modules under flow.*
    for _, module_name, _ in pkgutil.walk_packages([str(base_pkg_path)], prefix="flow."):
        try:
            importlib.import_module(module_name)
            successes += 1
        except Exception:
            failures.append((module_name, traceback.format_exc()))

    print("")
    print(f"Successfully imported {successes} modules under 'flow'.")
    if failures:
        print(f"\nFAILED to import {len(failures)} modules:\n")
        for name, tb in failures:
            print(f"--- {name} ---")
            print(tb)
        return 1

    print("All modules imported successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
