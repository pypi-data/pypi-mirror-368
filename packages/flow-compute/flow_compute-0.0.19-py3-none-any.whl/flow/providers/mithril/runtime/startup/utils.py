from __future__ import annotations

"""Utility functions for startup scripts to ensure required commands are available."""

import textwrap


def ensure_command_available(command: str, install_method: str | None = None) -> str:
    """Generate script to ensure a command is available, installing if needed.

    Args:
        command: The command to check for availability
        install_method: Optional installation method if command is not found

    Returns:
        Shell script snippet to ensure the command is available
    """
    if not install_method:
        # Default installation plans for common commands (cross-distro where possible)
        if command == "aws":
            # Ensure unzip and curl, then install AWS CLI v2
            install_method = (
                "if ! command -v curl >/dev/null 2>&1; then install_pkgs curl ca-certificates || true; fi\n"
                "if ! command -v unzip >/dev/null 2>&1; then install_pkgs unzip || true; fi\n"
                "curl -sL https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o /tmp/awscliv2.zip && unzip -q /tmp/awscliv2.zip -d /tmp && /tmp/aws/install && rm -rf /tmp/aws*"
            )
        elif command == "docker":
            install_method = (
                "if ! command -v curl >/dev/null 2>&1; then install_pkgs curl ca-certificates || true; fi\n"
                "curl -fsSL https://get.docker.com | sh"
            )
        elif command == "s3fs":
            # s3fs on Debian-based is s3fs; on RHEL-based often s3fs-fuse
            install_method = "install_pkgs s3fs || install_pkgs s3fs-fuse || true"
        elif command == "uuidgen":
            # util-linux provides uuidgen on many distros; Debian uses uuid-runtime
            install_method = "install_pkgs uuid-runtime || install_pkgs util-linux || true"
        elif command == "pip3":
            install_method = "install_pkgs python3-pip || install_pkgs py3-pip || true"
        elif command in {"curl", "wget", "bc", "jq", "python3", "nginx"}:
            install_method = f"install_pkgs {command} || true"
        else:
            # Fallback: try to install a package named like the command
            install_method = f"install_pkgs {command} || true"

    if install_method:
        return textwrap.dedent(
            f"""
            # Ensure {command} is available
            if ! command -v {command} >/dev/null 2>&1; then
                echo "Installing {command}..."
                export DEBIAN_FRONTEND=noninteractive
                {install_method}
            fi
            """
        ).strip()
    else:
        # Just check without installing
        return textwrap.dedent(
            f"""
            # Check for {command}
            if ! command -v {command} >/dev/null 2>&1; then
                echo "WARNING: {command} not found and no installation method configured"
            fi
            """
        ).strip()


def ensure_curl_available() -> str:
    """Ensure curl is available since it's used extensively in startup scripts."""
    return textwrap.dedent(
        """
        # Ensure curl is available (required for many operations)
        if ! command -v curl >/dev/null 2>&1; then
            echo "Installing curl (required for startup operations)..."
            export DEBIAN_FRONTEND=noninteractive
            install_pkgs curl ca-certificates || true
        fi
        """
    ).strip()


def ensure_docker_available() -> str:
    """Ensure Docker is available with proper error handling."""
    return textwrap.dedent(
        """
        # Ensure Docker is available
        if ! command -v docker >/dev/null 2>&1; then
            echo "Docker not found, installing..."

            # Ensure curl is available first
            if ! command -v curl >/dev/null 2>&1; then
                export DEBIAN_FRONTEND=noninteractive
                install_pkgs curl ca-certificates || true
            fi

            # Install Docker
            MAX_RETRIES=3
            RETRY_COUNT=0
            while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
                if curl -fsSL https://get.docker.com -o /tmp/get-docker.sh && sh /tmp/get-docker.sh; then
                    rm -f /tmp/get-docker.sh
                    break
                else
                    RETRY_COUNT=$((RETRY_COUNT + 1))
                    echo "Docker installation attempt $RETRY_COUNT failed, retrying..."
                    sleep 5
                fi
            done

            if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
                echo "ERROR: Failed to install Docker after $MAX_RETRIES attempts"
                exit 1
            fi
        fi

        # Enable and start Docker
        if command -v systemctl >/dev/null 2>&1; then
            systemctl enable docker || true
            systemctl start docker || true

            # Wait for Docker to be ready
            DOCKER_READY=false
            for i in {1..30}; do
                if docker info >/dev/null 2>&1; then
                    DOCKER_READY=true
                    break
                fi
                sleep 1
            done

            if [ "$DOCKER_READY" = "false" ]; then
                echo "WARNING: Docker did not become ready in time"
            fi
        fi
        """
    ).strip()


