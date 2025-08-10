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
    
    # Specialize VRIN with your custom prompt engineering
    custom_prompt = '''You are an expert M&A legal advisor with 20+ years of experience in billion-dollar acquisitions. When analyzing documents, focus on:
    
    1. Hidden legal risks and regulatory exposures
    2. Cross-document synthesis of financial and legal liabilities  
    3. Strategic valuation adjustments based on risk factors
    4. Deal structure recommendations to protect buyer interests
    
    Always provide quantified risk assessments and specific legal recommendations
    that only a top-tier M&A team would identify.'''
    
    result = client.specialize(custom_prompt, analysis_depth="expert")
    print(f"✅ Specialized VRIN: {result.get('message', 'Ready')}")
    
    # Insert complex M&A documents
    client.insert(
        content="TechCorp Financial Statement 2024: Revenue $250M (15% decline), $75M debt...",
        title="TechCorp Financial Statement"
    )
    
    # Query with expert-level multi-hop reasoning  
    response = client.query("What are the key financial risks in acquiring TechCorp for $180M?")
    print(f"🧠 Expert Analysis: {response['summary']}")
    print(f"⚡ Reasoning chains: {response.get('multi_hop_chains', 0)}")
    print(f"🔄 Cross-document patterns: {response.get('cross_document_patterns', 0)}")
    
    # Get your current specialization
    settings = client.get_specialization()
    if settings.get('success'):
        spec = settings.get('specialization', {})
        print(f"Custom prompt active: {'Yes' if spec.get('custom_prompts') else 'No'}")
"""

from .client import VRINClient
from .models import Document, QueryResult, JobStatus
from .exceptions import VRINError, JobFailedError, TimeoutError

__version__ = "0.3.2"
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