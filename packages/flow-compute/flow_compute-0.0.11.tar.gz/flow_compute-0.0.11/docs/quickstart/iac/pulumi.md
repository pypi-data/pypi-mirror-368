# Pulumi Flow Provider Quickstart

Infrastructure as code for GPU workloads using Pulumi with TypeScript, Python, or Go.

## Prerequisites
- Pulumi CLI installed
- Flow API key
- Node.js (for TypeScript) or Python 3.8+

## 1. Project Setup (2 minutes)

### TypeScript Setup

```bash
# Create new project
pulumi new typescript --name flow-gpu-infra

# Install Flow provider
npm install @pulumi/flow

# Set Flow API key
pulumi config set flow:apiKey your-api-key --secret
```

### Python Setup

```bash
# Create new project
pulumi new python --name flow-gpu-infra

# Install Flow provider
pip install pulumi-flow

# Set Flow API key
pulumi config set flow:apiKey your-api-key --secret
```

## 2. Basic GPU Task (TypeScript)

### Simple Inference Server

```typescript
// index.ts
import * as flow from "@pulumi/flow";
import * as pulumi from "@pulumi/pulumi";

// Create vLLM inference server
const inferenceServer = new flow.Task("vllm-server", {
    name: "llama-inference",
    command: `
        pip install vllm
        vllm serve meta-llama/Llama-2-7b-chat-hf \
            --host 0.0.0.0 \
            --port 8000 \
            --max-model-len 4096
    `,
    instanceType: "l40s",  // 48GB VRAM
    
    // Resource limits
    maxRunTimeHours: 24,
    maxPricePerHour: 1.50,
    
    // Enable spot instances
    spotInstance: true,
    maxInterruptions: 3,
    
    // Networking
    ports: [8000],
    
    // Environment
    environment: {
        HF_TOKEN: process.env.HF_TOKEN || "",
        CUDA_VISIBLE_DEVICES: "0",
    },
    
    // Tags
    tags: {
        team: "ml-platform",
        workload: "inference",
    },
});

// Export endpoint
export const endpoint = inferenceServer.endpoints.apply(
    endpoints => endpoints["8000"]
);

// Export cost estimate
export const hourlyCost = inferenceServer.estimatedCostPerHour;
```

## 3. Production Patterns (Python)

### Auto-scaling Task Group

```python
# __main__.py
import pulumi
import pulumi_flow as flow

# Configuration
config = pulumi.Config()
model_name = config.get("modelName") or "meta-llama/Llama-2-7b-chat-hf"
min_instances = config.get_int("minInstances") or 2
max_instances = config.get_int("maxInstances") or 10

# Create auto-scaling task group
inference_fleet = flow.TaskGroup("inference-fleet",
    name="llama-inference-fleet",
    
    # Task template
    task_template=flow.TaskTemplateArgs(
        command=f"""
            pip install vllm
            vllm serve {model_name} \
                --host 0.0.0.0 \
                --port 8000 \
                --tensor-parallel-size 1
        """,
        instance_type="l40s",
        spot_instance=True,
        ports=[8000],
        environment={
            "MODEL_NAME": model_name,
            "MAX_BATCH_SIZE": "32",
        }
    ),
    
    # Scaling configuration
    scaling=flow.ScalingConfigArgs(
        min_instances=min_instances,
        max_instances=max_instances,
        target_metric="pending_requests",
        target_value=100,
        scale_up_cooldown=60,
        scale_down_cooldown=300,
    ),
    
    # Load balancer
    load_balancer=flow.LoadBalancerConfigArgs(
        type="application",
        health_check_path="/health",
        health_check_interval=30,
    ),
)

# Export load balancer endpoint
pulumi.export("lb_endpoint", inference_fleet.load_balancer_endpoint)
pulumi.export("active_instances", inference_fleet.active_instance_count)
```

## 4. Complex Workflows (TypeScript)

### Training Pipeline with Checkpoints

