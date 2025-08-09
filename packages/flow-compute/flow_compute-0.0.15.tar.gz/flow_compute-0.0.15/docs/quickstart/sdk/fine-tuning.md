# Fine-tune LLMs in 5 Minutes

Fine-tune large language models efficiently using LoRA and QLoRA techniques.

## Prerequisites
- Flow SDK installed: `pip install flow-sdk`
- API key configured: `flow init`
- HuggingFace token (for gated models): Get from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

## 1. Quick LoRA Fine-tuning Example

### Create Fine-tuning Script

Save as `finetune_lora.py`:

```python
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    BitsAndBytesConfig
)
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
from trl import SFTTrainer
import os

def print_trainable_parameters(model):
    """Print the percentage of trainable parameters."""
    trainable_params = 0
    all_param = 0
    for _, param in model.named_parameters():
        all_param += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
    print(
        f"trainable params: {trainable_params:,} || "
        f"all params: {all_param:,} || "
        f"trainable%: {100 * trainable_params / all_param:.2f}"
    )

def main():
    # Model configuration
    model_name = "meta-llama/Llama-2-7b-hf"
    
    # Check for HuggingFace token
    if "HF_TOKEN" not in os.environ:
        print("Warning: HF_TOKEN not set. May not be able to access gated models.")
    
    print(f"Loading model: {model_name}")
    
    # 4-bit quantization config for QLoRA
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )
    
    # Load model with quantization
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        token=os.environ.get("HF_TOKEN")
    )
    
    # Prepare model for training
    model = prepare_model_for_kbit_training(model)
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True,
        token=os.environ.get("HF_TOKEN")
    )
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    # LoRA configuration
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,  # LoRA rank
        lora_alpha=32,
        lora_dropout=0.1,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        bias="none"
    )
    
    # Apply LoRA
    model = get_peft_model(model, lora_config)
    print_trainable_parameters(model)
    
    # Load dataset
    print("Loading dataset...")
    dataset = load_dataset("tatsu-lab/alpaca", split="train[:1000]")
    
    # Format dataset
    def format_instruction(sample):
        return f"""### Instruction:
{sample['instruction']}

### Input:
{sample['input']}

### Response:
{sample['output']}"""
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="./llama-lora-alpaca",
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        num_train_epochs=3,
        learning_rate=2e-4,
        warmup_steps=100,
        logging_steps=25,
        save_strategy="epoch",
        evaluation_strategy="no",
        save_total_limit=2,
        load_best_model_at_end=False,
        report_to="none",  # Disable wandb for quickstart
        remove_unused_columns=False,
        fp16=True,
        bf16=False,
        gradient_checkpointing=True,
        ddp_find_unused_parameters=False,
    )
    
    # Create trainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        tokenizer=tokenizer,
        max_seq_length=512,
        formatting_func=format_instruction,
        args=training_args,
    )
    
    # Start training
    print("Starting training...")
    trainer.train()
    
    # Save LoRA weights
    print("Saving LoRA weights...")
    trainer.model.save_pretrained("./llama-lora-alpaca/final")
    tokenizer.save_pretrained("./llama-lora-alpaca/final")
    
    print("Fine-tuning completed!")
    print(f"LoRA weights saved to ./llama-lora-alpaca/final")

if __name__ == "__main__":
    main()
```

### Run Fine-tuning on GPU

