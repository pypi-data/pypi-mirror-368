"""
Data models for the Nebula Client SDK
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


class RetrievalType(str, Enum):
    """Types of retrieval available"""
    BASIC = "basic"
    ADVANCED = "advanced"
    CUSTOM = "custom"


@dataclass
class Memory:
    """A memory stored in Nebula

    Exactly one of `content` or `chunks` will be populated by the SDK when
    creating a memory via `NebulaClient.store`:
    - If you sent raw `content`, you'll get `content` back
    - If you sent `chunks`, you'll get `chunks` back
    """

    id: str
    content: Optional[str] = None
    chunks: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    cluster_ids: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Memory":
        """Create a Memory from a dictionary"""
        created_at = None
        if data.get("created_at"):
            if isinstance(data["created_at"], str):
                created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            elif isinstance(data["created_at"], datetime):
                created_at = data["created_at"]

        updated_at = None
        if data.get("updated_at"):
            if isinstance(data["updated_at"], str):
                updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
            elif isinstance(data["updated_at"], datetime):
                updated_at = data["updated_at"]

        # Handle chunk response format (API returns chunks, not memories)
        memory_id = str(data.get("id", ""))
        
        # Prefer explicit chunks if present; otherwise map 'text'/'content' → content
        content: Optional[str] = data.get("content") or data.get("text")
        chunks: Optional[List[str]] = None
        if "chunks" in data and isinstance(data["chunks"], list):
            if all(isinstance(x, str) for x in data["chunks"]):
                chunks = data["chunks"]
            else:
                # Some APIs may return list of objects with a 'text' field
                extracted: List[str] = []
                for item in data["chunks"]:
                    if isinstance(item, dict) and "text" in item:
                        extracted.append(item["text"])  # type: ignore[index]
                chunks = extracted or None
        
        # API returns 'collection_ids', store as cluster_ids for user consistency
        metadata = data.get("metadata", {})
        cluster_ids = data.get("collection_ids", [])
        if data.get("document_id"):
            metadata["document_id"] = data["document_id"]
        
        # Handle document-based approach - if this is a document response
        if data.get("document_id") and not memory_id:
            memory_id = data["document_id"]
        
        # If we have document metadata, merge it
        if data.get("document_metadata"):
            metadata.update(data["document_metadata"])

        return cls(
            id=memory_id,
            content=content,
            chunks=chunks,
            metadata=metadata,
            cluster_ids=cluster_ids,
            created_at=created_at,
            updated_at=updated_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Memory to dictionary"""
        result = {
            "id": self.id,
            "content": self.content,
            "chunks": self.chunks,
            "metadata": self.metadata,
            "cluster_ids": self.cluster_ids,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        return result


@dataclass
class Cluster:
    """A cluster of memories in Nebula (alias for Collection)"""

    id: str
    name: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    memory_count: int = 0
    owner_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Cluster":
        """Create a Cluster from a dictionary"""
        created_at = None
        if data.get("created_at"):
            if isinstance(data["created_at"], str):
                created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            elif isinstance(data["created_at"], datetime):
                created_at = data["created_at"]

        updated_at = None
        if data.get("updated_at"):
            if isinstance(data["updated_at"], str):
                updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
            elif isinstance(data["updated_at"], datetime):
                updated_at = data["updated_at"]

        # Handle different field mappings from API response
        cluster_id = str(data.get("id", ""))  # Convert UUID to string
        cluster_name = data.get("name", "")
        cluster_description = data.get("description")
        cluster_owner_id = str(data.get("owner_id", "")) if data.get("owner_id") else None
        
        # Map API fields to SDK fields
        # API has document_count, SDK expects memory_count
        memory_count = data.get("document_count", 0)
        
        # Create metadata from API-specific fields
        metadata = {
            "graph_cluster_status": data.get("graph_cluster_status", ""),
            "graph_sync_status": data.get("graph_sync_status", ""),
            "user_count": data.get("user_count", 0),
            "document_count": data.get("document_count", 0)
        }

        return cls(
            id=cluster_id,
            name=cluster_name,
            description=cluster_description,
            metadata=metadata,
            created_at=created_at,
            updated_at=updated_at,
            memory_count=memory_count,
            owner_id=cluster_owner_id
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Cluster to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "memory_count": self.memory_count,
            "owner_id": self.owner_id,
        }


@dataclass
class SearchResult:
    """A search result from Nebula"""

    id: str
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResult":
        """Create a SearchResult from a dictionary"""
        # API returns 'text' field, SDK expects 'content'
        content = data.get("content") or data.get("text", "")
        
        # Handle chunk search results
        result_id = data.get("id") or data.get("chunk_id", "")
        
        return cls(
            id=result_id,
            content=content,
            score=data.get("score", 0.0),
            metadata=data.get("metadata", {}),
            source=data.get("source")
        )


@dataclass
class AgentResponse:
    """A response from an agent"""

    content: str
    agent_id: str
    conversation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    citations: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentResponse":
        """Create an AgentResponse from a dictionary"""
        return cls(
            content=data["content"],
            agent_id=data["agent_id"],
            conversation_id=data.get("conversation_id"),
            metadata=data.get("metadata", {}),
            citations=data.get("citations", [])
        )


@dataclass
class SearchOptions:
    """Options for search operations"""

    limit: int = 10
    filters: Optional[Dict[str, Any]] = None
    retrieval_type: RetrievalType = RetrievalType.ADVANCED


# @dataclass
# class AgentOptions:
#     """Options for agent operations"""
# 
#     model: str = "gpt-4"
#     temperature: float = 0.7
#     max_tokens: Optional[int] = None
#     retrieval_type: RetrievalType = RetrievalType.SIMPLE 