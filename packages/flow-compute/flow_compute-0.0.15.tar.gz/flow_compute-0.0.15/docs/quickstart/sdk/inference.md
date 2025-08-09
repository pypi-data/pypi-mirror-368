# GPU Inference in 5 Minutes

Run production-ready model inference with vLLM on GPUs in under 5 minutes.

## Prerequisites
- Flow SDK installed: `pip install flow-sdk`
- API key from [app.mithril.ai/account/apikeys](https://app.mithril.ai/account/apikeys)

## 1. Initialize (30 seconds)

```bash
flow init
```

Enter your API key when prompted.

## 2. Validate GPU Access (1 minute)

```python
import flow
from flow import TaskConfig

# Quick GPU validation
validation_config = TaskConfig(
    name="gpu-validation",
    command="""
    nvidia-smi -L && 
    python -c "
import torch
print(f'GPU: {torch.cuda.get_device_name(0)}')
print(f'Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB')
print(f'CUDA: {torch.version.cuda}')
"
    """,
    instance_type="a100",
    max_run_time_seconds=30,
    max_price_per_hour=10.00  # Set budget limit
)

# Run validation
flow_client = flow.Flow()
task = flow_client.run(validation_config)
print(f"Task ID: {task.task_id}")

# Wait for completion and check logs
task.wait()
print(task.logs())
print(f"Validation cost: {task.total_cost}")
```

## 3. Run vLLM Inference Server (3 minutes)

### Option 1: Single GPU for 7B Models

```python
import flow
from flow import TaskConfig
import time

# vLLM server configuration
vllm_config = TaskConfig(
    name="vllm-qwen-7b",
    command="""
    # Install vLLM
    pip install vllm
    
    # Start vLLM server
    python -m vllm.entrypoints.openai.api_server \
        --model Qwen/Qwen2.5-7B-Instruct \
        --host 0.0.0.0 \
        --port 8000 \
        --max-model-len 4096 \
        --trust-remote-code
    """,
    instance_type="a100",  # 80GB VRAM for 7B model with headroom
    ports=[8000],
    max_run_time_hours=24,
    max_price_per_hour=10.00
)

# Launch server
flow_client = flow.Flow()
server_task = flow_client.run(vllm_config, wait=True)
print(f"Server starting: {server_task.task_id}")
print(f"Cost per hour: {server_task.cost_per_hour}")

# Wait for server to be ready
print("Waiting for vLLM server to start...")
while server_task.status == "RUNNING":
    logs = server_task.logs(tail=20)
    if "Uvicorn running on" in logs:
        print("vLLM server is ready!")
        break
    time.sleep(5)
    server_task.refresh()

# Get endpoint URL (if exposed through load balancer)
if server_task.endpoints:
    endpoint_url = server_task.endpoints.get("8000", "Not available")
    print(f"Server endpoint: {endpoint_url}")
else:
    print(f"Connect via SSH forwarding: {server_task.ssh_command}")
    print("Then access at: http://localhost:8000")

# Test the server
# Note: In production, you'd use the endpoint URL or SSH tunnel
print("\nTo test the server:")
print("1. Set up SSH tunnel: ssh -L 8000:localhost:8000 <ssh_command>")
print("2. Send request:")
print("""
import requests
response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "messages": [{"role": "user", "content": "Hello, how are you?"}],
        "max_tokens": 100
    }
)
print(response.json()["choices"][0]["message"]["content"])
""")
```

### Option 2: Multi-GPU for Large Models

```python
import flow
from flow import TaskConfig

# Multi-GPU vLLM configuration for 70B model
large_model_config = TaskConfig(
    name="vllm-llama-70b",
    command="""
    # Install vLLM
    pip install vllm
    
    # Start vLLM with tensor parallelism
    python -m vllm.entrypoints.openai.api_server \
        --model meta-llama/Llama-3.1-70B-Instruct \
        --tensor-parallel-size 4 \
        --host 0.0.0.0 \
        --port 8000 \
        --max-model-len 8192 \
        --trust-remote-code
    """,
    instance_type="4xa100",  # 4x80GB = 320GB for 70B model
    ports=[8000],
    max_run_time_hours=24,
    max_price_per_hour=50.00,
    environment={
        "HF_TOKEN": "your-huggingface-token"  # For gated models
    }
)

# Launch with error handling
try:
    flow_client = flow.Flow()
    task = flow_client.run(large_model_config, wait=True)
    print(f"Large model server started: {task.task_id}")
    print(f"Cost: {task.cost_per_hour}/hour")
    
    # Monitor logs
    for line in task.logs(follow=True, tail=50):
        print(line, end='')
        if "Application startup complete" in line:
            break
            
except flow.errors.ResourceUnavailableError as e:
    print(f"No instances available: {e}")
    print("Try: smaller instance type, higher price limit, or different region")
except Exception as e:
    print(f"Error: {e}")
```

## 4. Batch Inference Example

```python
import flow
from flow import TaskConfig

# Batch inference script
batch_script = '''
import json
from vllm import LLM, SamplingParams

# Initialize model
llm = LLM(model="microsoft/phi-2", trust_remote_code=True)
sampling_params = SamplingParams(temperature=0.8, top_p=0.95, max_tokens=100)

# Load prompts
prompts = [
    "Explain quantum computing in simple terms:",
    "What are the benefits of exercise?",
    "How does photosynthesis work?",
]

# Run inference
outputs = llm.generate(prompts, sampling_params)

# Save results
results = []
for output in outputs:
    results.append({
        "prompt": output.prompt,
        "generated_text": output.outputs[0].text
    })

with open("/workspace/results.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"Processed {len(results)} prompts")
'''

# Run batch inference
batch_config = TaskConfig(
    name="batch-inference",
    command=f"python -c '{batch_script}'",
    instance_type="a100",
    max_run_time_hours=1,
    max_price_per_hour=10.00
)

flow_client = flow.Flow()
batch_task = flow_client.run(batch_config)
print(f"Batch inference started: {batch_task.task_id}")

# Wait and show results
batch_task.wait()
print(batch_task.logs())
print(f"Total cost: {batch_task.total_cost}")
```

## Cost Analysis

| Model Size | Instance Type | Notes |
|------------|---------------|---------|
| 7B (Qwen, Llama) | a100 | Single A100 80GB |
| 13B | a100 | Fits comfortably |
| 70B | 4xa100 | Multi-GPU required |
| Mixtral 8x7B | 2xa100 | MoE architecture |

**Cost Optimization Tips:**
- Use single A100 for models ≤ 13B parameters
- Enable quantization for larger models
- Consider batch inference vs. server for one-time jobs
- Monitor GPU utilization to right-size instances

## Error Handling

```python
import flow
from flow import TaskConfig
from flow.errors import FlowError, ResourceUnavailableError, AuthenticationError

def run_inference_with_retry(config: TaskConfig, max_retries: int = 3):
    """Run inference with automatic retry on failure."""
    flow_client = flow.Flow()
    
    for attempt in range(max_retries):
        try:
            task = flow_client.run(config, wait=True)
            
            # Check if task started successfully
            if task.status == "FAILED":
                print(f"Task failed: {task.message}")
                if "out of memory" in task.message.lower():
                    # Try smaller model or larger instance
                    config.instance_type = "2xa100"
                    continue
            
            return task
            
        except ResourceUnavailableError as e:
            print(f"No instances available (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                # Try different instance type
                alternatives = ["a100", "2xa100", "4xa100"]
                for alt in alternatives:
                    if alt != config.instance_type:
                        config.instance_type = alt
                        print(f"Trying {alt}...")
                        break
            else:
                raise
                
        except AuthenticationError:
            print("Authentication failed. Run 'flow init' to configure API key")
            raise
            
        except Exception as e:
            print(f"Unexpected error: {e}")
            if attempt == max_retries - 1:
                raise

# Use with retry logic
config = TaskConfig(
    name="inference-with-retry",
    command="python -m vllm.entrypoints.openai.api_server --model gpt2",
    instance_type="a100",
    max_price_per_hour=10.00
)

task = run_inference_with_retry(config)
if task:
    print(f"Success! Task: {task.task_id}")
```

## Next Steps

- [Production Serving Guide](../../guides/production-inference.md) - Load balancing, auto-scaling
- [Model Optimization](../../guides/model-optimization.md) - Quantization, pruning
- [Multi-Region Deployment](../../guides/multi-region.md) - Global inference
- [Monitoring & Observability](../../guides/monitoring.md) - Metrics, logging

## Troubleshooting

### Common Issues

1. **"CUDA out of memory"**
   - Use larger instance: `a100` → `2xa100`
   - Reduce `max_model_len` parameter
   - Enable quantization with `--quantization awq`

2. **"Model not found"**
   - Check model name on HuggingFace
   - Provide HF_TOKEN for gated models
   - Use `--trust-remote-code` for custom models

3. **Server not accessible**
   - Check firewall rules
   - Verify port configuration
   - Use SSH tunneling for development

4. **High latency**
   - Use region closer to users
   - Enable continuous batching
   - Optimize model with TensorRT-LLM