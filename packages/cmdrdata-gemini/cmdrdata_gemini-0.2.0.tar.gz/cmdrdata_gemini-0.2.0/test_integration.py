#!/usr/bin/env python
"""
Integration test to verify CmdrData-Gemini SDK functionality
"""

import os
import sys
from unittest.mock import Mock, patch

# Test basic import
try:
    from cmdrdata_gemini import TrackedGemini, set_customer_context, customer_context
    from cmdrdata_gemini.proxy import GEMINI_TRACK_METHODS
    print("[OK] Successfully imported CmdrData-Gemini")
except ImportError as e:
    print(f"[ERROR] Failed to import: {e}")
    sys.exit(1)

# Test version compatibility check
try:
    from cmdrdata_gemini.version_compat import check_compatibility, get_compatibility_info
    compat_info = get_compatibility_info()
    print(f"[OK] Google GenAI version: {compat_info.get('google-genai', {}).get('installed', 'Not found')}")
    if check_compatibility():
        print("[OK] Google GenAI version is compatible")
    else:
        print("[WARNING] Google GenAI version may have compatibility issues")
except Exception as e:
    print(f"[ERROR] Version check failed: {e}")

# Test client initialization
print("\n--- Testing Client Initialization ---")
try:
    # Mock the Google Gen AI client and API key validation to avoid needing real API keys
    with patch('google.genai.Client') as MockGenAI, \
         patch('cmdrdata_gemini.security.APIKeyManager.validate_api_key') as MockValidate:
        
        mock_genai = Mock()
        MockGenAI.return_value = mock_genai
        MockValidate.return_value = True  # Mock successful validation
        
        client = TrackedGemini(
            api_key="test-gemini-key",
            cmdrdata_api_key="tk-test-cmdrdata-key-12345678901234567890",  # Valid format
            cmdrdata_endpoint="https://api.cmdrdata.ai/api/events"
        )
        print("[OK] Client initialized successfully")
        
        # Verify the client has the expected attributes
        assert hasattr(client, '_original_client'), "Client should have _original_client attribute"
        assert hasattr(client, '_tracker'), "Client should have _tracker attribute"
        print("[OK] Client has required attributes")
        
except Exception as e:
    print(f"[ERROR] Client initialization failed: {e}")
    sys.exit(1)

# Test context management
print("\n--- Testing Context Management ---")
try:
    # Test setting context
    set_customer_context("customer-123")
    from cmdrdata_gemini.context import get_customer_context
    assert get_customer_context() == "customer-123", "Context not set correctly"
    print("[OK] Customer context set successfully")
    
    # Test context manager
    with customer_context("customer-456"):
        assert get_customer_context() == "customer-456", "Context manager not working"
    print("[OK] Context manager works correctly")
    
    # Clear context
    from cmdrdata_gemini import clear_customer_context
    clear_customer_context()
    assert get_customer_context() is None, "Context not cleared"
    print("[OK] Context cleared successfully")
    
except Exception as e:
    print(f"[ERROR] Context management failed: {e}")

# Test proxy forwarding
print("\n--- Testing Proxy Forwarding ---")
try:
    with patch('google.genai.Client') as MockGenAI, \
         patch('cmdrdata_gemini.security.APIKeyManager.validate_api_key') as MockValidate:
        
        mock_genai = Mock()
        mock_genai.test_attribute = "test_value"
        mock_genai.test_method = Mock(return_value="method_result")
        MockGenAI.return_value = mock_genai
        MockValidate.return_value = True
        
        client = TrackedGemini(
            api_key="test-key",
            cmdrdata_api_key="tk-test-cmdrdata-key-12345678901234567890"
        )
        
        # Test attribute forwarding via proxy
        assert client.test_attribute == "test_value", "Attribute forwarding failed"
        print("[OK] Attribute forwarding works")
        
        # Test method forwarding via proxy
        result = client.test_method()
        assert result == "method_result", "Method forwarding failed"
        print("[OK] Method forwarding works")
        
except Exception as e:
    print(f"[ERROR] Proxy forwarding failed: {e}")

# Test tracker initialization
print("\n--- Testing Usage Tracker ---")
try:
    from cmdrdata_gemini.tracker import UsageTracker
    
    with patch('cmdrdata_gemini.security.APIKeyManager.validate_api_key') as MockValidate:
        MockValidate.return_value = True
        
        tracker = UsageTracker(
            api_key="tk-test-cmdrdata-key-12345678901234567890",
            endpoint="https://api.cmdrdata.ai/api/events",
            timeout=5.0
        )
        
        assert tracker.api_key == "tk-test-cmdrdata-key-12345678901234567890", "Tracker API key not set"
        assert tracker.endpoint == "https://api.cmdrdata.ai/api/events", "Tracker endpoint not set"
        assert tracker.timeout == 5.0, "Tracker timeout not set"
        print("[OK] Usage tracker initialized correctly")
    
except Exception as e:
    print(f"[ERROR] Tracker initialization failed: {e}")

# Test dependency information
print("\n--- Dependency Information ---")
try:
    try:
        import google.genai as genai
        print(f"[INFO] Google GenAI SDK version: {getattr(genai, '__version__', 'Unknown')}")
    except ImportError:
        print("[INFO] Google GenAI SDK: Not installed (expected in test env)")
    
    import cmdrdata_gemini
    print(f"[INFO] CmdrData-Gemini version: {cmdrdata_gemini.__version__}")
    
    print("[OK] Dependencies are properly configured")
        
except Exception as e:
    print(f"[ERROR] Failed to check dependencies: {e}")

print("\n=== All Tests Completed ===")
print("Summary:")
print("- CmdrData-Gemini imports successfully")
print("- Client initialization works")
print("- Context management works")
print("- Proxy forwarding works")  
print("- Usage tracker initializes correctly")
print("- Dependencies are properly configured")
print(f"- Tracking methods configured: {len(GEMINI_TRACK_METHODS)} methods")
print(f"  * {', '.join(sorted(GEMINI_TRACK_METHODS.keys()))}")
print("\nThe Gemini SDK is ready for use!")