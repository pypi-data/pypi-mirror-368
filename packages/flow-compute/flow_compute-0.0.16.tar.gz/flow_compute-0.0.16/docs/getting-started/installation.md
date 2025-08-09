# Installation

## Requirements

- Python 3.11 or later
- pip package manager
- Linux, macOS, or Windows

## Install Flow SDK

### Using pip (recommended)

```bash
pip install flow-sdk
```

### From source

For development or latest features:

```bash
git clone https://github.com/flowcloud/flow-sdk.git
cd flow-sdk
pip install -e .
```

### Using uv

If you prefer the fast uv package manager:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Flow SDK
uv pip install flow-sdk
```

## Verify Installation

```bash
# Check CLI
flow --version

# Test Python import
python -c "import flow; print('Flow SDK installed')"
```

## Quick Test

Run a simple GPU test:

```python
import flow
task_id = flow.run("nvidia-smi", instance_type="a100")
print(f"Task submitted: {task_id}")
```

## Troubleshooting

### Import Error

If `import flow` fails:

1. Check Python version:
   ```bash
   python --version  # Must be 3.11+
   ```

2. Verify installation:
   ```bash
   pip show flow-sdk
   ```

3. Try reinstalling:
   ```bash
   pip uninstall flow-sdk
   pip install flow-sdk
   ```

### Permission Error

Use a virtual environment:

```bash
python -m venv flow-env
source flow-env/bin/activate  # On Windows: flow-env\Scripts\activate
pip install flow-sdk
```

### Behind Corporate Proxy

Set proxy environment variables:

```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
pip install flow-sdk
```

## Next Steps

- [Configure authentication](authentication.md) - Set up API access
- [Run your first job](first-gpu-job.md) - Submit a GPU task
- [Core concepts](core-concepts.md) - Understand Flow's design