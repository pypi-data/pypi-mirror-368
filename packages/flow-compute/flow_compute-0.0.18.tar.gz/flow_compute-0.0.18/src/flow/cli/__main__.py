"""Enable running the CLI as a module: python -m flow.cli"""

import sys

from .app import cli

if __name__ == "__main__":
    sys.exit(cli())
