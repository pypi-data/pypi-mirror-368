# Manual GPUd Setup

If you've started GPU instances through the console or other means without Flow's startup scripts, you can manually install GPUd to enable GPU health monitoring.

## Install GPUd

To install from the official release:

```bash
curl -fsSL https://pkg.gpud.dev/install.sh | sh
sudo gpud up
```

To specify a version:

```bash
curl -fsSL https://pkg.gpud.dev/install.sh | sh -s v0.5.1
```

Then open http://localhost:15132 (or https://localhost:15132 with `-k`) for the local web UI.

### Flow-recommended (local-only) startup

For Flow health checks, we recommend running GPUd in private mode bound to localhost to avoid exposing the service externally and to match Flow's defaults:

```bash
sudo gpud up --private --web-address="127.0.0.1:15132"
```

### Managed mode (optional)

If you use the Lepton platform, you can supply a workspace token to register the node:

```bash
# Start with token
sudo gpud up --token <LEPTON_AI_TOKEN>

# Or login later, then restart
sudo gpud login --token <LEPTON_AI_TOKEN>
# To logout
sudo gpud logout
# To logout and reset state
sudo gpud logout --reset-state
```

### Quick checks

After install, run a simple one-time scan:

```bash
gpud scan
```

## Verify Installation

After installation, verify GPUd is running:

```bash
# Health check (HTTP)
curl http://localhost:15132/healthz

# If GPUd serves HTTPS, use -kL for self-signed certs
curl -kL https://localhost:15132/healthz

# Machine info
curl http://localhost:15132/machine-info | jq

# Metrics and states
curl http://localhost:15132/v1/metrics | jq
curl http://localhost:15132/v1/states | jq
curl http://localhost:15132/v1/events | jq

# GPU inventory (if available)
curl http://localhost:15132/v1/gpu | jq
```

## Enable Flow Health Monitoring

Once GPUd is installed, Flow health commands will automatically detect and use it:

```bash
# Check health of your task
flow health --task <task-name>

# View GPU metrics across all tasks
flow health --gpu
```

## Systemd Service (Optional)

For persistent monitoring across reboots, create a systemd service:

```bash
sudo tee /etc/systemd/system/gpud.service >/dev/null << 'EOF'
[Unit]
Description=GPUd Health Monitor
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/local/bin/gpud up --private --web-address="127.0.0.1:15132"
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable gpud
sudo systemctl start gpud
```

## Upgrade GPUd

```bash
# Stop the existing gpud server (if managed by systemd)
sudo systemctl stop gpud.service || true

# Remove old binary if present
sudo rm -f /usr/sbin/gpud
sudo rm -f /usr/local/bin/gpud

# Install the desired version
curl -fsSL https://pkg.gpud.dev/install.sh | sh -s v0.5.1
which gpud

# (Optional) if upgrading from very old versions
sudo cp /usr/local/bin/gpud /usr/sbin/gpud || true

# Verify systemd points to the right binary (if using systemd)
sudo systemctl cat gpud || true

# Restart gpud
sudo systemctl restart gpud || true
```

## Kubernetes (optional)

To deploy GPUd in Kubernetes, use the official Helm chart:

- Chart: https://github.com/leptonai/gpud/tree/main/charts/gpud

## Build (optional)

To build and run GPUd locally from source:

```bash
make all
./bin/gpud up
```

To run without systemd (e.g., macOS or environments without systemd):

```bash
./bin/gpud run
```

## Advanced: Local API endpoints and testing

```bash
# Health of the GPUd process itself
curl -kL https://localhost:15132/healthz

# Basic machine information
curl -kL https://localhost:15132/machine-info | jq | less

# Health states, events, metrics
curl -kL https://localhost:15132/v1/states | jq | less
curl -kL https://localhost:15132/v1/events | jq | less
curl -kL https://localhost:15132/v1/metrics | jq | less
```

Fault injection (for testing XID and other events):

```bash
# Via CLI
gpud inject-fault \
  --kernel-log-level KERN_EMERG \
  --kernel-message "hello"

# Via API (requires gpud run/up)
curl -kX POST https://localhost:15132/inject-fault \
  -H "Content-Type: application/json" \
  -d '{
    "kernel_message": {"priority": "KERN_DEBUG", "message": "Debug fault injection test"}
  }'
```

For full tutorials, plugins, and API specs, see upstream GPUd docs:

- Tutorials: https://github.com/leptonai/gpud/blob/main/docs/TUTORIALS.md
- API types: https://github.com/leptonai/gpud/blob/main/api/v1/types.go
- OpenAPI (JSON): https://github.com/leptonai/gpud/blob/main/docs/apis/swagger.json
- OpenAPI (YAML): https://github.com/leptonai/gpud/blob/main/docs/apis/swagger.yaml

## Uninstall

```bash
# Stop service and remove unit (if used)
sudo systemctl stop gpud || true
sudo rm -f /etc/systemd/system/gpud.service
sudo systemctl daemon-reload

# Stop GPUd if running without systemd
sudo gpud down || true

# Remove binary (path may vary)
sudo rm -f /usr/local/bin/gpud
```

## Notes

- GPUd can run with a local web UI at http://localhost:15132 or https://localhost:15132 (self-signed).
- Flow automatically detects GPUd when checking GPU health.
- Tasks started with `flow run` include GPUd automatically.
- For security, we recommend `--private --web-address="127.0.0.1:15132"` on shared or public networks.
- The install script targets Linux amd64. On macOS/arm64, prefer the build-and-run steps above.
