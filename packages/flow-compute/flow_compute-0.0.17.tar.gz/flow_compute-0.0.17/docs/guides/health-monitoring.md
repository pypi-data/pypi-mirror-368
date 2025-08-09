# GPU Health Monitoring

Flow SDK includes built-in GPU health monitoring powered by [GPUd](https://github.com/leptonai/gpud), providing comprehensive visibility into your GPU fleet's health and performance.

## Overview

The health monitoring system automatically:
- Installs GPUd on all GPU instances during startup
- Collects GPU metrics, system health, and performance data
- Stores metrics locally with automatic rotation
- Optionally streams metrics to a remote endpoint
- Provides fleet-wide health visibility through the CLI

## Quick Start

### Check GPU Health Across Your Fleet
```bash
# View health status of all GPU tasks
flow health --gpu

# Include non-GPU tasks in the health check
flow health --gpu --all

# Check specific task health
flow health --task task-abc123

# View historical health data (last 24 hours)
flow health --task task-abc123 --history 24

# Output health data as JSON for automation
flow health --gpu --json
```

## Configuration

### Environment Variables

Configure health monitoring behavior through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `FLOW_HEALTH_MONITORING` | Enable/disable health monitoring | `true` |
| `FLOW_GPUD_VERSION` | GPUd version to install | `v0.5.1` |
| `FLOW_GPUD_PORT` | Port for GPUd API | `15132` |
| `FLOW_GPUD_BIND` | Bind address for GPUd | `127.0.0.1` |
| `FLOW_METRICS_ENDPOINT` | Remote endpoint for metrics streaming | None |
| `FLOW_METRICS_INTERVAL` | Metrics collection interval (seconds) | `60` |
| `FLOW_METRICS_BATCH_SIZE` | Number of metrics to batch before sending | `100` |
| `FLOW_METRICS_RETENTION_DAYS` | Days to retain local metrics | `7` |
| `FLOW_METRICS_COMPRESS_AFTER_DAYS` | Compress metrics older than N days | `1` |
| `FLOW_METRICS_AUTH_TOKEN` | Authentication token for remote endpoint | None |

### Configuration File

You can also configure health monitoring in `~/.flow/config.yaml`:

```yaml
health:
  enabled: true
  gpud_version: v0.5.1
  gpud_port: 15132
  gpud_bind: 127.0.0.1
  metrics_endpoint: https://metrics.example.com/v1/ingest
  metrics_interval: 60
  metrics_batch_size: 100
  retention_days: 7
  compress_after_days: 1
```

## Architecture

### Component Overview

1. **GPUd Service**: Runs on each GPU instance, exposing health APIs
2. **Metrics Collector**: Python daemon that collects and batches metrics
3. **Local Storage**: JSONL files with automatic rotation and compression
4. **Health Checker**: CLI component that queries GPUd via SSH tunnels
5. **Health Renderer**: Rich terminal UI for displaying health status

### Data Flow

```
GPU Instance                    Flow CLI
┌─────────────┐               ┌──────────────┐
│   GPUd      │◄──SSH Tunnel──│ Health Check │
│  (port 15132)│               │   Command    │
└──────┬──────┘               └──────┬───────┘
       │                             │
       ▼                             ▼
┌─────────────┐               ┌──────────────┐
│  Metrics    │               │   Health     │
│ Collector   │               │  Renderer    │
└──────┬──────┘               └──────────────┘
       │
       ▼
┌─────────────┐
│Local Storage│──Optional──► Remote Endpoint
│   (JSONL)   │
└─────────────┘
```

## Metrics Collected

### GPU Metrics
- Temperature and thermal status
- Power draw and limits
- Memory usage and bandwidth
- GPU/SM utilization
- Clock speeds and throttling
- ECC errors and XID events
- NVLink status

### System Metrics
- CPU usage and load average
- System memory usage
- Disk usage
- Network I/O
- Process information

### Health States
- Component health status
- Critical events and warnings
- Performance degradation indicators

## Health Scoring

The system calculates health scores based on multiple factors:

- **Temperature**: Critical >85°C, Warning >75°C
- **GPU Utilization**: Penalized if <10% (underutilized) or >95% (bottlenecked)
- **Memory Pressure**: Warning >90%, Critical >95%
- **Throttling**: Significant penalty if GPU is throttling
- **ECC Errors**: Major penalty for any ECC errors

Health Status Levels:
- **Healthy** (80-100%): All systems operating normally
- **Degraded** (60-79%): Minor issues detected
- **Critical** (<60%): Major issues requiring attention
- **Unknown**: Unable to determine health status

## Remote Metrics Streaming

To stream metrics to a remote endpoint:

1. Set the endpoint URL:
```bash
export FLOW_METRICS_ENDPOINT="https://metrics.example.com/v1/ingest"
```

2. (Optional) Set authentication:
```bash
export FLOW_METRICS_AUTH_TOKEN="your-api-token"
```

3. Configure batching:
```bash
export FLOW_METRICS_BATCH_SIZE=100  # Batch size before sending
export FLOW_METRICS_INTERVAL=60     # Collection interval in seconds
```

The metrics are sent as JSON with the following structure:
```json
{
  "source": "flow-sdk",
  "version": "1.0",
  "metrics": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "task_id": "task-abc123",
      "task_name": "training-job",
      "instance_type": "h100.8xlarge",
      "gpud_metrics": { ... },
      "system_metrics": { ... }
    }
  ]
}
```

## Troubleshooting

### GPUd Not Starting
If GPUd fails to start on an instance:
1. Check instance logs: `flow logs <task-name>`
2. Verify the instance has GPUs: `flow ssh <task-name> -- nvidia-smi`
3. Check GPUd installation: `flow ssh <task-name> -- which gpud`

### No Metrics Being Collected
1. Verify health monitoring is enabled: `echo $FLOW_HEALTH_MONITORING`
2. Check metrics collector status: `flow ssh <task-name> -- systemctl status flow-metrics-streamer`
3. Review collector logs: `flow ssh <task-name> -- journalctl -u flow-metrics-streamer`

### SSH Tunnel Issues
If health checks fail with SSH errors:
1. Verify SSH connectivity: `flow ssh <task-name>`
2. Check if GPUd port is accessible: `flow ssh <task-name> -- curl http://localhost:15132/healthz`
3. Ensure SSH keys are properly configured

### Metrics Storage Issues
1. Check local metrics directory: `ls -la ~/.flow/metrics/`
2. Verify disk space: `df -h ~/.flow/metrics/`
3. Review metrics store logs in your Flow logs

## Advanced Usage

### Custom Health Checks
You can extend health monitoring by querying GPUd directly:

```bash
# Get raw GPU metrics via SSH tunnel
flow ssh <task-name> -- curl http://localhost:15132/v1/gpu

# Check specific GPU health
flow ssh <task-name> -- curl http://localhost:15132/v1/states

# View recent events
flow ssh <task-name> -- curl http://localhost:15132/v1/events
```

### Metrics Analysis
Access historical metrics programmatically:

```python
from flow.health.storage import MetricsStore, MetricsAggregator

# Read metrics
store = MetricsStore()
snapshots = list(store.read_snapshots(task_id="task-abc123"))

# Analyze trends
aggregator = MetricsAggregator(store)
summary = aggregator.get_task_summary("task-abc123", hours=24)
```

### Integration with Monitoring Systems
The health monitoring system can integrate with popular monitoring platforms:

- **Prometheus**: Use the metrics endpoint to push to Pushgateway
- **Datadog**: Stream metrics to Datadog API
- **CloudWatch**: Send to CloudWatch custom metrics
- **Grafana**: Visualize metrics from any supported backend

## Best Practices

1. **Enable Monitoring Early**: Configure health monitoring before launching GPU workloads
2. **Set Appropriate Intervals**: Balance between data granularity and overhead
3. **Monitor Disk Usage**: Ensure sufficient space for local metrics storage
4. **Use Batching**: Reduce network overhead with appropriate batch sizes
5. **Secure Endpoints**: Always use HTTPS and authentication for remote endpoints
6. **Regular Cleanup**: Monitor and clean up old metrics files periodically

## Limitations

- GPUd requires root/sudo access for some metrics
- SSH tunneling adds latency to health checks
- Local storage is limited by disk space
- Some metrics may not be available on all GPU types
- Remote streaming requires network connectivity