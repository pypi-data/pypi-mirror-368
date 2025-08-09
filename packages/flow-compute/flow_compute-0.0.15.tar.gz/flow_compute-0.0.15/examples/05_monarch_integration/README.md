# Monarch Integration Examples

> ⚠️ **WARNING: Experimental Feature**
> 
> The Monarch integration is in early prototype stage. These examples show
> what currently works (basic compute allocation) but actor functionality
> is not yet implemented.

## Current State

The Monarch integration can:
- ✅ Allocate compute resources through Flow
- ✅ Install Monarch on worker nodes
- ✅ Provide SSH access to workers

The Monarch integration cannot:
- ❌ Spawn actors
- ❌ Enable actor communication
- ❌ Run actual Monarch workloads

## Examples

### basic_allocation.py

Shows what actually works today:
```bash
python basic_allocation.py
```

This will:
1. Create a Monarch backend using Flow
2. Allocate compute resources (Flow tasks)
3. Demonstrate that actor spawning fails

## Managing Allocated Resources

Since Monarch processes are just Flow tasks:

```bash
# List tasks
flow status

# View logs
flow logs <task-id>

# SSH into a worker
flow ssh <task-id>

# Clean up
flow cancel <task-id>
```

## Future Vision

For the aspirational design of what this integration could become, see:
`/docs/proposals/monarch-integration-vision.md`

## Should You Use This?

**No.** This is experimental infrastructure for future development.

If you need distributed actor systems today, consider:
- Using Monarch directly
- Ray
- Horovod