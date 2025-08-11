# Pulumi Integration

Flow SDK integrates directly with Pulumi for infrastructure as code. No custom provider needed.

## Quick Start

```python
import pulumi
import flow

task = flow.run("sleep infinity", instance_type="8xa100", max_price_per_hour=50.0)
pulumi.export("gpu_ips", [i.public_ip for i in task.instances])
```

## Documentation

- [Integration Guide](PULUMI_INTEGRATION.md) - Complete integration reference
- [Patterns](PULUMI_PATTERN.md) - Production patterns and best practices
- [xAI Recommendation](PULUMI_XAI_RECOMMENDATION.md) - Specific guidance for xAI team
- [Examples](examples/) - Working code examples

## Key Concepts

- Mithril uses spot instances with bidding
- Set high `max_price_per_hour` for persistent infrastructure
- Handle preemption at the application layer
- Direct SDK usage is simpler than custom providers