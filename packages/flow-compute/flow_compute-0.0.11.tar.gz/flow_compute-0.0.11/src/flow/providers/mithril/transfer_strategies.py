"""File transfer strategies for uploading code to Mithril instances.

This module provides various strategies for transferring files to remote
instances, with rsync as the primary implementation for efficiency.
"""

import logging
import os
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, List, Optional, Protocol

from flow.errors import FlowError

logger = logging.getLogger(__name__)


class TransferError(FlowError):
    """Raised when file transfer fails."""

    pass


@dataclass
class TransferProgress:
    """Progress information for ongoing transfer."""

    bytes_transferred: int
    total_bytes: Optional[int]
    percentage: Optional[float]
    speed: Optional[str]  # e.g., "2.34MB/s"
    eta: Optional[str]  # e.g., "0:00:03"
    current_file: Optional[str]

    @property
    def is_complete(self) -> bool:
        """Check if transfer is complete."""
        return self.percentage is not None and self.percentage >= 100


@dataclass
class TransferResult:
    """Result of a file transfer operation."""

    success: bool
    bytes_transferred: int
    duration_seconds: float
    files_transferred: int
    error_message: Optional[str] = None

    @property
    def transfer_rate(self) -> str:
        """Calculate average transfer rate."""
        if self.duration_seconds == 0:
            return "N/A"
        rate_mbps = (self.bytes_transferred / self.duration_seconds) / (1024 * 1024)
        return f"{rate_mbps:.2f} MB/s"


class ITransferStrategy(Protocol):
    """Protocol for file transfer strategies."""

    def transfer(
        self,
        source: Path,
        target: str,
        connection: "SSHConnectionInfo",
        progress_callback: Optional[Callable[[TransferProgress], None]] = None,
    ) -> TransferResult:
        """Transfer files from source to target.

        Args:
            source: Local source directory
            target: Remote target path
            connection: SSH connection information
            progress_callback: Optional callback for progress updates

        Returns:
            TransferResult with outcome details

        Raises:
            TransferError: If transfer fails
        """
        ...


