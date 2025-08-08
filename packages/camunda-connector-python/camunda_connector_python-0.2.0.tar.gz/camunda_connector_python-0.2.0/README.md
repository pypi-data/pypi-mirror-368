# Camunda Connector Python Library

A micro library for building Camunda connectors in Python using decorators. This library implements the Camunda Connector Server Protocol and allows you to create connectors with minimal boilerplate code.

## Features

- **Simple decorator-based API** - Define connectors using `@connector` decorators
- **Type-safe** - Uses Pydantic models for input/output validation
- **Auto-generated endpoints** - Automatically creates HTTP endpoints following the CSP protocol
- **Async support** - Supports both synchronous and asynchronous connector functions
- **Error handling** - Built-in error handling with proper JSON-RPC error responses
- **Callback support** - Handles asynchronous processing with callback URLs

## Installation

```bash
pip install camunda-connector-python
```

## Quick Start

Here's a simple example of creating a connector:

```python
from pydantic import BaseModel
from camunda_connector import connector, ConnectorServer, ConnectorInput, ConnectorOutput

# Define input and output models
class CalculatorInput(ConnectorInput):
    action: str  # "add", "subtract", "multiply", "divide"
    a: float
    b: float

class CalculatorOutput(ConnectorOutput):
    result: float
    action: str

# Define the connector
@connector(name="io.example:calculator:1")
def calculate(input_data: CalculatorInput) -> CalculatorOutput:
    actions = {
        "add": lambda a, b: a + b,
        "subtract": lambda a, b: a - b,
        "multiply": lambda a, b: a * b,
        "divide": lambda a, b: a / b if b != 0 else None
    }
    
    if input_data.action not in actions:
        raise ValueError(f"Unsupported action: {input_data.action}")
    
    result = actions[input_data.action](input_data.a, input_data.b)
    
    return CalculatorOutput(
        result=result,
        action=input_data.action
    )

# Create and run the server
if __name__ == "__main__":
    server = ConnectorServer(title="Calculator Connector", version="1.0.0")
    server.run(host="0.0.0.0", port=8080)
```

## Usage

### 1. Define Input/Output Models

Create Pydantic models that inherit from `ConnectorInput` and `ConnectorOutput`:

```python
from camunda_connector import ConnectorInput, ConnectorOutput

class MyConnectorInput(ConnectorInput):
    message: str
    count: int = 1

class MyConnectorOutput(ConnectorOutput):
    result: str
    processed_count: int
```

### 2. Create Connector Functions

Use the `@connector` decorator to register your connector functions:

```python
@connector(name="io.example:my-connector:1")
def my_connector(input_data: MyConnectorInput) -> MyConnectorOutput:
    # Your connector logic here
    result = f"Processed: {input_data.message}"
    return MyConnectorOutput(
        result=result,
        processed_count=input_data.count
    )
```

### 3. Async Connectors

You can also create asynchronous connectors:

```python
@connector(name="io.example:async-connector:1")
async def async_connector(input_data: MyConnectorInput) -> MyConnectorOutput:
    import asyncio
    await asyncio.sleep(1)  # Simulate async work
    
    return MyConnectorOutput(
        result="Async result",
        processed_count=input_data.count
    )
```

### 4. Run the Server

Create a `ConnectorServer` instance and run it:

```python
server = ConnectorServer(title="My Connectors", version="1.0.0")
server.run(host="0.0.0.0", port=8080)
```

## API Endpoints

The server automatically creates the following endpoints:

- `POST /csp/connector` - Invoke a connector (connector type specified in method parameter)
- `GET /csp/connectors` - List all registered connectors
- `GET /health` - Health check endpoint

## Making Requests

To invoke a connector, send a JSON-RPC request to the connector endpoint:

```bash
curl -X POST http://localhost:8080/csp/connector \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 12345,
    "method": "io.example:calculator:1",
    "params": {
      "input": {
        "action": "add",
        "a": 5,
        "b": 3
      }
    }
  }'
```

Response:
```json
{
  "jsonrpc": "2.0",
  "id": 12345,
  "result": {
    "output": {
      "result": 8.0,
      "action": "add"
    },
    "statusCode": 200,
    "error": null
  }
}
```

## Error Handling

The library provides built-in error handling. You can raise `ConnectorError` for custom errors:

```python
from camunda_connector import ConnectorError

@connector(name="io.example:validator:1")
def validate_data(input_data: MyInput) -> MyOutput:
    if not input_data.message:
        raise ConnectorError(
            message="Message cannot be empty",
            code=-32602,
            data={"field": "message"}
        )
    # ... rest of the logic
```

## Asynchronous Processing

For long-running operations, you can use asynchronous processing with callbacks:

```python
@connector(name="io.example:long-task:1")
def long_running_task(input_data: MyInput) -> MyOutput:
    # The framework will automatically handle the callback
    # if a callbackUrl is provided in the request
    import time
    time.sleep(10)  # Simulate long work
    
    return MyOutput(result="Task completed")
```

When a `callbackUrl` is provided in the request, the connector will:
1. Return a 202 Accepted response immediately
2. Process the connector function
3. Send the result to the callback URL when complete

---

# Connector Server Protocol

Connector Server Protocol is a JSON RPC protocol that allows the Camunda Connector runtime to 
invoke external connectors. It is designed to be used with the Camunda Connector runtime,
and offers the benefit of abstracting the underlying Zeebe API and job worker context, while
still allowing to use the classic variable binding and secret resolution features of the
Camunda Connector runtime.

An external connector is an HTTP server that implements the Connector Server Protocol.

## Connector endpoint URL

The URL of the connector endpoint should follow the standardized format:

```
https://<host>:<port>/csp/connector
```

Where `<host>` is the hostname or IP address of the connector server, and `<port>` is the port on which the connector server is listening.

## Request object

```json
{
  "jsonrpc": "2.0",
  "id": 99999999,
  "method": "io.camunda:connector-type:1",
  "params": {
    "input": {
      "key1": "value1",
      "key2": "value2"
    },
    "callbackUrl": "https://bru-2.connectors.camunda.io/csp/callback"
  }
}
```

## Response object

```json
{
  "jsonrpc": "2.0",
  "id": 99999999,
  "result": {
    "output": {
      "key1": "value1",
      "key2": "value2"
    },
    "statusCode": 200,
    "error": null
  }
}
```

### Synchronous response

The connector can respond synchronously by returning a response object with the `result` field and
the `statusCode` field set to 200 OK.

### Asynchronous response

The connector can respond asynchronously by returning a 202 Accepted response. In this case, the
connector must issue a callback to the `callbackUrl` provided in the request with the `result`
object.

## Error response object

```json
{
  "jsonrpc": "2.0",
  "id": 99999999,
  "error": {
    "code": -32603,
    "message": "Internal error",
    "data": {
      "errorMessage": "Invalid input for connector type io.camunda:connector-type:1"
    }
  }
}
```
