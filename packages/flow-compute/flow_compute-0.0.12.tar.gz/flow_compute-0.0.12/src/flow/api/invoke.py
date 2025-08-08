"""Zero-import remote function invocation.

This module provides an invoker pattern that enables running Python functions
remotely without requiring Flow imports in user code.

The key insight: decorators contaminate user code with infrastructure concerns.
This invoker pattern maintains clean separation - ML code remains pure Python,
infrastructure stays in Flow.

Example:
    User's ML code (train.py) - Pure Python, no Flow imports::

        def train_model(data_path: str, epochs: int = 100):
            import torch
            model = torch.nn.Linear(10, 1)
            # ... training logic
            return {"accuracy": 0.95, "loss": 0.01}

    Infrastructure code (runner.py) - Only this needs Flow::

        from flow import invoke

        result = invoke("train.py", "train_model",
                       args=["s3://bucket/data"],
                       kwargs={"epochs": 200},
                       gpu="a100",
                       max_price_per_hour=25.0)
        print(result)  # {"accuracy": 0.95, "loss": 0.01}

Serialization approach:
    Arguments and return values must be JSON-serializable. This constraint is
    intentional - it ensures debuggability and prevents version mismatches.

    For complex types (numpy arrays, models), save to disk and pass paths::

        # Instead of: invoke("train.py", "process", args=[numpy_array])
        # Do:
        np.save("/tmp/data.npy", numpy_array)
        result = invoke("train.py", "process", args=["/tmp/data.npy"])

    This explicit approach creates more reliable, debuggable systems.
"""

import json
import os
from pathlib import Path
from typing import Any, List, Optional

from flow import Flow
from flow.api.models import Task, TaskConfig
from flow.errors import InvalidResponseError, TaskExecutionError, ValidationError


def _serialize_to_json(obj: Any, obj_name: str) -> str:
    """Serialize object to JSON with helpful error messages.

    Args:
        obj: Object to serialize.
        obj_name: Human-readable name for error messages.

    Returns:
        JSON string representation.

    Raises:
        TypeError: If object cannot be serialized to JSON.
    """
    try:
        return json.dumps(obj)
    except (TypeError, ValueError) as e:
        # Show a preview of the problematic object
        obj_repr = repr(obj)[:100] + "..." if len(repr(obj)) > 100 else repr(obj)
        obj_type = type(obj).__name__

        # Provide type-specific guidance
        specific_help = ""
        if "numpy" in obj_type.lower() or "ndarray" in obj_type:
            specific_help = "np.save('/tmp/data.npy', obj) then pass '/tmp/data.npy'"
        elif "dataframe" in obj_type.lower():
            specific_help = "df.to_parquet('/tmp/data.parquet') then pass the path"
        elif "tensor" in obj_type.lower():
            specific_help = "torch.save(obj, '/tmp/model.pt') then pass the path"
        elif hasattr(obj, "__dict__"):
            specific_help = "save with pickle.dump() or convert to dict"
        else:
            specific_help = "convert to a JSON-serializable type or save to disk"

        raise TypeError(
            f"Cannot serialize {obj_name} to JSON.\n"
            f"Value: {obj_repr}\n"
            f"Type: {obj_type}\n"
            f"\n"
            f"For {obj_type} objects, {specific_help}\n"
            f"\n"
            f"JSON only supports: dict, list, str, int, float, bool, None\n"
            f"This explicit approach ensures reproducibility and debuggability."
        ) from e


