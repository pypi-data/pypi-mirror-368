"""Shell completion support for Flow CLI.

This internal module provides shell completion functionality for bash, zsh,
and fish shells. It's automatically configured during `flow init` and provides:

- Command and subcommand completion
- Dynamic task ID completion for cancel, logs, ssh commands
- Volume ID completion for volume commands
- YAML file completion for run command
- GPU instance type suggestions

The completion functions are used by Click's shell_complete parameter
on command arguments and options.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console

from flow.api import Flow
from flow.cli.utils.config_validator import ConfigValidator
from flow.errors import FlowError


console = Console()


class CompletionCommand:
    """Shell completion helper for Flow CLI."""

    SUPPORTED_SHELLS = ["bash", "zsh", "fish"]

    SHELL_CONFIGS = {
        "bash": {
            "rc_file": "~/.bashrc",
            "completion_dir": "~/.bash_completion.d",
        },
        "zsh": {
            "rc_file": "~/.zshrc",
            "completion_dir": "~/.zsh/completions",
        },
        "fish": {
            "rc_file": "~/.config/fish/config.fish",
            "completion_dir": "~/.config/fish/completions",
        },
    }

    def _render_completion_script(self, shell: str) -> str:
        """Return the completion script text for a given shell.

        This mirrors _generate_completion but returns a string instead of echoing.
        """
        import subprocess
        import shutil

        # Try to use the installed 'flow' command first
        flow_cmd = shutil.which("flow")
        cmd = [flow_cmd] if flow_cmd else [sys.executable, "-m", "flow.cli"]

        # Ask Click to output the completion script
        result = subprocess.run(
            cmd,
            env={**os.environ, "_FLOW_COMPLETE": f"{shell}_source"},
            capture_output=True,
            text=True,
        )

        if result.stdout and not result.stdout.startswith("Usage:"):
            return result.stdout

        # Fallback: manual script (development mode)
        if shell == "bash":
            return """_flow_completion() {
    local IFS=$'\n'
    local response

    response=$(env COMP_WORDS=\"${COMP_WORDS[*]}\" COMP_CWORD=$COMP_CWORD _FLOW_COMPLETE=bash_complete flow)

    for completion in $response; do
        IFS=',' read type value <<< \"$completion\"

        if [[ $type == 'dir' ]]; then
            COMPREPLY=()
            compopt -o dirnames
        elif [[ $type == 'file' ]]; then
            COMPREPLY=()
            compopt -o default
        elif [[ $type == 'plain' ]]; then
            COMPREPLY+=($value)
        fi
    done

    return 0
}

complete -o nosort -F _flow_completion flow"""
        if shell == "zsh":
            return """#compdef flow

_flow_completion() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    (( ! $+commands[flow] )) && return 1

    response=(\"${(@f)$(env COMP_WORDS=\"${words[*]}\" COMP_CWORD=$((CURRENT-1)) _FLOW_COMPLETE=zsh_complete flow)}\")

    for type key descr in ${response}; do
        if [[ \"$type\" == \"plain\" ]]; then
            if [[ \"$descr\" == \"_\" ]]; then
                completions+=(\"$key\")
            else
                completions_with_descriptions+=(\"$key\":\"$descr\")
            fi
        elif [[ \"$type\" == \"dir\" ]]; then
            _path_files -/
            return
        elif [[ \"$type\" == \"file\" ]]; then
            _path_files
            return
        fi
    done

    if [ -n \"$completions_with_descriptions\" ]; then
        _describe -t commands completion completions_with_descriptions
    fi

    if [ -n \"$completions\" ]; then
        compadd -U -a completions
    fi
}

if [[ $zsh_eval_context[-1] == loadautofunc ]]; then
    _flow_completion \"$@\"
else
    compdef _flow_completion flow
fi"""
        if shell == "fish":
            return '''function _flow_completion
    set -l response (env COMP_WORDS=(commandline -cp) COMP_CWORD=(commandline -t) _FLOW_COMPLETE=fish_complete flow)

    for completion in $response
        set -l metadata (string split "," $completion)

        if test $metadata[1] = "dir"
            __fish_complete_directories
        else if test $metadata[1] = "file"
            __fish_complete_path
        else if test $metadata[1] = "plain"
            echo $metadata[2]
        end
    end
end

complete -c flow -f -a "(_flow_completion)"'''
        raise FlowError(f"Unsupported shell: {shell}")

    def _get_standard_completion_path(self, shell: str) -> Path:
        """Return the standard completion file path for the given shell."""
        if shell == "bash":
            return Path(os.path.expanduser("~/.bash_completion.d/flow"))
        if shell == "zsh":
            return Path(os.path.expanduser("~/.zsh/completions/_flow"))
        if shell == "fish":
            return Path(os.path.expanduser("~/.config/fish/completions/flow.fish"))
        raise FlowError(f"Unsupported shell: {shell}")

    def _generate_completion(self, shell: str) -> None:
        """Generate completion script for specified shell."""
        try:
            import subprocess
            import shutil

            # Try to use the installed 'flow' command first
            flow_cmd = shutil.which("flow")
            if flow_cmd:
                cmd = [flow_cmd]
            else:
                # Fallback to running as module
                cmd = [sys.executable, "-m", "flow.cli"]

            # Click will output the completion script when the env var is set
            result = subprocess.run(
                cmd,
                env={**os.environ, "_FLOW_COMPLETE": f"{shell}_source"},
                capture_output=True,
                text=True,
            )

            if result.stdout and not result.stdout.startswith("Usage:"):
                # Output the completion script
                click.echo(result.stdout, nl=False)
            else:
                # Provide manual completion script for development mode
                if shell == "bash":
                    script = """_flow_completion() {
    local IFS=$'\n'
    local response

    response=$(env COMP_WORDS="${COMP_WORDS[*]}" COMP_CWORD=$COMP_CWORD _FLOW_COMPLETE=bash_complete flow)

    for completion in $response; do
        IFS=',' read type value <<< "$completion"

        if [[ $type == 'dir' ]]; then
            COMPREPLY=()
            compopt -o dirnames
        elif [[ $type == 'file' ]]; then
            COMPREPLY=()
            compopt -o default
        elif [[ $type == 'plain' ]]; then
            COMPREPLY+=($value)
        fi
    done

    return 0
}

complete -o nosort -F _flow_completion flow"""
                elif shell == "zsh":
                    script = """#compdef flow

_flow_completion() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    (( ! $+commands[flow] )) && return 1

    response=("${(@f)$(env COMP_WORDS="${words[*]}" COMP_CWORD=$((CURRENT-1)) _FLOW_COMPLETE=zsh_complete flow)}")

    for type key descr in ${response}; do
        if [[ "$type" == "plain" ]]; then
            if [[ "$descr" == "_" ]]; then
                completions+=("$key")
            else
                completions_with_descriptions+=("$key":"$descr")
            fi
        elif [[ "$type" == "dir" ]]; then
            _path_files -/
            return
        elif [[ "$type" == "file" ]]; then
            _path_files
            return
        fi
    done

    if [ -n "$completions_with_descriptions" ]; then
        _describe -t commands completion completions_with_descriptions
    fi

    if [ -n "$completions" ]; then
        compadd -U -a completions
    fi
}

if [[ $zsh_eval_context[-1] == loadautofunc ]]; then
    _flow_completion "$@"
else
    compdef _flow_completion flow
fi"""
                elif shell == "fish":
                    script = '''function _flow_completion
    set -l response (env COMP_WORDS=(commandline -cp) COMP_CWORD=(commandline -t) _FLOW_COMPLETE=fish_complete flow)

    for completion in $response
        set -l metadata (string split "," $completion)

        if test $metadata[1] = "dir"
            __fish_complete_directories
        else if test $metadata[1] = "file"
            __fish_complete_path
        else if test $metadata[1] = "plain"
            echo $metadata[2]
        end
    end
end

complete -c flow -f -a "(_flow_completion)"'''
                else:
                    console.print(f"[red]Error: Unsupported shell: {shell}[/red]")
                    return

                click.echo(script)

        except Exception as e:
            from rich.markup import escape
            console.print(f"[red]Error generating completion: {escape(str(e))}[/red]")

    def _install_completion(self, shell: Optional[str], path: Optional[str]) -> None:
        """Install completion script to user's shell configuration."""
        try:
            # Auto-detect shell if not specified
            if not shell:
                shell = self._detect_shell()
                if not shell:
                    console.print(
                        "[red]Could not auto-detect shell. Please specify with --shell[/red]"
                    )
                    return

            console.print(f"Installing completion for {shell}...")

            # If a path is provided, treat it as an rc file to append a guarded eval line
            if path:
                install_path = Path(path).expanduser()
                install_path.parent.mkdir(parents=True, exist_ok=True)
                completion_line = self._get_completion_line(shell)
                existing = install_path.read_text() if install_path.exists() else ""
                if completion_line in existing:
                    console.print(
                        f"[yellow]Completion already installed in {install_path}[/yellow]"
                    )
                else:
                    with open(install_path, "a") as f:
                        f.write(f"\n# Flow CLI completion\n{completion_line}\n")
                    from flow.cli.utils.theme_manager import theme_manager as _tm
                    success_color = _tm.get_color("success")
                    console.print(f"[{success_color}]✓ Appended to {install_path}[/{success_color}]")
                console.print(f"\nTo enable completion now, run:\n  [bold]source {install_path}[/bold]")
                console.print(f"Or restart your {shell} shell.")
                return

            # Preferred: write completion script into standard per-shell location
            target_file = self._get_standard_completion_path(shell)
            target_file.parent.mkdir(parents=True, exist_ok=True)

            script_text = self._render_completion_script(shell)
            target_file.write_text(script_text)
            from flow.cli.utils.theme_manager import theme_manager as _tm2
            success_color = _tm2.get_color("success")
            console.print(f"[{success_color}]✓ Installed completion file: {target_file}[/{success_color}]")

            # Ensure it's active: for bash/zsh we also add a guarded eval line in rc as fallback
            rc_file = Path(self.SHELL_CONFIGS[shell]["rc_file"]).expanduser()
            completion_line = self._get_completion_line(shell)
            rc_content = rc_file.read_text() if rc_file.exists() else ""
            if completion_line not in rc_content:
                rc_file.parent.mkdir(parents=True, exist_ok=True)
                with open(rc_file, "a") as f:
                    f.write(f"\n# Flow CLI completion\n{completion_line}\n")
                from flow.cli.utils.theme_manager import theme_manager as _tm3
                success_color = _tm3.get_color("success")
                console.print(f"[{success_color}]✓ Updated {rc_file} with activation line[/{success_color}]")

            # Final guidance
            console.print(f"\nTo enable completion now, run:\n  [bold]source {rc_file}[/bold]")
            console.print(f"Or restart your {shell} shell.")

        except Exception as e:
            from rich.markup import escape
            console.print(f"[red]Installation failed: {escape(str(e))}[/red]")

    def _uninstall_completion(self, shell: Optional[str], path: Optional[str]) -> None:
        """Uninstall completion by removing files and rc entries."""
        try:
            if not shell:
                shell = self._detect_shell()
                if not shell:
                    console.print(
                        "[red]Could not auto-detect shell. Please specify with --shell[/red]"
                    )
                    return

            console.print(f"Uninstalling completion for {shell}...")

            # Remove standard completion file
            try:
                target_file = self._get_standard_completion_path(shell)
                if target_file.exists():
                    target_file.unlink()
                    from flow.cli.utils.theme_manager import theme_manager as _tm4
                    success_color = _tm4.get_color("success")
                    console.print(f"[{success_color}]✓ Removed {target_file}[/{success_color}]")
            except Exception:
                pass

            # Determine rc file to clean
            rc_file = Path(path).expanduser() if path else Path(self.SHELL_CONFIGS[shell]["rc_file"]).expanduser()
            if rc_file.exists():
                content = rc_file.read_text()
                # Remove our marker block or guarded eval lines
                lines = content.splitlines()
                new_lines = []
                skip_next = False
                for line in lines:
                    if skip_next:
                        skip_next = False
                        continue
                    if line.strip() == "# Flow CLI completion":
                        # Skip this marker and the very next line (the activation line)
                        skip_next = True
                        continue
                    if ("_FLOW_COMPLETE=" in line and "flow" in line) or ("python -m flow.cli completion generate" in line):
                        # Be defensive: remove any stray activation lines
                        continue
                    new_lines.append(line)
                if new_lines != lines:
                    rc_file.write_text("\n".join(new_lines) + ("\n" if content.endswith("\n") else ""))
                    from flow.cli.utils.theme_manager import theme_manager as _tm5
                    success_color = _tm5.get_color("success")
                    console.print(f"[{success_color}]✓ Cleaned {rc_file}[/{success_color}]")

            from flow.cli.utils.theme_manager import theme_manager as _tm6
            success_color = _tm6.get_color("success")
            console.print(
                f"[{success_color}]✓ Completion uninstalled[/{success_color}]\nYou may need to restart your shell or re-source your rc file."
            )
        except Exception as e:
            from rich.markup import escape
            console.print(f"[red]Uninstall failed: {escape(str(e))}[/red]")

    def _detect_shell(self) -> Optional[str]:
        """Detect user's current shell."""
        # Check SHELL environment variable
        shell_path = os.environ.get("SHELL", "")
        shell_name = os.path.basename(shell_path)

        if shell_name in self.SUPPORTED_SHELLS:
            return shell_name

        # Check parent process name
        try:
            import psutil

            parent = psutil.Process(os.getppid())
            parent_name = parent.name()

            for shell in self.SUPPORTED_SHELLS:
                if shell in parent_name:
                    return shell
        except Exception:
            pass

        return None

    def _get_completion_line(self, shell: str) -> str:
        """Get the line to add to shell config for completion."""
        import shutil

        # Check if flow is installed as a command
        if shutil.which("flow"):
            # Guard per-shell to avoid evaluating the wrong script in mixed environments
            if shell == "bash":
                return 'if [ -n "${BASH_VERSION-}" ]; then eval "$(_FLOW_COMPLETE=bash_source flow)"; fi'
            elif shell == "zsh":
                return 'if [ -n "${ZSH_VERSION-}" ]; then eval "$(_FLOW_COMPLETE=zsh_source flow)"; fi'
            elif shell == "fish":
                # Fish should use a pipe to source the generated script
                return 'if test -n "$FISH_VERSION"; _FLOW_COMPLETE=fish_source flow | source; end'
            else:
                return f"# Unsupported shell: {shell}"
        else:
            # For development mode, source the completion script directly
            if shell == "bash":
                return 'if [ -n "${BASH_VERSION-}" ]; then eval "$(python -m flow.cli completion generate bash)"; fi'
            elif shell == "zsh":
                return 'if [ -n "${ZSH_VERSION-}" ]; then eval "$(python -m flow.cli completion generate zsh)"; fi'
            elif shell == "fish":
                return 'if test -n "$FISH_VERSION"; python -m flow.cli completion generate fish | source; end'
            else:
                return f"# Run: flow completion generate {shell}"


# Dynamic completion functions for Click


def complete_task_ids(ctx, args, incomplete):
    """Complete task IDs for commands that operate on tasks."""
    try:
        # Only complete if we have credentials
        validator = ConfigValidator()
        if not validator.validate_credentials():
            return []

        flow = Flow()
        tasks = flow.list_tasks(limit=50)  # Get Task objects, not dicts

        # Return task IDs and names that match the incomplete string
        completions = []
        for task in tasks:
            # Match by task_id or name
            if task.task_id.startswith(incomplete) or (
                task.name and task.name.lower().startswith(incomplete.lower())
            ):
                completions.append(task.task_id)
                # Also include the name as an alias if it's different
                if task.name and task.name != task.task_id:
                    completions.append(task.name)

        return completions[:50]  # Limit to 50 suggestions
    except Exception:
        return []


def complete_volume_ids(ctx, args, incomplete):
    """Complete volume IDs for volume commands."""
    try:
        validator = ConfigValidator()
        if not validator.validate_credentials():
            return []

        flow = Flow()
        volumes = flow.list_volumes()

        return [vol.id for vol in volumes if vol.id.startswith(incomplete)][:50]
    except Exception:
        return []


def complete_yaml_files(ctx, args, incomplete):
    """Complete YAML configuration files."""
    try:
        # Get current directory files
        from pathlib import Path

        cwd = Path.cwd()

        yaml_files = []
        # Look for YAML files
        for pattern in ["*.yaml", "*.yml"]:
            yaml_files.extend(cwd.glob(pattern))

        # Also search in common directories
        for subdir in ["configs", "config", "tasks", ".flow"]:
            subdir_path = cwd / subdir
            if subdir_path.exists():
                yaml_files.extend(subdir_path.glob("*.yaml"))
                yaml_files.extend(subdir_path.glob("*.yml"))

        # Return matching paths
        results = []
        for f in yaml_files:
            path_str = str(f.relative_to(cwd))
            if path_str.startswith(incomplete):
                results.append(path_str)

        return sorted(results)[:50]
    except Exception:
        return []


def complete_instance_types(ctx, args, incomplete):
    """Complete GPU instance types."""
    # Common instance types
    instance_types = [
        "h100x8",
        "h100x4",
        "h100x2",
        "h100x1",
        "a100-80gbx8",
        "a100-80gbx4",
        "a100-80gbx2",
        "a100-80gbx1",
        "a100-40gbx8",
        "a100-40gbx4",
        "a100-40gbx2",
        "a100-40gbx1",
        "a10gx8",
        "a10gx4",
        "a10gx2",
        "a10gx1",
        "t4x8",
        "t4x4",
        "t4x2",
        "t4x1",
        "rtx4090x8",
        "rtx4090x4",
        "rtx4090x2",
        "rtx4090x1",
        "cpu",
    ]

    return [t for t in instance_types if t.startswith(incomplete)]


def complete_container_names(ctx, args, incomplete):
    """Complete container names for a task.

    Looks for --task argument and queries containers on that task.
    """
    try:
        # Find task ID from args
        task_id = None
        for i, arg in enumerate(args):
            if arg in ("--task", "-t") and i + 1 < len(args):
                task_id = args[i + 1]
                break

        if not task_id:
            return []

        # Get containers from task
        flow = Flow(auto_init=True)
        output = flow.provider.remote_operations.execute_command(
            task_id, "docker ps --format '{{.Names}}'"
        )

        containers = [name.strip() for name in output.strip().split("\n") if name.strip()]

        return [name for name in containers if name.startswith(incomplete)][:50]
    except Exception:
        return []


# Export command instance
command = CompletionCommand()
