# Authentication

Configure Flow SDK to access GPU infrastructure.

## Quick Setup

```bash
flow init
```

This interactive setup will:
1. Prompt for your Mithril API key
2. Configure default project
3. Set up SSH keys (optional)
4. Save configuration

Get your API key at: [app.mithril.ai/account/apikeys](https://app.mithril.ai/account/apikeys)

## Configuration Methods

### 1. Interactive Setup (Recommended)

```bash
flow init
```

### 2. Environment Variables

```bash
export Mithril_API_KEY="your-api-key"
export Mithril_PROJECT="your-project-id"  # Optional
export Mithril_REGION="us-central1-b"     # Optional
```

### 3. Configuration File

Create `~/.flow/config.yaml`:

```yaml
api_key: your-api-key
project: your-project-id
region: us-central1-b
ssh_keys:
  - my-ssh-key-name
```

### 4. Python Code

```python
from flow import Flow

# Pass API key directly
flow = Flow(api_key="your-api-key")

# Or use environment variables (automatic)
flow = Flow()  # Uses Mithril_API_KEY env var
```

## Configuration Precedence

Flow checks for configuration in this order:
1. Direct parameters: `Flow(api_key="...")`
2. Environment variables: `Mithril_API_KEY`
3. Config file: `~/.flow/config.yaml`
4. Interactive prompt if none found

## SSH Access

### Default SSH Key

Flow can use your default SSH key:

```yaml
# ~/.flow/config.yaml
ssh_keys:
  - default  # Uses ~/.ssh/id_rsa.pub
```

### Named SSH Keys

Use SSH keys registered in Mithril:

```python
from flow import TaskConfig

config = TaskConfig(
    command="python train.py",
    instance_type="a100",
    ssh_keys=["my-gpu-key"]  # Key name in Mithril
)
```

### Add SSH Key to Mithril

```bash
# Upload your public key to Mithril
flow ssh-keys add my-gpu-key ~/.ssh/id_rsa.pub
```

## Projects and Regions

### Default Project

Set a default project to avoid specifying it each time:

```bash
export Mithril_PROJECT="ml-training"
```

Or in config:
```yaml
project: ml-training
```

### Region Selection

Mithril regions:
- `us-central1-b` (Iowa)
- `us-central1-b` (Iowa)
- `us-central1-f` (Iowa)
- `us-east1-b` (South Carolina)
- `us-west1-a` (Oregon)
- `us-west1-b` (Oregon)
- `us-west4-b` (Nevada)

Set default:
```bash
export Mithril_REGION="us-west1-a"
```

Or per task:
```python
config = TaskConfig(
    command="python train.py",
    instance_type="a100",
    region="us-west4-b"  # Nevada
)
```

## Verifying Setup

### Check Configuration

```bash
# Show current config
flow config

# Test API connection
flow status
```

### Python Verification

```python
from flow import Flow

# This will fail if auth is not configured
flow = Flow()
print("Authentication successful!")

# List available instances
instances = flow.find_instances({})
print(f"Found {len(instances)} available instances")
```

## Security Best Practices

### 1. Protect Your API Key

Never commit API keys to version control:

```bash
# .gitignore
.env
.flow/
config.yaml
```

### 2. Use Environment Variables in CI

GitHub Actions:
```yaml
- name: Run GPU job
  env:
    Mithril_API_KEY: ${{ secrets.Mithril_API_KEY }}
  run: |
    pip install flow-sdk
    python train.py
```

GitLab CI:
```yaml
train:
  script:
    - pip install flow-sdk
    - python train.py
  variables:
    Mithril_API_KEY: $Mithril_API_KEY
```

### 3. Rotate Keys Regularly

1. Generate new key at [app.mithril.ai/account/apikeys](https://app.mithril.ai/account/apikeys)
2. Update your configuration
3. Delete old key

### 4. Use Project Isolation

Create separate projects for:
- Development
- Staging
- Production

## Troubleshooting

### Authentication Failed

```
Error: Authentication failed: Invalid API key
```

**Solutions:**
1. Check API key is correct (no extra spaces)
2. Verify key at [app.mithril.ai/account/apikeys](https://app.mithril.ai/account/apikeys)
3. Ensure key is active (not deleted)

### No Configuration Found

```
Error: No API key found. Please run 'flow init' or set Mithril_API_KEY
```

**Solutions:**
1. Run `flow init`
2. Set `export Mithril_API_KEY="your-key"`
3. Pass directly: `Flow(api_key="your-key")`

### Permission Denied

```
Error: Permission denied for project 'xyz'
```

**Solutions:**
1. Verify project ID is correct
2. Check you have access to the project
3. Use a project you own or have access to

### Region Not Available

```
Error: No instances available in region 'us-east1-a'
```

**Solutions:**
1. Try a different region
2. Check [status page](https://status.mithril.ai) for outages
3. Use `flow.find_instances({})` to find available regions

## Advanced Configuration

### Multiple Profiles

Manage multiple accounts/projects:

```yaml
# ~/.flow/profiles.yaml
profiles:
  dev:
    api_key: ${DEV_API_KEY}
    project: ml-dev
    
  prod:
    api_key: ${PROD_API_KEY}
    project: ml-prod
    region: us-central1-a
```

Use profiles:
```bash
export FLOW_PROFILE=prod
flow run "python train.py" --instance-type a100
```

### Proxy Configuration

For corporate networks:

```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1
```

## Next Steps

- [Run your first GPU job](first-gpu-job.md)
- [Understand core concepts](core-concepts.md)
- [Explore the API](../API_REFERENCE.md)