def _create_invoke_script(
    module_path: str,
    function_name: str,
    args: List[Any],
    kwargs: dict[str, Any],
    result_path: str,
    temp_dir: Optional[str] = None,
    max_result_size: int = 10 * 1024 * 1024,
) -> str:
    """Create the wrapper script for remote function invocation.

    Args:
        module_path: Path to the Python module.
        function_name: Name of the function to call.
        args: Positional arguments for the function.
        kwargs: Keyword arguments for the function.
        result_path: Path where result JSON will be written.
        temp_dir: Optional temporary directory to clean up (for async).
        max_result_size: Maximum allowed result size in bytes.

    Returns:
        The Python script as a string.
    """
    # Common script template
    if temp_dir:
        # Async version with cleanup
        return '''
import sys
import json
import importlib.util
import os
import shutil

# Safely load parameters
module_path = {module_path_repr}
function_name = {function_name_repr}
args = {args_json}
kwargs = {kwargs_json}
result_path = {result_path_repr}
temp_dir = {temp_dir_repr}
max_result_size = {max_result_size}

def cleanup():
    """Clean up temporary directory."""
    try:
        shutil.rmtree(temp_dir)
    except:
        pass

# Load the module
try:
    print(f"Loading function '{{function_name}}' from {{module_path}}")
    spec = importlib.util.spec_from_file_location("user_module", module_path)
    if not spec or not spec.loader:
        print("ERROR: Could not load module", file=sys.stderr)
        cleanup()
        sys.exit(1)

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Get the function
    if not hasattr(module, function_name):
        print(f"ERROR: Function '{{function_name}}' not found in module", file=sys.stderr)
        cleanup()
        sys.exit(1)

    func = getattr(module, function_name)

    # Call with provided arguments
    print(f"Executing {{function_name}}...")
    result = func(*args, **kwargs)
    print(f"Execution completed successfully")
    
    # Serialize result to check size
    result_json = json.dumps(result)
    result_size = len(result_json.encode('utf-8'))
    
    if result_size > max_result_size:
        print(f"ERROR: Result too large ({{result_size}} bytes > {{max_result_size}} bytes)", file=sys.stderr)
        cleanup()
        sys.exit(1)
    
    # Write result to file
    with open(result_path, 'w') as f:
        f.write(result_json)
    
    print(f"Result written to {{result_path}} ({{result_size}} bytes)")
    
except Exception as e:
    print(f"ERROR: Function execution failed: {{e}}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    cleanup()
    sys.exit(1)
'''.format(
            module_path_repr=repr(str(module_path)),
            function_name_repr=repr(function_name),
            args_json=_serialize_to_json(args, "arguments"),
            kwargs_json=_serialize_to_json(kwargs, "keyword arguments"),
            result_path_repr=repr(str(result_path)),
            temp_dir_repr=repr(str(temp_dir)),
            max_result_size=max_result_size,
        )
    else:
        # Sync version without cleanup
        return """
import sys
import json
import importlib.util
import os

# Safely load parameters
module_path = {module_path_repr}
function_name = {function_name_repr}
args = {args_json}
kwargs = {kwargs_json}
result_path = {result_path_repr}

# Load the module
print(f"Loading function '{{function_name}}' from {{module_path}}")
spec = importlib.util.spec_from_file_location("user_module", module_path)
if not spec or not spec.loader:
    print("ERROR: Could not load module", file=sys.stderr)
    sys.exit(1)

module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Get the function
if not hasattr(module, function_name):
    print(f"ERROR: Function '{{function_name}}' not found in module", file=sys.stderr)
    sys.exit(1)

func = getattr(module, function_name)

# Call with provided arguments
try:
    print(f"Executing {{function_name}}...")
    result = func(*args, **kwargs)
    print(f"Execution completed successfully")
    
    # Check result size before writing
    result_json = json.dumps(result)
    result_size = len(result_json.encode('utf-8'))
    max_result_size = {max_result_size}  # User-specified limit
    
    if result_size > max_result_size:
        print(f"ERROR: Result too large ({{result_size}} bytes > {{max_result_size}} bytes)", file=sys.stderr)
        print("Consider saving large results to disk and returning the path instead:", file=sys.stderr)
        print("  return '/tmp/results.npy'  # Instead of returning the array", file=sys.stderr)
        sys.exit(1)
    
    # Write result to file (side-channel)
    with open(result_path, 'w') as f:
        f.write(result_json)
    
    print(f"Result written to {{result_path}} ({{result_size}} bytes)")
except Exception as e:
    print(f"ERROR: Function execution failed: {{e}}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
""".format(
            module_path_repr=repr(str(module_path)),
            function_name_repr=repr(function_name),
            args_json=_serialize_to_json(args, "arguments"),
            kwargs_json=_serialize_to_json(kwargs, "keyword arguments"),
            result_path_repr=repr(str(result_path)),
            max_result_size=max_result_size,
        )