```typescript
// training-pipeline.ts
import * as flow from "@pulumi/flow";
import * as pulumi from "@pulumi/pulumi";

// Create persistent volume for checkpoints
const checkpointVolume = new flow.Volume("training-checkpoints", {
    name: "model-checkpoints",
    size: 500, // GB
    type: "ssd",
});

// Training job with automatic recovery
const trainingJob = new flow.Task("distributed-training", {
    name: "bert-training",
    command: pulumi.interpolate`
        # Install dependencies
        pip install torch transformers accelerate
        
        # Resume from checkpoint if exists
        CHECKPOINT_DIR="/checkpoints"
        RESUME_FLAG=""
        if [ -d "$CHECKPOINT_DIR/latest" ]; then
            echo "Resuming from checkpoint..."
            RESUME_FLAG="--resume_from_checkpoint $CHECKPOINT_DIR/latest"
        fi
        
        # Launch distributed training
        accelerate launch \
            --num_processes 4 \
            --num_machines 1 \
            --mixed_precision fp16 \
            train.py \
                --model_name bert-large-uncased \
                --dataset_name squad \
                --output_dir /checkpoints \
                --save_steps 500 \
                --eval_steps 100 \
                $RESUME_FLAG
    `,
    
    instanceType: "4xa100_80gb",
    
    // Mount checkpoint volume
    volumes: [{
        source: checkpointVolume.id,
        mountPath: "/checkpoints",
    }],
    
    // Long-running configuration
    maxRunTimeHours: 72,
    maxTotalCost: 2000,
    
    // Enable automatic retry on spot interruption
    retryPolicy: {
        maxAttempts: 3,
        backoffSeconds: 300,
        retryOnSpotInterruption: true,
    },
    
    // Monitoring
    monitoring: {
        logGroup: "/flow/training/bert",
        metrics: ["gpu_utilization", "memory_usage", "loss"],
    },
});

// Create notification on completion
const notification = new flow.Notification("training-complete", {
    taskId: trainingJob.id,
    events: ["completed", "failed"],
    channels: [{
        type: "email",
        target: "ml-team@company.com",
    }, {
        type: "slack",
        target: process.env.SLACK_WEBHOOK!,
    }],
});
```

## 5. Component Resources

### Reusable ML Task Component

```typescript
// components/MLTask.ts
import * as flow from "@pulumi/flow";
import * as pulumi from "@pulumi/pulumi";

export interface MLTaskArgs {
    workloadType: "inference" | "training" | "finetuning";
    modelSize: "small" | "medium" | "large";
    useSpot?: boolean;
    maxBudget?: number;
}

export class MLTask extends pulumi.ComponentResource {
    public readonly task: flow.Task;
    public readonly endpoint?: pulumi.Output<string>;
    public readonly estimatedCost: pulumi.Output<number>;
    
    constructor(name: string, args: MLTaskArgs, opts?: pulumi.ComponentResourceOptions) {
        super("custom:flow:MLTask", name, {}, opts);
        
        // Instance selection logic
        const instanceMap = {
            inference: {
                small: "l40s",
                medium: "a100_40gb",
                large: "4xa100_40gb",
            },
            training: {
                small: "a100_40gb",
                medium: "4xa100_40gb",
                large: "8xa100_80gb",
            },
            finetuning: {
                small: "a100_40gb",
                medium: "a100_80gb",
                large: "4xa100_80gb",
            },
        };
        
        const instanceType = instanceMap[args.workloadType][args.modelSize];
        
        // Create task with standard configuration
        this.task = new flow.Task(`${name}-task`, {
            name: name,
            instanceType: instanceType,
            spotInstance: args.useSpot ?? true,
            
            // Standard monitoring
            monitoring: {
                logGroup: `/flow/${args.workloadType}/${name}`,
                metrics: ["gpu_utilization", "memory_usage"],
            },
            
            // Cost controls
            maxTotalCost: args.maxBudget,
            
            tags: {
                workload_type: args.workloadType,
                model_size: args.modelSize,
                component: "MLTask",
            },
        }, { parent: this });
        
        this.endpoint = this.task.endpoints.apply(e => e["8000"]);
        this.estimatedCost = this.task.estimatedCostPerHour;
        
        this.registerOutputs({
            task: this.task,
            endpoint: this.endpoint,
            estimatedCost: this.estimatedCost,
        });
    }
}

// Usage
const inferenceTask = new MLTask("llama-inference", {
    workloadType: "inference",
    modelSize: "medium",
    useSpot: true,
    maxBudget: 500,
});
```

## 6. Dynamic Resource Creation

### Environment-based Deployment

