# Terraform Flow Provider Quickstart

Manage GPU infrastructure declaratively using Terraform with the Flow provider.

## Prerequisites
- Terraform >= 1.0
- Flow API key
- Basic Terraform knowledge

## 1. Provider Setup (2 minutes)

### Install Provider

```hcl
# versions.tf
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    flow = {
      source  = "flow-ai/flow"
      version = "~> 1.0"
    }
  }
}

# provider.tf
provider "flow" {
  api_key = var.flow_api_key
  # Or use environment variable: FLOW_API_KEY
}

# variables.tf
variable "flow_api_key" {
  description = "Flow API key"
  type        = string
  sensitive   = true
}
```

### Initialize Terraform

```bash
# Set API key
export TF_VAR_flow_api_key="your-api-key"

# Initialize provider
terraform init

# Validate configuration
terraform validate
```

## 2. GPU Task Resources (3 minutes)

### Basic GPU Task

```hcl
# main.tf
resource "flow_task" "inference" {
  name        = "vllm-inference-server"
  command     = file("scripts/start_vllm.sh")
  
  instance_type = "l40s"  # 48GB VRAM
  
  # Resource limits
  max_run_time_hours = 24
  max_price_per_hour = 1.50
  
  # Enable spot instances for 70% savings
  spot_instance = true
  max_interruptions = 3
  
  # Networking
  ports = [8000]
  
  # Environment variables
  environment = {
    MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"
    HF_TOKEN   = var.huggingface_token
  }
  
  # Tags for organization
  tags = {
    team        = "ml-platform"
    environment = "production"
    workload    = "inference"
  }
}

# Output the endpoint
output "inference_endpoint" {
  value = flow_task.inference.endpoints["8000"]
  description = "vLLM server endpoint"
}
```

### Multi-GPU Training Task

```hcl
resource "flow_task" "training" {
  name        = "distributed-training"
  command     = file("scripts/train_model.sh")
  
  instance_type = "4xa100_80gb"  # 4x A100 80GB
  
  # Volumes for data and checkpoints
  volumes = [
    {
      name       = "training-data"
      source     = "s3://my-bucket/datasets/imagenet"
      mount_path = "/data"
      read_only  = true
    },
    {
      name       = "checkpoints"
      source     = "flow-volume://checkpoint-storage"
      mount_path = "/checkpoints"
      read_only  = false
    }
  ]
  
  # Long-running training
  max_run_time_hours = 72
  max_total_cost     = 2000.00
  
  # Monitoring
  monitoring = {
    log_group = "/flow/training/${var.project_name}"
    metrics   = ["gpu_utilization", "memory_usage", "loss"]
  }
  
  # Retry configuration
  retry_policy = {
    max_attempts      = 3
    backoff_seconds   = 300
    retry_on_failure  = true
    retry_on_spot_interruption = true
  }
}
```

## 3. Production Patterns

### Auto-scaling Inference Fleet

```hcl
# Auto-scaling configuration
resource "flow_task_group" "inference_fleet" {
  name = "llama-inference-fleet"
  
  # Task template
  task_template = {
    command       = file("scripts/vllm_server.sh")
    instance_type = "l40s"
    spot_instance = true
    ports         = [8000]
    
    environment = {
      MODEL_NAME = var.model_name
      MAX_BATCH_SIZE = "32"
    }
  }
  
  # Scaling configuration
  scaling = {
    min_instances = 2
    max_instances = 10
    
    # Scale based on queue depth
    target_metric = "pending_requests"
    target_value  = 100
    
    # Scale up/down rates
    scale_up_cooldown   = 60
    scale_down_cooldown = 300
  }
  
  # Load balancer
  load_balancer = {
    type              = "application"
    health_check_path = "/health"
    health_check_interval = 30
  }
}
```

### Scheduled Fine-tuning Jobs

```hcl
resource "flow_scheduled_task" "nightly_finetune" {
  name = "nightly-model-update"
  
  # Cron schedule (daily at 2 AM)
  schedule = "0 2 * * *"
  
  # Task configuration
  task_config = {
    command       = file("scripts/finetune_pipeline.sh")
    instance_type = "a100_80gb"
    spot_instance = true
    
    max_run_time_hours = 4
    max_price_per_hour = 5.00
    
    volumes = [
      {
        name       = "model-registry"
        source     = "s3://models/production"
        mount_path = "/models"
      }
    ]
    
    # Notification on completion
    notifications = {
      on_success = "sns:arn:aws:sns:us-east-1:123456789:ml-team"
      on_failure = "pagerduty:${var.pagerduty_key}"
    }
  }
  
  # Only run if new data exists
  condition = {
    type = "s3_object_exists"
    path = "s3://training-data/new/*.jsonl"
  }
}
```