def _parse_invoke_result(result_json: str) -> Any:
    """Parse the JSON result from an invoke operation.

    Args:
        result_json: JSON string to parse.

    Returns:
        The parsed result.

    Raises:
        json.JSONDecodeError: If the JSON is invalid.
    """
    return json.loads(result_json)


class InvokeTask:
    """Result handle for async invoke operations.

    Provides access to the underlying task and handles result retrieval
    with automatic cleanup of temporary files.
    """

    def __init__(self, task: Task, result_path: Path, temp_dir: Path):
        """Initialize with task and paths.

        Args:
            task: The underlying Flow task
            result_path: Path to the result JSON file
            temp_dir: Temporary directory to clean up
        """
        self.task = task  # Public access to underlying task
        self._result_path = result_path
        self._temp_dir = temp_dir
        self._result_cached = None
        self._cleaned_up = False

    def get_result(self) -> Any:
        """Get the function result after task completes.

        Returns:
            The function's return value

        Raises:
            RuntimeError: If task failed or result not available
            JSONDecodeError: If result cannot be parsed
        """
        # Return cached result if available
        if self._result_cached is not None:
            return self._result_cached

        # Ensure task has completed
        if self.task.status not in ["completed", "failed"]:
            raise TaskExecutionError(
                f"Cannot get result, task is {self.task.status}",
                suggestions=[
                    "Call task.wait() first to wait for completion",
                    "Check task status with task.status",
                    "Use task.logs() to monitor progress",
                ],
                error_code="TASK_004",
            )

        if self.task.status == "failed":
            raise TaskExecutionError(
                "Task failed during execution",
                suggestions=[
                    "Check task logs with task.logs() for error details",
                    "Verify your function doesn't have syntax errors",
                    "Ensure all dependencies are available in the remote environment",
                ],
                error_code="TASK_002",
            )

        # Read result file
        try:
            with open(self._result_path) as f:
                self._result_cached = json.load(f)
                return self._result_cached
        except FileNotFoundError:
            raise TaskExecutionError(
                "Result file not found",
                suggestions=[
                    "Task may have failed - check logs with task.logs()",
                    "Ensure your function returns a JSON-serializable value",
                    "Check if the task completed successfully",
                ],
                error_code="TASK_005",
            )
        except json.JSONDecodeError as e:
            raise InvalidResponseError(
                f"Failed to parse result JSON: {str(e)}",
                suggestions=[
                    "Ensure the remote function returns JSON-serializable data",
                    "Check for numpy arrays or other non-serializable types",
                    "Consider saving complex data to disk and returning the path",
                ],
                error_code="RESPONSE_002",
            ) from e
        finally:
            # Clean up after reading result
            self._cleanup()

    def _cleanup(self):
        """Clean up temporary files."""
        if self._cleaned_up:
            return

        try:
            import shutil

            shutil.rmtree(self._temp_dir)
            self._cleaned_up = True
        except:
            # Best effort cleanup
            pass

    def __del__(self):
        """Ensure cleanup on deletion."""
        self._cleanup()


