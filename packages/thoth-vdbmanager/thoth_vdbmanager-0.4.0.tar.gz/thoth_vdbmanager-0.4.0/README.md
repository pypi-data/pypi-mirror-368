# Thoth Vector Database Manager v2.0

A high-performance, Haystack-based vector database manager with support for multiple backends and local embedding capabilities.

## 🤖 MCP Server Support

This project is configured with MCP (Model Context Protocol) servers for enhanced AI-assisted development:
- **Context7**: Enhanced context management
- **Serena**: IDE assistance and development support

See [docs/MCP_SETUP.md](docs/MCP_SETUP.md) for details.

## 🚀 Features

- **Multi-backend support**: Qdrant, Weaviate, Chroma, PostgreSQL pgvector, Milvus, Pinecone
- **Haystack integration**: Uses Haystack as an abstraction layer over vector stores
- **Local embeddings**: Uses open-source Sentence Transformers for local embedding generation
- **Memory optimization**: Lazy loading and efficient batch processing
- **API compatibility**: Maintains backward compatibility with existing ThothVectorStore API
- **Type safety**: Full type hints and Pydantic validation
- **Flexible deployment**: Multiple modes (memory, filesystem, server) for different use cases
- **Production-ready**: Comprehensive testing and robust error handling

## 📦 Installation

### 🚀 **Recommended: uv Package Manager**

