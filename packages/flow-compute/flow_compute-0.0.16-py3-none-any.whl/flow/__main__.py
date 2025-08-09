"""Direct module execution support for flow."""

import sys

# Check Python version before any imports that might use modern syntax
if sys.version_info < (3, 10):
    print(
        f"Error: Flow SDK requires Python 3.10 or later. "
        f"You are using Python {sys.version_info.major}.{sys.version_info.minor}.\n\n"
        f"Recommended: Install and use 'uv' for automatic Python version management:\n"
        f"  curl -LsSf https://astral.sh/uv/install.sh | sh\n"
        f"  uv tool install flow-compute\n\n"
        f"Alternative: Upgrade your Python installation to 3.10 or later.",
        file=sys.stderr,
    )
    sys.exit(1)

from flow.cli import main

if __name__ == "__main__":
    main()
