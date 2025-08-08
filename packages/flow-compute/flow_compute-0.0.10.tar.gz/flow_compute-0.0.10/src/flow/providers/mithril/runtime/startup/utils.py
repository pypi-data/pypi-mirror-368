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
        # Default installation methods for common commands
        install_methods = {
            "curl": "apt-get update -qq && apt-get install -y -qq curl",
            "wget": "apt-get update -qq && apt-get install -y -qq wget",
            "bc": "apt-get update -qq && apt-get install -y -qq bc",
            "jq": "apt-get update -qq && apt-get install -y -qq jq",
            "python3": "apt-get update -qq && apt-get install -y -qq python3",
            "pip3": "apt-get update -qq && apt-get install -y -qq python3-pip",
            "uuidgen": "apt-get update -qq && apt-get install -y -qq uuid-runtime",
            "aws": "curl -sL https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o /tmp/awscliv2.zip && unzip -q /tmp/awscliv2.zip -d /tmp && /tmp/aws/install && rm -rf /tmp/aws*",
            "docker": "curl -fsSL https://get.docker.com | sh",
            "nginx": "apt-get update -qq && apt-get install -y -qq nginx",
            "s3fs": "apt-get update -qq && apt-get install -y -qq s3fs",
        }
        install_method = install_methods.get(command)

    if install_method:
        return textwrap.dedent(f"""
            # Ensure {command} is available
            if ! command -v {command} >/dev/null 2>&1; then
                echo "Installing {command}..."
                export DEBIAN_FRONTEND=noninteractive
                {install_method}
            fi
        """).strip()
    else:
        # Just check without installing
        return textwrap.dedent(f"""
            # Check for {command}
            if ! command -v {command} >/dev/null 2>&1; then
                echo "WARNING: {command} not found and no installation method configured"
            fi
        """).strip()


def ensure_curl_available() -> str:
    """Ensure curl is available since it's used extensively in startup scripts."""
    return textwrap.dedent("""
        # Ensure curl is available (required for many operations)
        if ! command -v curl >/dev/null 2>&1; then
            echo "Installing curl (required for startup operations)..."
            export DEBIAN_FRONTEND=noninteractive
            apt-get update -qq
            apt-get install -y -qq curl ca-certificates
        fi
    """).strip()


def ensure_docker_available() -> str:
    """Ensure Docker is available with proper error handling."""
    return textwrap.dedent("""
        # Ensure Docker is available
        if ! command -v docker >/dev/null 2>&1; then
            echo "Docker not found, installing..."
            
            # Ensure curl is available first
            if ! command -v curl >/dev/null 2>&1; then
                export DEBIAN_FRONTEND=noninteractive
                apt-get update -qq && apt-get install -y -qq curl ca-certificates
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
            systemctl enable docker
            systemctl start docker
            
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
    """).strip()


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
    return textwrap.dedent("""
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
        
        # Install commonly needed tools that might be missing
        TOOLS_TO_INSTALL=""
        
        # Check for curl (critical for many operations)
        if ! command -v curl >/dev/null 2>&1; then
            TOOLS_TO_INSTALL="$TOOLS_TO_INSTALL curl ca-certificates"
        fi
        
        # Check for other useful tools
        if ! command -v uuidgen >/dev/null 2>&1; then
            TOOLS_TO_INSTALL="$TOOLS_TO_INSTALL uuid-runtime"
        fi
        
        if ! command -v bc >/dev/null 2>&1; then
            TOOLS_TO_INSTALL="$TOOLS_TO_INSTALL bc"
        fi
        
        if ! command -v timeout >/dev/null 2>&1; then
            TOOLS_TO_INSTALL="$TOOLS_TO_INSTALL coreutils"
        fi
        
        # Install missing tools if any
        if [ -n "$TOOLS_TO_INSTALL" ]; then
            echo "Installing missing tools:$TOOLS_TO_INSTALL"
            export DEBIAN_FRONTEND=noninteractive
            apt-get update -qq
            apt-get install -y -qq $TOOLS_TO_INSTALL
        fi
    """).strip()
