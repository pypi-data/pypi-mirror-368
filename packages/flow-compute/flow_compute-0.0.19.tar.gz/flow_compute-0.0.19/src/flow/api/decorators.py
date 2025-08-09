"""Decorator-based interface for remote function execution.

This module provides a clean decorator pattern for executing Python functions
on remote GPU infrastructure. Functions remain pure Python, infrastructure
concerns are separated, and the API provides clear boundaries.

The decorator pattern complements the invoker pattern, providing an alternative
interface for users who prefer annotation-based configuration over explicit
function calls.

Example:
    Basic usage with GPU specification::

        from flow import FlowApp

        app = FlowApp()

        @app.function(gpu="a100")
        def train_model(data_path: str, epochs: int = 100):
            import torch
            # Training logic here
            return {"loss": 0.01, "accuracy": 0.99}

        # Execute remotely
        result = train_model.remote("s3://bucket/data.csv", epochs=50)

        # Execute locally for testing
        local_result = train_model("./local_data.csv")

    Advanced usage with full resource specification::

        @app.function(
            gpu="h100:8",  # 8x H100 GPUs
            memory=65536,  # 64GB RAM
            cpu=16.0,      # 16 CPU cores
            image="pytorch/pytorch:2.0.0",
            volumes={"/models": "model-cache"},
            environment={"WANDB_API_KEY": "..."},
        )
        def distributed_training(config_path: str):
            # Multi-GPU training code
            return {"status": "completed"}

    Handling complex data types::

        @app.function(gpu="a100")
        def process_embeddings(embeddings_path: str, output_path: str):
            import numpy as np
            embeddings = np.load(embeddings_path)
            # Process embeddings...
            results = embeddings @ embeddings.T
            np.save(output_path, results)
            return {"shape": list(results.shape), "output": output_path}

        # Usage
        embeddings = np.random.randn(1000, 768)
        np.save("/tmp/embeddings.npy", embeddings)
        result = process_embeddings.remote("/tmp/embeddings.npy", "/tmp/results.npy")
"""

import functools
import inspect
import json
from pathlib import Path
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union

from typing_extensions import ParamSpec

from flow.api.client import Flow
from flow.api.models import TaskConfig, Retries
from flow.api.secrets import Secret, validate_secrets
from flow.errors import FlowError

P = ParamSpec("P")
R = TypeVar("R")


