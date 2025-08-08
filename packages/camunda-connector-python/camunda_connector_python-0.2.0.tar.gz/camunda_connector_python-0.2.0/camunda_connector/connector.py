"""
Core connector decorator and server implementation
"""

import asyncio
import inspect
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, get_type_hints

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError

from .models import (
    ConnectorError,
    JsonRpcErrorData,
    JsonRpcParams,
    JsonRpcRequest,
    JsonRpcResponse,
    JsonRpcResult,
)


class ConnectorEntry:
    """Metadata for a registered connector"""

    def __init__(
        self,
        function: Callable,
        input_model: Type[BaseModel],
        output_model: Type[BaseModel],
        operation: Optional[str] = None,
    ) -> None:
        self.function = function
        self.input_model = input_model
        self.output_model = output_model
        self.operation = operation


class ConnectorRegistry:
    """Registry to store connector functions and their metadata"""

    def __init__(self) -> None:
        self.connectors: Dict[str, List[ConnectorEntry]] = {}

    def register(
        self,
        connector_type: str,
        operation: Optional[str],
        func: Callable,
        input_model: Type[BaseModel],
        output_model: Type[BaseModel],
    ) -> None:
        """Register a connector function"""
        metadata = ConnectorEntry(
            function=func, input_model=input_model, output_model=output_model, operation=operation
        )
        if connector_type not in self.connectors:
            self.connectors[connector_type] = []
        self.connectors[connector_type].append(metadata)

    def get_connector(
        self, connector_type: str, operation: Optional[str] = None
    ) -> Optional[ConnectorEntry]:
        """Get a registered connector by type"""
        connector_entry = self.connectors.get(connector_type)
        if not connector_entry:
            return None
        # If operation is specified, filter by operation
        if operation:
            for entry in connector_entry:
                if entry.operation == operation:
                    return entry
            return None
        # Return the first matching connector if no operation is specified
        return connector_entry[0]

    def list_connectors(self) -> Dict[str, str]:
        """List all registered connectors"""
        return {connector_type: connector_type for connector_type in self.connectors.keys()}


# Global registry instance
_registry = ConnectorRegistry()


def connector(name: str, operation: Optional[str] = None) -> Callable[[Callable], Callable]:
    """
    Decorator to register a function as a Camunda connector

    Args:
        name: The connector type name (e.g., "io.camunda:my-connector:1")

    Usage:
        @connector(name="io.camunda:my-connector:1")
        def my_connector(input_data: MyInputModel) -> MyOutputModel:
            # Connector logic here
            return MyOutputModel(result="success")
    """

    def decorator(func: Callable) -> Callable:
        # Get type hints to determine input and output models
        type_hints = get_type_hints(func)

        # Extract input and output types from function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.values())

        if len(params) != 1:
            raise ValueError(f"Connector function {func.__name__} must have exactly one parameter")

        input_param = params[0]
        input_model = type_hints.get(input_param.name)
        output_model = type_hints.get("return")

        if not input_model or not issubclass(input_model, BaseModel):
            raise ValueError(f"Input parameter must be a Pydantic BaseModel, got {input_model}")

        if not output_model or not issubclass(output_model, BaseModel):
            raise ValueError(f"Return type must be a Pydantic BaseModel, got {output_model}")

        # Register the connector
        _registry.register(name, operation, func, input_model, output_model)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        # Store metadata on the function
        setattr(wrapper, "_connector_name", name)
        setattr(wrapper, "_input_model", input_model)
        setattr(wrapper, "_output_model", output_model)

        return wrapper

    return decorator