This project now uses [uv](https://docs.astral.sh/uv/) for fast, reliable Python package management. Install uv first:

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### ⚠️ **IMPORTANT: Backend Compatibility**

**Weaviate and Milvus cannot be installed together** due to conflicting gRPC requirements. Choose one of the following installation options:

#### Option 1: Milvus Configuration (Recommended)

```bash
# Basic installation with Milvus support
uv add thoth-vdbmanager[milvus]

# All backends except Weaviate (includes Milvus)
uv add thoth-vdbmanager[all]
```

#### Option 2: Weaviate Configuration

```bash
# Basic installation with Weaviate support
uv add thoth-vdbmanager[weaviate]

# All backends except Milvus (includes Weaviate)
uv add thoth-vdbmanager[all-with-weaviate]
```

#### Option 3: Safe Backends Only

```bash
# No gRPC conflicts (Qdrant, Chroma, pgvector, Pinecone)
uv add thoth-vdbmanager[all-safe]

# Individual backends
uv add thoth-vdbmanager[qdrant]
uv add thoth-vdbmanager[chroma]
uv add thoth-vdbmanager[pgvector]
uv add thoth-vdbmanager[pinecone]
```

### 🔄 **Legacy pip Installation (Still Supported)**

If you prefer to use pip, all the above commands work by replacing `uv add` with `pip install`:

```bash
# Example with pip
pip install thoth-vdbmanager[all]
```

📖 **For detailed compatibility information, see [Backend Compatibility Guide](docs/BACKEND_COMPATIBILITY.md)**

## 🏗️ Architecture

The library is built on a clean architecture with:

- **Core**: Base interfaces and document types
- **Adapters**: Backend-specific implementations using Haystack
- **Factory**: Unified creation interface
- **Compatibility**: Legacy API support

## 🚀 Quick Start

### New API (Recommended)

```python
from vdbmanager import VectorStoreFactory, ColumnNameDocument, SqlDocument, HintDocument

# Create a vector store
store = VectorStoreFactory.create(
    backend="qdrant",
    collection="my_collection",
    host="localhost",
    port=6333
)

# Add documents
column_doc = ColumnNameDocument(
    table_name="users",
    column_name="email",
    original_column_name="user_email",
    column_description="User email address",
    value_description="Valid email format"
)

doc_id = store.add_column_description(column_doc)

# Search documents
results = store.search_similar(
    query="user email",
    doc_type="column_name",
    top_k=5
)
```

### Legacy API (Backward Compatible)

```python
from vdbmanager import ThothVectorStore

# Works exactly like before
store = ThothVectorStore(
    backend="qdrant",
    collection="my_collection",
    host="localhost",
    port=6333
)

# All existing methods work
doc_id = store.add_column_description(column_doc)
results = store.search_similar("user email", "column_name")
```

## 🔧 Configuration

### Qdrant
```python
store = VectorStoreFactory.create(
    backend="qdrant",
    collection="my_collection",
    host="localhost",
    port=6333,
    api_key="your-api-key",  # Optional
    embedding_dim=384,  # Optional
    hnsw_config={"m": 16, "ef_construct": 100}
)
```

### Weaviate (Production-Ready with Docker)

**Docker Setup (Recommended):**
```python
store = VectorStoreFactory.create(
    backend="weaviate",
    collection="MyCollection",
    url="http://localhost:8080",
    use_docker=True,
    docker_compose_file="docker-compose-weaviate.yml"
)
```

**Manual Configuration:**
```python
store = VectorStoreFactory.create(
    backend="weaviate",
    collection="MyCollection",
    url="http://localhost:8080",
    timeout=30,
    skip_init_checks=False,  # Set to True if gRPC issues
    api_key="your-api-key"  # Optional
)
```

> 📖 **See [Weaviate Configuration Guide](docs/WEAVIATE_CONFIGURATION.md) for detailed setup instructions**

### Chroma (Multiple Modes)

**Memory Mode (Recommended for Testing):**
```python
store = VectorStoreFactory.create(
    backend="chroma",
    collection="my_collection",
    mode="memory"  # Fast, isolated, no persistence
)
```

**Filesystem Mode:**
```python
store = VectorStoreFactory.create(
    backend="chroma",
    collection="my_collection",
    mode="filesystem",
    persist_path="./chroma_db"
)
```

**Server Mode (Production):**
```python
store = VectorStoreFactory.create(
    backend="chroma",
    collection="my_collection",
    mode="server",
    host="localhost",
    port=8000
)
```

> 📖 **See [Chroma Configuration Guide](docs/CHROMA_CONFIGURATION.md) for detailed setup instructions**

### PostgreSQL pgvector
```python
store = VectorStoreFactory.create(
    backend="pgvector",
    collection="my_table",
    connection_string="postgresql://user:pass@localhost:5432/dbname"
)
```

### Milvus (Multiple Modes)

**Lite Mode (Recommended for Testing):**
```python
store = VectorStoreFactory.create(
    backend="milvus",
    collection="my_collection",
    mode="lite",
    connection_uri="./milvus.db"  # File-based storage
)
```

**Server Mode (Production):**
```python
store = VectorStoreFactory.create(
    backend="milvus",
    collection="my_collection",
    mode="server",
    host="localhost",
    port=19530
)
```

> 📖 **See [Milvus Configuration Guide](docs/MILVUS_CONFIGURATION.md) for detailed setup instructions**

### Pinecone
```python
store = VectorStoreFactory.create(
    backend="pinecone",
    collection="my-index",
    api_key="your-api-key",
    environment="us-west1-gcp-free"
)
```

## 📊 Performance Optimizations

### Memory Usage
- **Lazy initialization**: Embedders and connections are initialized on first use
- **Singleton pattern**: Same configuration reuses existing instances
- **Batch processing**: Efficient bulk operations

### Performance Tuning
```python
# Optimize for specific use cases
store = VectorStoreFactory.create(
    backend="qdrant",
    collection="optimized",
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",  # 384-dim, fast
    hnsw_config={"m": 32, "ef_construct": 200}  # Better search quality
)
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific backend tests
pytest tests/test_qdrant.py -v

# Run with coverage
pytest --cov=vdbmanager tests/
```

## 📈 Migration Guide

### From v1.x to v2.x

#### Simple Migration
```python
# Old code (v1.x)
from vdbmanager import QdrantHaystackStore

store = QdrantHaystackStore(
    collection="my_docs",
    host="localhost",
    port=6333
)

# New code (v2.x) - fully compatible
from vdbmanager import QdrantHaystackStore  # Still works!

# Or use new API
from vdbmanager import VectorStoreFactory

store = VectorStoreFactory.create(
    backend="qdrant",
    collection="my_docs",
    host="localhost",
    port=6333
)
```

#### Advanced Migration
```python
# Old code
from vdbmanager import ThothVectorStore

# New code - same interface, better internals
from vdbmanager import ThothVectorStore  # Still works with warnings

# Recommended new approach
from vdbmanager import QdrantAdapter

store = QdrantAdapter(
    collection="my_docs",
    host="localhost",
    port=6333
)
```

## 🔍 API Reference

### Core Classes

#### VectorStoreFactory
```python
# Create store
store = VectorStoreFactory.create(backend, collection, **kwargs)

# From config
config = {"backend": "qdrant", "params": {...}}
store = VectorStoreFactory.from_config(config)

# List backends
backends = VectorStoreFactory.list_backends()
```

#### Document Types
- `ColumnNameDocument`: Column metadata
- `SqlDocument`: SQL examples
- `HintDocument`: General hints

### Methods
- `add_column_description(doc)`: Add column metadata
- `add_sql(doc)`: Add SQL example
- `add_hint(doc)`: Add hint
- `search_similar(query, doc_type, top_k=5, score_threshold=0.7)`: Semantic search
- `get_document(doc_id)`: Retrieve by ID
- `bulk_add_documents(docs)`: Batch insert
- `get_collection_info()`: Get stats

## 🐛 Troubleshooting

### Common Issues

#### Connection Errors
```python
# Check service availability
import requests
requests.get("http://localhost:6333")  # Qdrant
```

#### Memory Issues
```python
# Use smaller embedding model
store = VectorStoreFactory.create(
    backend="qdrant",
    collection="my_collection",
    embedding_model="sentence-transformers/all-MiniLM-L6-v2"  # 384-dim
)
```

#### Performance Issues
```python
# Tune HNSW parameters
store = VectorStoreFactory.create(
    backend="qdrant",
    collection="my_collection",
    hnsw_config={"m": 16, "ef_construct": 100}
)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## Directory structure
vdbmanager/
├── core/                    # Base interfaces and document types
│   ├── base.py             # Core document classes and interfaces
│   └── __init__.py
├── adapters/               # Backend-specific implementations
│   ├── haystack_adapter.py # Base Haystack adapter
│   ├── qdrant_adapter.py   # Qdrant implementation
│   ├── weaviate_adapter.py # Weaviate implementation
│   ├── chroma_adapter.py   # Chroma implementation
│   ├── pgvector_adapter.py # PostgreSQL pgvector
│   ├── milvus_adapter.py   # Milvus implementation
│   └── pinecone_adapter.py # Pinecone implementation
├── factory.py              # Unified creation interface
├── compat/                 # Legacy compatibility layer
│   ├── __init__.py
│   └── thoth_vector_store.py
└── __init__.py            # Public API exports


## NewAPI (reccomended)
from vdbmanager import VectorStoreFactory, ColumnNameDocument

### Create any backend
store = VectorStoreFactory.create(
    backend="qdrant",
    collection="my_docs",
    host="localhost",
    port=6333
)

### Use optimized methods
doc_id = store.add_column_description(column_doc)
results = store.search_similar("user email", "column_name")


## Old API (Fully compatible)
from vdbmanager import ThothVectorStore  # Works with warnings

### Existing code continues to work
store = ThothVectorStore(
    backend="qdrant",
    collection="my_docs",
    host="localhost",
    port=6333
)
