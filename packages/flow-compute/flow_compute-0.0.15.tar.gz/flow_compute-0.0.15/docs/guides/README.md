# Guides

Practical guides and patterns for using Flow SDK effectively.

## Available Guides

### Core Patterns
- [Decorator Pattern](decorator-pattern.md) - Function-based GPU execution
- [Running Jobs](running-jobs.md) - Task submission patterns
- [Invoker Pattern](INVOKER_PATTERN.md) - Zero-import remote execution
- [Invoke Best Practices](INVOKE_BEST_PRACTICES.md) - Production invoke patterns

### Configuration & Data
- [Configuration](CONFIGURATION.md) - Config file setup and management
- [Data Handling](DATA_HANDLING.md) - Working with datasets and volumes
- [Data Mounting Guide](DATA_MOUNTING_GUIDE.md) - Mount S3, volumes, and URLs
- [Instance Type Conventions](INSTANCE_TYPE_CONVENTIONS.md) - GPU instance naming standards

### Monitoring & Operations
- [Health Monitoring](health-monitoring.md) - GPU health monitoring and metrics
- [Manual GPUd Setup](manual-gpud-setup.md) - Manual GPU daemon installation guide



## Quick Examples

### Decorator Pattern
```python
from flow import FlowApp

app = FlowApp()

@app.function(gpu="a100")
def train_model(data_path: str):
    # Your training code here
    return results
```

### Data Mounting
```python
import flow

# Mount S3 bucket
task = flow.run(
    "python analyze.py",
    data={"s3://my-bucket/data": "/data"}
)
```

### Configuration Files
```yaml
# .flow/config.yaml
version: 1
mithril:
  api_key: ${FLOW_API_KEY}
  default_region: us-west-2
```
