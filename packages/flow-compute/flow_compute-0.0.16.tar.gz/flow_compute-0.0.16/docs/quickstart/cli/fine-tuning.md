# CLI Fine-Tuning Quickstart

Fine-tune large language models using Flow's command-line interface with LoRA and QLoRA techniques.

## Prerequisites
- Flow CLI installed: `pip install flow-sdk`
- API key configured: `flow init`
- HuggingFace token (for gated models): `export HF_TOKEN=hf_xxxxx`

## 1. Quick LoRA Fine-tuning (5 minutes)

### Basic LoRA Fine-tuning

```bash
# Create fine-tuning script
cat > lora_finetune.sh << 'EOF'
#!/bin/bash

# Install dependencies
pip install transformers accelerate peft datasets bitsandbytes

# Run LoRA fine-tuning
python - << 'PYTHON_SCRIPT'
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, TaskType
from trl import SFTTrainer

# Model configuration
model_name = "meta-llama/Llama-2-7b-hf"
output_dir = "./llama2-lora"

print(f"Loading model: {model_name}")

# Load model in 4-bit for QLoRA
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_4bit=True,
    torch_dtype=torch.float16,
    device_map="auto",
    token=os.environ.get("HF_TOKEN")
)

# Tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name, token=os.environ.get("HF_TOKEN"))
tokenizer.pad_token = tokenizer.eos_token

# LoRA configuration
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,
    lora_alpha=32,
    lora_dropout=0.1,
    target_modules=["q_proj", "v_proj"]
)

# Apply LoRA
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# Load dataset
dataset = load_dataset("tatsu-lab/alpaca", split="train[:1000]")

# Training arguments
training_args = TrainingArguments(
    output_dir=output_dir,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    learning_rate=2e-4,
    fp16=True,
    save_strategy="epoch",
    logging_steps=10,
    report_to="none"
)

# Trainer
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    tokenizer=tokenizer,
    args=training_args,
    dataset_text_field="text",
    max_seq_length=512
)

# Train
print("Starting training...")
trainer.train()

# Save LoRA weights
trainer.save_model(f"{output_dir}/final")
print(f"LoRA weights saved to {output_dir}/final")
PYTHON_SCRIPT
EOF

# Run fine-tuning
flow run \
    --name "llama2-lora-finetune" \
    --instance-type "a100" \
    --env "HF_TOKEN=$HF_TOKEN" \
    --max-runtime "3h" \
    --max-price 15.00 \
    --download "./llama2-lora/*" \
    lora_finetune.sh

# Monitor progress
flow logs llama2-lora-finetune --follow
```

## 2. Custom Dataset Fine-tuning

### Prepare Custom Data

```bash
# Create custom dataset
cat > prepare_dataset.py << 'EOF'
import json
import pandas as pd

# Your custom training data
training_data = [
    {
        "instruction": "What is machine learning?",
        "input": "",
        "output": "Machine learning is a subset of artificial intelligence..."
    },
    {
        "instruction": "Explain neural networks",
        "input": "in simple terms",
        "output": "Neural networks are computing systems inspired by the brain..."
    }
]

# Save in Alpaca format
with open("custom_dataset.json", "w") as f:
    json.dump(training_data, f, indent=2)

# Convert to CSV for easier processing
df = pd.DataFrame(training_data)
df['text'] = df.apply(lambda x: f"### Instruction: {x['instruction']}\n### Input: {x['input']}\n### Response: {x['output']}", axis=1)
df[['text']].to_csv("custom_dataset.csv", index=False)
print(f"Saved {len(training_data)} examples")
EOF

# Fine-tune with custom data
flow run \
    --name "custom-finetune" \
    --instance-type "a100" \
    --upload "custom_dataset.csv" \
    --command "
        pip install transformers accelerate peft datasets
        
        python finetune_custom.py \
            --model_name microsoft/phi-2 \
            --dataset_file custom_dataset.csv \
            --output_dir ./phi2-custom
    " \
    --download "./phi2-custom/*"
```

## 3. Multi-GPU Fine-tuning

### Distributed LoRA Training

