# CLI Inference Quickstart

Deploy and serve models using Flow's command-line interface.

## Prerequisites
- Flow CLI installed: `pip install flow-sdk`
- API key configured: `flow init`

## 1. Quick Model Serving (2 minutes)

### Serve with vLLM

```bash
# Deploy Llama model with vLLM
flow run \
    --name "llama-server" \
    --instance-type "a100" \
    --ports 8000 \
    --max-runtime "24h" \
    --max-price 10.00 \
    --command "
        pip install vllm
        vllm serve meta-llama/Llama-2-7b-chat-hf \
            --host 0.0.0.0 \
            --port 8000 \
            --max-model-len 4096
    "

# Get server endpoint
flow status llama-server
```

### Test the Server

```bash
# Get the task ID
TASK_ID=$(flow list --name "llama-server" --format json | jq -r '.[0].task_id')

# Port forward to local
flow port-forward $TASK_ID 8000:8000

# Test inference
curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "meta-llama/Llama-2-7b-chat-hf",
        "messages": [{"role": "user", "content": "Hello!"}],
        "max_tokens": 100
    }'
```

## 2. Batch Inference

### Create Batch Script

Save as `batch_inference.sh`:

```bash
#!/bin/bash
# Batch inference with vLLM

# Install dependencies
pip install vllm pandas tqdm

# Run batch inference
python - << 'EOF'
import pandas as pd
from vllm import LLM, SamplingParams
import json

# Load model
llm = LLM("mistralai/Mistral-7B-v0.1", max_model_len=8192)

# Load input data
prompts = [
    "Explain quantum computing in simple terms.",
    "What are the benefits of renewable energy?",
    "How does machine learning work?",
    # Add more prompts from your dataset
]

# Inference parameters
params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=200
)

# Run batch inference
outputs = llm.generate(prompts, params)

# Save results
results = []
for prompt, output in zip(prompts, outputs):
    results.append({
        "prompt": prompt,
        "response": output.outputs[0].text
    })

with open("inference_results.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"Processed {len(results)} prompts")
EOF
```

### Run Batch Job

```bash
# Submit batch inference job
flow run \
    --name "batch-inference" \
    --instance-type "a100" \
    --max-runtime "2h" \
    --max-price 20.00 \
    --upload "data/prompts.txt" \
    --download "inference_results.json" \
    batch_inference.sh

# Monitor progress
flow logs batch-inference --follow

# Download results when complete
flow download batch-inference inference_results.json ./results/
```

## 3. Multi-Model Serving

### Deploy Multiple Models

```bash
# Create serving script
cat > multi_model_server.py << 'EOF'
from fastapi import FastAPI
from vllm import LLM
import uvicorn

app = FastAPI()

# Load multiple models
models = {
    "small": LLM("microsoft/phi-2", max_model_len=2048),
    "medium": LLM("mistralai/Mistral-7B-v0.1", max_model_len=4096),
    "large": LLM("meta-llama/Llama-2-13b-chat-hf", max_model_len=4096)
}

@app.post("/generate/{model_size}")
async def generate(model_size: str, prompt: str, max_tokens: int = 100):
    if model_size not in models:
        return {"error": f"Model size {model_size} not available"}
    
    output = models[model_size].generate([prompt], max_tokens=max_tokens)
    return {"response": output[0].outputs[0].text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Deploy multi-model server
flow run \
    --name "multi-model-server" \
    --instance-type "a100" \
    --ports 8000 \
    --max-runtime "24h" \
    --command "
        pip install vllm fastapi uvicorn
        python multi_model_server.py
    "
```

## 4. TGI (Text Generation Inference)

### Deploy with Hugging Face TGI

```bash
# Deploy TGI server
flow run \
    --name "tgi-server" \
    --instance-type "a100" \
    --container "ghcr.io/huggingface/text-generation-inference:latest" \
    --ports 8080 \
    --env "HF_TOKEN=$HF_TOKEN" \
    --max-runtime "24h" \
    --command "
        text-generation-launcher \
            --model-id meta-llama/Llama-2-7b-chat-hf \
            --port 8080 \
            --max-input-length 2048 \
            --max-total-tokens 4096
    "

# Test TGI endpoint
flow exec tgi-server -- curl http://localhost:8080/generate \
    -X POST \
    -H 'Content-Type: application/json' \
    -d '{"inputs": "What is deep learning?", "parameters": {"max_new_tokens": 100}}'
```

## 5. Custom Inference Server

### FastAPI Model Server

Save as `model_server.py`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import uvicorn

app = FastAPI()

# Request/Response models
class InferenceRequest(BaseModel):
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7

class InferenceResponse(BaseModel):
    text: str
    tokens_generated: int

# Load model on startup
model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

if torch.cuda.is_available():
    model = model.to("cuda")

@app.post("/generate", response_model=InferenceResponse)
async def generate(request: InferenceRequest):
    # Tokenize input
    inputs = tokenizer(request.prompt, return_tensors="pt")
    if torch.cuda.is_available():
        inputs = inputs.to("cuda")
    
    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=request.max_tokens,
            temperature=request.temperature,
            do_sample=True
        )
    
    # Decode
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    new_tokens = len(outputs[0]) - len(inputs.input_ids[0])
    
    return InferenceResponse(
        text=generated_text,
        tokens_generated=new_tokens
    )

