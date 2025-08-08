# Instance Type Naming Conventions

This guide documents the instance type naming conventions used in Flow SDK and Mithril (Flow Compute Platform).

## Overview

Flow SDK uses simplified instance type names that are automatically mapped to provider-specific formats. This provides a consistent interface across different cloud providers while maintaining compatibility with their native instance types.

## Standard Naming Format

### Single GPU Instances
For single GPU instances, use the GPU model name directly:
- `a100` - NVIDIA A100 GPU
- `h100` - NVIDIA H100 GPU
- `v100` - NVIDIA V100 GPU
- `t4` - NVIDIA T4 GPU
- `a10` - NVIDIA A10 GPU

### Multi-GPU Instances
For multi-GPU instances, prefix the count to the GPU model:
- `8xh100` - 8x NVIDIA H100 GPUs
- `4xa100` - 4x NVIDIA A100 GPUs
- `2xv100` - 2x NVIDIA V100 GPUs

## Provider Mappings

### Mithril Provider
The Mithril provider automatically maps between simplified names and full instance specifications:

```python
# User specifies:
instance_type = "8xh100"

# Mithril translates to:
provider_instance_type = "h100-80gb.sxm.8x"
```

Common mappings:
- `h100` → `h100-80gb`
- `8xh100` → `h100-80gb.sxm.8x`
- `a100` → `a100-80gb`
- `4xa100` → `a100-80gb.pcie.4x`

## Usage Examples

### CLI
```bash
# Single GPU
flow run --gpu h100 train.py

# Multi-GPU
flow run --gpu 8xh100 distributed_train.py
```

### SDK
```python
import flow

# Single GPU
task = flow.run(
    "python train.py",
    instance_type="h100"
)

# Multi-GPU
task = flow.run(
    "python distributed_train.py", 
    instance_type="8xh100"
)
```

### Decorator Pattern
```python
from flow import FlowApp

app = FlowApp()

@app.function(gpu="h100")
def train_single_gpu():
    pass

@app.function(gpu="8xh100")
def train_multi_gpu():
    pass
```

## Best Practices

1. **Use Simplified Names**: Always use the simplified format (e.g., `h100`, `8xh100`) in your code and configurations.

2. **Avoid Provider-Specific Names**: Don't use provider-specific formats like `h100-80gb.sxm.8x` directly, as these may change between providers.

3. **Consistent Casing**: Instance types are case-insensitive but lowercase is preferred for consistency.

4. **Validation**: The SDK automatically validates instance types and provides helpful error messages for invalid types.

## Error Handling

If you specify an invalid instance type, Flow SDK provides helpful error messages:

```python
# Invalid instance type
task = flow.run("train.py", instance_type="nvidia-a100")
# Error: Unknown instance type 'nvidia-a100'. Did you mean 'a100'?
```

## Testing Considerations

When writing tests that involve instance types:

1. **Use Standard Names**: Tests should use the simplified instance type names.
2. **Mock Appropriately**: When mocking providers, ensure the instance type mappings are consistent.
3. **Verify Mappings**: Integration tests should verify that instance types are correctly mapped to provider-specific formats.

Example test:
```python
def test_instance_type_mapping():
    config = TaskConfig(
        name="test",
        instance_type="8xh100",  # Use simplified name
        command="echo test"
    )
    
    # Provider should handle mapping internally
    assert config.instance_type == "8xh100"
```

## Future Compatibility

The simplified naming convention is designed to remain stable even as cloud providers introduce new instance types. New GPU models will follow the same pattern:
- Single GPU: `{gpu_model}`
- Multi-GPU: `{count}x{gpu_model}`

This ensures code written today will continue to work with future GPU releases without modification.