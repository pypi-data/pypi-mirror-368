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

Get your API key at: [app.mithril.ai/account/apikeys][api_keys]

## Configuration Methods

### 1. Interactive Setup (Recommended)

```bash
flow init
```

### 2. Environment Variables

```bash
export MITHRIL_API_KEY="your-api-key"
export MITHRIL_DEFAULT_PROJECT="your-project-id"  # Optional
export MITHRIL_DEFAULT_REGION="us-central1-b"     # Optional
```

Compatibility note: the SDK also accepts legacy-cased `Mithril_API_KEY`, but `MITHRIL_API_KEY` is the canonical form and should be preferred.

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

# Recommended: configure via environment and config files
flow = Flow()
```

## Configuration Precedence

Flow checks for configuration in this order:
1. Environment variables: `MITHRIL_API_KEY`, `MITHRIL_DEFAULT_PROJECT`, `MITHRIL_DEFAULT_REGION`
2. Config files: `./flow.yaml` then `~/.flow/config.yaml`
3. Interactive prompt (CLI `flow init`) if none found

## SSH Access

### Default SSH Key (required)

Your Default SSH Key is how you SSH into running instances. You must choose one during `flow init`.

- Auto‑generate per instance (recommended): Each instance gets a unique key created by Mithril. The private key is saved to `~/.flow/keys/` for you. Secure, zero hassle.
- Use an existing key: Pick a key you’ve uploaded to your Mithril account.

Manage or upload keys at: [`app.mithril.ai/account/ssh-keys`][ssh_keys]

Note:
- SSH keys are scoped to a Mithril project. Admins can mark certain keys as required for all new instances in a project. When such keys exist, Flow will automatically include them in every launch in that project.

To set explicitly in config:

```yaml
# ~/.flow/config.yaml
provider: mithril
mithril:
  project: my-project
  region: us-central1-b
  ssh_keys:
    - _auto_                 # Auto‑generate per instance (recommended)
    # - sshkey_ABC123...    # Or a specific platform key ID
    # Required project keys are auto-included; you do not need to list them here
```

### Use a specific key in code

```python
from flow import TaskConfig

config = TaskConfig(
    command="python train.py",
    instance_type="a100",
    ssh_keys=["sshkey_ABC123"]  # Mithril platform key ID
)
```

### Add a new SSH key to Mithril

```bash
# Upload your public key to Mithril (uses your ~/.ssh/*.pub)
flow ssh-keys upload ~/.ssh/id_ed25519.pub

# Or open the web UI to manage keys
open [app.mithril.ai/account/ssh-keys][ssh_keys]

# Admins: mark/unmark keys as required
flow ssh-keys require sshkey_ABC123
flow ssh-keys require --unset sshkey_ABC123
```

## Projects and Regions

### Default Project

Set a default project to avoid specifying it each time:

```bash
export MITHRIL_DEFAULT_PROJECT="ml-training"
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
export MITHRIL_DEFAULT_REGION="us-central1-b"
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
flow init --show

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
    MITHRIL_API_KEY: ${{ secrets.MITHRIL_API_KEY }}
  run: |
    pip install flow-compute
    python train.py
```

GitLab CI:
```yaml
train:
  script:
    - pip install flow-compute
    - python train.py
  variables:
    MITHRIL_API_KEY: $MITHRIL_API_KEY
```

### 3. Rotate Keys Regularly

1. Generate new key at [app.mithril.ai/account/apikeys][api_keys]
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
2. Verify key at [app.mithril.ai/account/apikeys][api_keys]
3. Ensure key is active (not deleted)

### No Configuration Found

```
Error: No API key found. Please run 'flow init' or set MITHRIL_API_KEY
```

**Solutions:**
1. Run `flow init`
2. Set `export MITHRIL_API_KEY="your-key"`
3. Pass directly: `Flow(config=Config.from_env())`

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
2. Check [status page][status] for outages

[api_keys]: {{ WEB_BASE }}/account/apikeys
[ssh_keys]: {{ WEB_BASE }}/account/ssh-keys
[status]: {{ STATUS_BASE }}
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
- [Explore the API](../api-reference.md)