# Anthropic Dependency Management Guide

## How CmdrData-Anthropic Works With Your Anthropic Installation

### The Architecture
CmdrData-Anthropic is a **wrapper**, not a replacement. It works by:

1. **Importing** the official Anthropic SDK
2. **Wrapping** it with tracking capabilities  
3. **Forwarding** all calls transparently
4. **Tracking** usage without interfering

### Installation Scenarios

#### Scenario 1: You Already Have Anthropic Installed
```bash
# You have:
anthropic==0.57.1  # Your existing version

# Install CmdrData:
pip install cmdrdata-anthropic

# Result:
anthropic==0.57.1  # Keeps your version!
cmdrdata-anthropic==0.1.0  # Adds tracking
```

#### Scenario 2: Fresh Installation
```bash
# Install CmdrData:
pip install cmdrdata-anthropic

# Result:
anthropic==0.57.1  # Latest compatible version
cmdrdata-anthropic==0.1.0  # With tracking
```

#### Scenario 3: Specific Anthropic Version Required
```bash
# Install specific versions:
pip install anthropic==0.25.0 cmdrdata-anthropic

# Result:
anthropic==0.25.0  # Your specified version
cmdrdata-anthropic==0.1.0  # Works with it!
```

## Compatibility

### Supported Anthropic Versions
- **Minimum**: 0.21.0 (required for base features)
- **Maximum**: <1.0.0 (upper bound to avoid breaking changes)
- **Tested**: 0.21.0 - 0.57.1

### Version Checking
CmdrData-Anthropic checks compatibility at import:

```python
from cmdrdata_anthropic import TrackedAnthropic
# Automatically validates Anthropic version
# Warns if potential incompatibility detected
```

## Common Questions

### Q: Will CmdrData-Anthropic conflict with my Anthropic version?
**A: No!** CmdrData-Anthropic uses the Anthropic SDK you have installed. It doesn't replace or modify it.

### Q: Can I upgrade Anthropic independently?
**A: Yes, within the supported range!** You can upgrade Anthropic:
```bash
pip install --upgrade anthropic
# CmdrData-Anthropic continues working (if version is compatible)
```

### Q: What if I need a specific Anthropic version for another project?
**A: Use virtual environments:**
```bash
# Project A (newer Anthropic):
python -m venv projectA
source projectA/bin/activate
pip install anthropic==0.57.1 cmdrdata-anthropic

# Project B (older Anthropic):
python -m venv projectB  
source projectB/bin/activate
pip install anthropic==0.25.0 cmdrdata-anthropic
```

### Q: How do I check what versions I have?
```bash
pip list | grep -E "anthropic|cmdrdata"
# Shows both packages and versions
```

## Troubleshooting

### Import Error: Anthropic not found
```python
ConfigurationError: Anthropic SDK not found
```
**Solution**: Install Anthropic first:
```bash
pip install anthropic>=0.21.0
```

### Version Warning
```python
UserWarning: Anthropic SDK version X.X.X may not be fully supported
```
**Solution**: Update to supported version:
```bash
pip install "anthropic>=0.21.0,<1.0.0"
```

### Conflicting Dependencies
If you see dependency conflicts:
```bash
# Clean reinstall:
pip uninstall anthropic cmdrdata-anthropic
pip install cmdrdata-anthropic
```

## Best Practices

### 1. Use Virtual Environments
```bash
python -m venv myproject
source myproject/bin/activate
pip install cmdrdata-anthropic
```

### 2. Pin Versions in Production
```txt
# requirements.txt
anthropic==0.57.1
cmdrdata-anthropic==0.1.0
```

### 3. Test After Upgrades
```python
# Quick test after upgrading:
from cmdrdata_anthropic import TrackedAnthropic

client = TrackedAnthropic(
    api_key="ant-...",
    cmdrdata_api_key="tk-..."
)

# Test a simple call:
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=100,
    messages=[{"role": "user", "content": "test"}],
    customer_id="test-customer"
)
print("Integration working!")
```

## Technical Details

### Why Anthropic is a Dependency
1. **Simplicity**: One command installs everything
2. **Compatibility**: pip resolves versions automatically
3. **Maintenance**: We test against specific versions
4. **User Experience**: No manual dependency management

### How the Proxy Pattern Works
```python
# Simplified internal structure:
class TrackedAnthropic:
    def __init__(self, **kwargs):
        # Create real Anthropic client
        self._original_client = anthropic.Anthropic(**kwargs)
        
    def __getattr__(self, name):
        # Forward all calls to real client
        return getattr(self._original_client, name)
```

### Zero Overhead Design
- Tracking happens asynchronously
- Failures don't affect Anthropic calls
- No performance impact on API calls
- Thread-safe and production-ready

## Support

### Getting Help
- **GitHub Issues**: [Report problems](https://github.com/cmdrdata-ai/cmdrdata-anthropic/issues)
- **Documentation**: [Full docs](https://docs.cmdrdata.ai/anthropic)
- **Email Support**: team@cmdrdata.ai

### Version Compatibility Matrix
| CmdrData Version | Anthropic Min | Anthropic Max | Python | Status |
|-----------------|---------------|---------------|---------|---------|
| 0.1.0 | 0.21.0 | 0.99.99 | 3.8-3.12 | ✅ Stable |
| 0.2.0 (planned) | 0.25.0 | 1.99.99 | 3.8-3.13 | 🚧 Development |