def invoke(
    module_path: str,
    function_name: str,
    args: Optional[List[Any]] = None,
    kwargs: Optional[dict[str, Any]] = None,
    max_result_size: int = 10 * 1024 * 1024,
    retries: int = 0,
    retry_delay: float = 1.0,
    retry_backoff: float = 2.0,
    **task_params,
) -> Any:
    """Run a Python function remotely with zero imports needed in user code.

    This function enables true portability by keeping ML code free of Flow
    dependencies. The remote function is executed in its natural environment
    and its return value is captured and returned.

    Compatible with Linux/macOS only (uses Unix file paths and commands).
    Result size limited to 10MB by default (configurable).

    Args:
        module_path: Path to Python module (e.g., "train.py" or "src/model.py")
        function_name: Name of function to call
        args: Positional arguments for the function
        kwargs: Keyword arguments for the function
        max_result_size: Maximum result size in bytes (default 10MB).
            Increase for large data science results.
        retries: Number of retry attempts if task fails (default 0)
        retry_delay: Initial delay between retries in seconds (default 1.0)
        retry_backoff: Exponential backoff multiplier (default 2.0)
        **task_params: Flow task parameters (gpu, instance_type, max_price_per_hour, etc.)

    Returns:
        The return value of the remote function (deserialized from JSON)

    Raises:
        FlowError: If task submission or execution fails
        ValueError: If module or function cannot be found
        JSONDecodeError: If function return value cannot be serialized

    Example:
        Basic usage:
        >>> result = invoke("process.py", "analyze_data", args=["input.csv"])

        With GPU and arguments:
        >>> metrics = invoke(
        ...     "train.py",
        ...     "train_model",
        ...     kwargs={"batch_size": 32, "lr": 0.001},
        ...     gpu="a100",
        ...     max_price_per_hour=20.0
        ... )

        Large results:
        >>> result = invoke("analysis.py", "process_data",
        ...                 max_result_size=100*1024*1024)  # 100MB limit

        With retry logic:
        >>> result = invoke("train.py", "train_model",
        ...                 retries=3,  # Retry up to 3 times
        ...                 retry_delay=2.0,  # Start with 2s delay
        ...                 retry_backoff=2.0)  # Double delay each retry
    """
    # Validate module path
    module_path = Path(module_path)
    if not module_path.exists():
        raise ValidationError(
            f"Module not found: {module_path}",
            suggestions=[
                "Check the file path is correct and exists",
                "Use an absolute path for clarity",
                "Ensure the file has a .py extension",
            ],
            error_code="VALIDATION_003",
        )

    import tempfile

    # Create a unique result file path for this invocation
    result_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    result_path = result_file.name
    result_file.close()

    # Build the wrapper script using helper function
    wrapper_code = _create_invoke_script(
        module_path=str(module_path),
        function_name=function_name,
        args=args or [],
        kwargs=kwargs or {},
        result_path=result_path,
        temp_dir=None,  # Sync version doesn't need cleanup
        max_result_size=max_result_size,
    )

    # Write wrapper to temporary file for security
    wrapper_file = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)
    wrapper_path = wrapper_file.name
    wrapper_file.write(wrapper_code)
    wrapper_file.close()

    # Command now just runs the temp file
    command = f"python {wrapper_path}"

    # Extract Flow-specific parameters
    flow_params = {
        "name": task_params.pop("name", f"invoke-{function_name}"),
        "command": " ".join(command) if isinstance(command, list) else command,
    }

    # Map common parameters
    if "gpu" in task_params:
        flow_params["instance_type"] = task_params.pop("gpu")
    elif "instance_type" in task_params:
        flow_params["instance_type"] = task_params.pop("instance_type")

    # Handle num_instances separately
    if "num_instances" in task_params:
        flow_params["num_instances"] = task_params.pop("num_instances")

    # Pass through all other parameters
    flow_params.update(task_params)

    # Create task config
    config = TaskConfig(**flow_params)

    # Run the task with retry logic
    import time

    last_exception = None
    for attempt in range(retries + 1):
        try:
            with Flow() as flow:
                task = flow.run(config, wait=True)

                # Check if task succeeded
                if task.status != "completed":
                    logs = task.logs()
                    error_msg = f"Task failed with status {task.status}. Logs:\n{logs}"

                    # Check if this is retryable
                    if attempt < retries:
                        last_exception = RuntimeError(error_msg)
                        delay = retry_delay * (retry_backoff**attempt)
                        time.sleep(delay)
                        continue
                    else:
                        raise RuntimeError(error_msg)

                # Read result from the side-channel JSON file
                try:
                    with open(result_path, "r") as f:
                        result = json.load(f)
                    # Success - clean up and return
                    try:
                        os.unlink(result_path)
                        os.unlink(wrapper_path)
                    except:
                        pass
                    return result
                except FileNotFoundError:
                    # If result file not found, check logs for errors
                    logs = task.logs()
                    if "ERROR:" in logs:
                        error_lines = [line for line in logs.split("\n") if "ERROR:" in line]
                        if error_lines:
                            error_msg = f"Remote execution failed: {error_lines[0]}"
                        else:
                            error_msg = (
                                f"Result file not found at {result_path}. Full logs:\n{logs}"
                            )
                    else:
                        error_msg = f"Result file not found at {result_path}. Full logs:\n{logs}"

                    if attempt < retries:
                        last_exception = RuntimeError(error_msg)
                        delay = retry_delay * (retry_backoff**attempt)
                        time.sleep(delay)
                        continue
                    else:
                        raise RuntimeError(error_msg)
                except json.JSONDecodeError as e:
                    error_msg = f"Could not parse result JSON from {result_path}: {e}"
                    if attempt < retries:
                        last_exception = RuntimeError(error_msg)
                        delay = retry_delay * (retry_backoff**attempt)
                        time.sleep(delay)
                        continue
                    else:
                        raise RuntimeError(error_msg)

        except Exception as e:
            # Any other exception during task execution
            if attempt < retries:
                last_exception = e
                delay = retry_delay * (retry_backoff**attempt)
                time.sleep(delay)
                continue
            else:
                raise

    # If we get here, all retries failed
    if last_exception:
        raise last_exception

    # Clean up on final failure
    try:
        os.unlink(result_path)
        os.unlink(wrapper_path)
    except:
        pass


