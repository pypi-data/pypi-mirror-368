# Basic Terraform Example

Simple example of deploying a vLLM inference server using Terraform.

## Prerequisites

- Terraform installed
- Flow API key

## Usage

1. Set your API key:
```bash
export FLOW_API_KEY="your-api-key"
```

2. Initialize Terraform:
```bash
terraform init
```

3. Preview the deployment:
```bash
terraform plan
```

4. Deploy:
```bash
terraform apply
```

5. Get the endpoint:
```bash
terraform output endpoint
```

6. Clean up:
```bash
terraform destroy
```

## Estimated Costs

- Spot instance (l40s): ~$0.36/hour
- On-demand (l40s): ~$1.20/hour

## Files

- `main.tf` - Main configuration
- `terraform.tfvars.example` - Example variables file

## Next Steps

- Add auto-scaling
- Configure monitoring
- Set up CI/CD pipeline