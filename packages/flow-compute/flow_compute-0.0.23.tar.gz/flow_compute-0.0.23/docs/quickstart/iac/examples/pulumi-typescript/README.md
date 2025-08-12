# Pulumi TypeScript Example

Deploy GPU infrastructure using Pulumi with TypeScript.

## Prerequisites

- Node.js 18+
- Pulumi CLI
- Flow API key

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set your API key:
```bash
pulumi config set flow:apiKey your-api-key --secret
```

3. Configure options (optional):
```bash
pulumi config set modelName "mistralai/Mistral-7B-v0.1"
pulumi config set instanceType "a100_40gb"
pulumi config set useSpot false
```

## Deploy

1. Create a new stack:
```bash
pulumi stack init dev
```

2. Preview changes:
```bash
pulumi preview
```

3. Deploy:
```bash
pulumi up
```

4. Get outputs:
```bash
pulumi stack output endpoint
pulumi stack output costSavings
```

## Clean Up

```bash
pulumi destroy
pulumi stack rm dev
```

## Stack Management

```bash
# List stacks
pulumi stack ls

# Switch stacks
pulumi stack select prod

# Export state
pulumi stack export > backup.json
```

## Estimated Costs

Default configuration with spot instances:
- ~$0.36/hour (70% savings)

## Next Steps

- Add auto-scaling
- Create reusable components
- Set up CI/CD with GitHub Actions