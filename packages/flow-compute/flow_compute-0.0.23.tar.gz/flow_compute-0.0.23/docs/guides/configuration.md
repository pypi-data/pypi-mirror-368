# Configuration

This document describes the canonical Flow configuration model and environment variable precedence.

## Canonical YAML structure

Configuration is persisted at `~/.flow/config.yaml`.

Top-level keys:

- `provider`: one of `mithril` (default) or `mock` (demo)
- `api_key`: Mithril API key (masked in displays)
- `mithril`: provider-specific section
  - `project`: project name
  - `region`: default region
  - `api_url`: API endpoint (defaults to `https://api.mithril.ai`)
  - `ssh_keys`: list of SSH key identifiers
    - `['_auto_']` to auto-generate per instance (recommended)
    - Or one or more platform key IDs like `sshkey_...`

Example:

```yaml
provider: mithril
api_key: fkey_xxxxxxxxxxxxxxxxxxxx
mithril:
  project: my-project
  region: us-central1-b
  ssh_keys:
    - _auto_
```

## Environment variable precedence

At runtime, values resolve with the following precedence (highest first):

1. Environment variables
   - `MITHRIL_API_KEY`
   - `MITHRIL_PROJECT`
   - `MITHRIL_REGION`
   - `MITHRIL_API_URL`
   - `MITHRIL_SSH_KEYS` (comma-separated)
2. YAML file `~/.flow/config.yaml`

Other env:

- `FLOW_PROVIDER` overrides `provider` for the current process.
- `FLOW_DEMO_MODE=1` forces demo mode unless `FLOW_PROVIDER` explicitly selects a non-mock provider.

## Single source of truth

Flow uses a centralized `ConfigManager` to:

- Read sources (env + YAML)
- Normalize transient inputs (e.g., `default_ssh_key` → `mithril.ssh_keys`)
- Persist configuration via atomic writes
- Generate `~/.flow/env.sh` with canonical `MITHRIL_*` variables

CLI and setup wizard are wired to the same manager to ensure consistent behavior.


Flow SDK configuration through environment variables and config files.

## Environment Variables

### Core
- `FLOW_PROVIDER`: Provider selection (default: `mithril`)
- `MITHRIL_API_KEY`: API authentication token

### API Endpoints
- `MITHRIL_API_URL`: API base URL (default: `https://api.mithril.ai`)
- `MITHRIL_WEB_URL`: Dashboard URL (default: `https://app.mithril.ai`)
- `MITHRIL_DOCS_URL`: Documentation URL (default: `https://docs.mithril.ai`)
- `MITHRIL_STATUS_URL`: Status page URL (default: `https://status.mithril.ai`)

### Instance Types
Configure user-friendly names to provider IDs:

```bash
export MITHRIL_INSTANCE_MAPPINGS='{"a100": "instance-id-123", "h100": "instance-id-456"}'
```

Or use `~/.flow/instance_types.json`:
```json
{
  "a100": "instance-id-123",
  "h100": "instance-id-456",
  "4xa100": "instance-id-789"
}
```

### Provider Settings
- `MITHRIL_DEFAULT_PROJECT`: Default project
- `MITHRIL_DEFAULT_REGION`: Default region (default: `us-central1-a`)
- `MITHRIL_SSH_USER`: SSH username (default: `ubuntu`)
- `MITHRIL_SSH_PORT`: SSH port (default: `22`)
- `MITHRIL_SSH_KEYS`: Comma-separated SSH key IDs to include on launch. Note: any project-required keys are auto-included regardless of this setting.

CLI examples:

```bash
# Mark a key as required (admin)
flow ssh-keys require sshkey_ABC123

# Clear required flag (admin)
flow ssh-keys require --unset sshkey_ABC123
```
- `MITHRIL_LOG_DIR`: Provider logs (default: `/var/log/foundry`)
- `FLOW_LOG_DIR`: SDK logs (default: `/var/log/flow`)

## Configuration Files

Load order (later overrides earlier):
1. `~/.flow/config.yaml` - User config
2. `flow.yaml` - Project config
3. Environment variables (highest precedence)

Example `~/.flow/config.yaml`:
```yaml
provider: mithril
mithril:
  project: my-project
  region: us-east-1
  ssh_keys:
    - my-key-name
```

## Custom Providers

Configure a different provider:

```bash
export FLOW_PROVIDER=custom
export MITHRIL_API_URL=https://api.custom-provider.com
export MITHRIL_INSTANCE_MAPPINGS='{"gpu-small": "t2.micro", "gpu-large": "p3.2xlarge"}'
export MITHRIL_SSH_USER=ec2-user
```

## Security

- Never commit API keys
- Use environment variables for credentials
- Hidden directories excluded from git

## Troubleshooting

**Instance types not recognized:**
- Check JSON formatting in `MITHRIL_INSTANCE_MAPPINGS`
- Verify `~/.flow/instance_types.json` validity
- Use `MITHRIL_INCLUDE_DEFAULT_MAPPINGS=true`

**API connection issues:**
- Verify `MITHRIL_API_URL`
- Check API key validity
- Ensure network connectivity