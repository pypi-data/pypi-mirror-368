# Quickstart

Get GPU workloads running in under 5 minutes. Choose your preferred interface:

## 🚀 Quick Decision Guide

### I want to...

**Write Python code** → [Python SDK Path](#python-sdk-recommended)  
**Use command line** → [CLI/SLURM Path](#command-line-slurm-compatible)  
**Deploy infrastructure** → [Infrastructure as Code](#infrastructure-as-code)  
**Experiment interactively** → [Jupyter Notebooks](#jupyter-notebooks)

## Interface Options

### Python SDK (Recommended)
**Best for:** ML engineers, researchers, production deployments

Direct API control with type safety and comprehensive error handling.

```python
import flow
from flow import TaskConfig

# GPU inference in 3 lines
config = TaskConfig(command="python model.py", instance_type="a100")
task = flow.Flow().run(config)
print(task.logs())
```

#### SDK Quickstarts:
- [**Inference**](sdk/inference.md) - Deploy models with vLLM, TGI, or custom servers
- [**Training**](sdk/training.md) - Distributed training with PyTorch/TensorFlow
- [**Fine-tuning**](sdk/fine-tuning.md) - LoRA/QLoRA for LLMs

**Key Features:**
- ✅ Full API access
- ✅ Type hints & IDE support
- ✅ Programmatic control
- ✅ Error handling

---

### Command Line (SLURM Compatible)
**Best for:** HPC users, batch processing, shell scripts

Familiar bash workflows with SLURM compatibility.

```bash
# Submit a job
uv run flow run "python train.py" --instance-type a100

# SLURM compatibility
uv run flow run --slurm my-job.slurm
```

#### CLI Quickstarts:
- [**SLURM Migration**](cli/slurm-migration.md) - Transition from SLURM to Flow
- [**Inference**](cli/inference.md) - Serve models via CLI
- [**Training**](cli/training.md) - Submit training jobs
- [**Fine-tuning**](cli/fine-tuning.md) - Fine-tune from command line

**Key Features:**
- ✅ SLURM script compatibility
- ✅ Batch job arrays
- ✅ Environment modules
- ✅ Familiar commands

---

### Infrastructure as Code
**Best for:** Platform teams, GitOps, reproducible deployments

Declarative configuration with version control.

```hcl
resource "flow_task" "training" {
  command       = "python train.py"
  instance_type = "8xa100"
  max_price     = 20.0
}
```

#### IaC Quickstarts:
- [**Terraform**](iac/terraform.md) - Manage Flow resources with Terraform
- [**Pulumi**](iac/pulumi.md) - Deploy with Pulumi (Python/TypeScript)
- [**Examples**](iac/examples/) - Production-ready templates

**Key Features:**
- ✅ Version controlled
- ✅ Reproducible
- ✅ CI/CD integration
- ✅ State management

---

### Jupyter Notebooks
**Best for:** Data scientists, prototyping, interactive development

Interactive experimentation with immediate feedback.

```python
# In Jupyter
%load_ext flow
%flow run --instance-type a100 --interactive
```

#### Notebook Quickstarts:
- [**Getting Started**](notebook/getting-started.ipynb) - First GPU notebook
- [**Inference**](notebook/inference.ipynb) - Interactive model serving
- [**Training**](notebook/training.ipynb) - Experiment tracking
- [**Fine-tuning**](notebook/fine-tuning.ipynb) - Interactive LoRA

**Key Features:**
- ✅ Interactive development
- ✅ Visualization support
- ✅ Experiment tracking
- ✅ Quick iteration

## By Use Case

### Model Inference
Deploy and serve models at scale:
- **SDK**: [vLLM & TGI deployment](sdk/inference.md)
- **CLI**: [Batch inference](cli/inference.md)
- **IaC**: [Production serving](iac/terraform.md#inference)
- **Notebook**: [Interactive testing](notebook/inference.ipynb)

### Model Training
Train from scratch or continue training:
- **SDK**: [Distributed PyTorch](sdk/training.md)
- **CLI**: [Submit training jobs](cli/training.md)
- **IaC**: [Managed training](iac/terraform.md#training)
- **Notebook**: [Experiment tracking](notebook/training.ipynb)

### Fine-tuning
Adapt pre-trained models:
- **SDK**: [LoRA/QLoRA setup](sdk/fine-tuning.md)
- **CLI**: [Fine-tune scripts](cli/fine-tuning.md)
- **IaC**: [Automated pipelines](iac/terraform.md#fine-tuning)
- **Notebook**: [Interactive tuning](notebook/fine-tuning.ipynb)

## Instance Types

| GPU Type | Memory | Use Case |
|----------|--------|----------|
| `a100` | 1×80GB | Training, fine-tuning |
| `2xa100` | 2×80GB | Medium-scale training |
| `4xa100` | 4×80GB | Distributed training |
| `8xa100` | 8×80GB | Large scale training |
| `h100` | 8×80GB | Latest architecture (8 GPUs) |

**Note**: All A100s are 80GB with SXM4. H100 defaults to 8× configuration.

💡 **Pricing**: Mithril uses dynamic auction-based pricing. Use `flow instances` to see current availability and spot prices.

## Prerequisites

1. **Install Flow SDK**
   ```bash
   pip install flow-sdk
   ```

2. **Configure API Key**
   ```bash
   flow init
   ```
   Get your key at [app.mithril.ai/account/apikeys](https://app.mithril.ai/account/apikeys)

3. **Verify Setup** (30 seconds)
   ```bash
   flow test-gpu
   ```

## Quick Links

- [Core Concepts](../getting-started/core-concepts.md) - Understand Flow's architecture
- [Authentication](../getting-started/authentication.md) - API key management
- [Examples](../../examples/) - Complete working examples
- [Troubleshooting](../troubleshooting/) - Common issues

## Support

- **Documentation**: [docs.flow.ai](https://docs.flow.ai)
- **Community**: [discord.gg/flow](https://discord.gg/flow)
- **Issues**: [github.com/flow-ai/flow-sdk](https://github.com/flow-ai/flow-sdk)

---

Ready to start? Choose your path above and get GPU workloads running in minutes!