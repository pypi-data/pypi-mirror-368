"""Cross-platform clipboard support for Flow CLI.

Provides unified clipboard access with graceful fallback for environments
without clipboard support. Designed for copying task IDs, commands, and
other CLI output.
"""

import os
import platform
import subprocess
import sys
from typing import Optional


class ClipboardManager:
    """Cross-platform clipboard operations with graceful fallback."""

    def __init__(self):
        """Initialize clipboard manager."""
        self._clipboard_available = None
        self._copy_command = None
        self._paste_command = None
        self._detect_clipboard_commands()

    def _detect_clipboard_commands(self) -> None:
        """Detect platform-specific clipboard commands."""
        system = platform.system()

        if system == "Darwin":  # macOS
            self._copy_command = ["pbcopy"]
            self._paste_command = ["pbpaste"]
        elif system == "Linux":
            # Try different clipboard utilities in order of preference
            if self._command_exists("xclip"):
                self._copy_command = ["xclip", "-selection", "clipboard"]
                self._paste_command = ["xclip", "-selection", "clipboard", "-o"]
            elif self._command_exists("xsel"):
                self._copy_command = ["xsel", "--clipboard", "--input"]
                self._paste_command = ["xsel", "--clipboard", "--output"]
            elif self._command_exists("wl-copy") and os.environ.get("WAYLAND_DISPLAY"):
                # Wayland support
                self._copy_command = ["wl-copy"]
                self._paste_command = ["wl-paste"]
        elif system == "Windows":
            # Windows has clip.exe for copy, PowerShell for paste
            self._copy_command = ["clip.exe"]
            self._paste_command = ["powershell.exe", "-command", "Get-Clipboard"]

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH.

        Args:
            command: Command name to check

        Returns:
            True if command exists
        """
        try:
            subprocess.run(
                ["which", command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @property
    def is_available(self) -> bool:
        """Check if clipboard operations are available.

        Returns:
            True if clipboard can be accessed
        """
        if self._clipboard_available is not None:
            return self._clipboard_available

        # Check if we have copy command
        if not self._copy_command:
            self._clipboard_available = False
            return False

        # Test clipboard access
        try:
            self.copy("test")
            self._clipboard_available = True
        except Exception:
            self._clipboard_available = False

        return self._clipboard_available

    def copy(self, text: str) -> bool:
        """Copy text to clipboard.

        Args:
            text: Text to copy

        Returns:
            True if successful, False otherwise
        """
        if not self._copy_command:
            return False

        try:
            process = subprocess.Popen(
                self._copy_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            process.communicate(input=text.encode("utf-8"))
            return process.returncode == 0
        except Exception:
            return False

    def paste(self) -> Optional[str]:
        """Get text from clipboard.

        Returns:
            Clipboard contents or None if failed
        """
        if not self._paste_command:
            return None

        try:
            result = subprocess.run(self._paste_command, capture_output=True, text=True, check=True)
            return result.stdout
        except Exception:
            return None

    def copy_with_feedback(self, text: str, description: str = "Text") -> str:
        """Copy text and return feedback message.

        Args:
            text: Text to copy
            description: Description of what was copied

        Returns:
            Feedback message for user
        """
        if self.copy(text):
            return f"✓ {description} copied to clipboard"
        else:
            return f"✗ Could not copy to clipboard (you can manually copy: {text})"


# Global clipboard instance
clipboard = ClipboardManager()
