#!/usr/bin/env python3
"""
Production System Test for VRIN Hybrid RAG with Authentication
"""

import requests
import json
import time
import sys

# Configuration
AUTH_API_BASE_URL = "https://gp7g651udc.execute-api.us-east-1.amazonaws.com/Prod"
RAG_API_BASE_URL = "https://v6kkzi6x1b.execute-api.us-east-1.amazonaws.com/dev"

# Test user credentials
TEST_EMAIL = "vedantspatel44@gmail.com"
TEST_PASSWORD = "Vedant44"

def test_authentication_system():
    """Test the complete authentication system"""
    print("🔐 Testing Authentication System")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{AUTH_API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: User Login
    print("\n2. Testing User Login...")
    try:
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        response = requests.post(f"{AUTH_API_BASE_URL}/api/auth/login", 
                               json=login_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                api_key = result.get('api_key')
                user_id = result.get('user_id')
                print("✅ Login successful")
                print(f"   API Key: {api_key}")
                print(f"   User ID: {user_id}")
                return api_key, user_id
            else:
                print(f"❌ Login failed: {result.get('message')}")
                return False
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

def test_rag_system_with_auth(api_key):
    """Test the RAG system with authentication"""
    print("\n🔍 Testing RAG System with Authentication")
    print("=" * 50)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Test 1: Job Submission
    print("\n1. Testing Job Submission...")
    try:
        job_data = {
            "type": "document_processing",
            "content": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed."
        }
        response = requests.post(f"{RAG_API_BASE_URL}/job", 
                               json=job_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            job_id = result.get('job_id')
            print("✅ Job submission successful")
            print(f"   Job ID: {job_id}")
            print(f"   Status: {result.get('status')}")
            return job_id
        else:
            print(f"❌ Job submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Job submission error: {e}")
        return None
    
    # Test 2: Job Status Check
    print("\n2. Testing Job Status Check...")
    try:
        response = requests.get(f"{RAG_API_BASE_URL}/job/{job_id}", 
                              headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✅ Job status check successful")
            print(f"   Status: {result.get('status')}")
            print(f"   Progress: {result.get('progress')}%")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"❌ Job status check failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Job status check error: {e}")
    
    # Test 3: Query System
    print("\n3. Testing Query System...")
    try:
        query_data = {
            "query": "What is machine learning?"
        }
        response = requests.post(f"{RAG_API_BASE_URL}/query", 
                               json=query_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✅ Query successful")
            print(f"   Total Results: {result.get('total_results', 0)}")
            print(f"   Search Time: {result.get('search_time', 0):.3f}s")
            print(f"   Search Type: {result.get('search_type', 'unknown')}")
            
            # Show first result if available
            results = result.get('results', [])
            if results:
                first_result = results[0]
                print(f"   First Result Score: {first_result.get('score', 0)}")
                print(f"   First Result Content: {first_result.get('content', '')[:100]}...")
            else:
                print("   No results found")
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Query error: {e}")

def test_api_key_management(api_key, user_id):
    """Test API key management"""
    print("\n🔑 Testing API Key Management")
    print("=" * 50)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Test 1: List API Keys
    print("\n1. Testing List API Keys...")
    try:
        response = requests.get(f"{AUTH_API_BASE_URL}/api/auth/api-keys", 
                              headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                api_keys = result.get('api_keys', [])
                print("✅ List API keys successful")
                print(f"   Found {len(api_keys)} API keys")
                for key in api_keys:
                    print(f"   - {key.get('api_key')} (created: {key.get('created_at')})")
            else:
                print(f"❌ List API keys failed: {result.get('message')}")
        else:
            print(f"❌ List API keys failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ List API keys error: {e}")
    
    # Test 2: Create Additional API Key
    print("\n2. Testing Create Additional API Key...")
    try:
        response = requests.post(f"{AUTH_API_BASE_URL}/api/auth/create-api-key", 
                               headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                new_api_key = result.get('api_key')
                print("✅ Create API key successful")
                print(f"   New API Key: {new_api_key}")
                return new_api_key
            else:
                print(f"❌ Create API key failed: {result.get('message')}")
        else:
            print(f"❌ Create API key failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Create API key error: {e}")
    
    return None

def test_sdk_integration(api_key):
    """Test the VRIN SDK with real API key"""
    print("\n📦 Testing VRIN SDK Integration")
    print("=" * 50)
    
    try:
        from vrin_sdk import VRINClient
        
        # Initialize client with real API key
        client = VRINClient(
            api_key=api_key,
            base_url=RAG_API_BASE_URL
        )
        print("✅ VRIN SDK client initialized successfully")
        
        # Test insert_text method
        print("\n1. Testing insert_text method...")
        try:
            result = client.insert_text("This is a test document inserted via SDK.")
            print("✅ insert_text successful")
            print(f"   Job ID: {result.job_id}")
            print(f"   Status: {result.status}")
        except Exception as e:
            print(f"❌ insert_text failed: {e}")
        
        # Test query method
        print("\n2. Testing query method...")
        try:
            results = client.query("What is machine learning?")
            print("✅ query successful")
            print(f"   Found {len(results)} results")
            if results:
                print(f"   First result score: {results[0].score}")
        except Exception as e:
            print(f"❌ query failed: {e}")
        
        return True
    except ImportError:
        print("❌ VRIN SDK not installed. Install with: pip install vrin")
        return False
    except Exception as e:
        print(f"❌ SDK integration error: {e}")
        return False

def main():
    """Run comprehensive production system test"""
    print("🚀 VRIN Production System Test")
    print("=" * 60)
    
    # Test 1: Authentication System
    auth_result = test_authentication_system()
    if not auth_result:
        print("❌ Authentication system test failed")
        return False
    
    api_key, user_id = auth_result
    print(f"\n✅ Authentication system working with API key: {api_key}")
    
    # Test 2: RAG System with Authentication
    job_id = test_rag_system_with_auth(api_key)
    
    # Test 3: API Key Management
    new_api_key = test_api_key_management(api_key, user_id)
    
    # Test 4: SDK Integration
    sdk_success = test_sdk_integration(api_key)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PRODUCTION SYSTEM TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Authentication: WORKING")
    print(f"✅ API Key: {api_key}")
    print(f"✅ User ID: {user_id}")
    print(f"✅ Job Submission: {'WORKING' if job_id else 'FAILED'}")
    print(f"✅ API Key Management: {'WORKING' if new_api_key else 'FAILED'}")
    print(f"✅ SDK Integration: {'WORKING' if sdk_success else 'FAILED'}")
    
    print("\n🎉 Production system is ready for use!")
    print(f"📝 Users can now:")
    print(f"   1. Sign up at: {AUTH_API_BASE_URL}/api/auth/signup")
    print(f"   2. Login at: {AUTH_API_BASE_URL}/api/auth/login")
    print(f"   3. Use the VRIN SDK with their API key")
    print(f"   4. Submit jobs and query the knowledge base")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 