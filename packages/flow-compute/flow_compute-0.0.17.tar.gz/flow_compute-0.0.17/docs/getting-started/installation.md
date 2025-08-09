# Installation

## Requirements

- Python 3.10 or later
- Linux, macOS, or Windows

## Install Flow SDK

### Using uv (recommended)

1) Install uv (one-time):

- macOS/Linux:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- Windows (PowerShell):
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- More options: see the uv guide: [docs.astral.sh/uv/getting-started/installation](https://docs.astral.sh/uv/getting-started/installation/)

2) Install Flow

- Global CLI managed by uv:
  ```bash
  uv tool install flow-compute
  ```

- Per‑project install:
  ```bash
  uv init my-project
  cd my-project
  uv add flow-compute
  uv sync
  ```

### Using pip

```bash
pip install flow-compute
```

### From source

For development or latest features:

```bash
git clone https://github.com/mithrilcompute/flow.git
cd flow
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
   python --version  # Must be 3.10+
   ```

2. Verify installation:
   ```bash
   pip show flow-compute
   ```

3. Try reinstalling:
   ```bash
   pip uninstall flow-compute
   pip install flow-compute
   ```

### Permission Error

Use a virtual environment:

```bash
python -m venv flow-env
source flow-env/bin/activate  # On Windows: flow-env\Scripts\activate
pip install flow-compute
```

### Behind Corporate Proxy

Set proxy environment variables:

```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
pip install flow-compute
```

## Next Steps

- [Configure authentication](authentication.md) - Set up API access
- [Run your first job](first-gpu-job.md) - Submit a GPU task
- [Core concepts](core-concepts.md) - Understand Flow's design