class RsyncTransferStrategy:
    """Transfer files using rsync for efficiency.

    Uses rsync for transfers with support for:
    - Compression during transfer
    - Incremental updates
    - Progress reporting
    - .flowignore exclusions
    """

    def __init__(self):
        """Initialize rsync transfer strategy."""
        self.rsync_path = self._find_rsync()

    def transfer(
        self,
        source: Path,
        target: str,
        connection: "SSHConnectionInfo",
        progress_callback: Optional[Callable[[TransferProgress], None]] = None,
    ) -> TransferResult:
        """Transfer files using rsync.

        Args:
            source: Local source directory
            target: Remote target path
            connection: SSH connection information
            progress_callback: Optional callback for progress updates

        Returns:
            TransferResult with outcome details

        Raises:
            TransferError: If rsync fails
        """
        if not source.exists():
            raise TransferError(f"Source path does not exist: {source}")

        if not source.is_dir():
            raise TransferError(f"Source must be a directory: {source}")

        # Create exclude file from .flowignore
        exclude_file = self._create_exclude_file(source)

        # Optional: prepare git-based incremental file list (auto-detected)
        files_from_file = None  # type: Optional[Path]
        files_from_is_from0 = False
        files_from_count = 0
        try:
            git_files = self._get_git_changed_files(source)
            if git_files and git_files.get("list_path") and git_files.get("count", 0) >= 0:
                files_from_file = git_files["list_path"]
                files_from_is_from0 = git_files.get("from0", False)
                files_from_count = git_files.get("count", 0)
                if files_from_count == 0:
                    # Nothing changed; short-circuit
                    logger.info("Git-based sync detected no changes; skipping upload.")
                    return TransferResult(
                        success=True,
                        bytes_transferred=0,
                        duration_seconds=0.0,
                        files_transferred=0,
                        error_message=None,
                    )
                logger.info(f"Using git-based incremental sync: {files_from_count} file(s)")
        except Exception:
            # Any failure in git detection falls back to normal rsync behavior
            files_from_file = None

        try:
            # Build rsync command
            cmd = self._build_rsync_command(
                source,
                target,
                connection,
                exclude_file,
                files_from=files_from_file,
                use_from0=files_from_is_from0,
            )

            # Fast path: dry-run to detect no-op syncs
            preflight_cmd = cmd.copy()
            # Insert dry-run flags after rsync binary
            preflight_cmd.insert(1, "--dry-run")
            preflight_cmd.insert(2, "--itemize-changes")

            preflight = subprocess.run(preflight_cmd, capture_output=True, text=True)
            if preflight.returncode == 0:
                # If no changes, rsync outputs stats but no change lines starting with >f, *deleting, etc.
                has_changes = False
                for line in preflight.stdout.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    # rsync itemize lines start with a change marker, and deletions contain "*deleting"
                    if line.startswith(">") or line.startswith("cd+") or "*deleting" in line:
                        has_changes = True
                        break
                if not has_changes:
                    logger.info("Rsync dry-run detected no changes; skipping upload.")
                    return TransferResult(
                        success=True,
                        bytes_transferred=0,
                        duration_seconds=0.0,
                        files_transferred=0,
                        error_message=None,
                    )

            # Execute transfer
            start_time = time.time()
            result = self._execute_with_progress(cmd, progress_callback, source_path=source)
            duration = time.time() - start_time

            # Parse results
            return TransferResult(
                success=True,
                bytes_transferred=result["bytes_transferred"],
                duration_seconds=duration,
                files_transferred=result["files_transferred"],
                error_message=None,
            )

        except Exception as e:
            logger.error(f"Rsync transfer failed: {e}")
            raise TransferError(f"Transfer failed: {str(e)}") from e
        finally:
            # Clean up exclude file
            if exclude_file and exclude_file.exists():
                exclude_file.unlink()
            # Clean up temp files-from list if created
            if files_from_file and files_from_file.exists():
                try:
                    files_from_file.unlink()
                except Exception:
                    pass

    def _find_rsync(self) -> str:
        """Find rsync executable.

        Returns:
            Path to rsync executable

        Raises:
            TransferError: If rsync not found
        """
        try:
            result = subprocess.run(["which", "rsync"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        # Try common locations
        for path in ["/usr/bin/rsync", "/usr/local/bin/rsync", "/opt/homebrew/bin/rsync"]:
            if Path(path).exists():
                return path

        raise TransferError(
            "rsync not found. Please install rsync:\n"
            "  - macOS: brew install rsync\n"
            "  - Ubuntu/Debian: apt-get install rsync\n"
            "  - RHEL/CentOS: yum install rsync"
        )

    def _create_exclude_file(self, source: Path) -> Optional[Path]:
        """Create exclude file from .flowignore patterns.

        Args:
            source: Source directory

        Returns:
            Path to temporary exclude file, or None if no .flowignore
        """
        flowignore = source / ".flowignore"
        if not flowignore.exists():
            # Use default exclusions
            default_excludes = [
                ".git/",
                ".git",
                "__pycache__/",
                "*.pyc",
                ".pytest_cache/",
                ".mypy_cache/",
                ".ruff_cache/",
                ".coverage",
                "*.egg-info/",
                ".env",
                ".venv/",
                "venv/",
                "node_modules/",
                ".DS_Store",
                "*.swp",
                "*.swo",
                "*~",
                ".idea/",
                ".vscode/",
                "*.log",
            ]

            exclude_file = tempfile.NamedTemporaryFile(
                mode="w", delete=False, prefix="flow-rsync-exclude-"
            )
            exclude_file.write("\n".join(default_excludes))
            exclude_file.close()
            return Path(exclude_file.name)

        # Create temp file with .flowignore contents
        exclude_file = tempfile.NamedTemporaryFile(
            mode="w", delete=False, prefix="flow-rsync-exclude-"
        )

        with open(flowignore, "r") as f:
            # Process .flowignore patterns
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith("#"):
                    exclude_file.write(line + "\n")

        exclude_file.close()
        return Path(exclude_file.name)

    def _get_git_changed_files(self, source: Path) -> Optional[dict]:
        """Build a NUL-separated list of changed files for rsync.

        Returns a dict with keys:
        - list_path: Path to temp file containing NUL-separated relative paths
        - count: number of paths written
        - from0: True (indicates NUL-separated list)

        On any error or when not inside a git repository, returns None to
        signal fallback to full rsync.
        """
        # Allow opting out via environment variable
        disable = os.environ.get("FLOW_GIT_INCREMENTAL", "1").lower() in {"0", "false", "no"}
        if disable:
            return None

        try:
            # Verify this is a git repository
            check = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=source,
                capture_output=True,
                text=True,
            )
            if check.returncode != 0 or check.stdout.strip().lower() != "true":
                return None

            # Helper to run git and parse NUL-separated output
            def _run_git(args: list[str]) -> list[str]:
                res = subprocess.run(
                    ["git", "-c", "core.quotepath=false", *args],
                    cwd=source,
                    capture_output=True,
                    text=False,  # capture bytes for -z
                )
                if res.returncode != 0 or res.stdout is None:
                    return []
                data = res.stdout
                # Split on NUL for -z-safe parsing
                paths = [p.decode("utf-8", "surrogateescape") for p in data.split(b"\0") if p]
                return paths

            changed: set[str] = set()
            deleted: set[str] = set()

            # Unstaged changes (Added/Copied/Modified/Renamed)
            for p in _run_git(["diff", "--name-only", "-z", "--diff-filter=ACMR"]):
                changed.add(p)

            # Staged changes
            for p in _run_git(["diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"]):
                changed.add(p)

            # Untracked files
            for p in _run_git(["ls-files", "--others", "--exclude-standard", "-z"]):
                changed.add(p)

            # Deletions (unstaged + staged + known deleted)
            for p in _run_git(["diff", "--name-only", "-z", "--diff-filter=D"]):
                deleted.add(p)
            for p in _run_git(["diff", "--cached", "--name-only", "-z", "--diff-filter=D"]):
                deleted.add(p)
            for p in _run_git(["ls-files", "--deleted", "-z"]):
                deleted.add(p)

            all_paths = list(changed | deleted)

            # Create a temp file with NUL-separated entries (rsync --from0)
            tmp = tempfile.NamedTemporaryFile(
                mode="wb", delete=False, prefix="flow-rsync-files-", suffix=".lst"
            )
            try:
                for rel_path in all_paths:
                    # Ensure paths are relative (git outputs relative paths by default)
                    rel_bytes = rel_path.encode("utf-8", "surrogateescape")
                    tmp.write(rel_bytes + b"\0")
            finally:
                tmp.close()

            # Optionally enable deletion of missing args if requested
            enable_delete_missing = (
                os.environ.get("FLOW_RSYNC_DELETE_MISSING_ARGS", "0").lower() in {"1", "true", "yes"}
            )

            return {
                "list_path": Path(tmp.name),
                "count": len(all_paths),
                "from0": True,
                "enable_delete_missing": enable_delete_missing,
            }

        except Exception:
            return None

    def _build_rsync_command(
        self,
        source: Path,
        target: str,
        connection: "SSHConnectionInfo",
        exclude_file: Optional[Path],
        *,
        files_from: Optional[Path] = None,
        use_from0: bool = False,
    ) -> List[str]:
        """Build rsync command with appropriate flags.

        Args:
            source: Local source directory
            target: Remote target path
            connection: SSH connection details
            exclude_file: Optional path to exclude file

        Returns:
            List of command arguments
        """
        # SSH command for rsync
        ssh_cmd = (
            f"ssh -p {connection.port} "
            f"-i {connection.key_path} "
            f"-o StrictHostKeyChecking=no "
            f"-o UserKnownHostsFile=/dev/null "
            f"-o ConnectTimeout=10 "
            f"-o ServerAliveInterval=10 "
            f"-o ServerAliveCountMax=3"
        )

        cmd = [
            self.rsync_path,
            "-avz",  # archive, verbose, compress
            "--update",  # Skip files that are newer on receiver (faster for already-synced)
            "--progress",  # Show progress
            "--human-readable",  # Human-readable sizes
            "--stats",  # Show statistics
            "--partial",  # Keep partial files for resume
            "--partial-dir=.rsync-partial",  # Store partials in hidden dir
            "--timeout=30",  # I/O timeout for network issues
            "--contimeout=10",  # Connection timeout
            "-e",
            ssh_cmd,  # Use custom SSH command
        ]

        # Add exclude file if present
        if exclude_file:
            cmd.extend(["--exclude-from", str(exclude_file)])

        # Add files-from list for git-based incremental sync
        if files_from:
            cmd.extend(["--files-from", str(files_from)])
            if use_from0:
                cmd.append("--from0")
            # Deleting missing args can break on older remote rsync; guard via env
            if os.environ.get("FLOW_RSYNC_DELETE_MISSING_ARGS", "0").lower() in {"1", "true", "yes"}:
                cmd.append("--delete-missing-args")

        # Add source and destination
        # Trailing slash on source to copy contents, not directory itself
        cmd.append(f"{source}/")
        cmd.append(f"{connection.destination}:{target}/")

        return cmd

    def _execute_with_progress(
        self,
        cmd: List[str],
        progress_callback: Optional[Callable[[TransferProgress], None]],
        source_path: Optional[Path] = None,
    ) -> dict:
        """Execute rsync with progress monitoring.

        Args:
            cmd: Rsync command to execute
            progress_callback: Optional progress callback
            source_path: Source directory path for calculating statistics

        Returns:
            Dictionary with transfer statistics

        Raises:
            TransferError: If rsync fails
        """
        logger.debug(f"Executing rsync: {' '.join(cmd[:3])}...")

        # Track statistics
        bytes_transferred = 0
        files_transferred = 0
        current_file = None

        try:
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
            )

            # Process output line by line
            for line in process.stdout:
                line = line.strip()
                if not line:
                    continue

                # Parse progress updates
                progress = self._parse_rsync_progress(line)
                if progress and progress_callback:
                    if progress.current_file:
                        current_file = progress.current_file
                    progress_callback(progress)

                # Track statistics
                if "Number of files transferred:" in line:
                    match = re.search(r"(\d+)", line)
                    if match:
                        files_transferred = int(match.group(1))

                elif "Total transferred file size:" in line:
                    # Parse size (can be in various units)
                    match = re.search(r"([\d,]+)", line)
                    if match:
                        bytes_transferred = int(match.group(1).replace(",", ""))

            # Wait for completion
            process.wait()

            if process.returncode != 0:
                stderr = process.stderr.read()
                raise TransferError(f"rsync failed with code {process.returncode}: {stderr}")

            # Return collected stats
            return {
                "bytes_transferred": bytes_transferred,
                "files_transferred": files_transferred,
            }

        except Exception as e:
            raise TransferError(f"rsync execution failed: {e}") from e

    def _parse_rsync_progress(self, line: str) -> Optional[TransferProgress]:
        """Parse rsync progress line into structured data.

        Args:
            line: A line of rsync output

        Returns:
            TransferProgress if parsed, otherwise None
        """
        # Example formats to parse:
        # 123,456  12%   2.34MB/s    0:00:03 (xfr#12, to-chk=345/678)
        # filename.ext
        # Number of files transferred: 12
        # Total transferred file size: 1,234,567 bytes
        try:
            # Detect current file lines (not numeric progress)
            if (
                not any(ch.isdigit() for ch in line)
                and not line.startswith("Total ")
                and not line.startswith("Number ")
            ):
                return TransferProgress(
                    bytes_transferred=0,
                    total_bytes=None,
                    percentage=None,
                    speed=None,
                    eta=None,
                    current_file=line,
                )

            # Parse percentage, speed, eta if present
            pct_match = re.search(r"\b(\d+)%\b", line)
            speed_match = re.search(r"(\d+\.\d+\s*[kKmMgG][bB]/s)", line)
            eta_match = re.search(r"(\d+:\d+:\d+|\d+:\d+)\s*$", line)

            percentage = float(pct_match.group(1)) if pct_match else None
            speed = speed_match.group(1) if speed_match else None
            eta = eta_match.group(1) if eta_match else None

            return TransferProgress(
                bytes_transferred=0,  # We track totals from stats lines
                total_bytes=None,
                percentage=percentage,
                speed=speed,
                eta=eta,
                current_file=None,
            )
        except Exception:
            return None
