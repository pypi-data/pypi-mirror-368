"""
Data models for Camunda Connector Python library
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class ConnectorInput(BaseModel):
    """Base class for connector input data"""

    pass


class ConnectorOutput(BaseModel):
    """Base class for connector output data"""

    pass


class ConnectorError(Exception):
    """Exception class for connector errors"""

    def __init__(self, message: str, code: int = -32603, data: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.data = data or {}
        super().__init__(message)


class JsonRpcRequest(BaseModel):
    """JSON-RPC request model"""

    jsonrpc: str = "2.0"
    id: int
    method: str
    params: Dict[str, Any]


class JsonRpcParams(BaseModel):
    """Parameters for connector invocation"""

    input: Dict[str, Any]
    callbackUrl: Optional[str] = None
    operation: Optional[str] = None


class JsonRpcResult(BaseModel):
    """Result data for successful responses"""

    output: Dict[str, Any]
    statusCode: int = 200
    error: Optional[str] = None


class JsonRpcErrorData(BaseModel):
    """Error data for JSON-RPC error responses"""

    code: int
    message: str
    data: Optional[Dict[str, Any]] = None


class JsonRpcResponse(BaseModel):
    """JSON-RPC response model"""

    jsonrpc: str = "2.0"
    id: int
    result: Optional[JsonRpcResult] = None
    error: Optional[JsonRpcErrorData] = None
