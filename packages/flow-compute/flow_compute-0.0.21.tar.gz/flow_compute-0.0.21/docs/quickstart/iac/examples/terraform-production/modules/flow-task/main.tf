# Reusable Flow task module for production use

variable "name" {
  description = "Name of the Flow task"
  type        = string
}

variable "command" {
  description = "Command to execute"
  type        = string
}

variable "workload_type" {
  description = "Type of workload: inference, training, or finetuning"
  type        = string
  default     = "inference"
  
  validation {
    condition     = contains(["inference", "training", "finetuning"], var.workload_type)
    error_message = "Workload type must be inference, training, or finetuning"
  }
}

variable "size" {
  description = "Size of the workload: small, medium, or large"
  type        = string
  default     = "small"
  
  validation {
    condition     = contains(["small", "medium", "large"], var.size)
    error_message = "Size must be small, medium, or large"
  }
}

variable "use_spot" {
  description = "Use spot instances"
  type        = bool
  default     = true
}

variable "max_hourly_cost" {
  description = "Maximum cost per hour in USD"
  type        = number
  default     = 10.0
}

variable "max_total_cost" {
  description = "Maximum total cost in USD"
  type        = number
  default     = null
}

variable "environment" {
  description = "Environment variables"
  type        = map(string)
  default     = {}
}

variable "volumes" {
  description = "Volume mounts"
  type = list(object({
    source     = string
    mount_path = string
    read_only  = bool
  }))
  default = []
}

variable "ports" {
  description = "Ports to expose"
  type        = list(number)
  default     = []
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

locals {
  # Instance selection based on workload type and size
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
  
  instance_type = local.instance_map[var.workload_type][var.size]
  
  # Default tags
  default_tags = {
    workload_type = var.workload_type
    size          = var.size
    module        = "flow-task"
    managed_by    = "terraform"
  }
}

# Main Flow task resource
resource "flow_task" "task" {
  name          = var.name
  command       = var.command
  instance_type = local.instance_type
  
  # Spot configuration
  spot_instance     = var.use_spot
  max_interruptions = var.use_spot ? 3 : 0
  
  # Cost controls
  max_price_per_hour = var.max_hourly_cost
  max_total_cost     = var.max_total_cost
  
  # Runtime limits based on workload type
  max_run_time_hours = var.workload_type == "inference" ? 720 : 72 # 30 days for inference, 3 days for training
  
  # Environment and volumes
  environment = var.environment
  dynamic "volumes" {
    for_each = var.volumes
    content {
      source     = volumes.value.source
      mount_path = volumes.value.mount_path
      read_only  = volumes.value.read_only
    }
  }
  
  # Networking
  ports = var.ports
  
  # Monitoring
  monitoring = {
    log_group = "/flow/${var.workload_type}/${var.name}"
    metrics   = ["gpu_utilization", "memory_usage", "cost"]
  }
  
  # Retry policy for training/finetuning
  dynamic "retry_policy" {
    for_each = var.workload_type != "inference" ? [1] : []
    content {
      max_attempts               = 3
      backoff_seconds           = 300
      retry_on_failure          = true
      retry_on_spot_interruption = var.use_spot
    }
  }
  
  # Tags
  tags = merge(local.default_tags, var.tags)
}

# Outputs
output "task_id" {
  description = "The ID of the Flow task"
  value       = flow_task.task.id
}

output "endpoints" {
  description = "Task endpoints"
  value       = flow_task.task.endpoints
}

output "status" {
  description = "Task status"
  value       = flow_task.task.status
}

output "instance_type" {
  description = "Selected instance type"
  value       = local.instance_type
}

output "estimated_hourly_cost" {
  description = "Estimated hourly cost in USD"
  value       = flow_task.task.estimated_cost_per_hour
}