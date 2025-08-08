# Troubleshooting Guides

Solutions for common issues when using Flow SDK.

## Available Guides

- [Google Colab Issues](COLAB_TROUBLESHOOTING.md) - Jupyter and Colab-specific problems

## Common Issues

### Authentication
See [Authentication Guide](../getting-started/authentication.md) for API key setup.

### Task Failures
Check task logs:
```python
task = flow.get_task(task_id)
for line in task.logs():
    print(line)
```

### Network Issues
Verify connectivity to Mithril API:
```bash
# Check basic connectivity (should return "Success")
curl https://api.mithril.ai/

# Or use Python to validate API key
from flow import Flow
with Flow() as client:
    # This will validate your API key and connection
    print("Connected successfully")

## Getting Help

- Check [API Reference](../API_REFERENCE.md) for method signatures
- Review [User Guide](../USER_GUIDE.md) for patterns
- Contact support@mithril.com for additional assistance