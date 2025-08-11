# Flow CLI Commands Architecture

This directory contains the modular command implementation for the Flow CLI, following a clean architecture pattern where each command is implemented in its own module.

## Architecture

### Design Principles
1. **Single Responsibility**: Each command module handles one specific command
2. **Consistent Interface**: All commands inherit from `BaseCommand`
3. **Testability**: Individual commands can be tested in isolation
4. **Maintainability**: Commands are easy to find, modify, and extend

### Structure
```
commands/
├── __init__.py          # Command discovery and registration
├── base.py              # BaseCommand abstract class
├── utils.py             # Shared utilities
├── run.py               # flow run
├── status.py            # flow status
├── cancel.py            # flow cancel
├── volumes.py           # flow volumes (command group)
├── logs.py              # flow logs
├── ssh.py               # flow ssh
└── ...
```

### Command Pattern
Each command module must:
1. Define a class that inherits from `BaseCommand`
2. Implement required properties: `name`, `help`
3. Implement `get_command()` that returns a click.Command or click.Group
4. Export a `command` instance at module level

Example:
```python
from .base import BaseCommand

class MyCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "mycommand"
    
    @property
    def help(self) -> str:
        return "Description of my command"
    
    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        def mycommand():
            # Implementation
            pass
        return mycommand

command = MyCommand()
```

### Adding a New Command
1. Create a new module: `commands/newcmd.py`
2. Implement the command following the pattern above
3. Add import in `__init__.py`: `from . import newcmd`
4. Add to `COMMAND_MODULES` list

### Command Groups
For commands with subcommands (like `flow volumes list`):
1. Return a `click.Group` from `get_command()`
2. Add subcommands to the group
3. See `volumes.py` for example

### Shared Utilities
Common functionality is in `utils.py`:
- `display_config()`: Format task configuration
- `wait_for_task()`: Wait for task with progress
- `get_status_style()`: Color coding for statuses

### Testing
Commands can be tested individually:
```python
from flow.cli.commands.run import command

def test_run_command():
    cmd = command.get_command()
    # Test the command
```

## Migration from Monolithic app.py

The original `app.py` was a 1,400-line file containing all commands. This modular structure:
- Reduces file size by ~90%
- Makes commands discoverable
- Enables parallel development
- Improves test coverage
- Follows industry best practices

To complete the migration:
1. Port remaining commands from old app.py
2. Update tests to use new structure
3. Remove old app.py backup once stable