## 4. Cost Management

### Budget Controls

```hcl
# Organization-wide budget
resource "flow_budget" "ml_budget" {
  name = "ml-team-monthly"
  
  amount = 10000.00
  period = "monthly"
  
  # Alert thresholds
  alerts = [
    {
      threshold_percent = 50
      recipients = ["ml-team@company.com"]
    },
    {
      threshold_percent = 80
      recipients = ["ml-team@company.com", "finance@company.com"]
    },
    {
      threshold_percent = 90
      recipients = ["ml-team@company.com", "cto@company.com"]
      actions = ["pause_non_critical_tasks"]
    }
  ]
  
  # Spending limits by tag
  tag_limits = {
    environment = {
      development = 2000.00
      staging     = 3000.00
      production  = 5000.00
    }
  }
}

# Per-project budgets
resource "flow_budget" "project_budget" {
  for_each = var.projects
  
  name   = "${each.key}-budget"
  amount = each.value.monthly_budget
  period = "monthly"
  
  # Restrict to project tags
  tag_filter = {
    project = each.key
  }
}
```

### Cost Optimization Rules

```hcl
resource "flow_cost_policy" "spot_preference" {
  name = "prefer-spot-instances"
  
  # Automatically use spot for eligible workloads
  rules = [
    {
      condition = "task.max_interruptions > 0"
      action    = "force_spot_instance"
    },
    {
      condition = "task.tags.environment == 'development'"
      action    = "force_spot_instance"
    }
  ]
}

resource "flow_cost_policy" "instance_optimization" {
  name = "optimize-instance-selection"
  
  rules = [
    {
      # Downgrade instance if underutilized
      condition = "avg(gpu_utilization) < 50 AND runtime > 1h"
      action    = "suggest_smaller_instance"
    },
    {
      # Upgrade if OOM errors
      condition = "error_count('OutOfMemory') > 0"
      action    = "suggest_larger_instance"
    }
  ]
}
```

## 5. State Management

### Remote State with Locking

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "flow/production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

### State Import for Existing Resources

```bash
# Import existing Flow tasks
terraform import flow_task.inference task-abc123

# Import with resource mapping
cat > import.tf << EOF
import {
  to = flow_task.existing_inference
  id = "task-xyz789"
}
EOF

terraform plan -generate-config-out=generated.tf
```

## 6. GitOps Workflow

### GitHub Actions Integration

```yaml
# .github/workflows/deploy.yml
name: Deploy Flow Infrastructure

on:
  push:
    branches: [main]
    paths:
      - 'terraform/**'

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        
      - name: Terraform Init
        run: terraform init
        working-directory: terraform
        
      - name: Terraform Plan
        run: terraform plan -out=plan.tfplan
        working-directory: terraform
        env:
          TF_VAR_flow_api_key: ${{ secrets.FLOW_API_KEY }}
          
      - name: Upload Plan
        uses: actions/upload-artifact@v3
        with:
          name: tfplan
          path: terraform/plan.tfplan
          
  apply:
    needs: plan
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v3
      
      - name: Download Plan
        uses: actions/download-artifact@v3
        with:
          name: tfplan
          path: terraform/
          
      - name: Terraform Apply
        run: terraform apply -auto-approve plan.tfplan
        working-directory: terraform
        env:
          TF_VAR_flow_api_key: ${{ secrets.FLOW_API_KEY }}
```

## 7. Module Development

### Reusable Task Module

```hcl
# modules/flow-task/main.tf
variable "name" {
  description = "Task name"
  type        = string
}

variable "workload_type" {
  description = "Type of workload: inference, training, or finetuning"
  type        = string
  
  validation {
    condition = contains(["inference", "training", "finetuning"], var.workload_type)
    error_message = "Workload type must be inference, training, or finetuning"
  }
}

locals {
  instance_map = {
    inference = {
      small  = "l40s"
      medium = "a100_40gb"
      large  = "4xa100_40gb"
    }
    training = {
      small  = "a100_40gb"
      medium = "4xa100_40gb"
      large  = "8xa100_80gb"
    }
    finetuning = {
      small  = "a100_40gb"
      medium = "a100_80gb"
      large  = "4xa100_80gb"
    }
  }
}

resource "flow_task" "task" {
  name          = var.name
  command       = var.command
  instance_type = local.instance_map[var.workload_type][var.size]
  
  spot_instance = var.use_spot
  
  # Standard monitoring
  monitoring = {
    log_group = "/flow/${var.workload_type}/${var.name}"
    metrics   = ["gpu_utilization", "memory_usage"]
  }
  
  # Cost controls
  max_price_per_hour = var.max_hourly_cost
  max_total_cost     = var.max_total_cost
  
  tags = merge(var.additional_tags, {
    workload_type = var.workload_type
    module        = "flow-task"
  })
}

output "task_id" {
  value = flow_task.task.id
}

output "endpoints" {
  value = flow_task.task.endpoints
}
```