```bash
# Create distributed fine-tuning script
cat > distributed_finetune.sh << 'EOF'
#!/bin/bash

# Install dependencies
pip install transformers accelerate peft datasets deepspeed

# Create DeepSpeed config
cat > ds_config.json << 'DS_CONFIG'
{
    "fp16": {
        "enabled": true
    },
    "zero_optimization": {
        "stage": 3,
        "offload_optimizer": {
            "device": "cpu",
            "pin_memory": true
        },
        "offload_param": {
            "device": "cpu",
            "pin_memory": true
        }
    },
    "gradient_accumulation_steps": 4,
    "train_batch_size": "auto",
    "train_micro_batch_size_per_gpu": "auto"
}
DS_CONFIG

# Launch distributed training
accelerate launch \
    --config_file accelerate_config.yaml \
    --num_processes 4 \
    --num_machines 1 \
    --mixed_precision fp16 \
    --deepspeed_config_file ds_config.json \
    finetune_distributed.py \
    --model_name meta-llama/Llama-2-13b-hf \
    --dataset_name yahma/alpaca-cleaned \
    --output_dir ./llama13b-lora
EOF

# Run on multiple GPUs
flow run \
    --name "distributed-finetune" \
    --instance-type "4xa100" \
    --env "HF_TOKEN=$HF_TOKEN" \
    --max-runtime "6h" \
    --max-price 30.00 \
    distributed_finetune.sh
```

## 4. Continuous Fine-tuning Pipeline

### Automated Fine-tuning Workflow

```bash
# Create pipeline script
cat > finetune_pipeline.sh << 'EOF'
#!/bin/bash

# Configuration
MODEL_NAME="${1:-meta-llama/Llama-2-7b-hf}"
DATASET="${2:-tatsu-lab/alpaca}"
OUTPUT_DIR="${3:-./output}"

# Step 1: Validate dataset
echo "Validating dataset..."
python validate_dataset.py --dataset $DATASET

# Step 2: Run fine-tuning with checkpointing
echo "Starting fine-tuning..."
python finetune_with_resume.py \
    --model_name $MODEL_NAME \
    --dataset $DATASET \
    --output_dir $OUTPUT_DIR \
    --save_steps 500 \
    --eval_steps 100 \
    --logging_steps 10

# Step 3: Evaluate fine-tuned model
echo "Evaluating model..."
python evaluate_model.py \
    --model_path $OUTPUT_DIR/final \
    --test_dataset $DATASET-test

# Step 4: Convert to GGUF for llama.cpp
echo "Converting to GGUF..."
python convert_to_gguf.py \
    --model_path $OUTPUT_DIR/final \
    --output_path $OUTPUT_DIR/model.gguf

echo "Pipeline complete!"
EOF

# Run pipeline with automatic retries
flow run \
    --name "finetune-pipeline" \
    --instance-type "a100" \
    --env "HF_TOKEN=$HF_TOKEN" \
    --max-runtime "8h" \
    --retry-on-failure \
    --retry-count 3 \
    --volume "name=checkpoints,mount=/workspace/checkpoints" \
    "bash finetune_pipeline.sh mistralai/Mistral-7B-v0.1 custom-dataset ./models"
```

## 5. Parameter-Efficient Fine-tuning Comparison

### Compare Different PEFT Methods

```bash
# Create comparison script
cat > compare_peft_methods.py << 'EOF'
import os
import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, PrefixTuningConfig, PromptTuningConfig, get_peft_model
import json

def compare_methods(model_name, dataset):
    results = {}
    
    # Base model
    base_model = AutoModelForCausalLM.from_pretrained(
        model_name,
        load_in_8bit=True,
        device_map="auto"
    )
    base_params = sum(p.numel() for p in base_model.parameters())
    
    # LoRA
    lora_config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"])
    lora_model = get_peft_model(base_model, lora_config)
    lora_trainable = sum(p.numel() for p in lora_model.parameters() if p.requires_grad)
    
    results["lora"] = {
        "trainable_params": lora_trainable,
        "percentage": (lora_trainable / base_params) * 100
    }
    
    # Prefix Tuning
    prefix_config = PrefixTuningConfig(num_virtual_tokens=20)
    prefix_model = get_peft_model(base_model, prefix_config)
    prefix_trainable = sum(p.numel() for p in prefix_model.parameters() if p.requires_grad)
    
    results["prefix_tuning"] = {
        "trainable_params": prefix_trainable,
        "percentage": (prefix_trainable / base_params) * 100
    }
    
    # Save results
    with open("peft_comparison.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    compare_methods("gpt2", "imdb")
EOF

# Run comparison
flow run \
    --name "peft-comparison" \
    --instance-type "a100" \
    --command "
        pip install transformers peft accelerate
        python compare_peft_methods.py
    " \
    --download "peft_comparison.json"
```

## 6. Production Fine-tuning

### Scheduled Fine-tuning Jobs

