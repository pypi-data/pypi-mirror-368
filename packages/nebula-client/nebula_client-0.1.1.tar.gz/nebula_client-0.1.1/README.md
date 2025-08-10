# Nebula Client SDK

A Python SDK for interacting with the Nebula Cloud API, providing a clean interface to Nebula's memory and retrieval capabilities.

## Overview

This SDK has been updated to use the **documents endpoint** instead of the chunks endpoint for storing memories, following the pattern used in the R2R evaluation pipeline. This approach provides better support for conversational memory storage and collection management.

## Key Features

- **Document-based Memory Storage**: Uses the `/v3/documents` endpoint for storing memories as documents with chunks
- **Collection Management**: Full CRUD operations for collections (formerly clusters)
- **Conversational Memory**: Specialized methods for storing conversation data
- **Deduplication**: Deterministic document IDs based on content hashing
- **Flexible Metadata**: Rich metadata support for memories and collections
- **Search & Retrieval**: Advanced search capabilities with filtering and ranking

## Installation

```bash
pip install nebula-client
```

## Quick Start

### Basic Setup

```python
from nebula_client import NebulaClient

# Initialize client
client = NebulaClient(
    api_key="your-api-key",  # or set NEBULA_API_KEY env var
    base_url="https://api.nebulacloud.app"
)
```

### Collection Management

```python
# Create a collection
collection = client.create_collection(
    name="my_conversations",
    description="Collection for storing conversation memories"
)

# List collections
collections = client.list_collections()

# Get specific collection
collection = client.get_collection(collection_id)

# Update collection
updated_collection = client.update_collection(
    collection_id,
    name="updated_name",
    description="Updated description"
)

# Delete collection
client.delete_collection(collection_id)
```

### Storing Memories

#### Individual Memory

```python
# Store a single memory
memory = client.store(
    agent_id="my_agent",
    content="This is an important memory about machine learning.",
    metadata={"topic": "machine_learning", "importance": "high"},
    collection_id=collection.id,
    conversation_id="conv_123",
    timestamp="2024-01-15T10:30:00Z",
    speaker="user"
)
```

#### Conversation Storage

```python
# Store a conversation as multiple memories
conversation = [
    {
        "timestamp": "2024-01-15T10:30:00Z",
        "speaker": "user",
        "text": "What is machine learning?"
    },
    {
        "timestamp": "2024-01-15T10:30:05Z",
        "speaker": "assistant",
        "text": "Machine learning is a subset of AI that enables computers to learn from data."
    }
]

memories = client.store_conversation(
    agent_id="my_agent",
    conversation=conversation,
    metadata={"topic": "machine_learning", "conversation_type": "qa"},
    collection_id=collection.id,
    batch_size=2  # Store 2 messages per document
)
```

### Retrieving Memories

```python
# Retrieve relevant memories
results = client.retrieve(
    agent_id="my_agent",
    query="What is machine learning?",
    limit=5,
    collection_id=collection.id
)

for result in results:
    print(f"Content: {result.content}")
    print(f"Score: {result.score}")
```

### Chat with Memories

```python
# Chat with an agent using its memories
response = client.chat(
    agent_id="my_agent",
    message="Explain machine learning concepts",
    collection_id=collection.id,
    model="gpt-4o-mini",
    temperature=0.7
)

print(f"Response: {response.content}")
```

### Search Across All Memories

```python
# Search across all memories
results = client.search(
    query="artificial intelligence",
    limit=10,
    filters={"collection_ids": [collection.id]}
)

for result in results:
    print(f"Found: {result.content[:100]}...")
```

## API Reference

### Core Methods

#### Collection Management

- `create_collection(name, description=None, metadata=None)` - Create a new collection
- `get_collection(collection_id)` - Get collection details
- `list_collections(limit=100, offset=0)` - List all collections
- `update_collection(collection_id, name=None, description=None, metadata=None)` - Update collection
- `delete_collection(collection_id)` - Delete collection

#### Memory Storage

