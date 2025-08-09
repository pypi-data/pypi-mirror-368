# Thoth Vector Database Manager v0.4.0

A high-performance, Haystack v2-based vector database manager with support for 4 production-ready backends and local embedding capabilities.

## 🤖 MCP Server Support

This project is configured with MCP (Model Context Protocol) servers for enhanced AI-assisted development:
- **Context7**: Enhanced context management
- **Serena**: IDE assistance and development support

See [docs/MCP_SETUP.md](docs/MCP_SETUP.md) for details.

## 🚀 Features

- **Multi-backend support**: Qdrant, Chroma, PostgreSQL pgvector, Milvus
- **Haystack v2 integration**: Uses haystack-ai v2.12.0+ as an abstraction layer over vector stores
- **Local embeddings**: Uses open-source Sentence Transformers for local embedding generation
- **Memory optimization**: Lazy loading and efficient batch processing
- **API compatibility**: Maintains backward compatibility with existing ThothVectorStore API
- **Type safety**: Full type hints and Pydantic validation
- **Flexible deployment**: Multiple modes (memory, filesystem, server) for different use cases
- **Production-ready**: Comprehensive testing and robust error handling
- **No dependency conflicts**: All 4 supported databases can be installed together

## 📦 Installation

### 🚀 **Recommended: uv Package Manager**

This project uses [uv](https://docs.astral.sh/uv/) for fast, reliable Python package management. Install uv first:

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### ✅ **No Dependency Conflicts**

Version 0.4.0 resolves all dependency conflicts! All 4 supported databases can now be installed together:

#### All Databases (Recommended)

```bash
# Install all supported backends (Qdrant, Chroma, PgVector, Milvus)
uv add thoth-vdbmanager[all]
```

#### Individual Backends

```bash
# Individual backend installation
uv add thoth-vdbmanager[qdrant]    # Qdrant support
uv add thoth-vdbmanager[chroma]    # Chroma support
uv add thoth-vdbmanager[pgvector]  # PostgreSQL pgvector support
uv add thoth-vdbmanager[milvus]    # Milvus support
```

#### Development Installation

```bash
# For development with all backends and testing tools
uv add thoth-vdbmanager[all,test,dev]
```

### 🔄 **pip Installation (Also Supported)**

If you prefer pip, all commands work by replacing `uv add` with `pip install`:

```bash
# Example with pip
pip install thoth-vdbmanager[all]
```

### 🔄 **Breaking Changes in v0.4.0**

- **Removed**: Weaviate and Pinecone support (no longer maintained)
- **Updated**: Now requires haystack-ai v2.12.0+ (not compatible with legacy haystack)
- **Improved**: All remaining databases work together without conflicts

## 🏗️ Architecture

The library is built on a clean architecture with:

- **Core**: Base interfaces and document types
- **Adapters**: Backend-specific implementations using Haystack
- **Factory**: Unified creation interface
- **Compatibility**: Legacy API support

## 🚀 Quick Start

### New API (Recommended)

```python
from thoth_vdbmanager import VectorStoreFactory, ColumnNameDocument, SqlDocument, EvidenceDocument

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

### Available Classes

```python
from thoth_vdbmanager import (
    VectorStoreFactory,      # Main factory for creating stores
    ColumnNameDocument,      # Column metadata documents
    SqlDocument,            # SQL example documents
    EvidenceDocument,       # Evidence/hint documents
    ThothType,              # Document type enumeration
    VectorStoreInterface    # Base interface for all stores
)
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

### From v0.3.x to v0.4.0

#### Breaking Changes
- **Removed databases**: Weaviate and Pinecone are no longer supported
- **Haystack version**: Now requires haystack-ai v2.12.0+ (not compatible with legacy haystack)
- **Dependencies**: All remaining databases can now be installed together without conflicts

#### Migration Steps

**1. Update installation:**
```bash
# Old installation (v0.3.x)
pip install thoth-vdbmanager[all-safe]  # Avoided conflicts

# New installation (v0.4.0)
pip install thoth-vdbmanager[all]  # No conflicts!
```

**2. Update code (if using removed databases):**
```python
# If you were using Weaviate - migrate to Qdrant or Chroma
# Old code (v0.3.x)
store = VectorStoreFactory.create(
    backend="weaviate",  # No longer supported
    collection="MyCollection",
    url="http://localhost:8080"
)

# New code (v0.4.0) - migrate to similar database
store = VectorStoreFactory.create(
    backend="qdrant",  # Recommended alternative
    collection="my_collection",
    host="localhost",
    port=6333
)
```

**3. Existing supported databases work unchanged:**
```python
# This code works exactly the same in v0.4.0
store = VectorStoreFactory.create(
    backend="qdrant",  # ✅ Still supported
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
- `EvidenceDocument`: General evidence/hints

### Methods
- `add_column_description(doc)`: Add column metadata
- `add_sql(doc)`: Add SQL example
- `add_evidence(doc)`: Add evidence/hint
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

## 📁 Directory Structure

```
thoth_vdbmanager/
├── vdbmanager/
│   ├── core/                    # Base interfaces and document types
│   │   ├── base.py             # Core document classes and interfaces
│   │   └── __init__.py
│   ├── adapters/               # Backend-specific implementations
│   │   ├── haystack_adapter.py # Base Haystack adapter
│   │   ├── qdrant_adapter.py   # Qdrant implementation
│   │   ├── chroma_adapter.py   # Chroma implementation
│   │   ├── pgvector_adapter.py # PostgreSQL pgvector
│   │   └── milvus_adapter.py   # Milvus implementation
│   ├── factory.py              # Unified creation interface
│   └── __init__.py            # Public API exports
├── test_e2e_vectordb/          # End-to-end tests
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## 🚀 Quick API Reference

### Main API

```python
from thoth_vdbmanager import VectorStoreFactory, ColumnNameDocument

# Create any backend
store = VectorStoreFactory.create(
    backend="qdrant",
    collection="my_docs",
    host="localhost",
    port=6333
)

# Use the methods
doc_id = store.add_column_description(column_doc)
results = store.search_similar("user email", "column_name")
```

---

**🎉 Ready to use with Haystack v2 and 4 production-ready vector databases!**
