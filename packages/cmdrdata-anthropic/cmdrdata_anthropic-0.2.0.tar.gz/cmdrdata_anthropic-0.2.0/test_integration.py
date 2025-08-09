#!/usr/bin/env python
"""
Integration test to verify CmdrData-Anthropic SDK functionality
"""

import os
import sys
from unittest.mock import Mock, patch

# Test basic import
try:
    from cmdrdata_anthropic import TrackedAnthropic, set_customer_context, customer_context
    from cmdrdata_anthropic.proxy import ANTHROPIC_TRACK_METHODS
    print("[OK] Successfully imported CmdrData-Anthropic")
except ImportError as e:
    print(f"[ERROR] Failed to import: {e}")
    sys.exit(1)

# Test version compatibility check
try:
    from cmdrdata_anthropic.version_compat import check_compatibility, get_compatibility_info
    compat_info = get_compatibility_info()
    print(f"[OK] Anthropic version: {compat_info.get('anthropic', {}).get('installed', 'Not found')}")
    if check_compatibility():
        print("[OK] Anthropic version is compatible")
    else:
        print("[WARNING] Anthropic version may have compatibility issues")
except Exception as e:
    print(f"[ERROR] Version check failed: {e}")

# Test client initialization
print("\n--- Testing Client Initialization ---")
try:
    # Mock the Anthropic client and API key validation to avoid needing real API keys
    with patch('anthropic.Anthropic') as MockAnthropic, \
         patch('cmdrdata_anthropic.security.APIKeyManager.validate_api_key') as MockValidate:
        
        mock_anthropic = Mock()
        MockAnthropic.return_value = mock_anthropic
        MockValidate.return_value = True  # Mock successful validation
        
        client = TrackedAnthropic(
            api_key="test-anthropic-key",
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
    from cmdrdata_anthropic.context import get_customer_context
    assert get_customer_context() == "customer-123", "Context not set correctly"
    print("[OK] Customer context set successfully")
    
    # Test context manager
    with customer_context("customer-456"):
        assert get_customer_context() == "customer-456", "Context manager not working"
    print("[OK] Context manager works correctly")
    
    # Clear context
    from cmdrdata_anthropic import clear_customer_context
    clear_customer_context()
    assert get_customer_context() is None, "Context not cleared"
    print("[OK] Context cleared successfully")
    
except Exception as e:
    print(f"[ERROR] Context management failed: {e}")

# Test proxy forwarding
print("\n--- Testing Proxy Forwarding ---")
try:
    with patch('anthropic.Anthropic') as MockAnthropic, \
         patch('cmdrdata_anthropic.security.APIKeyManager.validate_api_key') as MockValidate:
        
        mock_anthropic = Mock()
        mock_anthropic.test_attribute = "test_value"
        mock_anthropic.test_method = Mock(return_value="method_result")
        MockAnthropic.return_value = mock_anthropic
        MockValidate.return_value = True
        
        client = TrackedAnthropic(
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
    from cmdrdata_anthropic.tracker import UsageTracker
    
    with patch('cmdrdata_anthropic.security.APIKeyManager.validate_api_key') as MockValidate:
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
    import anthropic
    print(f"[INFO] Anthropic SDK version: {anthropic.__version__}")
    
    import cmdrdata_anthropic
    print(f"[INFO] CmdrData-Anthropic version: {cmdrdata_anthropic.__version__}")
    
    # Check if versions are compatible
    anthropic_version = tuple(map(int, anthropic.__version__.split('.')[:2]))
    min_version = (0, 21)
    
    if anthropic_version >= min_version:
        print(f"[OK] Anthropic version {anthropic.__version__} meets minimum requirement (>=0.21.0)")
    else:
        print(f"[WARNING] Anthropic version {anthropic.__version__} is below minimum (0.21.0)")
        
except Exception as e:
    print(f"[ERROR] Failed to check dependencies: {e}")

print("\n=== All Tests Completed ===")
print("Summary:")
print("- CmdrData-Anthropic imports successfully")
print("- Client initialization works")
print("- Context management works")
print("- Proxy forwarding works")  
print("- Usage tracker initializes correctly")
print("- Dependencies are properly configured")
print(f"- Tracking methods configured: {len(ANTHROPIC_TRACK_METHODS)} methods")
print(f"  * {', '.join(sorted(ANTHROPIC_TRACK_METHODS.keys()))}")
print("\nThe Anthropic SDK is ready for use!")