```python
import flow
from flow import TaskConfig
from flow.errors import ResourceUnavailableError, FlowError

# Fine-tuning configuration
finetune_config = TaskConfig(
    name="llama2-lora-finetuning",
    command="""
    # Install dependencies
    pip install transformers accelerate peft trl datasets bitsandbytes
    
    # Run fine-tuning
    python finetune_lora.py
    """,
    instance_type="a100_80gb",  # 80GB for 7B model + optimizer states
    max_run_time_hours=3,
    max_price_per_hour=5.00,
    environment={
        "HF_TOKEN": "your-huggingface-token",  # Replace with actual token
        "TRANSFORMERS_CACHE": "/workspace/cache"
    }
)

# Run with error handling
flow_client = flow.Flow()

try:
    task = flow_client.run(finetune_config, wait=True)
    print(f"Fine-tuning task: {task.task_id}")
    print(f"Instance: {task.instance_type}")
    print(f"Cost per hour: {task.cost_per_hour}")
    
    # Monitor training progress
    print("\nTraining logs:")
    for line in task.logs(follow=True):
        print(line, end='')
        
        # Check for completion
        if "Fine-tuning completed!" in line:
            print("\n✓ Training finished successfully!")
            break
        
        # Check for errors
        if "error" in line.lower() and "wandb" not in line.lower():
            print(f"\n⚠️  Potential error detected: {line}")
    
    # Final status
    task.refresh()
    print(f"\nFinal status: {task.status}")
    print(f"Total runtime: {task.runtime_seconds / 3600:.2f} hours")
    print(f"Total cost: {task.total_cost}")
    
except ResourceUnavailableError as e:
    print(f"❌ No instances available: {e}")
    print("\nTry:")
    print("- Different instance: a100_40gb or 2xa100_40gb")
    print("- Higher price limit: max_price_per_hour=10.00")
    print("- Different region")
    
except FlowError as e:
    print(f"❌ Flow error: {e}")
    if "authentication" in str(e).lower():
        print("Run 'flow init' to configure API key")
        
except Exception as e:
    print(f"❌ Unexpected error: {e}")
```

## 2. Multi-GPU Fine-tuning

### Distributed Fine-tuning Script

Save as `finetune_distributed.py`:

```python
import os
import torch
import torch.distributed as dist
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, TaskType

def setup_distributed():
    """Initialize distributed training if available."""
    if "LOCAL_RANK" in os.environ:
        dist.init_process_group("nccl")
        torch.cuda.set_device(int(os.environ["LOCAL_RANK"]))
        return dist.get_rank(), dist.get_world_size()
    return 0, 1

def main():
    rank, world_size = setup_distributed()
    
    if rank == 0:
        print(f"Training on {world_size} GPUs")
    
    # Model setup
    model_name = "mistralai/Mistral-7B-v0.1"
    
    # Load model (distributed across GPUs)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto" if world_size == 1 else None,
        trust_remote_code=True
    )
    
    if world_size > 1:
        model = model.to(f"cuda:{rank}")
    
    # LoRA config
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=32,  # Higher rank for better quality
        lora_alpha=64,
        lora_dropout=0.1,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )
    
    model = get_peft_model(model, lora_config)
    
    # Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    # Dataset
    dataset = load_dataset("yahma/alpaca-cleaned", split="train")
    
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            padding="max_length",
            max_length=512
        )
    
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    
    # Training arguments for distributed
    training_args = TrainingArguments(
        output_dir="./mistral-lora-distributed",
        per_device_train_batch_size=8,
        gradient_accumulation_steps=2,
        num_train_epochs=1,
        learning_rate=1e-4,
        fp16=False,
        bf16=True,
        logging_steps=10,
        save_strategy="steps",
        save_steps=500,
        evaluation_strategy="no",
        ddp_find_unused_parameters=False if world_size > 1 else None,
        report_to="none"
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )
    
    # Train
    if rank == 0:
        print("Starting distributed training...")
    
    trainer.train()
    
    # Save from rank 0 only
    if rank == 0:
        trainer.save_model("./mistral-lora-distributed/final")
        print("Model saved!")
    
    if world_size > 1:
        dist.destroy_process_group()

if __name__ == "__main__":
    main()
```

### Launch Multi-GPU Training

```python
import flow
from flow import TaskConfig

# Multi-GPU fine-tuning
distributed_config = TaskConfig(
    name="distributed-finetuning",
    command="""
    # Install dependencies
    pip install transformers accelerate peft datasets
    
    # Run distributed training
    torchrun \
        --nproc_per_node=4 \
        --master_port=29501 \
        finetune_distributed.py
    """,
    instance_type="4xa100_80gb",  # 4x 80GB GPUs
    max_run_time_hours=4,
    max_price_per_hour=20.00
)

flow_client = flow.Flow()
task = flow_client.run(distributed_config, wait=True)
print(f"Distributed fine-tuning: {task.task_id}")
print(f"Cost: {task.cost_per_hour}/hour on {task.instance_type}")
```

