# Flow Cancel

Cancel running GPU tasks with support for pattern matching.

## Synopsis

```bash
flow cancel [TASK_IDENTIFIER] [OPTIONS]
```

## Description

The `flow cancel` command terminates running tasks gracefully. It supports:
- Single task cancellation by ID or name
- Pattern matching for bulk cancellation
- Interactive task selection
- Confirmation prompts (can be skipped with `--yes`)

## Options

- `TASK_IDENTIFIER` - Task ID or name to cancel (optional - shows interactive selector if omitted)
- `--yes`, `-y` - Skip confirmation prompt
- `--all` - Cancel all running tasks
- `--name-pattern`, `-n` - Cancel tasks matching name pattern (supports wildcards)
- `--regex` - Treat pattern as regex instead of wildcard

## Examples

### Basic Usage

```bash
# Interactive task selector
flow cancel

# Cancel specific task
flow cancel task-123456

# Cancel by name
flow cancel my-training-job

# Skip confirmation
flow cancel task-123456 --yes
```

### Pattern Matching

```bash
# Cancel all tasks starting with "dev-"
flow cancel --name-pattern "dev-*"

# Cancel all flow-dev tasks
flow cancel -n "flow-dev-*" --yes

# Use regex for complex patterns
flow cancel -n ".*-gpu-[48]x.*" --regex

# Cancel all experiment runs
flow cancel -n "experiment-run-*"
```

### Bulk Operations

```bash
# Cancel all running tasks
flow cancel --all --yes

# Cancel all development instances
flow cancel --name-pattern "dev-*" --yes

# Cancel all tasks with specific GPU type in name
flow cancel -n "*-h100-*" --yes
```

## Pattern Matching Details

### Wildcard Patterns (Default)
- `*` matches any characters
- `?` matches single character
- `[seq]` matches any character in seq
- `[!seq]` matches any character not in seq

Examples:
- `dev-*` - Matches: dev-1, dev-test, dev-experiment
- `flow-dev-?` - Matches: flow-dev-1, flow-dev-a
- `test-[0-9]*` - Matches: test-1, test-99

### Regex Patterns (--regex flag)
Full Python regex syntax supported:
- `.*` matches any characters
- `\d+` matches digits
- `^` and `$` for start/end anchors

Examples:
- `^dev-\d+$` - Matches: dev-1, dev-99
- `.*-(gpu|cpu)-.*` - Matches tasks with gpu or cpu in name

## Notes

- Only tasks in 'pending' or 'running' state can be cancelled
- Pattern matching only applies to task names, not IDs
- Cancelled tasks cannot be resumed
- When using pattern matching, you'll see a preview of matching tasks before confirmation

## See Also

- `flow status` - View all tasks
- `flow run` - Submit new tasks
- `flow logs` - View task logs