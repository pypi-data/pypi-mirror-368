#!/usr/bin/env python3
"""Invoker pattern basic example.

Runs a function in another module remotely without importing Flow in user code.
"""

from pathlib import Path

from flow import invoke


def main() -> int:
    # Ensure the user module exists next to this script
    module = Path(__file__).with_name("user_code.py")
    if not module.exists():
        raise SystemExit(f"Missing user module: {module}")

    result = invoke(
        str(module),
        "add_and_scale",
        args=[3, 4],
        kwargs={"scale": 10},
        gpu="a100",
        max_price_per_hour=5.0,
    )
    print("Result:", result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
