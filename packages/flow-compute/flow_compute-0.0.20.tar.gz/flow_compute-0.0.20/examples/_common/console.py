from __future__ import annotations

import sys


def _print(prefix: str, message: str) -> None:
    sys.stdout.write(f"{prefix} {message}\n")
    sys.stdout.flush()


def info(message: str) -> None:
    _print("[INFO]", message)


def warn(message: str) -> None:
    _print("[WARN]", message)


def error(message: str) -> None:
    _print("[ERROR]", message)


def success(message: str) -> None:
    _print("[ OK ]", message)