## 3. Fine-tuning with Custom Datasets

```python
# Custom dataset fine-tuning script
custom_dataset_script = '''
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import Dataset
from peft import LoraConfig, get_peft_model, TaskType

# Load your custom data
def load_custom_data(file_path):
    """Load custom JSON training data."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Expected format: [{"prompt": "...", "completion": "..."}, ...]
    return Dataset.from_list(data)

def main():
    # Load custom dataset
    train_dataset = load_custom_data("custom_training_data.json")
    print(f"Loaded {len(train_dataset)} training examples")
    
    # Model setup
    model_name = "microsoft/phi-2"
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    # LoRA configuration
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=8,  # Lower rank for smaller model
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=["q_proj", "v_proj"],
    )
    
    model = get_peft_model(model, lora_config)
    
    # Tokenize function
    def tokenize_function(examples):
        # Combine prompt and completion
        texts = [
            f"### Human: {prompt}\n### Assistant: {completion}"
            for prompt, completion in zip(examples["prompt"], examples["completion"])
        ]
        
        model_inputs = tokenizer(
            texts,
            max_length=512,
            truncation=True,
            padding="max_length"
        )
        
        # Set labels (same as input_ids for causal LM)
        model_inputs["labels"] = model_inputs["input_ids"].copy()
        
        return model_inputs
    
    # Tokenize dataset
    tokenized_dataset = train_dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=train_dataset.column_names
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="./phi2-custom-lora",
        per_device_train_batch_size=8,
        num_train_epochs=3,
        learning_rate=5e-5,
        warmup_ratio=0.1,
        logging_steps=50,
        save_strategy="epoch",
        fp16=True,
        report_to="none",
        gradient_checkpointing=True,
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        tokenizer=tokenizer,
    )
    
    # Train
    print("Starting training on custom dataset...")
    trainer.train()
    
    # Save model
    trainer.save_model("./phi2-custom-lora/final")
    print("Custom fine-tuning completed!")

if __name__ == "__main__":
    main()
'''

# Prepare custom data
custom_data = [
    {"prompt": "What is machine learning?", "completion": "Machine learning is a subset of AI..."},
    {"prompt": "Explain neural networks", "completion": "Neural networks are computing systems..."},
    # Add your training examples
]

# Run custom fine-tuning
import json

custom_config = TaskConfig(
    name="custom-dataset-finetuning",
    command=f"""
    # Save custom data
    cat > custom_training_data.json << 'EOF'
{json.dumps(custom_data, indent=2)}
EOF

    # Install dependencies
    pip install transformers accelerate peft datasets
    
    # Run fine-tuning
    python -c '{custom_dataset_script}'
    """,
    instance_type="a100_40gb",
    max_run_time_hours=2,
    max_price_per_hour=3.50
)

flow_client = flow.Flow()
task = flow_client.run(custom_config)
print(f"Custom fine-tuning: {task.task_id}")
```

## 4. Resume from Checkpoint

```python
def create_resume_config(checkpoint_path: str = None):
    """Create config for resuming training from checkpoint."""
    
    resume_script = f'''
import os
from transformers import Trainer, TrainingArguments

# Check for existing checkpoint
checkpoint_dir = "./llama-lora-alpaca"
checkpoints = []
if os.path.exists(checkpoint_dir):
    checkpoints = [
        os.path.join(checkpoint_dir, d) 
        for d in os.listdir(checkpoint_dir) 
        if d.startswith("checkpoint-")
    ]
    checkpoints.sort(key=lambda x: int(x.split("-")[-1]))

resume_from_checkpoint = None
if checkpoints:
    resume_from_checkpoint = checkpoints[-1]
    print(f"Resuming from checkpoint: {{resume_from_checkpoint}}")
else:
    print("Starting fresh training")

# ... rest of training setup ...

# Train with resume
trainer.train(resume_from_checkpoint=resume_from_checkpoint)
'''
    
    return TaskConfig(
        name="resume-finetuning",
        command=f"python -c '{resume_script}'",
        instance_type="a100_80gb",
        max_run_time_hours=2,
        volumes=[{
            "name": "checkpoints",
            "mount_path": "/workspace/llama-lora-alpaca"
        }]
    )
```