class RemoteFunction(Generic[P, R]):
    """A function wrapper that enables remote GPU execution.

    This class wraps a Python function to allow both local and remote execution.
    When called normally, the function executes locally. When called via .remote(),
    it executes on cloud GPU infrastructure.

    The design ensures zero coupling between user code and infrastructure code.
    Functions remain testable, portable, and free of framework dependencies.
    """

    def __init__(
        self,
        func: Callable[P, R],
        flow_client: Flow,
        gpu: Optional[str] = None,
        cpu: Optional[Union[float, tuple[float, float]]] = None,
        memory: Optional[Union[int, tuple[int, int]]] = None,
        image: Optional[str] = None,
        retries: Union[int, Retries] = 0,
        timeout: Optional[int] = None,
        volumes: Optional[Dict[str, Any]] = None,
        environment: Optional[Dict[str, str]] = None,
        secrets: Optional[List[Secret]] = None,
        **kwargs,
    ):
        """Initialize a RemoteFunction.

        Args:
            func: The function to wrap.
            flow_client: Flow client for task submission.
            gpu: GPU specification (e.g., "a100", "h100:4").
            cpu: CPU cores as float or (request, limit) tuple.
            memory: Memory in MB as int or (request, limit) tuple.
            image: Docker image name. Defaults to python:3.11.
            retries: Retry configuration. Either an int for simple retries
                or a Retries object for advanced configuration.
            timeout: Maximum execution time in seconds.
            volumes: Volume mount specifications.
            environment: Environment variables for execution.
            secrets: List of Secret objects for secure credential injection.
            **kwargs: Additional TaskConfig parameters.
        """
        self.func = func
        self.flow_client = flow_client
        self.gpu = gpu
        self.cpu = cpu
        self.memory = memory
        self.image = image or "python:3.11"
        self.retries = retries
        self.timeout = timeout
        self.volumes = volumes or {}
        self.environment = environment or {}
        self.env = self.environment  # Backward compatibility
        self.secrets = secrets or []
        self.kwargs = kwargs

        # Validate secrets if provided
        if self.secrets:
            validate_secrets(self.secrets)

        # Copy function metadata
        functools.update_wrapper(self, func)
        # Preserve the original function signature for better introspection
        try:
            self.__signature__ = inspect.signature(func)  # type: ignore[attr-defined]
        except (ValueError, TypeError):
            # Some callables may not have retrievable signatures; ignore silently
            pass

        # Store function location
        self.module_name = func.__module__
        self.func_name = func.__name__

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Execute the function locally.

        This allows the decorated function to be called normally for local
        testing and development. The function executes in the current process
        with no infrastructure overhead.

        Args:
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            The function's return value.

        Example:
            >>> @app.function(gpu="a100")
            ... def process(x: int) -> int:
            ...     return x * 2
            >>> result = process(5)  # Runs locally
            >>> assert result == 10
        """
        return self.func(*args, **kwargs)

    def remote(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Execute the function remotely on GPU infrastructure.

        Submits the function for execution on cloud GPUs with the configured
        resources. Blocks until execution completes and returns the result.

        Args:
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            The function's return value, deserialized from the remote execution.

        Raises:
            FlowError: If remote execution fails or times out.

        Example:
            >>> @app.function(gpu="h100", memory=32768)
            ... def train(data: str, lr: float = 0.001):
            ...     # ML training code
            ...     return {"loss": 0.15}
            >>> result = train.remote("s3://data/train.csv", lr=0.0001)
            >>> print(result["loss"])
            0.15
        """
        # Prepare the execution script
        wrapper_script = self._create_wrapper_script(args, kwargs)

        # Build TaskConfig
        config = self._build_task_config(wrapper_script)

        # Submit task and wait for terminal state, then extract result
        task = self.flow_client.run(config, wait=True)
        # Use Task.result() to surface rich error information if the function failed
        return self._extract_result(task)

    def spawn(self, *args: P.args, **kwargs: P.kwargs) -> str:
        """Execute the function remotely without waiting.

        Submits the function for asynchronous execution and returns immediately
        with a task ID. Use this for fire-and-forget operations or when you
        need to manage multiple concurrent executions.

        Args:
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            Task ID that can be used to check status or retrieve results.

        Example:
            >>> @app.function(gpu="a100")
            ... def process_batch(batch_id: int):
            ...     # Process data batch
            ...     return {"processed": batch_id}
            >>>
            >>> # Launch multiple tasks
            >>> task_ids = []
            >>> for i in range(10):
            ...     task_id = process_batch.spawn(i)
            ...     task_ids.append(task_id)
            >>>
            >>> # Check status later
            >>> from flow import status
            >>> for task_id in task_ids:
            ...     print(f"{task_id}: {status(task_id)}")
        """
        # Prepare the execution script
        wrapper_script = self._create_wrapper_script(args, kwargs)

        # Build TaskConfig
        config = self._build_task_config(wrapper_script)

        # Submit task without waiting
        task = self.flow_client.run(config, wait=False)
        return task.id

    def _create_wrapper_script(self, args: tuple, kwargs: dict) -> str:
        """Create a Python script for remote execution.

        Generates a self-contained Python script that imports the target
        function, deserializes arguments, executes the function, and saves
        the result. This ensures clean separation between user code and
        infrastructure code.

        Args:
            args: Positional arguments for the function.
            kwargs: Keyword arguments for the function.

        Returns:
            Python script as a string.
        """
        # Serialize arguments with helpful errors
        try:
            args_json = json.dumps({"args": list(args), "kwargs": kwargs})
        except (TypeError, ValueError) as e:
            # Provide specific guidance for common ML types
            error_msg = self._get_serialization_error_message(args, kwargs, e)
            raise TypeError(error_msg) from e

        # Get the source file path
        module = inspect.getmodule(self.func)
        if module and hasattr(module, "__file__"):
            source_file = Path(module.__file__).name
        else:
            source_file = "function.py"

        wrapper = f"""
import json
import sys
import traceback
import inspect
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from {self.module_name} import {self.func_name}

args_data = json.loads({json.dumps(args_json)!r})
args = args_data["args"]
kwargs = args_data["kwargs"]

try:
    func = {self.func_name}
    if inspect.iscoroutinefunction(func):
        result = asyncio.run(func(*args, **kwargs))
    else:
        result = func(*args, **kwargs)
    
    # Result must be JSON-serializable
    try:
        json.dumps(result)
    except (TypeError, ValueError) as e:
        # Provide guidance if result is not JSON-serializable
        raise TypeError(
            f"Function returned non-JSON-serializable result: {{type(result).__name__}}\\n"
            f"\\n"
            f"Functions must return JSON-serializable values:\\n"
            f"  - Basic types: str, int, float, bool, None\\n"
            f"  - Collections: list, dict (with JSON-serializable values)\\n"
            f"  - File paths: Return paths to saved outputs\\n"
            f"\\n"
            f"For complex outputs, save to disk and return the path:\\n"
            f"  def {self.func_name}(...):\\n"
            f"      # Process data...\\n"
            f"      np.save('/outputs/result.npy', result_array)\\n"
            f"      return {{'result_path': '/outputs/result.npy', 'metrics': {{...}}}}\\n"
        ) from e
    
    with open("/tmp/flow_result.json", "w") as f:
        json.dump({{"success": True, "result": result}}, f)
        
except Exception as e:
    # Capture full traceback for better debugging
    tb = traceback.format_exc()
    error_obj = {{
        "type": type(e).__name__,
        "message": str(e),
        "traceback": tb
    }}
    
    with open("/tmp/flow_result.json", "w") as f:
        json.dump({{"success": False, "error": error_obj}}, f)
    
    # Still raise to ensure non-zero exit code
    raise
"""
        return wrapper

    def _get_serialization_error_message(
        self, args: tuple, kwargs: dict, original_error: Exception
    ) -> str:
        """Generate helpful error messages for non-serializable types.

        Detects common ML/scientific types and provides specific guidance
        on how to save and load them properly.
        """
        import re

        # Try to detect common non-serializable types
        all_values = list(args) + list(kwargs.values())

        # Import common ML packages only if available
        numpy_array_type = None
        pandas_dataframe_type = None
        torch_tensor_type = None
        sklearn_model_types = []

        try:
            import numpy as np

            numpy_array_type = np.ndarray
        except ImportError:
            pass

        try:
            import pandas as pd

            pandas_dataframe_type = pd.DataFrame
        except ImportError:
            pass

        try:
            import torch

            torch_tensor_type = torch.Tensor
        except ImportError:
            pass

        try:
            from sklearn.base import BaseEstimator

            sklearn_model_types.append(BaseEstimator)
        except ImportError:
            pass

        # Check each argument for known types
        for i, arg in enumerate(all_values):
            arg_name = (
                f"argument {i + 1}"
                if i < len(args)
                else f"kwarg '{list(kwargs.keys())[i - len(args)]}'"
            )

            # NumPy arrays
            if numpy_array_type and isinstance(arg, numpy_array_type):
                return (
                    f"Cannot serialize numpy array ({arg_name}) to JSON.\n"
                    f"Flow uses JSON serialization to ensure reproducibility across environments.\n"
                    f"\n"
                    f"Save the array to disk and pass the path instead:\n"
                    f"\n"
                    f"  # Save locally:\n"
                    f"  np.save('/tmp/data.npy', array)\n"
                    f"  result = {self.func_name}.remote('/tmp/data.npy')\n"
                    f"\n"
                    f"  # Or use a volume:\n"
                    f"  np.save('/outputs/data.npy', array)  # Saved to persistent volume\n"
                    f"  result = {self.func_name}.remote('volume://outputs/data.npy')\n"
                    f"\n"
                    f"  # In your function:\n"
                    f"  def {self.func_name}(data_path: str):\n"
                    f"      data = np.load(data_path)\n"
                    f"      # ... process data ...\n"
                )

            # Pandas DataFrames
            elif pandas_dataframe_type and isinstance(arg, pandas_dataframe_type):
                return (
                    f"Cannot serialize pandas DataFrame ({arg_name}) to JSON.\n"
                    f"Flow uses JSON serialization to ensure reproducibility across environments.\n"
                    f"\n"
                    f"Save the DataFrame to disk and pass the path instead:\n"
                    f"\n"
                    f"  # Parquet (recommended - preserves types, efficient):\n"
                    f"  df.to_parquet('/tmp/data.parquet')\n"
                    f"  result = {self.func_name}.remote('/tmp/data.parquet')\n"
                    f"\n"
                    f"  # CSV (simpler but loses type info):\n"
                    f"  df.to_csv('/tmp/data.csv', index=False)\n"
                    f"  result = {self.func_name}.remote('/tmp/data.csv')\n"
                    f"\n"
                    f"  # In your function:\n"
                    f"  def {self.func_name}(data_path: str):\n"
                    f"      df = pd.read_parquet(data_path)  # or pd.read_csv()\n"
                    f"      # ... process dataframe ...\n"
                )

            # PyTorch tensors/models
            elif torch_tensor_type and isinstance(arg, torch_tensor_type):
                return (
                    f"Cannot serialize PyTorch tensor ({arg_name}) to JSON.\n"
                    f"Flow uses JSON serialization to ensure reproducibility across environments.\n"
                    f"\n"
                    f"Save the tensor to disk and pass the path instead:\n"
                    f"\n"
                    f"  # Save tensor:\n"
                    f"  torch.save(tensor, '/tmp/tensor.pt')\n"
                    f"  result = {self.func_name}.remote('/tmp/tensor.pt')\n"
                    f"\n"
                    f"  # In your function:\n"
                    f"  def {self.func_name}(tensor_path: str):\n"
                    f"      tensor = torch.load(tensor_path)\n"
                    f"      # ... use tensor ...\n"
                )

            # PyTorch models (have state_dict method)
            elif hasattr(arg, "state_dict") and callable(getattr(arg, "state_dict")):
                return (
                    f"Cannot serialize PyTorch model ({arg_name}) to JSON.\n"
                    f"Flow uses JSON serialization to ensure reproducibility across environments.\n"
                    f"\n"
                    f"Save the model checkpoint and pass the path instead:\n"
                    f"\n"
                    f"  # Save model state:\n"
                    f"  torch.save(model.state_dict(), '/tmp/model.pt')\n"
                    f"  result = {self.func_name}.remote('/tmp/model.pt', 'config.json')\n"
                    f"\n"
                    f"  # Or save complete model:\n"
                    f"  torch.save(model, '/tmp/model_complete.pt')\n"
                    f"\n"
                    f"  # In your function:\n"
                    f"  def {self.func_name}(checkpoint_path: str, config_path: str):\n"
                    f"      # Load config and recreate model\n"
                    f"      config = json.load(open(config_path))\n"
                    f"      model = ModelClass(**config)\n"
                    f"      model.load_state_dict(torch.load(checkpoint_path))\n"
                    f"      # ... use model ...\n"
                )

            # Sklearn models
            elif sklearn_model_types and any(isinstance(arg, t) for t in sklearn_model_types):
                return (
                    f"Cannot serialize scikit-learn model ({arg_name}) to JSON.\n"
                    f"Flow uses JSON serialization to ensure reproducibility across environments.\n"
                    f"\n"
                    f"Save the model to disk and pass the path instead:\n"
                    f"\n"
                    f"  # Using joblib (recommended):\n"
                    f"  import joblib\n"
                    f"  joblib.dump(model, '/tmp/model.joblib')\n"
                    f"  result = {self.func_name}.remote('/tmp/model.joblib')\n"
                    f"\n"
                    f"  # In your function:\n"
                    f"  def {self.func_name}(model_path: str):\n"
                    f"      model = joblib.load(model_path)\n"
                    f"      # ... use model ...\n"
                )

        # Generic error for other types
        type_match = re.search(r"of type '?([^']+)'? is not JSON serializable", str(original_error))
        problem_type = type_match.group(1) if type_match else "unknown"

        return (
            f"Cannot serialize {problem_type} object to JSON.\n"
            f"Flow uses JSON serialization to ensure reproducibility across environments.\n"
            f"\n"
            f"Only JSON-serializable types are supported for function arguments:\n"
            f"  - Basic types: str, int, float, bool, None\n"
            f"  - Collections: list, dict (with JSON-serializable values)\n"
            f"  - Paths to data files: '/path/to/data.ext'\n"
            f"\n"
            f"For complex objects, save to disk and pass the path:\n"
            f"  1. Save your data locally or to a volume\n"
            f"  2. Pass the file path as a string argument\n"
            f"  3. Load the data inside your function\n"
            f"\n"
            f"Example patterns:\n"
            f"  # NumPy: np.save('/tmp/data.npy', array)\n"
            f"  # Pandas: df.to_parquet('/tmp/data.parquet')\n"
            f"  # PyTorch: torch.save(model.state_dict(), '/tmp/model.pt')\n"
            f"  # Pickle: pickle.dump(obj, open('/tmp/object.pkl', 'wb'))\n"
        )

    def _build_task_config(self, command: str) -> TaskConfig:
        """Build TaskConfig from decorator parameters.

        Translates the decorator arguments into a TaskConfig object,
        handling resource specifications, volume mounts, and other
        configuration options.

        Args:
            command: Python command to execute.

        Returns:
            Configured TaskConfig ready for submission.
        """
        # Parse resource requirements
        instance_type = None
        min_gpu_memory_gb = None

        if self.gpu:
            instance_type = self.gpu

        # For now, CPU and memory constraints are stored but not used
        # TaskConfig doesn't support these fields yet
        # They could be used in future for instance selection logic

        if self.memory and not self.gpu:
            # Only use memory for GPU selection if no explicit GPU specified
            if isinstance(self.memory, tuple):
                min_gpu_memory_gb = self.memory[0] // 1024  # Convert MB to GB
            else:
                min_gpu_memory_gb = self.memory // 1024

        # Merge environment variables from secrets
        env = self.environment.copy()
        for secret in self.secrets:
            secret_env = secret.to_env_dict()
            # Check for conflicts
            for key in secret_env:
                if key in env and env[key] != secret_env[key]:
                    raise ValueError(
                        f"Environment variable '{key}' is set both directly "
                        f"and by secret '{secret.name}'. Remove the direct "
                        f"setting to use the secret."
                    )
            env.update(secret_env)

        config_dict = {
            "name": f"{self.func_name}-remote",
            "command": ["python", "-c", command],
            "image": self.image,
            "env": env,
            **self.kwargs,
        }

        if instance_type:
            config_dict["instance_type"] = instance_type
        if min_gpu_memory_gb:
            config_dict["min_gpu_memory_gb"] = min_gpu_memory_gb

        if self.volumes:
            volume_specs = []
            for mount_path, volume_ref in self.volumes.items():
                if isinstance(volume_ref, str):
                    volume_specs.append({"name": volume_ref, "mount_path": mount_path})
                elif isinstance(volume_ref, dict):
                    volume_spec = volume_ref.copy()
                    volume_spec["mount_path"] = mount_path
                    volume_specs.append(volume_spec)
            config_dict["volumes"] = volume_specs

        # Map timeout (seconds) to TaskConfig.max_run_time_hours if provided
        if self.timeout and self.timeout > 0:
            try:
                config_dict["max_run_time_hours"] = float(self.timeout) / 3600.0
            except Exception:
                # Ignore invalid values silently; validation will happen downstream if needed
                pass

        return TaskConfig(**config_dict)

    def _extract_result(self, task) -> Any:
        """Extract result from completed task.

        Retrieves and deserializes the function's return value from the
        completed task using SSH to fetch the result file.

        Args:
            task: Completed Task object.

        Returns:
            The function's return value.

        Raises:
            FlowError: If result cannot be retrieved or function failed.
        """
        # Use the Task.result() method to fetch results
        return task.result()


