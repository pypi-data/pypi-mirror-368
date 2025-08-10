"""
Nebula Client SDK - A clean, intuitive SDK for Nebula Cloud API

This SDK provides a simplified interface to Nebula's memory and retrieval capabilities,
focusing on chunks and hiding the complexity of the underlying R2R system.
"""

from .client import NebulaClient
from .exceptions import (
    NebulaException, 
    NebulaClientException,
    NebulaAuthenticationException,
    NebulaRateLimitException,
    NebulaValidationException,
    NebulaClusterNotFoundException,
)
from .models import Memory, Cluster, SearchResult, RetrievalType, AgentResponse

__version__ = "0.1.2"
__all__ = [
    "NebulaClient",
    "NebulaException", 
    "NebulaClientException",
    "NebulaAuthenticationException",
    "NebulaRateLimitException",
    "NebulaValidationException",
    "NebulaClusterNotFoundException",
    "Memory",
    "Cluster",
    "SearchResult", 
    "RetrievalType",
    "AgentResponse",
] 