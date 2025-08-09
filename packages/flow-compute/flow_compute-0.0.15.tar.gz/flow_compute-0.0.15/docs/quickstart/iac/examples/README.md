# Infrastructure as Code Examples

Production-ready examples for managing GPU infrastructure with Flow.

## Examples

### 1. Basic Examples
- **terraform-basic/** - Simple Terraform configuration for getting started
- **pulumi-typescript/** - Basic Pulumi setup with TypeScript

### 2. Production Examples
- **terraform-production/** - Full production setup with modules, environments, and best practices
- **pulumi-production/** - Production Pulumi configuration with components and policies

## Quick Start

### Terraform
```bash
cd terraform-basic
terraform init
terraform apply
```

### Pulumi
```bash
cd pulumi-typescript
npm install
pulumi up
```

## Key Concepts

### Cost Management
All examples include:
- Budget limits
- Spot instance usage where appropriate
- Cost estimation outputs

### Monitoring
Production examples include:
- Logging configuration
- Metrics collection
- Alerting setup

### High Availability
Production configurations feature:
- Auto-scaling groups
- Load balancing
- Health checks
- Multi-region support

## Best Practices

1. **State Management**
   - Use remote state (S3, Pulumi Service)
   - Enable state locking
   - Regular backups

2. **Security**
   - Store secrets in secure backends
   - Use IAM roles where possible
   - Encrypt sensitive data

3. **Cost Optimization**
   - Use spot instances for non-critical workloads
   - Set budget alerts
   - Regular cost reviews

4. **CI/CD Integration**
   - Automated testing
   - Plan/preview on PRs
   - Apply on merge to main

## Directory Structure

```
examples/
├── terraform-basic/          # Simple getting started
│   ├── main.tf
│   └── README.md
├── terraform-production/     # Production setup
│   ├── modules/             # Reusable modules
│   ├── environments/        # Per-env configs
│   └── README.md
├── pulumi-typescript/       # TypeScript example
│   ├── index.ts
│   ├── package.json
│   └── README.md
└── pulumi-production/       # Production Pulumi
    ├── components/          # Custom components
    ├── policies/           # Policy as code
    └── README.md
```

## Common Patterns

### Multi-Environment
```bash
# Terraform
terraform workspace select prod
terraform apply

# Pulumi
pulumi stack select prod
pulumi up
```

### Blue-Green Deployment
See production examples for implementation details.

### Cost Tracking
All examples output estimated costs:
```bash
# Terraform
terraform output monthly_cost_estimate

# Pulumi
pulumi stack output estimatedMonthlyCost
```

## Troubleshooting

### Instance Availability
If instances aren't available, examples include fallback logic:
- Automatic instance type selection
- Region failover
- Spot to on-demand fallback

### State Issues
```bash
# Terraform
terraform refresh
terraform state list

# Pulumi
pulumi refresh
pulumi stack export
```

## Next Steps

1. Start with basic examples
2. Customize for your use case
3. Graduate to production patterns
4. Implement CI/CD pipeline

## Support

- [Flow Documentation](https://docs.flow.ai)
- [Terraform Docs](https://registry.terraform.io/providers/flow-ai/flow)
- [Pulumi Docs](https://www.pulumi.com/registry/packages/flow)