```python
# __main__.py
import pulumi
import pulumi_flow as flow
from typing import Dict, List

# Get environment
env = pulumi.get_stack()
config = pulumi.Config()

# Environment-specific configuration
env_config = {
    "dev": {
        "instance_types": ["l40s"],
        "use_spot": True,
        "max_instances": 2,
    },
    "staging": {
        "instance_types": ["a100_40gb"],
        "use_spot": True,
        "max_instances": 5,
    },
    "prod": {
        "instance_types": ["a100_80gb", "4xa100_80gb"],
        "use_spot": False,
        "max_instances": 20,
    },
}

current_config = env_config.get(env, env_config["dev"])

# Create tasks dynamically based on environment
tasks = []
for i, instance_type in enumerate(current_config["instance_types"]):
    task = flow.Task(f"ml-task-{i}",
        name=f"{env}-ml-task-{i}",
        instance_type=instance_type,
        spot_instance=current_config["use_spot"],
        command="""
            python -c "
            import torch
            print(f'Running on {torch.cuda.get_device_name(0)}')
            # Your ML workload here
            "
        """,
        max_run_time_hours=24,
        tags={
            "environment": env,
            "instance_type": instance_type,
        }
    )
    tasks.append(task)

# Create load balancer for production
if env == "prod":
    lb = flow.LoadBalancer("prod-lb",
        name="production-load-balancer",
        backends=[{
            "task_id": task.id,
            "weight": 100 // len(tasks),
        } for task in tasks],
        health_check={
            "path": "/health",
            "interval": 30,
            "timeout": 10,
        }
    )
    pulumi.export("load_balancer_endpoint", lb.endpoint)
```

## 7. State Management & Secrets

### Using Pulumi Secrets

```typescript
// config.ts
import * as pulumi from "@pulumi/pulumi";

const config = new pulumi.Config();

// Encrypted secrets
export const flowApiKey = config.requireSecret("flowApiKey");
export const hfToken = config.requireSecret("huggingfaceToken");
export const wandbKey = config.requireSecret("wandbApiKey");

// Regular config
export const modelName = config.get("modelName") || "meta-llama/Llama-2-7b";
export const maxBudget = config.getNumber("maxBudget") || 1000;
```

### Using Stack References

```typescript
// Cross-stack references
const networkStack = new pulumi.StackReference("organization/network/prod");
const vpcId = networkStack.getOutput("vpcId");
const subnetIds = networkStack.getOutput("privateSubnetIds");

const gpuTask = new flow.Task("gpu-task", {
    // ... other config ...
    networkConfig: {
        vpcId: vpcId,
        subnetIds: subnetIds,
        securityGroupIds: [networkStack.getOutput("mlSecurityGroupId")],
    },
});
```

## 8. Testing and Validation

### Policy as Code

```python
# policy.py
from pulumi_policy import (
    EnforcementLevel,
    PolicyPack,
    ResourceValidationPolicy,
)

def max_cost_validator(args, report):
    """Ensure no task exceeds $50/hour"""
    if args.resource_type == "flow:Task":
        max_price = args.props.get("maxPricePerHour", float('inf'))
        if max_price > 50:
            report(
                EnforcementLevel.MANDATORY,
                f"Task hourly cost ${max_price} exceeds limit of $50"
            )

def spot_instance_validator(args, report):
    """Require spot instances for dev environment"""
    if args.resource_type == "flow:Task":
        tags = args.props.get("tags", {})
        if tags.get("environment") == "dev":
            if not args.props.get("spotInstance", False):
                report(
                    EnforcementLevel.MANDATORY,
                    "Development tasks must use spot instances"
                )

PolicyPack(
    name="flow-cost-policies",
    enforcement_level=EnforcementLevel.MANDATORY,
    policies=[
        ResourceValidationPolicy(
            name="max-cost-limit",
            description="Limit maximum hourly cost",
            validate=max_cost_validator,
        ),
        ResourceValidationPolicy(
            name="dev-spot-instances",
            description="Require spot for dev",
            validate=spot_instance_validator,
        ),
    ],
)
```

## 9. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy Flow Infrastructure

on:
  push:
    branches: [main]
  pull_request:

env:
  PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
  FLOW_API_KEY: ${{ secrets.FLOW_API_KEY }}

jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18
          
      - name: Install dependencies
        run: npm ci
        
      - name: Run tests
        run: npm test
        
      - name: Pulumi Preview
        uses: pulumi/actions@v4
        with:
          command: preview
          stack-name: dev
          comment-on-pr: true
          
  deploy:
    needs: preview
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        environment: [dev, staging, prod]
        
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to ${{ matrix.environment }}
        uses: pulumi/actions@v4
        with:
          command: up
          stack-name: ${{ matrix.environment }}
          upsert: true
```

## 10. Advanced Patterns

### Blue-Green Deployment

```typescript
// blue-green.ts
import * as flow from "@pulumi/flow";
import * as pulumi from "@pulumi/pulumi";

interface BlueGreenDeploymentArgs {
    activeColor: "blue" | "green";
    modelVersions: {
        blue: string;
        green: string;
    };
}

export class BlueGreenDeployment extends pulumi.ComponentResource {
    public readonly endpoint: pulumi.Output<string>;
    