## 5. Cost Optimization Strategies

### Efficient Fine-tuning Configuration

```python
def get_optimal_config(model_size: str, dataset_size: int) -> dict:
    """Get optimal configuration for model size and dataset."""
    
    configs = {
        "7B": {
            "small": {  # < 10k samples
                "instance": "a100_40gb",
                "lora_r": 8,
                "batch_size": 4,
                "gradient_accumulation": 4
            },
            "medium": {  # 10k-100k samples
                "instance": "a100_80gb",
                "lora_r": 16,
                "batch_size": 8,
                "gradient_accumulation": 2
            },
            "large": {  # > 100k samples
                "instance": "2xa100_80gb",
                "lora_r": 32,
                "batch_size": 16,
                "gradient_accumulation": 1
            }
        },
        "13B": {
            "small": {
                "instance": "a100_80gb",
                "lora_r": 8,
                "batch_size": 2,
                "gradient_accumulation": 8
            }
        },
        "70B": {
            "small": {
                "instance": "4xa100_80gb",
                "lora_r": 16,
                "batch_size": 1,
                "gradient_accumulation": 16
            }
        }
    }
    
    size_category = "small" if dataset_size < 10000 else "medium" if dataset_size < 100000 else "large"
    return configs.get(model_size, {}).get(size_category, configs["7B"]["small"])

# Example usage
config = get_optimal_config("7B", 50000)
print(f"Recommended: {config['instance']} with LoRA rank {config['lora_r']}")
```

## Cost Analysis

### Fine-tuning Cost Estimates

| Model | Method | Dataset | Time | Cost |
|-------|--------|---------|------|------|
| Llama-2-7B | LoRA (r=16) | 1k samples | 1 hr | ~$5 |
| Llama-2-7B | LoRA (r=16) | 10k samples | 3 hrs | ~$15 |
| Llama-2-13B | LoRA (r=8) | 10k samples | 4 hrs | ~$28 |
| Llama-2-70B | LoRA (r=16) | 1k samples | 2 hrs | ~$56 |
| Mistral-7B | Full | 10k samples | 8 hrs | ~$56 |

### QLoRA vs LoRA vs Full Fine-tuning

| Method | Memory Usage | Training Speed | Quality | Cost |
|--------|--------------|----------------|---------|------|
| QLoRA | 25% | 80% | 95% | $ |
| LoRA | 50% | 90% | 97% | $$ |
| Full | 100% | 100% | 100% | $$$$ |

## Next Steps

- [Production Fine-tuning](../../guides/production-finetuning.md) - Best practices
- [Model Evaluation](../../guides/model-evaluation.md) - Benchmarking
- [Deployment](../inference.md) - Serve fine-tuned models
- [Dataset Preparation](../../guides/dataset-preparation.md) - Data processing

## Troubleshooting

### Common Issues

1. **"CUDA out of memory"**
   ```python
   # Reduce batch size
   per_device_train_batch_size=2
   # Increase gradient accumulation
   gradient_accumulation_steps=8
   # Enable gradient checkpointing
   gradient_checkpointing=True
   ```

2. **"Cannot access model"**
   ```python
   # Set HuggingFace token
   environment={"HF_TOKEN": "hf_xxxxx"}
   # Or use public models
   model_name = "teknium/OpenHermes-2.5-Mistral-7B"
   ```

3. **"Training loss not decreasing"**
   ```python
   # Adjust learning rate
   learning_rate=5e-5  # Try 1e-4 or 1e-5
   # Increase LoRA rank
   r=32  # Higher rank = more parameters
   # Check data format
   ```

4. **"Checkpoint save failed"**
   ```python
   # Use persistent volume
   volumes=[{"name": "checkpoints", "mount_path": "/workspace/output"}]
   # Reduce checkpoint frequency
   save_steps=1000
   ```