# Basic Terraform configuration for Flow GPU tasks

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    flow = {
      source  = "flow-ai/flow"
      version = "~> 1.0"
    }
  }
}

# Configure the Flow provider
provider "flow" {
  # API key can be set via FLOW_API_KEY env var
}

# Simple vLLM inference server
resource "flow_task" "inference_server" {
  name    = "vllm-inference-basic"
  command = <<-EOT
    pip install vllm
    vllm serve meta-llama/Llama-2-7b-chat-hf \
      --host 0.0.0.0 \
      --port 8000 \
      --max-model-len 4096
  EOT
  
  instance_type = "l40s"
  
  # Cost controls
  max_run_time_hours = 24
  max_price_per_hour = 1.50
  
  # Use spot instances for cost savings
  spot_instance = true
  
  # Expose the service
  ports = [8000]
  
  # Basic tags
  tags = {
    purpose = "quickstart"
    type    = "inference"
  }
}

# Outputs
output "task_id" {
  value       = flow_task.inference_server.id
  description = "The ID of the Flow task"
}

output "endpoint" {
  value       = flow_task.inference_server.endpoints["8000"]
  description = "The inference server endpoint"
}

output "estimated_cost" {
  value       = flow_task.inference_server.estimated_cost_per_hour
  description = "Estimated hourly cost in USD"
}