class ConnectorServer:
    """
    FastAPI server for hosting Camunda connectors
    """

    def __init__(self, title: str = "Camunda Connector Server", version: str = "1.0.0"):
        self.app = FastAPI(title=title, version=version)
        self.setup_routes()

    def setup_routes(self) -> None:
        """Setup the connector routes"""

        @self.app.get("/health")
        async def health_check() -> Dict[str, str]:
            """Health check endpoint"""
            return {"status": "healthy"}

        @self.app.get("/csp/connectors")
        async def list_connectors() -> Dict[str, str]:
            """List all available connectors"""
            return _registry.list_connectors()

        @self.app.post("/csp/connector")
        async def invoke_connector(request: JsonRpcRequest) -> JsonRpcResponse:
            """Handle connector invocation requests"""
            try:
                # Use the method parameter as the connector type
                connector_type = request.method
                # Parse parameters
                params = JsonRpcParams(**request.params)

                # Find the connector
                connector_info = _registry.get_connector(connector_type, params.operation)
                if not connector_info:
                    raise HTTPException(
                        status_code=404, detail=f"Connector type not found: {connector_type}"
                    )

                # Parse input data using the connector's input model
                input_model = connector_info.input_model
                try:
                    input_data = input_model(**params.input)
                    print(input_data)
                except ValidationError as e:
                    raise ConnectorError(
                        f"Invalid input data: {str(e)}",
                        code=-32602,
                        data={"validationErrors": e.errors()},
                    )

                # Execute the connector function
                connector_func = connector_info.function

                # Handle asynchronous processing if callback URL is provided
                if params.callbackUrl:
                    # Return 202 Accepted immediately and process in background
                    asyncio.create_task(
                        self._execute_async_connector(
                            connector_func, input_data, params.callbackUrl, request.id
                        )
                    )
                    return JsonRpcResponse(
                        id=request.id, result=JsonRpcResult(output={}, statusCode=202)
                    )

                # Execute synchronously for non-async requests
                try:
                    print(f"Executing connector: {connector_type}, operation: {params.operation}")
                    print(f"Input data: {input_data}")
                    if asyncio.iscoroutinefunction(connector_func):
                        result = await connector_func(input_data)
                    else:
                        result = connector_func(input_data)
                except ConnectorError:
                    raise
                except Exception as e:
                    raise ConnectorError(f"Connector execution failed: {str(e)}", code=-32603)

                # Convert result to dict
                if isinstance(result, BaseModel):
                    output_data = result.model_dump()
                else:
                    output_data = result

                # Return synchronous response
                return JsonRpcResponse(id=request.id, result=JsonRpcResult(output=output_data))

            except ConnectorError as e:
                return JsonRpcResponse(
                    id=request.id,
                    error=JsonRpcErrorData(code=e.code, message=e.message, data=e.data),
                )
            except HTTPException:
                # Re-raise HTTPException to let FastAPI handle it properly
                raise
            except Exception as e:
                return JsonRpcResponse(
                    id=request.id,
                    error=JsonRpcErrorData(code=-32603, message=f"Internal error: {str(e)}"),
                )

    async def _execute_async_connector(
        self, connector_func: Callable, input_data: Any, callback_url: str, request_id: Any
    ) -> None:
        """Execute connector asynchronously and send result to callback URL"""
        try:
            # Execute the connector function
            if asyncio.iscoroutinefunction(connector_func):
                result = await connector_func(input_data)
            else:
                result = connector_func(input_data)

            # Convert result to dict
            if isinstance(result, BaseModel):
                output_data = result.model_dump()
            else:
                output_data = result

            # Send success callback
            callback_data = JsonRpcResponse(id=request_id, result=JsonRpcResult(output=output_data))

        except ConnectorError as e:
            # Send error callback
            callback_data = JsonRpcResponse(
                id=request_id, error=JsonRpcErrorData(code=e.code, message=e.message, data=e.data)
            )
        except Exception as e:
            # Send generic error callback
            callback_data = JsonRpcResponse(
                id=request_id,
                error=JsonRpcErrorData(
                    code=-32603, message=f"Connector execution failed: {str(e)}"
                ),
            )

        # Send callback
        try:
            async with httpx.AsyncClient() as client:
                await client.post(callback_url, json=callback_data.model_dump(), timeout=30.0)
        except Exception as e:
            # Log callback failure (in a real implementation, you'd use proper logging)
            print(f"Failed to send callback to {callback_url}: {e}")

    def run(self, host: str = "0.0.0.0", port: int = 8080, **kwargs: Any) -> None:
        """Run the connector server"""
        import uvicorn

        uvicorn.run(self.app, host=host, port=port, **kwargs)


def create_connector_server(
    title: str = "Camunda Connector Server", version: str = "1.0.0"
) -> ConnectorServer:
    """Create a new connector server instance"""
    return ConnectorServer(title=title, version=version)