```bash
# Create cron-like fine-tuning
cat > scheduled_finetune.sh << 'EOF'
#!/bin/bash

# Check for new data
NEW_DATA=$(aws s3 ls s3://my-bucket/new-training-data/ --recursive | wc -l)

if [ $NEW_DATA -gt 0 ]; then
    echo "New training data found: $NEW_DATA files"
    
    # Download new data
    aws s3 sync s3://my-bucket/new-training-data/ ./new_data/
    
    # Merge with existing dataset
    python merge_datasets.py \
        --existing ./data/train.json \
        --new ./new_data/*.json \
        --output ./data/train_updated.json
    
    # Run incremental fine-tuning
    python incremental_finetune.py \
        --base_model ./models/current/adapter_model.bin \
        --new_data ./data/train_updated.json \
        --output_dir ./models/updated/
    
    # Validate new model
    python validate_model.py --model_path ./models/updated/
    
    # Deploy if validation passes
    if [ $? -eq 0 ]; then
        echo "Deploying updated model..."
        cp -r ./models/updated/* ./models/current/
        
        # Trigger model reload
        curl -X POST http://model-server:8000/reload
    fi
    
    # Archive processed data
    aws s3 mv s3://my-bucket/new-training-data/ s3://my-bucket/processed/ --recursive
fi
EOF

# Schedule daily fine-tuning
flow run \
    --name "scheduled-finetune" \
    --instance-type "a100" \
    --schedule "0 2 * * *" \  # Run at 2 AM daily
    --env "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID" \
    --env "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY" \
    scheduled_finetune.sh
```

## 7. Cost Optimization Strategies

### Gradient Checkpointing & Mixed Precision

```bash
# Optimized fine-tuning configuration
flow run \
    --name "optimized-finetune" \
    --instance-type "a100" \  # Single A100 80GB
    --spot \  # 70% cost savings
    --max-interruptions 3 \
    --command "
        # Install with optimization libraries
        pip install transformers accelerate peft bitsandbytes
        
        # Run with memory optimizations
        python finetune.py \
            --model_name meta-llama/Llama-2-7b-hf \
            --load_in_8bit \
            --gradient_checkpointing \
            --fp16 \
            --per_device_train_batch_size 1 \
            --gradient_accumulation_steps 16 \
            --max_grad_norm 0.3 \
            --warmup_ratio 0.03
    "
```

### Budget-Aware Fine-tuning

```bash
# Set strict budget limits
MAX_BUDGET=50.00
HOURLY_RATE=5.00
MAX_HOURS=$(echo "$MAX_BUDGET / $HOURLY_RATE" | bc)

flow run \
    --name "budget-finetune" \
    --instance-type "a100" \
    --max-total-cost $MAX_BUDGET \
    --max-runtime "${MAX_HOURS}h" \
    --command "python finetune.py --early_stopping_patience 3"
```

## 8. Fine-tuning Monitoring

### Real-time Training Metrics

```bash
# Create monitoring script
cat > monitor_training.sh << 'EOF'
#!/bin/bash

# Start TensorBoard
tensorboard --logdir ./logs --host 0.0.0.0 --port 6006 &

# Start training with live metrics
python finetune.py \
    --logging_dir ./logs \
    --logging_steps 1 \
    --eval_steps 50 \
    --save_steps 100 \
    2>&1 | tee training.log

# Parse and display key metrics
tail -f training.log | grep -E "(loss|eval_loss|learning_rate)" | while read line; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $line"
done
EOF

# Run with monitoring
flow run \
    --name "monitored-finetune" \
    --instance-type "a100" \
    --ports 6006 \
    --command "bash monitor_training.sh"

# Access TensorBoard
flow port-forward monitored-finetune 6006:6006
```

## Common Issues and Solutions

### Out of Memory

```bash
# Reduce memory usage
flow run \
    --command "
        # Use gradient checkpointing
        export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
        
        python finetune.py \
            --gradient_checkpointing \
            --per_device_train_batch_size 1 \
            --gradient_accumulation_steps 32 \
            --load_in_8bit
    "
```

### Slow Training

```bash
# Optimize training speed
flow run \
    --instance-type "8xa100" \  # More GPUs
    --command "
        # Use DeepSpeed ZeRO
        deepspeed finetune.py \
            --deepspeed ds_config.json \
            --num_gpus 8
    "
```

### Model Quality Issues

```bash
# Improve model quality
flow run \
    --command "
        python finetune.py \
            --num_train_epochs 5 \  # More epochs
            --learning_rate 5e-5 \  # Lower LR
            --warmup_steps 500 \  # Longer warmup
            --eval_strategy steps \
            --eval_steps 100 \
            --save_best_model
    "
```

## Next Steps

- [Model Evaluation](../../guides/model-evaluation.md) - Test fine-tuned models
- [Model Deployment](../inference.md) - Serve fine-tuned models
- [Advanced Fine-tuning](../../guides/advanced-finetuning.md) - Multi-task, RLHF
- [Dataset Preparation](../../guides/dataset-preparation.md) - Data best practices