class FlowApp(Flow):
    """Flow client extended with decorator support.

    Provides a decorator-based interface for configuring remote function
    execution. This class extends the base Flow client with the @function
    decorator pattern for users who prefer declarative configuration.

    Example:
        >>> from flow import FlowApp
        >>>
        >>> app = FlowApp()
        >>>
        >>> @app.function(gpu="a100")
        >>> def compute(n: int) -> int:
        ...     return n ** 2
        >>>
        >>> result = compute.remote(10)  # Runs on GPU
        >>> local = compute(10)          # Runs locally
    """

    def function(
        self,
        gpu: Optional[str] = None,
        cpu: Optional[Union[float, tuple[float, float]]] = None,
        memory: Optional[Union[int, tuple[int, int]]] = None,
        image: Optional[str] = None,
        retries: Union[int, Retries] = 0,
        timeout: Optional[int] = None,
        volumes: Optional[Dict[str, Any]] = None,
        environment: Optional[Dict[str, str]] = None,
        env: Optional[Dict[str, str]] = None,  # Allow both env and environment
        secrets: Optional[List[Secret]] = None,
        **kwargs,
    ) -> Callable[[Callable[P, R]], RemoteFunction[P, R]]:
        """Decorator to create a remote function.

        Configures a function for remote execution with specified resources.
        The decorated function can be called normally for local execution
        or via .remote() for GPU execution.

        Args:
            gpu: GPU specification. Examples:
                - "a100": Single A100 GPU
                - "h100:4": Four H100 GPUs
                - "l40s:8": Eight L40S GPUs
            cpu: CPU cores. Either a float for cores or (request, limit) tuple.
            memory: Memory in MB. Either an int or (request, limit) tuple.
            image: Docker image name. Defaults to "python:3.11".
            retries: Retry configuration. Either an int for simple retries
                or a Retries object for advanced configuration.
            timeout: Maximum execution time in seconds.
            volumes: Volume mount specifications. Dict mapping mount paths to
                volume references. Example: {"/data": "training-data"}.
            environment: Environment variables for execution context.
            secrets: List of Secret objects for secure credential injection.
                Example: [Secret.from_name("api-key"), Secret.from_env("TOKEN")]
            **kwargs: Additional TaskConfig parameters.

        Returns:
            Decorator function that wraps the target function.

        Example:
            Simple GPU function::

                @app.function(gpu="a100")
                def inference(text: str) -> dict:
                    # Run inference
                    return {"sentiment": "positive"}

            Multi-GPU with resources::

                @app.function(
                    gpu="h100:8",
                    cpu=32.0,
                    memory=131072,  # 128GB
                    image="nvcr.io/nvidia/pytorch:23.10-py3",
                    volumes={
                        "/data": "imagenet",
                        "/models": "model-cache",
                    },
                    environment={
                        "NCCL_DEBUG": "INFO",
                        "CUDA_VISIBLE_DEVICES": "0,1,2,3,4,5,6,7"
                    },
                )
                def train_large_model(config_path: str) -> dict:
                    # Distributed training logic
                    return {"final_loss": 0.023}

            Resource limits::

                @app.function(
                    cpu=(4.0, 8.0),      # Request 4, limit 8 cores
                    memory=(16384, 32768),  # Request 16GB, limit 32GB
                )
                def cpu_intensive(data: list) -> list:
                    # CPU-bound processing
                    return processed_data
        """

        def decorator(func: Callable[P, R]) -> RemoteFunction[P, R]:
            # Use env if provided, otherwise use environment
            actual_env = env if env is not None else environment
            return RemoteFunction(
                func=func,
                flow_client=self,
                gpu=gpu,
                cpu=cpu,
                memory=memory,
                image=image,
                retries=retries,
                timeout=timeout,
                volumes=volumes,
                environment=actual_env,
                secrets=secrets,
                **kwargs,
            )

        return decorator


# Create a default app instance for convenience
# Lazy initialization to avoid auth checks during import
import threading

_app = None
_app_lock = threading.Lock()


def _get_app():
    """Get or create the default app instance (thread-safe)."""
    global _app
    if _app is None:
        with _app_lock:
            # Double-check pattern
            if _app is None:
                _app = FlowApp()
    return _app


class _LazyApp:
    """Lazy proxy for FlowApp that initializes on first use.

    This proxy ensures that FlowApp is only instantiated when actually used,
    preventing authentication checks during module import.
    """

    def __getattr__(self, name):
        """Delegate attribute access to the actual FlowApp instance."""
        return getattr(_get_app(), name)

    def __call__(self):
        """Allow calling app() to get the actual FlowApp instance."""
        return _get_app()

    def __repr__(self):
        """Represent as the underlying FlowApp for debugging."""
        return repr(_get_app())


# Create singleton instances for module-level use
app = _LazyApp()
function = lambda *args, **kwargs: _get_app().function(*args, **kwargs)