    constructor(
        name: string, 
        args: BlueGreenDeploymentArgs, 
        opts?: pulumi.ComponentResourceOptions
    ) {
        super("custom:flow:BlueGreenDeployment", name, {}, opts);
        
        // Create deployments for both colors
        const deployments = {
            blue: this.createDeployment("blue", args.modelVersions.blue),
            green: this.createDeployment("green", args.modelVersions.green),
        };
        
        // Configure load balancer with weighted routing
        const loadBalancer = new flow.LoadBalancer(`${name}-lb`, {
            name: `${name}-lb`,
            backends: [
                {
                    name: "blue",
                    taskIds: deployments.blue.taskIds,
                    weight: args.activeColor === "blue" ? 100 : 0,
                },
                {
                    name: "green",
                    taskIds: deployments.green.taskIds,
                    weight: args.activeColor === "green" ? 100 : 0,
                },
            ],
            healthCheck: {
                path: "/health",
                interval: 30,
                healthyThreshold: 2,
                unhealthyThreshold: 3,
            },
        }, { parent: this });
        
        this.endpoint = loadBalancer.endpoint;
        
        this.registerOutputs({
            endpoint: this.endpoint,
        });
    }
    
    private createDeployment(color: string, modelVersion: string) {
        return new flow.TaskGroup(`deployment-${color}`, {
            name: `inference-${color}`,
            taskTemplate: {
                command: `vllm serve ${modelVersion} --port 8000`,
                instanceType: "l40s",
                spotInstance: true,
                ports: [8000],
            },
            scaling: {
                minInstances: color === "blue" ? 2 : 0,
                maxInstances: 10,
            },
        }, { parent: this });
    }
}

// Usage with automatic switchover
const deployment = new BlueGreenDeployment("model-serving", {
    activeColor: "blue", // Change to "green" for switchover
    modelVersions: {
        blue: "meta-llama/Llama-2-7b-v1",
        green: "meta-llama/Llama-2-7b-v2",
    },
});

export const endpoint = deployment.endpoint;
```

### Cost Tracking Dashboard

```python
# cost_dashboard.py
import pulumi
import pulumi_flow as flow
from datetime import datetime, timedelta

# Query historical costs
cost_analyzer = flow.CostAnalyzer("ml-costs",
    time_range={
        "start": (datetime.now() - timedelta(days=30)).isoformat(),
        "end": datetime.now().isoformat(),
    },
    group_by=["tag:team", "tag:project", "instance_type"],
    filters={
        "tags": {
            "department": "ml",
        },
    },
)

# Create budget alerts
budget = flow.Budget("ml-budget",
    name="ml-team-monthly",
    amount=10000.0,
    period="monthly",
    alerts=[
        {
            "threshold_percent": 50,
            "channels": [{
                "type": "email",
                "targets": ["ml-team@company.com"],
            }],
        },
        {
            "threshold_percent": 80,
            "channels": [{
                "type": "slack",
                "targets": [pulumi.Config().require_secret("slack_webhook")],
            }],
        },
        {
            "threshold_percent": 90,
            "channels": [{
                "type": "pagerduty",
                "targets": [pulumi.Config().require_secret("pagerduty_key")],
            }],
            "actions": ["pause_non_critical_tasks"],
        },
    ],
)

# Export cost insights
pulumi.export("current_month_spend", cost_analyzer.current_month_total)
pulumi.export("cost_by_team", cost_analyzer.costs_by_group)
pulumi.export("top_expensive_tasks", cost_analyzer.top_expensive_tasks)
```

## Troubleshooting

### Common Issues

```typescript
// Error handling example
try {
    const task = new flow.Task("gpu-task", {
        // ... configuration ...
    });
} catch (error) {
    if (error.message.includes("ResourceUnavailable")) {
        // Try alternative instance type
        const task = new flow.Task("gpu-task-alt", {
            instanceType: "a100_40gb", // fallback option
            // ... rest of configuration ...
        });
    }
}
```

### Debugging Tips

```bash
# Enable verbose logging
export PULUMI_DEBUG=true

# Test configuration locally
pulumi preview --show-config

# Validate without applying
pulumi up --dry-run

# Check state
pulumi stack export | jq '.deployment.resources'
```

## Next Steps

- [Terraform Alternative](./terraform.md) - HCL-based infrastructure
- [Advanced Pulumi Patterns](../../guides/pulumi-advanced.md)
- [Multi-Cloud Deployment](../../guides/multi-cloud.md)
- [Cost Optimization](../../guides/cost-optimization.md)