- `store(agent_id, content, metadata=None, collection_id=None, conversation_id=None, timestamp=None, speaker=None)` - Store individual memory
- `store_conversation(agent_id, conversation, metadata=None, collection_id=None, batch_size=100)` - Store conversation as memories
- `delete(memory_id)` - Delete a memory

#### Memory Retrieval

- `retrieve(agent_id, query, limit=10, retrieval_type=RetrievalType.SIMPLE, filters=None, collection_id=None)` - Retrieve relevant memories
- `get(memory_id)` - Get specific memory
- `list_agent_memories(agent_id, limit=100, offset=0)` - List all memories for an agent

#### Search & Chat

- `search(query, limit=10, filters=None)` - Search across all memories
- `chat(agent_id, message, conversation_id=None, model="gpt-4", temperature=0.7, max_tokens=None, retrieval_type=RetrievalType.SIMPLE, collection_id=None)` - Chat with agent

### Data Models

#### Memory

```python
@dataclass
class Memory:
    id: str
    agent_id: str
    content: str
    metadata: Dict[str, Any]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
```

#### Cluster (Collection)

```python
@dataclass
class Cluster:
    id: str
    name: str
    description: Optional[str]
    metadata: Dict[str, Any]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    memory_count: int
    owner_id: Optional[str]
```

#### SearchResult

```python
@dataclass
class SearchResult:
    id: str
    content: str
    score: float
    metadata: Dict[str, Any]
    source: Optional[str]
```

## Key Changes from Previous Version

### 1. Documents Endpoint Usage

The SDK now uses the `/v3/documents` endpoint instead of `/v3/chunks` for storing memories. This provides:

- Better support for conversational data
- Automatic chunking and embedding
- Integration with R2R's document processing pipeline
- Support for orchestration workflows

### 2. Collection-First Approach

Collections are now the primary organizational unit:

- Memories are stored within collections
- Search can be scoped to specific collections
- Better access control and organization

### 3. Conversational Memory Support

New `store_conversation()` method for storing conversation data:

- Batches messages into manageable documents
- Preserves conversation structure and metadata
- Handles deduplication automatically

### 4. Deterministic Document IDs

Documents are created with deterministic IDs based on content hashing:

- Prevents duplicate storage of identical content
- Enables idempotent operations
- Improves data consistency

## Testing

Run the test suite to verify functionality:

```bash
cd backend/nebula-r2r/py/sdk/nebula_client
python test_documents_endpoint.py
```

The test suite covers:
- Collection management
- Individual memory storage
- Conversation storage
- Memory retrieval
- Chat functionality
- Search capabilities

## Backward Compatibility

The SDK maintains backward compatibility with the following aliases:

- `create_cluster` → `create_collection`
- `get_cluster` → `get_collection`
- `list_clusters` → `list_collections`
- `update_cluster` → `update_collection`
- `delete_cluster` → `delete_collection`
- `add_memory_to_cluster` → `add_memory_to_collection`
- `remove_memory_from_cluster` → `remove_memory_from_collection`
- `get_cluster_memories` → `get_collection_memories`

## Error Handling

The SDK provides comprehensive error handling:

```python
from nebula_client.exceptions import (
    NebulaException,
    NebulaClientException,
    NebulaAuthenticationException,
    NebulaRateLimitException,
    NebulaValidationException,
)

try:
    memory = client.store(agent_id="test", content="test")
except NebulaAuthenticationException:
    print("Invalid API key")
except NebulaRateLimitException:
    print("Rate limit exceeded")
except NebulaValidationException as e:
    print(f"Validation error: {e}")
except NebulaException as e:
    print(f"API error: {e}")
```

## Best Practices

1. **Use Collections for Organization**: Group related memories in collections
2. **Leverage Metadata**: Add rich metadata to improve search and filtering
3. **Handle Deduplication**: The SDK handles deduplication automatically
4. **Batch Conversations**: Use `store_conversation()` for multi-turn conversations
5. **Monitor Rate Limits**: Handle rate limit exceptions gracefully
6. **Use Appropriate Models**: Choose the right model for your chat use case

## Examples

See the `test_documents_endpoint.py` file for comprehensive examples of all SDK functionality. 