### Using the Module

```hcl
module "inference_server" {
  source = "./modules/flow-task"
  
  name          = "llama-inference"
  workload_type = "inference"
  size          = "medium"
  command       = file("scripts/serve_model.sh")
  
  use_spot        = true
  max_hourly_cost = 5.00
  max_total_cost  = 500.00
  
  additional_tags = {
    team = "ml-platform"
    env  = "prod"
  }
}
```

## 8. Monitoring and Observability

### DataDog Integration

```hcl
resource "flow_integration" "datadog" {
  name = "datadog-monitoring"
  type = "datadog"
  
  config = {
    api_key     = var.datadog_api_key
    app_key     = var.datadog_app_key
    
    # Metric forwarding
    forward_metrics = true
    metric_prefix   = "flow.gpu"
    
    # Log forwarding
    forward_logs = true
    log_tags = {
      service = "flow-compute"
      env     = var.environment
    }
  }
}

# Custom dashboards
resource "datadog_dashboard" "gpu_monitoring" {
  title = "Flow GPU Monitoring"
  
  widget {
    timeseries_definition {
      title = "GPU Utilization by Task"
      
      request {
        q = "avg:flow.gpu.utilization{*} by {task_name}"
      }
    }
  }
  
  widget {
    query_value_definition {
      title = "Total GPU Cost (24h)"
      
      request {
        q = "sum:flow.gpu.cost{*}.as_cost()"
        aggregator = "sum"
      }
    }
  }
}
```

## 9. Disaster Recovery

### Backup Configuration

```hcl
resource "flow_backup_policy" "ml_models" {
  name = "model-checkpoint-backup"
  
  # What to backup
  source_filter = {
    volume_names = ["checkpoints", "model-registry"]
    tag_filter = {
      backup = "required"
    }
  }
  
  # Backup schedule
  schedule = {
    frequency = "daily"
    time      = "03:00"
    retention_days = 30
  }
  
  # Backup destination
  destination = {
    type   = "s3"
    bucket = "ml-backups"
    prefix = "flow-checkpoints/"
  }
}
```

## 10. Advanced Patterns

### Blue-Green Deployments

```hcl
locals {
  active_version = data.terraform_remote_state.versions.outputs.active_version
  next_version   = local.active_version == "blue" ? "green" : "blue"
}

# Deploy new version
resource "flow_task_group" "model_serving" {
  for_each = toset(["blue", "green"])
  
  name = "inference-${each.key}"
  
  task_template = {
    command       = "vllm serve ${var.model_versions[each.key]}"
    instance_type = "l40s"
    ports         = [8000]
  }
  
  scaling = {
    min_instances = each.key == local.next_version ? 2 : 0
    max_instances = 10
  }
}

# Load balancer with weighted routing
resource "flow_load_balancer" "model_lb" {
  name = "model-serving-lb"
  
  backend_groups = [
    {
      name   = "blue"
      weight = local.active_version == "blue" ? 100 : 0
      tasks  = flow_task_group.model_serving["blue"].task_ids
    },
    {
      name   = "green"
      weight = local.active_version == "green" ? 100 : 0
      tasks  = flow_task_group.model_serving["green"].task_ids
    }
  ]
}
```

## Common Issues and Solutions

### Task Creation Failures

```hcl
# Add proper error handling
resource "flow_task" "gpu_task" {
  # ... configuration ...
  
  lifecycle {
    create_before_destroy = true
    
    # Ignore transient fields
    ignore_changes = [
      status,
      actual_instance_type
    ]
  }
  
  # Provisioner for validation
  provisioner "local-exec" {
    command = "flow validate-task ${self.id}"
  }
}
```

### State Drift Detection

```bash
# Check for drift
terraform plan -detailed-exitcode

# Refresh state
terraform refresh

# Force state sync
terraform apply -refresh-only
```

## Cost Estimation

```bash
# Preview costs before applying
terraform plan -out=plan.tfplan
terraform show -json plan.tfplan | jq '.resource_changes[] | 
  select(.type == "flow_task") | 
  {
    name: .address,
    instance: .change.after.instance_type,
    hourly_cost: .change.after.estimated_hourly_cost
  }'
```

## Next Steps

- [Pulumi Alternative](./pulumi.md) - TypeScript/Python infrastructure
- [Advanced Terraform Patterns](../../guides/terraform-advanced.md)
- [Cost Optimization](../../guides/cost-optimization.md)
- [Multi-Region Deployment](../../guides/multi-region.md)