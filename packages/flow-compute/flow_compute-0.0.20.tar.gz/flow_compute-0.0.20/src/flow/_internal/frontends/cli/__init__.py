"""CLI frontend adapter for Flow SDK.

The CLI adapter provides natural language and command-line interfaces for Flow,
allowing users to submit tasks using simple commands or natural language descriptions.
"""

from flow._internal.frontends.cli.adapter import CLIFrontendAdapter

__all__ = ["CLIFrontendAdapter"]
