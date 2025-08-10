# SDK Wrapper Creation Guide

## Instructions for Creating Usage-Tracking SDK Wrappers for AI Providers

This guide documents the pattern for creating drop-in SDK replacements with automatic usage tracking, based on the successful implementation of cmdrdata-anthropic.

### 1. Project Structure

Create a package structure following this pattern:

```
cmdrdata-{provider}/
├── cmdrdata_{provider}/
│   ├── __init__.py          # Main exports and public API
│   ├── client.py            # Sync tracked client
│   ├── async_client.py      # Async tracked client  
│   ├── proxy.py             # Dynamic proxy for method interception
│   ├── tracker.py           # Usage tracking logic
│   ├── context.py           # Customer context management
│   ├── exceptions.py        # Custom exceptions
│   ├── security.py          # API key validation
│   ├── logging_config.py    # Structured logging
│   ├── performance.py       # Performance monitoring
│   └── version_compat.py    # SDK version compatibility
├── tests/
│   ├── conftest.py          # Test fixtures and constants
│   ├── test_client.py       # Sync client tests
│   ├── test_async_client.py # Async client tests
│   ├── test_proxy.py        # Proxy system tests
│   └── test_*.py           # Other test files
└── pyproject.toml           # Project configuration
```

### 2. Key Implementation Components

#### Core Proxy Pattern (`proxy.py`)

The dynamic proxy system is the heart of transparent tracking:

```python
class TrackedProxy:
    def __init__(self, client, tracker, track_methods=None):
        object.__setattr__(self, "_client", client)
        object.__setattr__(self, "_tracker", tracker)
        object.__setattr__(self, "_track_methods", track_methods or {})
        object.__setattr__(self, "_tracked_attributes", {})

    def __getattr__(self, name: str):
        # Check cache first
        if name in self._tracked_attributes:
            return self._tracked_attributes[name]

        # Get attribute from underlying client
        attr = getattr(self._client, name)

        # For tracked methods, wrap with tracking
        if callable(attr) and name in self._track_methods:
            wrapped_attr = self._wrap_method(attr, name)
            self._tracked_attributes[name] = wrapped_attr
            return wrapped_attr

        # For nested objects (like client.messages), create sub-proxies
        elif hasattr(attr, "__dict__"):
            sub_track_methods = {
                k[len(name) + 1:]: v
                for k, v in self._track_methods.items()
                if k.startswith(f"{name}.")
            }
            
            if sub_track_methods:
                wrapped_attr = TrackedProxy(attr, self._tracker, sub_track_methods)
                self._tracked_attributes[name] = wrapped_attr
                return wrapped_attr

        # Cache and return original attribute
        self._tracked_attributes[name] = attr
        return attr
```

#### Method Wrapping with Customer Context

```python
def _wrap_method(self, method, method_name):
    tracker_func = self._track_methods[method_name]
    
    def wrapped(*args, **kwargs):
        # Extract tracking parameters using sentinel values
        customer_id = kwargs.pop("customer_id", ...)
        track_usage = kwargs.pop("track_usage", True)
        
        # Call original method
        result = method(*args, **kwargs)
        
        # Track usage if enabled
        if track_usage:
            try:
                tracker_func(
                    result=result,
                    customer_id=customer_id,
                    tracker=self._tracker,
                    method_name=method_name,
                    args=args,
                    kwargs=kwargs,
                )
            except Exception as e:
                logger.warning(f"Failed to track usage for {method_name}: {e}")
        
        return result
    
    return wrapped
```

#### Client Implementation Pattern (`client.py`)

```python
class TrackedProvider:
    def __init__(self, api_key=None, cmdrdata_api_key=None, **kwargs):
        # Import provider SDK lazily for better error messages
        try:
            import provider_sdk
        except ImportError:
            raise ConfigurationError("Provider SDK not found. Please install it.")
        
        # Validate API keys
        if api_key:
            APIKeyManager.validate_api_key(api_key, "provider")
        if cmdrdata_api_key:
            APIKeyManager.validate_api_key(cmdrdata_api_key, "cmdrdata")
        
        # Initialize original client
        self._original_client = provider_sdk.Client(api_key=api_key, **kwargs)
        
        # Set up tracking
        self._tracker = None
        self._track_usage = track_usage and cmdrdata_api_key is not None
        
        if self._track_usage:
            self._tracker = UsageTracker(
                api_key=cmdrdata_api_key,
                endpoint=cmdrdata_endpoint,
            )
        
        self._tracked_attributes = {}

    def __getattr__(self, name):
        # Check cache
        if name in self._tracked_attributes:
            return self._tracked_attributes[name]
        
        # Get attribute from original client
        attr = getattr(self._original_client, name)
        
        # Wrap with tracking if needed
        if self._track_usage and self._tracker:
            relevant_track_methods = {
                k: v for k, v in PROVIDER_TRACK_METHODS.items()
                if k == name or k.startswith(f"{name}.")
            }
            
            if relevant_track_methods:
                # Strip prefixes for sub-proxies
                sub_track_methods = {}
                for k, v in relevant_track_methods.items():
                    if k == name:
                        sub_track_methods[k] = v
                    elif k.startswith(f"{name}."):
                        sub_key = k[len(name) + 1:]
                        sub_track_methods[sub_key] = v
                
                wrapped_attr = TrackedProxy(attr, self._tracker, sub_track_methods)
                self._tracked_attributes[name] = wrapped_attr
                return wrapped_attr
        
        # Cache and return
        self._tracked_attributes[name] = attr
        return attr
```

### 3. Provider-Specific Tracking Functions

Each provider needs custom tracking functions that extract usage data:

```python
def track_provider_method(result, customer_id, tracker, method_name, args, kwargs):
    """Track usage for provider-specific method"""
    try:
        effective_customer_id = get_effective_customer_id(customer_id)
        
        # Track even if customer_id is None (for analytics)
        if hasattr(result, "usage") and result.usage:
            tracker.track_usage_background(
                customer_id=effective_customer_id,
                model=getattr(result, "model", kwargs.get("model", "unknown")),
                input_tokens=result.usage.input_tokens,
                output_tokens=result.usage.output_tokens,
                provider="provider_name",
                metadata={
                    "response_id": getattr(result, "id", None),
                    # Add provider-specific metadata fields
                },
            )
    except Exception as e:
        logger.warning(f"Failed to extract usage data: {e}")

# Configuration mapping
PROVIDER_TRACK_METHODS = {
    "endpoint.method": track_provider_method,
    "nested.endpoint.method": track_provider_method,
}
```

### 4. Test Suite Patterns

#### Test Configuration (`conftest.py`)

```python
import pytest
from unittest.mock import Mock

# Provider-specific API key patterns
VALID_PROVIDER_KEY = "prefix-" + "a" * required_length
VALID_CMDRDATA_KEY = "tk-" + "b" * 32

@pytest.fixture
def mock_provider_response():
    response = Mock()
    response.id = "resp_123"
    response.model = "provider-model"
    
    # Mock usage information - adjust to provider format
    response.usage = Mock()
    response.usage.input_tokens = 10
    response.usage.output_tokens = 20
    
    # Add provider-specific response attributes
    return response
```

#### Core Test Patterns

1. **Client Initialization Tests**: Test various initialization scenarios
2. **Proxy Forwarding Tests**: Verify transparent API forwarding
3. **Tracking Integration Tests**: Test usage tracking works correctly
4. **Error Handling Tests**: Ensure tracking failures don't break API calls
5. **Context Management Tests**: Test customer context propagation

### 5. Common Implementation Challenges and Solutions

#### API Key Validation
Research the provider's actual API key format and create proper validation:

```python
API_KEY_PATTERNS = {
    "provider": {
        "pattern": r"^prefix-[a-zA-Z0-9]{specific_length}$",
        "min_length": minimum_length,
        "description": "Provider API key format"
    }
}
```

#### Response Structure Differences
Each provider has different response formats. Study the actual SDK responses:

```python
# OpenAI format
response.usage.prompt_tokens
response.usage.completion_tokens

# Anthropic format  
response.usage.input_tokens
response.usage.output_tokens

# Other providers may use different field names
```

#### Async/Sync Consistency
Ensure both sync and async clients behave identically:

```python
# Sync client
class TrackedProvider:
    def _track_method(self, result, **kwargs):
        # Sync tracking logic
        pass

# Async client
class AsyncTrackedProvider:
    async def _track_method(self, result, **kwargs):
        # Async tracking logic (should be identical)
        pass
```

### 6. Testing Strategy

#### Initial Test Run Workflow
1. Run tests to identify failure categories
2. Fix import/naming issues first (usually global search/replace)
3. Address API key validation failures
4. Fix async configuration issues
5. Debug proxy/tracking integration
6. Update test expectations for new tracking behavior

#### Key Test Commands
```bash
# Full test suite
uv run --active python -m pytest

# Specific test file
uv run --active python -m pytest tests/test_client.py -v

# Minimal output for quick feedback
uv run --active python -m pytest --tb=no -q

# Debug specific failing test
uv run --active python -m pytest path/to/test::TestClass::test_method -v -s
```

### 7. Provider-Specific Considerations

#### Authentication Methods
- **API Keys**: Most common (OpenAI, Anthropic)
- **OAuth**: Some enterprise providers
- **Custom Headers**: Provider-specific authentication

#### Usage Metrics Variations
- **Token Counting**: Different providers count differently
- **Request/Response IDs**: Various formats and field names
- **Metadata**: Provider-specific response fields

#### SDK Architecture Differences
- **Async Patterns**: Some use asyncio, others use different patterns
- **Error Handling**: Provider-specific exception types
- **Client Structure**: Nested vs flat API organization

### 8. Debugging Tips

#### Common Failure Patterns
1. **Import Errors**: Wrong module names (use global search/replace)
2. **API Key Validation**: Test keys too short or wrong format
3. **Proxy Issues**: Method prefix stripping problems
4. **Context Issues**: Customer ID not propagating correctly
5. **Test Expectations**: Tests expecting different tracking behavior

#### Useful Debug Commands
```python
# Check proxy method resolution
print(dir(client.messages))

# Verify tracking configuration
print(PROVIDER_TRACK_METHODS)

# Test customer context
from cmdrdata_provider.context import get_effective_customer_id
print(get_effective_customer_id(None))
```

### 9. Performance Considerations

- **Attribute Caching**: Cache wrapped attributes to avoid re-wrapping
- **Lazy Loading**: Import provider SDKs only when needed
- **Background Tracking**: Use background threads for tracking to avoid blocking API calls
- **Error Resilience**: Never let tracking failures affect API functionality

### 10. Success Criteria

A successful SDK wrapper implementation should:

1. **Pass 100% of tests** without modification to the original provider SDK
2. **Maintain API compatibility** - existing code should work unchanged
3. **Track usage transparently** without affecting API performance
4. **Handle failures gracefully** - tracking errors don't break API calls
5. **Support both sync and async** patterns consistently
6. **Validate inputs properly** - catch configuration errors early

This pattern has been successfully implemented for both OpenAI and Anthropic SDKs and should adapt to any AI provider following similar architectural patterns.