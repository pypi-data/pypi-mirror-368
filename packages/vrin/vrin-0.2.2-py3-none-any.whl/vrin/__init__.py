"""
VRIN Hybrid RAG SDK v0.2.2
Enterprise-grade Hybrid RAG SDK with optimized knowledge graph traversal and vector search.

Features:
- ⚡ Optimized Hybrid RAG with graph + vector fusion
- 🧠 Intelligent entity extraction and graph traversal  
- 📊 Advanced fact extraction with confidence scoring
- 🔍 Sub-2s query response times
- 🎯 AI-powered natural language summaries
- 📈 Enterprise-ready with user isolation

Example usage:
    from vrin import VRINClient
    
    # Initialize client with API key
    client = VRINClient(api_key="your_vrin_api_key")
    
    # Insert knowledge with automatic fact extraction
    result = client.insert(
        content="Python is a programming language created by Guido van Rossum in 1991.",
        title="Python Facts",
        tags=["programming", "python"]
    )
    print(f"Extracted {result['facts_extracted']} facts")
    
    # Query with intelligent hybrid search
    response = client.query("Who created Python and when?")
    print(f"Answer: {response['summary']}")
    print(f"Found {response['total_facts']} facts in {response['search_time']}")
    
    # Get detailed results for advanced use
    details = client.get_raw_results("Python programming language")
    for fact in details['graph_facts']:
        print(f"Fact: {fact['subject']} {fact['predicate']} {fact['object']}")
"""

from .client import VRINClient
from .models import Document, QueryResult, JobStatus
from .exceptions import VRINError, JobFailedError, TimeoutError

__version__ = "0.2.2"
__author__ = "VRIN Team"
__email__ = "support@vrin.ai"

__all__ = [
    "VRINClient",
    "Document", 
    "QueryResult",
    "JobStatus",
    "VRINError",
    "JobFailedError",
    "TimeoutError"
] 