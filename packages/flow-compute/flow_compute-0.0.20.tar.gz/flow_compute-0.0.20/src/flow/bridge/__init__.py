"""Bridge module for exposing Flow SDK functionality to external processes.

JSON-based interface for external tools to interact with Flow
SDK components without reimplementing functionality.

Bridge Protocol:
- Input: JSON via stdin or command line args
- Output: JSON via stdout
- Errors: JSON error objects with type, message, and traceback
"""

import json
import sys
import traceback
from typing import Any, Dict, Optional, Type

from flow.bridge.adapters import ADAPTERS
from flow.bridge.base import BridgeAdapter
from flow.errors import FlowError


class BridgeProtocol:
    """Defines the bridge communication protocol."""

    REQUEST_SCHEMA = {
        "adapter": str,  # Name of the adapter (e.g., "config", "http", "mithril")
        "method": str,  # Method to call on the adapter
        "args": dict,  # Keyword arguments for the method
        "request_id": Optional[str],  # Optional request ID for correlation
    }

    RESPONSE_SCHEMA = {
        "success": bool,
        "data": Any,  # Response data if successful
        "error": Optional[dict[str, Any]],  # Error details if failed
        "request_id": Optional[str],  # Echo back request ID
    }

    ERROR_SCHEMA = {
        "type": str,  # Error class name
        "message": str,  # Error message
        "code": Optional[str],  # Error code if available
        "traceback": Optional[str],  # Full traceback for debugging
        "suggestions": Optional[list],  # Helpful suggestions from FlowError
    }


class Bridge:
    """Main bridge class that routes requests to appropriate adapters."""

    def __init__(self):
        """Initialize the bridge with all available adapters."""
        self.adapters = {}
        for name, adapter_class in ADAPTERS.items():
            self.adapters[name] = adapter_class()

    def process_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Process a bridge request and return response.

        Args:
            request: Request dictionary following REQUEST_SCHEMA

        Returns:
            Response dictionary following RESPONSE_SCHEMA
        """
        request_id = request.get("request_id")

        try:
            # Validate request
            adapter_name = request.get("adapter")
            method_name = request.get("method")
            args = request.get("args", {})

            if not adapter_name:
                raise ValueError("Missing required field: adapter")
            if not method_name:
                raise ValueError("Missing required field: method")

            # Get adapter
            adapter = self.adapters.get(adapter_name)
            if not adapter:
                raise ValueError(f"Unknown adapter: {adapter_name}")

            # Get method
            method = getattr(adapter, method_name, None)
            if not method or not callable(method):
                raise ValueError(f"Unknown method: {adapter_name}.{method_name}")

            # Call method
            result = method(**args)

            # Return success response
            return {
                "success": True,
                "data": result,
                "error": None,
                "request_id": request_id,
            }

        except Exception as e:
            # Return error response
            error_data = {
                "type": type(e).__name__,
                "message": str(e),
                "code": getattr(e, "error_code", None),
                "traceback": traceback.format_exc(),
            }

            # Add FlowError suggestions if available
            if isinstance(e, FlowError):
                error_data["suggestions"] = e.suggestions

            return {
                "success": False,
                "data": None,
                "error": error_data,
                "request_id": request_id,
            }


def main():
    """Main entry point for bridge CLI usage."""
    if len(sys.argv) < 2:
        # Read from stdin
        try:
            request = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            response = {
                "success": False,
                "data": None,
                "error": {
                    "type": "JSONDecodeError",
                    "message": f"Invalid JSON input: {e}",
                    "code": None,
                    "traceback": traceback.format_exc(),
                },
                "request_id": None,
            }
            print(json.dumps(response))
            sys.exit(1)
    else:
        # Parse from command line
        try:
            request = json.loads(sys.argv[1])
        except json.JSONDecodeError as e:
            response = {
                "success": False,
                "data": None,
                "error": {
                    "type": "JSONDecodeError",
                    "message": f"Invalid JSON argument: {e}",
                    "code": None,
                    "traceback": traceback.format_exc(),
                },
                "request_id": None,
            }
            print(json.dumps(response))
            sys.exit(1)

    # Process request
    bridge = Bridge()
    response = bridge.process_request(request)

    # Output response
    print(json.dumps(response, default=str))

    # Exit with appropriate code
    sys.exit(0 if response["success"] else 1)


if __name__ == "__main__":
    main()