def get_command_fallback(command: str) -> str:
    """Get fallback for commands that might not be available.

    Args:
        command: The command that might not be available

    Returns:
        Shell snippet with fallback logic
    """
    fallbacks = {
        "uuidgen": 'echo "task-$(date +%s)-$$"',
        "timeout": "( $@ ) & sleep $1; kill $! 2>/dev/null || true",
        "bc": "awk 'BEGIN {print $@}'",
    }

    fallback = fallbacks.get(command)
    if fallback:
        return f"command -v {command} >/dev/null 2>&1 && {command} || {fallback}"
    return command


def ensure_basic_tools() -> str:
    """Ensure basic tools required by most startup scripts are available."""
    return textwrap.dedent(
        """
        # Ensure basic tools are available
        echo "Checking for required system tools..."

        # Core utilities that should always be present
        MISSING_TOOLS=""
        for tool in bash grep sed awk cat echo mkdir chmod chown mount umount; do
            if ! command -v $tool >/dev/null 2>&1; then
                MISSING_TOOLS="$MISSING_TOOLS $tool"
            fi
        done

        if [ -n "$MISSING_TOOLS" ]; then
            echo "WARNING: Core system tools missing:$MISSING_TOOLS"
            echo "This may indicate a non-standard system image"
        fi

        install_pkgs() {
            if command -v apt-get >/dev/null 2>&1; then
                apt-get update -qq && apt-get install -y -qq "$@"
            elif command -v dnf >/dev/null 2>&1; then
                dnf -y install "$@"
            elif command -v yum >/dev/null 2>&1; then
                yum -y install "$@"
            elif command -v apk >/dev/null 2>&1; then
                apk add --no-cache "$@"
            elif command -v zypper >/dev/null 2>&1; then
                zypper -n install "$@"
            elif command -v pacman >/dev/null 2>&1; then
                pacman -Sy --noconfirm "$@"
            else
                echo "WARNING: No supported package manager found to install: $*"
                return 1
            fi
        }

        # Install commonly needed tools that might be missing
        export DEBIAN_FRONTEND=noninteractive

        # curl (critical for many operations)
        if ! command -v curl >/dev/null 2>&1; then
            install_pkgs curl ca-certificates || true
        fi

        # uuidgen
        if ! command -v uuidgen >/dev/null 2>&1; then
            install_pkgs uuid-runtime || install_pkgs util-linux || true
        fi

        # bc
        if ! command -v bc >/dev/null 2>&1; then
            install_pkgs bc || true
        fi

        # timeout and base64 (coreutils)
        if ! command -v timeout >/dev/null 2>&1 || ! command -v base64 >/dev/null 2>&1; then
            install_pkgs coreutils || true
        fi

        # tar and gzip (for archives)
        if ! command -v tar >/dev/null 2>&1; then
            install_pkgs tar || true
        fi
        if ! command -v gzip >/dev/null 2>&1; then
            install_pkgs gzip || true
        fi

        # unzip (used by some installers e.g., AWS CLI)
        if ! command -v unzip >/dev/null 2>&1; then
            install_pkgs unzip || true
        fi

        # Python runtime used by several helpers
        if ! command -v python3 >/dev/null 2>&1; then
            install_pkgs python3 || true
        fi
        if ! command -v pip3 >/dev/null 2>&1; then
            install_pkgs python3-pip || install_pkgs py3-pip || true
        fi
        """
    ).strip()
