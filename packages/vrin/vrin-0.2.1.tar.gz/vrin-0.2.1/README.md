# VRIN Hybrid RAG SDK v0.2.1

Optimized Hybrid RAG SDK with smart deduplication, enhanced fact extraction, and competitive performance.

## 🚀 New in v0.2.1 - Performance Optimizations

- 🎯 **Smart Deduplication** - Prevents duplicate facts and chunks, reduces storage by 40-60%
- ⚡ **Enhanced Performance** - Sub-3s queries with 7+ combined graph + vector results
- 🧠 **Improved Fact Quality** - 0.8+ confidence facts with self-updating system
- 💾 **Storage Optimization** - Only stores unique, fact-rich content
- 🔄 **Self-Improving** - Higher confidence facts automatically update existing ones
- 📊 **Competitive Edge** - Outperforms pure RAG and basic GraphRAG systems

## 🚀 Core Features

- ⚡ **Hybrid RAG Architecture** - Graph reasoning + Vector similarity search
- 🧠 **Intelligent Entity Matching** - AI-powered compound entity recognition
- 📊 **Advanced Fact Extraction** - High-confidence structured knowledge extraction
- 🔍 **Sub-3s Query Response** - Optimized retrieval with comprehensive coverage
- 🎯 **AI-Powered Summaries** - Natural language answers with cited sources
- 📈 **Enterprise-Ready** - User isolation, authentication, and production scaling

## 📦 Installation

```bash
pip install vrin
```

## 🔧 Quick Start

```python
from vrin import VRINClient

# Initialize with your API key
client = VRINClient(api_key="your_vrin_api_key")

# Insert knowledge with automatic fact extraction
result = client.insert(
    content="Python is a high-level programming language created by Guido van Rossum in 1991. It emphasizes code readability and supports multiple programming paradigms.",
    title="Python Programming Language",
    tags=["programming", "python", "language"]
)

print(f"✅ Extracted {result['facts_extracted']} facts")
# Output: ✅ Extracted 7 facts

# Query with intelligent hybrid search
response = client.query("Who created Python and when?")
print(f"📝 Answer: {response['summary']}")
print(f"⚡ Performance: {response['total_facts']} graph + {response['total_chunks']} vector = {response['combined_results']} results")
print(f"🔍 Query time: {response['search_time']}")

# Output: 
# 📝 Answer: Python was created by Guido van Rossum in 1991. It is a high-level programming language known for its simplicity and readability...
# ⚡ Performance: 4 graph + 5 vector = 9 results
# 🔍 Query time: 2.85s
```

## 🔍 Advanced Usage

### Storage Optimization Features
```python
# Insert content with optimization details
result = client.insert(content, title, tags)

print(f"🧠 Facts extracted: {result['facts_extracted']}")
print(f"💾 Storage optimization: {result['storage_optimization']}")
print(f"📦 Chunk stored: {result['chunk_stored']}")
print(f"⚡ Processing time: {result['processing_time']}")

# Check deduplication efficiency
storage = result['storage_result']
print(f"📈 New facts: {storage['stored_facts']}")
print(f"🔄 Updated facts: {storage['updated_facts']}")
print(f"⏭️ Skipped duplicates: {storage['skipped_duplicates']}")
print(f"💾 Efficiency: {storage['storage_efficiency']}")
```

### Raw Results Access
```python
# Get detailed graph facts and vector results
details = client.get_raw_results("Python programming language")

print("📊 Graph Facts:")
for fact in details['graph_facts']:
    confidence = fact['confidence']
    print(f"  • {fact['subject']} → {fact['predicate']} → {fact['object']} (confidence: {confidence:.2f})")

print(f"\n🔎 Vector Chunks: {len(details['vector_results'])}")
print(f"🧠 Entities Found: {details['entities_found']}")
```

### Knowledge Graph Visualization
```python
# Get knowledge graph data for visualization
graph = client.get_knowledge_graph()
print(f"📈 Graph: {len(graph['data']['nodes'])} nodes, {len(graph['data']['edges'])} edges")
```

### Batch Processing
```python
# Insert multiple documents efficiently
documents = [
    {"content": "Machine learning is a subset of AI...", "title": "ML Basics"},
    {"content": "Neural networks consist of layers...", "title": "Neural Networks"},
    {"content": "Deep learning uses multiple layers...", "title": "Deep Learning"}
]

for doc in documents:
    result = client.insert(doc['content'], doc['title'])
    print(f"Processed: {doc['title']} -> {result['facts_extracted']} facts")
```

## 🎯 API Reference

### VRINClient

#### `__init__(api_key: str)`
Initialize the VRIN client with your API key.

#### `insert(content: str, title: str = None, tags: List[str] = None) -> Dict`
Insert knowledge into the system with automatic fact extraction.

**Returns:**
- `success`: Whether the operation succeeded
- `facts_extracted`: Number of facts extracted
- `chunk_id`: Unique identifier for the content
- `message`: Status message

#### `query(query: str, include_summary: bool = True, include_raw_results: bool = False) -> Dict`
Query the knowledge base with optimized hybrid retrieval.

**Parameters:**
- `query`: Search query string
- `include_summary`: Include AI-generated summary (default: True)  
- `include_raw_results`: Include detailed graph facts and vector results

**Returns:**
- `success`: Whether the query succeeded
- `summary`: AI-generated comprehensive answer
- `search_time`: Query execution time
- `entities_found`: Extracted entities from the query
- `total_facts`: Number of graph facts found
- `total_chunks`: Number of vector chunks found

#### `get_raw_results(query: str) -> Dict`
Get complete raw results including graph facts and vector chunks.

#### `get_knowledge_graph() -> Dict`
Get knowledge graph visualization data with nodes and edges.

## 🔐 Authentication

1. Sign up at [VRIN Console](https://console.vrin.ai)
2. Create a new API key
3. Use the API key to initialize your client

```python
client = VRINClient(api_key="vrin_your_api_key_here")
```

## 🏗️ Architecture

VRIN uses a sophisticated Hybrid RAG architecture:

1. **Fact Extraction** - LLM-powered extraction of structured facts
2. **Graph Storage** - Facts stored as a knowledge graph in Neptune  
3. **Vector Storage** - Semantic embeddings in OpenSearch
4. **Hybrid Retrieval** - Combines graph traversal + vector similarity
5. **Result Fusion** - Intelligent ranking and result combination
6. **AI Summarization** - Natural language response generation

## 📊 Performance (v0.2.1 Optimized)

- **Fact Extraction**: 3-8 high-quality facts per insertion (0.8+ confidence)
- **Query Response**: Sub-3s with 7+ combined graph + vector results
- **Hybrid Coverage**: 2-5 graph facts + 3-5 vector chunks per query
- **Storage Efficiency**: 40-60% reduction through smart deduplication
- **Self-Improvement**: Facts automatically update with higher confidence versions
- **Competitive Advantage**: Outperforms single-method RAG systems

## 🛠️ Requirements

- Python 3.8+
- Active internet connection
- VRIN API key

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Support

- 📧 Email: support@vrin.ai
- 📚 Documentation: https://docs.vrin.ai
- 🐛 Issues: https://github.com/vrin-ai/vrin-sdk/issues

---

**Built with ❤️ by the VRIN Team**