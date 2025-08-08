# cmdrdata-openai

[![CI](https://github.com/cmdrdata-ai/cmdrdata-openai/workflows/CI/badge.svg)](https://github.com/cmdrdata-ai/cmdrdata-openai/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/cmdrdata-ai/cmdrdata-openai/branch/main/graph/badge.svg)](https://codecov.io/gh/cmdrdata-ai/cmdrdata-openai)
[![PyPI version](https://badge.fury.io/py/cmdrdata-openai.svg)](https://badge.fury.io/py/cmdrdata-openai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/cmdrdata-openai)](https://pypi.org/project/cmdrdata-openai/)
[![Downloads](https://pepy.tech/badge/cmdrdata-openai)](https://pepy.tech/project/cmdrdata-openai)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Customer tracking and usage-based billing for OpenAI APIs**

Transform your OpenAI integration into a customer-aware, usage-based billing system. Track exactly what each customer consumes and bill them accordingly with fine-grained precision.

## 🛡️ Production Ready

**Extremely robust and reliable** - Built for production environments with:

- **Resilient Tracking:** OpenAI calls succeed even if tracking fails.
- **Non-blocking I/O:** Fire-and-forget tracking never slows down your application.
- **Automatic Retries:** Failed tracking attempts are automatically retried with exponential backoff.
- **Thread-Safe Context:** Safely track usage across multi-threaded and async applications.
- **Enterprise Security:** API key sanitization and input validation.

## 💰 Customer Tracking & Usage-Based Billing

`cmdrdata-openai` enables **fine-grained customer tracking** and **usage-based billing** for your AI application:

### **Customer-Level Visibility**
- **Per-customer token consumption** - Track exactly how much each customer uses
- **Usage attribution** - Every API call is attributed to a specific customer
- **Customer context management** - Automatic customer tracking across your application

### **Fine-Grained Billing Control**
- **Custom pricing models** - Set your own rates beyond simple token counts
- **Arbitrary metadata tracking** - Attach any billing-relevant data to each API call
- **Multi-dimensional billing** - Bill based on tokens, requests, models, or custom metrics
- **Real-time usage monitoring** - Track costs and usage as they happen

### **What Gets Tracked**
- **Token usage** (input/output tokens for accurate billing)
- **Model information** (gpt-5, gpt-4o, gpt-4, gpt-3.5-turbo, etc.)
- **Customer identification** (your customer IDs)
- **Custom metadata** (request types, feature usage, geographic data, etc.)
- **Performance metrics** (response times, error rates)

## 🚀 Quick Start

### 1. Install

```bash
pip install cmdrdata-openai
```

**Note**: This package wraps the official OpenAI SDK. If you already have `openai` installed, CmdrData will use your existing version. If not, it will install a compatible version automatically. [Learn more about dependency management →](docs/DEPENDENCY_MANAGEMENT.md)

### 2. Replace Your OpenAI Import

It's a drop-in replacement. All you need to do is change how you initialize the client and add the `customer_id` to your API calls.

**Before:**
```python
from openai import OpenAI

# This client is not tracked
client = OpenAI(api_key="sk-...")
```

**After:**
```python
from cmdrdata_openai import TrackedOpenAI

# This client automatically tracks usage
client = TrackedOpenAI(
    api_key="sk-...",
    tracker_key="tk-..."  # Get this from your cmdrdata dashboard
)

# Add customer_id to your calls to enable tracking
response = client.chat.completions.create(
    model="gpt-5",  # Supports GPT-5, GPT-4o, GPT-4, etc.
    messages=[{"role": "user", "content": "Hello!"}],
    customer_id="customer-123"
)
```

That's it! **Every API call now automatically tracks token usage, performance, and errors.**

## 📖 Usage Patterns

### Flask/FastAPI Integration

```python
from flask import Flask, request, jsonify
from cmdrdata_openai import TrackedOpenAI, set_customer_context, clear_customer_context

app = Flask(__name__)
client = TrackedOpenAI(
    api_key="your-openai-key",
    tracker_key="your-cmdrdata-key"
)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    customer_id = data['customer_id']
    
    # Set context for this request
    set_customer_context(customer_id)
    
    try:
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": data['message']}]
        )
        return jsonify({"response": response.choices[0].message.content})
    finally:
        clear_customer_context()
```

### Context Manager (Automatic Cleanup)

```python
from cmdrdata_openai import customer_context

with customer_context("customer-456"):
    response1 = client.chat.completions.create(...)
    response2 = client.chat.completions.create(...)
    # Both calls tracked for customer-456
# Context automatically cleared
```

### Async Support

```python
from cmdrdata_openai import AsyncTrackedOpenAI

client = AsyncTrackedOpenAI(
    api_key="your-openai-key",
    tracker_key="your-cmdrdata-key"
)

response = await client.chat.completions.create(
    model="gpt-5",
    messages=[{"role": "user", "content": "Hello!"}],
    customer_id="customer-789"
)
```

### 💎 Fine-Grained Billing with Custom Metadata

Track arbitrary metadata with each API call to enable sophisticated billing models:

```python
# Example: SaaS application with feature-based billing
response = client.chat.completions.create(
    model="gpt-5",
    messages=[{"role": "user", "content": "Analyze this data..."}],
    customer_id="customer-123",
    # Custom metadata for fine-grained billing
    custom_metadata={
        "feature": "data_analysis",
        "plan_tier": "premium", 
        "region": "us-east",
        "request_size": "large",
        "processing_type": "batch"
    }
)

# Example: Usage-based pricing by request complexity
response = client.chat.completions.create(
    model="gpt-5",
    messages=long_conversation_history,
    customer_id="customer-456",
    custom_metadata={
        "request_complexity": "high",
        "conversation_length": len(long_conversation_history),
        "business_unit": "sales",
        "priority": "high"
    }
)
```

**Billing Use Cases:**
- **Feature-based pricing**: Bill differently for different app features
- **Complexity-based pricing**: Higher rates for complex requests
- **Geographic pricing**: Different rates by customer region  
- **Plan-tier pricing**: Premium customers pay different rates
- **Volume discounts**: Track cumulative usage for volume pricing
- **Department billing**: Track usage by business unit or team

## 🔧 Configuration

### Basic Configuration

```python
client = TrackedOpenAI(
    api_key="your-openai-key",           # OpenAI API key
    tracker_key="your-cmdrdata-key",     # cmdrdata API key
    tracker_endpoint="https://api.cmdrdata.ai/api/events",  # cmdrdata endpoint
    tracker_timeout=5.0                   # Timeout for tracking requests
)
```

### Environment Variables

```bash
export OPENAI_API_KEY="your-openai-key"
export CMDRDATA_API_KEY="your-cmdrdata-key"
```

```python
import os
client = TrackedOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    tracker_key=os.getenv("CMDRDATA_API_KEY")
)
```

## 🎛️ Advanced Features

### Disable Tracking for Specific Calls

```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Internal query"}],
    track_usage=False  # This call won't be tracked
)
```

### Priority System

Customer ID resolution follows this priority:

1. **Explicit `customer_id` parameter** (highest priority)
2. **Customer ID from context**
3. **No tracking** (warning logged)

```python
set_customer_context("context-customer")

# This will be tracked for "explicit-customer"
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
    customer_id="explicit-customer"  # Overrides context
)
```

### Error Handling

cmdrdata-openai is designed to never break your OpenAI calls:

- **Tracking failures are logged but don't raise exceptions**
- **OpenAI calls proceed normally even if tracking fails**
- **Background tracking doesn't block your application**

```python
# Even if cmdrdata is down, this still works
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
    customer_id="customer-123"
)
# OpenAI call succeeds, tracking failure is logged
```

## 📊 What Gets Tracked

For each OpenAI API call, cmdrdata-openai automatically tracks:

- **Customer ID** (from parameter or context)
- **Model used** (e.g., gpt-4, gpt-3.5-turbo)
- **Token usage** (input tokens, output tokens, total tokens)
- **Provider** (openai)
- **Timestamp** (when the call was made)
- **Metadata** (response ID, finish reason, etc.)

Example tracked event:
```json
{
  "customer_id": "customer-123",
  "model": "gpt-4",
  "input_tokens": 15,
  "output_tokens": 25,
  "total_tokens": 40,
  "provider": "openai",
  "timestamp": "2025-07-04T10:30:00Z",
  "metadata": {
    "response_id": "chatcmpl-abc123",
    "finish_reason": "stop"
  }
}
```

## 🔧 How It Works

CmdrData-OpenAI uses a **proxy pattern** to wrap your existing OpenAI client:

1. **You import CmdrData**: `from cmdrdata_openai import TrackedOpenAI`
2. **CmdrData imports OpenAI**: Uses your installed `openai` package
3. **Creates a wrapper**: Wraps the OpenAI client with tracking
4. **Forwards everything**: All OpenAI methods work exactly the same
5. **Tracks usage**: Intercepts responses to track token usage

**This means**:
- ✅ No conflicts with your OpenAI version
- ✅ All OpenAI features continue working
- ✅ You can upgrade OpenAI independently
- ✅ Zero performance overhead (async tracking)

## 🔌 Compatibility

- **OpenAI Models**: Full support for GPT-5, GPT-4o, GPT-4, GPT-3.5, DALL-E, Whisper, and all OpenAI models
- **OpenAI SDK**: Compatible with OpenAI SDK v1.0.0+ (tested with 1.99.0+)
- **Python**: Supports Python 3.9, 3.10, 3.11, 3.12, and 3.13
- **Async**: Full support for both sync and async usage
- **Frameworks**: Works with Flask, FastAPI, Django, etc.

## 📦 Installation

```bash
# Basic installation
pip install cmdrdata-openai

# For development
git clone https://github.com/cmdrdata-ai/cmdrdata-openai.git
cd cmdrdata-openai
uv pip install -e .[dev]
```

## 🛠️ Development

### Setup

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install with dev dependencies
uv pip install -e .[dev]
```

### Running Tests

```bash
# Run all tests  
uv run pytest

# Run with coverage reporting
uv run pytest --cov=cmdrdata_openai --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_client.py -v
```

### Code Quality

```bash
# Format code
uv run black cmdrdata_openai/

# Sort imports
uv run isort cmdrdata_openai/

# Type checking
uv run mypy cmdrdata_openai/ --ignore-missing-imports

# Security check
uv run safety check
```

### CI/CD

The project uses GitHub Actions for:

- **Continuous Integration** - Tests across Python 3.9-3.13
- **Code Quality** - Black, isort, mypy, safety checks  
- **Coverage Reporting** - >90% test coverage with Codecov
- **Automated Publishing** - PyPI releases on GitHub releases

## 🆘 Troubleshooting

### Common Issues

**"tracker_key is required" error:**
```python
# Make sure you provide the tracker_key
client = TrackedOpenAI(
    api_key="your-openai-key",
    tracker_key="your-cmdrdata-key"  # Don't forget this!
)
```

**No usage tracking:**
```python
# Make sure you provide customer_id or set context
set_customer_context("customer-123")
# OR
response = client.chat.completions.create(..., customer_id="customer-123")
```

**Tracking timeouts:**
```python
# Increase timeout for slow networks
client = TrackedOpenAI(
    api_key="your-openai-key",
    tracker_key="your-cmdrdata-key",
    tracker_timeout=10.0  # Increase from default 5.0
)
```

### Get Help

- 📧 **Email**: hello@cmdrdata.ai
- 🐛 **Issues**: [GitHub Issues](https://github.com/cmdrdata-ai/cmdrdata-openai/issues)
- 📖 **Docs**: [Documentation](https://github.com/cmdrdata-ai/cmdrdata-openai#readme)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚨 Important Notes

- **Never commit API keys** to version control
- **Always clean up context** in web applications
- **Test with small limits** before production deployment
- **Monitor tracking errors** in your logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run the test suite
5. Submit a pull request

For more details, see [CONTRIBUTING.md](CONTRIBUTING.md).