@app.get("/health")
async def health():
    return {"status": "healthy", "model": model_name}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Deploy Custom Server

```bash
# Deploy the server
flow run \
    --name "custom-model-server" \
    --instance-type "a100" \
    --upload "model_server.py" \
    --ports 8000 \
    --max-runtime "24h" \
    --command "
        pip install torch transformers fastapi uvicorn
        python model_server.py
    "

# Health check
flow exec custom-model-server -- curl http://localhost:8000/health

# Test inference
flow exec custom-model-server -- curl http://localhost:8000/generate \
    -X POST \
    -H 'Content-Type: application/json' \
    -d '{"prompt": "Once upon a time", "max_tokens": 50}'
```

## 6. Inference Pipeline

### Create Pipeline Script

```bash
#!/bin/bash
# inference_pipeline.sh - Complete inference pipeline

# Step 1: Download model
echo "Downloading model..."
flow run \
    --name "download-model" \
    --instance-type "cpu" \
    --command "
        pip install huggingface-hub
        python -c '
from huggingface_hub import snapshot_download
snapshot_download(\"mistralai/Mistral-7B-v0.1\", cache_dir=\"./models\")
'
    " \
    --download "./models"

# Step 2: Optimize model
echo "Optimizing model..."
flow run \
    --name "optimize-model" \
    --instance-type "a100" \
    --upload "./models" \
    --command "
        pip install optimum
        optimum-cli export onnx \
            --model ./models/mistralai/Mistral-7B-v0.1 \
            --task text-generation \
            ./optimized_model
    " \
    --download "./optimized_model"

# Step 3: Deploy optimized model
echo "Deploying model..."
flow run \
    --name "production-server" \
    --instance-type "a100" \
    --upload "./optimized_model" \
    --ports 8000 \
    --max-runtime "720h" \
    --spot \
    --command "
        pip install onnxruntime fastapi uvicorn
        python serve_optimized.py
    "

echo "Pipeline complete! Server running at production-server"
```

## 7. Cost Optimization

### Spot Instance Inference

```bash
# Use spot instances for 70% savings
flow run \
    --name "spot-inference" \
    --instance-type "a100" \
    --spot \
    --max-interruptions 3 \
    --command "python batch_inference.py"

# Auto-scaling inference
for i in {1..3}; do
    flow run \
        --name "inference-worker-$i" \
        --instance-type "a100" \
        --spot \
        --command "python inference_worker.py"
done
```

### Instance Selection Guide

```bash
# Small models (< 7B parameters)
flow run --instance-type "l40s" ...    # 48GB VRAM, $1.20/hr

# Medium models (7B-13B)
flow run --instance-type "a100" ...      # 80GB VRAM

# Large models (30B-70B)
flow run --instance-type "2xa100" ... # 80GB VRAM, $5.00/hr
flow run --instance-type "4xa100" ...    # 320GB VRAM

# Very large models (> 70B)
flow run --instance-type "8xa100" ...    # 640GB VRAM

# Note: Mithril uses dynamic pricing. Set --max-price to control costs.
```

## 8. Monitoring and Logs

```bash
# Real-time monitoring
flow logs <task_id> --follow

# Check resource usage
flow exec <task_id> -- nvidia-smi

# Monitor endpoint health
while true; do
    flow exec <task_id> -- curl -s http://localhost:8000/health
    sleep 30
done

# Export metrics
flow get <task_id> --format json > metrics.json
```

## Common Patterns

### Load Balancing

```bash
# Deploy multiple inference servers
for i in {1..3}; do
    flow run \
        --name "inference-server-$i" \
        --instance-type "a100" \
        --ports "800$i" \
        --command "vllm serve model --port 800$i"
done

# Simple load balancer
flow run \
    --name "load-balancer" \
    --instance-type "cpu" \
    --ports 80 \
    --command "nginx -g 'daemon off;'"
```

### A/B Testing

```bash
# Deploy model A
flow run \
    --name "model-a" \
    --instance-type "a100" \
    --env "MODEL_VERSION=v1" \
    --command "python serve.py"

# Deploy model B
flow run \
    --name "model-b" \
    --instance-type "a100" \
    --env "MODEL_VERSION=v2" \
    --command "python serve.py"

# Route traffic
flow run \
    --name "ab-router" \
    --command "python ab_test_router.py"
```

## Troubleshooting

### "CUDA out of memory"
```bash
# Use larger instance
flow cancel <task_id>
flow run --instance-type "2xa100" ...

# Or reduce batch size
--env "BATCH_SIZE=1"
```

### "Model download timeout"
```bash
# Pre-download model
flow run \
    --name "download" \
    --command "huggingface-cli download model-name"
```

### "Port not accessible"
```bash
# Check port forwarding
flow port-forward <task_id> 8000:8000

# Or use SSH tunnel
ssh -L 8000:localhost:8000 $(flow ssh-command <task_id>)
```

## Next Steps

- [CLI Training Guide](training.md) - Train models via CLI
- [CLI Fine-tuning Guide](fine-tuning.md) - Fine-tune models
- [Production Deployment](../../guides/production-inference.md) - Scale to production
- [Model Optimization](../../guides/model-optimization.md) - Optimize inference