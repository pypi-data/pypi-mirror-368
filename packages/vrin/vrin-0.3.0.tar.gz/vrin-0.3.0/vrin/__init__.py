"""
VRIN Hybrid RAG SDK v0.3.0
Enterprise-grade Hybrid RAG SDK with multi-hop reasoning and cross-document synthesis.

Features:
- 🧠 Multi-hop reasoning across documents with strategic insights  
- 🔄 Cross-document synthesis and pattern recognition
- 🎯 User-customizable domain specialization (legal, finance, M&A, etc.)
- ⚡ Expert-level analysis comparable to industry professionals
- 📊 Advanced fact extraction with confidence scoring
- 🔍 Sub-3s query response times for complex reasoning
- 📈 Enterprise-ready with user isolation and authentication

Example usage:
    from vrin import VRINClient
    
    # Initialize client with API key
    client = VRINClient(api_key="your_vrin_api_key")
    
    # Specialize VRIN for M&A due diligence analysis
    result = client.specialize_for_due_diligence()
    print(f"✅ Specialized for due diligence: {result['message']}")
    
    # Insert complex M&A documents
    client.insert(
        content="TechCorp Financial Statement 2024: Revenue $250M (15% decline), $75M debt, cash flow dropped from $32M to $18M...",
        title="TechCorp Financial Statement",
        tags=["finance", "due-diligence"]
    )
    
    # Query with expert-level multi-hop reasoning
    response = client.query("What are the key financial risks in acquiring TechCorp for $180M?")
    print(f"🧠 Expert Analysis: {response['summary']}")
    print(f"⚡ Reasoning chains: {response.get('multi_hop_chains', 0)}")
    print(f"🔄 Cross-document patterns: {response.get('cross_document_patterns', 0)}")
    
    # Get your current specialization settings
    settings = client.get_specialization()
    print(f"Current focus: {settings['specialization']['reasoning_focus']}")
"""

from .client import VRINClient
from .models import Document, QueryResult, JobStatus
from .exceptions import VRINError, JobFailedError, TimeoutError

__version__ = "0.3.0"
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