# Convenience function for async execution
def invoke_async(
    module_path: str,
    function_name: str,
    args: Optional[List[Any]] = None,
    kwargs: Optional[dict[str, Any]] = None,
    max_result_size: int = 10 * 1024 * 1024,
    **task_params,
) -> "InvokeTask":
    """Submit a function for remote execution without waiting.

    Returns an InvokeTask object that provides result retrieval and cleanup.
    Compatible with Linux/macOS only (uses Unix file paths).

    Args:
        module_path: Path to Python module
        function_name: Name of function to call
        args: Positional arguments for the function
        kwargs: Keyword arguments for the function
        max_result_size: Maximum result size in bytes (default 10MB)
        **task_params: Flow task parameters

    Returns:
        InvokeTask object with get_result() method

    Example:
        >>> invoke_task = invoke_async("train.py", "train_model", gpu="a100")
        >>> # Do other work...
        >>> invoke_task.task.wait()  # Access underlying task
        >>> result = invoke_task.get_result()
        >>> print(result)
    """
    # Validate module path
    module_path = Path(module_path)
    if not module_path.exists():
        raise ValidationError(
            f"Module not found: {module_path}",
            suggestions=[
                "Check the file path is correct and exists",
                "Use an absolute path for clarity",
                "Ensure the file has a .py extension",
            ],
            error_code="VALIDATION_003",
        )

    import tempfile
    import uuid

    # Use a unique subdirectory for this invocation to avoid conflicts
    invoke_id = str(uuid.uuid4())[:8]
    temp_dir = Path(tempfile.gettempdir()) / f"flow-invoke-{invoke_id}"
    temp_dir.mkdir(exist_ok=True)

    result_path = temp_dir / "result.json"
    wrapper_path = temp_dir / "wrapper.py"

    # Build the wrapper script using helper function
    wrapper_code = _create_invoke_script(
        module_path=str(module_path),
        function_name=function_name,
        args=args or [],
        kwargs=kwargs or {},
        result_path=str(result_path),
        temp_dir=str(temp_dir),  # Async version needs cleanup
        max_result_size=max_result_size,
    )

    # Write wrapper script
    wrapper_path.write_text(wrapper_code)

    # Command runs the wrapper
    command = ["python", str(wrapper_path)]

    flow_params = {
        "name": task_params.pop("name", f"invoke-{function_name}"),
        "command": " ".join(command) if isinstance(command, list) else command,
    }

    if "gpu" in task_params:
        flow_params["instance_type"] = task_params.pop("gpu")
        flow_params["num_instances"] = task_params.pop("num_instances", 1)

    flow_params.update(task_params)
    config = TaskConfig(**flow_params)

    # Submit without waiting
    flow = Flow()
    task = flow.run(config, wait=False)

    # Return wrapped task with result retrieval
    return InvokeTask(task, result_path, temp_dir)
