# Production environment configuration

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    flow = {
      source  = "flow-ai/flow"
      version = "~> 1.0"
    }
  }
  
  # Remote state configuration
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "flow/prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

# Variables
variable "flow_api_key" {
  description = "Flow API key"
  type        = string
  sensitive   = true
}

variable "hf_token" {
  description = "HuggingFace token"
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

# Provider configuration
provider "flow" {
  api_key = var.flow_api_key
}

# Local variables
locals {
  common_tags = {
    environment = var.environment
    team        = "ml-platform"
    cost_center = "engineering"
  }
}

# Production inference servers using module
module "llama_inference" {
  source = "../../modules/flow-task"
  
  name          = "${var.environment}-llama-inference"
  workload_type = "inference"
  size          = "medium"
  
  command = <<-EOT
    pip install vllm
    vllm serve meta-llama/Llama-2-13b-chat-hf \
      --host 0.0.0.0 \
      --port 8000 \
      --tensor-parallel-size 1 \
      --max-model-len 4096
  EOT
  
  use_spot        = false  # Production uses on-demand
  max_hourly_cost = 5.00
  
  environment = {
    HF_TOKEN = var.hf_token
    LOG_LEVEL = "INFO"
  }
  
  ports = [8000]
  tags  = local.common_tags
}

module "mistral_inference" {
  source = "../../modules/flow-task"
  
  name          = "${var.environment}-mistral-inference"
  workload_type = "inference"
  size          = "small"
  
  command = <<-EOT
    pip install vllm
    vllm serve mistralai/Mistral-7B-Instruct-v0.2 \
      --host 0.0.0.0 \
      --port 8000 \
      --max-model-len 8192
  EOT
  
  use_spot        = false
  max_hourly_cost = 2.00
  
  environment = {
    HF_TOKEN = var.hf_token
  }
  
  ports = [8000]
  tags  = local.common_tags
}

# Auto-scaling group for high availability
resource "flow_task_group" "inference_fleet" {
  name = "${var.environment}-inference-fleet"
  
  task_template = {
    command       = module.llama_inference.command
    instance_type = module.llama_inference.instance_type
    environment   = module.llama_inference.environment
    ports         = [8000]
  }
  
  scaling = {
    min_instances = 3
    max_instances = 10
    
    target_metric = "request_latency_p95"
    target_value  = 500  # milliseconds
    
    scale_up_cooldown   = 60
    scale_down_cooldown = 300
  }
  
  # Production load balancer
  load_balancer = {
    type = "application"
    
    health_check = {
      path                = "/health"
      interval            = 30
      timeout             = 10
      healthy_threshold   = 2
      unhealthy_threshold = 3
    }
    
    ssl_certificate_arn = "arn:aws:acm:us-east-1:123456789:certificate/abc"
  }
  
  tags = local.common_tags
}

# Budget controls
resource "flow_budget" "prod_budget" {
  name = "${var.environment}-ml-budget"
  
  amount = 50000.00  # $50k/month
  period = "monthly"
  
  alerts = [
    {
      threshold_percent = 50
      recipients        = ["ml-team@company.com"]
    },
    {
      threshold_percent = 80
      recipients        = ["ml-team@company.com", "finance@company.com"]
    },
    {
      threshold_percent = 90
      recipients        = ["ml-team@company.com", "cto@company.com"]
      actions           = ["notify_on_call"]
    }
  ]
  
  tag_filter = {
    environment = var.environment
  }
}

# Monitoring dashboard
resource "flow_dashboard" "prod_metrics" {
  name = "${var.environment}-gpu-metrics"
  
  panels = [
    {
      title = "GPU Utilization"
      type  = "timeseries"
      query = "avg(gpu_utilization) by (task_name)"
    },
    {
      title = "Request Latency"
      type  = "timeseries"
      query = "p95(request_latency) by (endpoint)"
    },
    {
      title = "Daily Cost"
      type  = "stat"
      query = "sum(cost_per_hour) * 24"
    },
    {
      title = "Active Tasks"
      type  = "gauge"
      query = "count(task_status{status='running'})"
    }
  ]
  
  refresh_interval = 60  # seconds
}

# Outputs
output "llama_endpoint" {
  description = "Llama model endpoint"
  value       = module.llama_inference.endpoints["8000"]
}

output "mistral_endpoint" {
  description = "Mistral model endpoint"
  value       = module.mistral_inference.endpoints["8000"]
}

output "load_balancer_endpoint" {
  description = "Load balancer endpoint"
  value       = flow_task_group.inference_fleet.load_balancer_endpoint
}

output "monthly_cost_estimate" {
  description = "Estimated monthly cost"
  value       = (module.llama_inference.estimated_hourly_cost + module.mistral_inference.estimated_hourly_cost) * 24 * 30
}