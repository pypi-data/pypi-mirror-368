# Flow SDK Cost Estimates Guide

Comprehensive pricing information and cost optimization strategies for GPU workloads.

## GPU Instance Types

### Available Instance Types (Mithril)

| Instance Type | GPUs | VRAM | Best For |
|--------------|------|------|----------|
| `a100` | 1× A100 | 80GB | Training, fine-tuning, inference |
| `2xa100` | 2× A100 | 160GB | Distributed training, larger models |
| `4xa100` | 4× A100 | 320GB | Large-scale training |
| `8xa100` | 8× A100 | 640GB | Massive workloads |
| `h100` | 8× H100 | 640GB | Cutting-edge performance |

**Note**: All A100 instances use 80GB GPUs with SXM4 interconnect. The H100 instance provides 8× H100 80GB GPUs.

## Dynamic Pricing

Mithril uses **auction-based spot pricing**, which means:
- Prices vary based on supply and demand
- You set a maximum price you're willing to pay
- Instances are allocated when capacity is available at or below your price
- Lower prices may result in longer wait times

### Checking Current Prices

```bash
# View current availability and pricing
flow instances

# Check specific instance type
flow instances --type a100

# View auction history
flow auctions --region us-central1-a
```

## Cost Optimization Strategies

### 1. Set Price Limits

```python
# Always set max_price_per_hour to control costs
config = TaskConfig(
    instance_type="a100",
    max_price_per_hour=20.00,  # Your budget limit
    max_total_cost=100.00       # Total budget cap
)
```

### 2. Use Spot Bidding Effectively

```python
# Lower price = potential longer wait
# Higher price = faster allocation
config = TaskConfig(
    instance_type="4xa100",
    max_price_per_hour=30.00,  # Competitive bid
    max_wait_time_minutes=30   # How long to wait for allocation
)
```

### 3. Right-Sizing Instances

```python
def select_optimal_instance(model_size_gb: float, batch_size: int) -> str:
    """Select the most cost-effective instance for your workload."""
    
    # VRAM needed = model_size + gradients + optimizer_states + activations
    vram_needed = model_size_gb * 3 + (batch_size * 0.5)
    
    if vram_needed < 80:
        return "a100"  # Single GPU
    elif vram_needed < 160:
        return "2xa100"
    elif vram_needed < 320:
        return "4xa100"
    else:
        return "8xa100"
```

### 4. Gradient Checkpointing

Reduce memory usage by 30-50%, allowing smaller (cheaper) instances:

```python
# Without gradient checkpointing: Needs 2xa100
# With gradient checkpointing: Fits on single a100

config = TaskConfig(
    instance_type="a100",  # Smaller instance
    command="""
    python train.py \
        --gradient_checkpointing \
        --batch_size 16
    """
)
```

### 5. Mixed Precision Training

Train 2x faster with automatic mixed precision:

```python
# FP16/BF16 training reduces time and cost
config = TaskConfig(
    command="python train.py --fp16 --batch_size 64"
)
```

### 6. Early Stopping

Avoid overtraining and reduce costs:

```python
config = TaskConfig(
    command="""
    python train.py \
        --early_stopping_patience 3 \
        --save_best_model \
        --eval_steps 100
    """,
    max_run_time_hours=24,  # Hard limit
    max_total_cost=100.00   # Budget limit
)
```

## Workload Estimates

### Model Inference

| Model Size | Instance | Throughput | Notes |
|------------|----------|------------|--------|
| 7B params | `a100` | ~100 tok/s | Single GPU sufficient |
| 13B params | `a100` | ~80 tok/s | Quantization helps |
| 70B params | `4xa100` | ~30 tok/s | Tensor parallelism required |
| Mixtral 8x7B | `2xa100` | ~50 tok/s | MoE architecture |

### Training Time Estimates

| Dataset | Model | Instance | Time Estimate |
|---------|-------|----------|---------------|
| CIFAR-10 | ResNet-50 | `a100` | ~2 hours |
| ImageNet | ResNet-152 | `8xa100` | ~40 hours |
| Custom 100K | BERT-Base | `a100` | ~8 hours |
| Custom 1M | GPT-2 | `4xa100` | ~48 hours |

### Fine-tuning Estimates

| Base Model | Method | Dataset Size | Instance | Time Estimate |
|------------|--------|--------------|----------|---------------|
| Llama-2-7B | LoRA | 1K samples | `a100` | ~1 hour |
| Llama-2-7B | LoRA | 10K samples | `a100` | ~3 hours |
| Llama-2-13B | LoRA | 10K samples | `a100` | ~5 hours |
| Llama-2-70B | LoRA | 1K samples | `4xa100` | ~2 hours |

## Budget Management

### Setting Spending Limits

```python
# Per-task limits
config = TaskConfig(
    max_price_per_hour=20.00,    # Won't bid above this
    max_total_cost=500.00,        # Stop when reached
    max_run_time_hours=48         # Time limit
)

# Check spending
flow spending --current-month
flow spending --by-project
```

### Cost Alerts

```bash
# Set up cost alerts
flow alerts create \
    --threshold 100.00 \
    --period daily \
    --email your@email.com

flow alerts create \
    --threshold 1000.00 \
    --period weekly \
    --slack webhook-url
```

## Monitoring Costs

### Real-time Cost Tracking

```python
# Monitor task costs
task = flow.run(config)
print(f"Current cost: ${task.total_cost}")
print(f"Hourly rate: ${task.cost_per_hour}")

# Historical analysis
costs = flow.get_costs(
    start_date="2024-01-01",
    end_date="2024-01-31",
    group_by="instance_type"
)
```

### Cost Dashboard

```python
# Create cost tracking dashboard
import flow
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Get last 30 days of costs
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

daily_costs = flow.get_costs(
    start_date=start_date,
    end_date=end_date,
    group_by="day"
)

# Plot daily spend
plt.figure(figsize=(12, 6))
plt.plot(daily_costs.dates, daily_costs.amounts)
plt.title("GPU Spend - Last 30 Days")
plt.xlabel("Date")
plt.ylabel("Cost ($)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

## Best Practices

1. **Always set budget limits** - Use max_total_cost
2. **Start with single GPU** - Scale up only if needed
3. **Monitor spot prices** - Bid competitively but not excessively
4. **Use checkpointing** - Resume from interruptions
5. **Optimize before scaling** - Better code saves more than better hardware
6. **Batch operations** - Combine multiple small jobs
7. **Clean up resources** - Stop tasks when done

## Common Cost Patterns

1. **Development/Testing**: Use single `a100` with conservative bids
2. **Production Inference**: Balance between latency needs and cost
3. **Training Runs**: Use checkpointing with spot instances
4. **Batch Processing**: Optimize for throughput over latency

## Tips for Cost Control

1. **Profile First**: Understand resource usage before scaling
   ```python
   # Run profiling
   config = TaskConfig(
       command="python profile_model.py",
       instance_type="a100",
       max_run_time_hours=1
   )
   ```

2. **Use Spot Effectively**: Lower bids for non-urgent work
3. **Implement Checkpointing**: Save progress frequently
4. **Monitor Utilization**: Ensure GPUs are fully utilized
5. **Batch Small Jobs**: Reduce overhead costs

## Next Steps

- Use `flow instances` for current pricing
- Try `flow estimate "python train.py"` for cost predictions
- See [Advanced Optimization Guide](../../guides/cost-optimization.md) for more strategies