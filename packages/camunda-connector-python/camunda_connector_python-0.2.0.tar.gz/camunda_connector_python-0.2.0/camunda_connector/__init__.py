"""
Camunda Connector Python Library

A micro library for building Camunda connectors in Python using decorators.
"""

from .connector import ConnectorServer, connector
from .models import ConnectorError, ConnectorInput, ConnectorOutput

__version__ = "0.2.0"
__all__ = ["connector", "ConnectorServer", "ConnectorInput", "ConnectorOutput", "ConnectorError"]
