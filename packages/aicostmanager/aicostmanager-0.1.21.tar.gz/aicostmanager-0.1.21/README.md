# AICostManager Python SDK

[![PyPI version](https://img.shields.io/pypi/v/aicostmanager.svg)](https://pypi.org/project/aicostmanager/)
[![Python Support](https://img.shields.io/pypi/pyversions/aicostmanager.svg)](https://pypi.org/project/aicostmanager/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AICostManager** is a comprehensive AI cost management platform that helps developers and agencies monitor, analyze, and optimize their LLM and API spending across all major providers. **[Sign up for a free account at aicostmanager.com](https://aicostmanager.com)** to access real-time analytics, budget alerts, client billing tools, and accounting integrations.

Stop being surprised by your AI costs. AICostManager provides complete cost management for AI-powered software—from real-time tracking to budget enforcement to automated client billing.

**🔒 Privacy-First**: AICostManager NEVER sees your API keys, requests, or responses. We only extract usage metadata (tokens, costs, model info) from responses. Your prompts and data remain completely private.

**🔄 Universal Compatibility**: One tracking wrapper works with ANY LLM provider's SDK. Works as a drop-in replacement for your existing LLM clients with zero code changes to your API calls.

**🎯 Supports**: OpenAI, Anthropic Claude, Google Gemini, AWS Bedrock, and any other LLM provider.

## 🚀 Why AICostManager?

### For Developers: One-Line Integration
- **Zero Code Changes**: Wrap your existing client and continue calling it exactly as before
- **Automatic Tracking**: Usage data is automatically extracted and sent to AICostManager in the background
- **Universal Support**: Works with OpenAI, Anthropic, Google, AWS Bedrock, and more
- **Stream Aware**: Streaming responses are tracked once the stream completes
- **Non-Intrusive**: Never blocks your application—all tracking happens asynchronously

### For Finance Teams: Complete Cost Control
- **Real-time Budget Control**: Set spending limits and get alerts before you hit them
- **Client-Based Billing**: Track costs per customer, project, or department for accurate billing
- **Accounting Integration**: Ready for QuickBooks, Xero, and other financial systems
- **Cost Projections**: Understand spending trends and plan budgets effectively
- **Multi-Tenant Ready**: Perfect for agencies and SaaS platforms managing multiple clients

### Cost Management ≠ Cost Tracking

Unlike free cost tracking from LangChain or other frameworks, AICostManager provides **complete cost management**:

| Feature | Free Cost Tracking | AICostManager |
|---------|-------------------|---------------|
| **Scope** | LLM tokens only | All API costs (LLM, speech, embeddings, storage) |
| **Control** | Monitor after the fact | Real-time budget enforcement & alerts |
| **Business Model** | Collects your data | Privacy-first, usage data only |
| **Multi-Tenant** | Basic tracking | Client billing, department allocation |
| **Integration** | Manual reconciliation | Automated accounting integration |
| **Management** | Shows what happened | Prevents cost surprises |

## 👤 Getting Started

> **🔑 CRITICAL: API Key Required**
>
> Before using AICostManager, you **MUST** have an AICostManager API key. **[Sign up for a free account at aicostmanager.com](https://aicostmanager.com)** to get your API key.
>
> **Without an API key, tracking will not work!**

### Installation

```bash
# Using uv (recommended)
uv pip install aicostmanager
# or add to a project
uv add aicostmanager
```

### Environment Setup

```bash
# Set your AICostManager API key (get this from aicostmanager.com)
export AICM_API_KEY="your-aicostmanager-api-key-here"
```

**🔒 Important**: Your existing LLM provider API keys (OpenAI, Anthropic, etc.) remain yours and are never shared with AICostManager. You continue to use them exactly as before—AICostManager only extracts usage metadata from responses.

## 🚀 Quick Start

### Basic Usage

```python
import os
import openai
from aicostmanager import CostManager

# Create OpenAI client as usual
openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Wrap with AICostManager tracking
tracked_client = CostManager(openai_client)  # reads AICM_API_KEY from env

# Use exactly as before - zero changes to your API calls
response = tracked_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
# Usage automatically logged to AICostManager dashboard
```

### Streaming Support

```python
stream = tracked_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Tell me a story."}],
    stream=True,
)

for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
# Usage tracked when stream completes
```

### Multi-Provider Examples

#### Anthropic Claude

```python
import anthropic
from aicostmanager import CostManager

claude_client = anthropic.Anthropic(api_key="your-anthropic-key")
tracked_claude = CostManager(claude_client)

response = tracked_claude.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Hello!"}]
)
```

#### Google Gemini

```python
import google.genai
from aicostmanager import CostManager

gemini_client = google.genai.Client(api_key="your-google-key")
tracked_gemini = CostManager(gemini_client)

response = tracked_gemini.models.generate_content(
    model="gemini-1.5-flash",
    contents="Hello!"
)
```

#### AWS Bedrock

```python
import boto3
from aicostmanager import CostManager

bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
tracked_bedrock = CostManager(bedrock_client)

# Use as normal - AICostManager automatically tracks usage
```

## 🏢 Multi-Tenant & Client Tracking

Perfect for agencies, SaaS platforms, and enterprise applications that need to track LLM costs across multiple clients or projects. AICostManager provides powerful tools for organizing and billing API usage by customer.

### Client-Based Cost Tracking

Track usage with client identifiers for accurate billing and cost allocation:

```python
from aicostmanager import CostManager
import openai

client = openai.OpenAI(api_key="your-key")

# Option 1: Set client info via constructor
tracked_client = CostManager(
    client,
    client_customer_key="customer_acme_corp",
    context={
        "project": "chatbot_v2",
        "user_id": "user_123", 
        "environment": "production"
    }
)

# Option 2: Organize usage via dashboard after tracking
# All usage is automatically tracked and can be organized
# by customer, project, or department in the AICostManager dashboard

response = tracked_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello customer support!"}]
)
# → Usage logged with client context for accurate billing
```

### Use Cases

- **🏢 Agencies**: Track costs per client for accurate project billing
- **🌐 SaaS Platforms**: Allocate AI costs across customer accounts  
- **🏗️ Enterprise**: Organize spending by department, project, or team
- **🔄 Multi-Environment**: Separate dev, staging, and production costs

**📖 [Complete Multi-Tenant Guide](docs/multi-tenant.md)** - Detailed examples and API usage patterns

## ✨ Key Features

- **🔄 Universal Provider Support**: Works with OpenAI, Anthropic, Google, AWS Bedrock, and any Python LLM SDK
- **🔒 Privacy-First Design**: NEVER sees API keys, requests, or responses—only usage metadata (tokens, costs, model info)
- **🏢 Multi-Tenant Ready**: Organize and allocate costs per customer, project, or department via dashboard
- **📊 Automatic Usage Tracking**: Captures tokens, costs, model info, and timestamps from response metadata
- **🎛️ Real-time Budget Control**: Set spending limits and get alerts before you exceed budgets
- **💰 Client-Based Billing**: Generate detailed reports for customer invoicing and cost allocation
- **📈 Advanced Analytics**: Understand spending patterns, trends, and optimization opportunities
- **🔔 Smart Alerts**: Get notified when approaching budget limits or unusual spending patterns
- **💾 Background Delivery**: Resilient background delivery with retry logic—never blocks your application
- **🌊 Stream Aware**: Streaming responses are properly tracked once the stream completes
- **🎯 Drop-in Replacement**: Zero code changes to your existing API calls
- **💼 Accounting Ready**: Export data for QuickBooks, Xero, and other financial systems
- **🚫 Non-Intrusive**: Original API responses remain completely unchanged

## 📊 Dashboard & Analytics

Visit [aicostmanager.com](https://aicostmanager.com) to access:

- **Real-time Cost Dashboard**: Monitor spending across all providers in one place
- **Budget Management**: Set and enforce spending limits with automated alerts
- **Client Billing**: Generate detailed reports for customer invoicing
- **Usage Analytics**: Understand patterns, trends, and optimization opportunities
- **Threshold Alerts**: Get notified before hitting budget limits
- **Export Tools**: Download data for accounting and financial planning

## 🔄 How Delivery Works

`CostManager` places extracted usage payloads on a global queue. A background worker batches and retries delivery so that instrumentation never blocks your application. The queue size, retry attempts and request timeout can be tuned when constructing the wrapper.

```python
tracked_client = CostManager(
    client,
    delivery_queue_size=1000,      # Queue size for batching
    delivery_max_retries=5,        # Retry failed deliveries
    delivery_timeout=10.0,         # Request timeout in seconds
    delivery_batch_interval=0.05,  # Wait up to 50ms for more items
    delivery_max_batch_size=100,   # Flush when batch reaches this size
    # delivery_mode="async",       # Use async delivery (or set AICM_DELIVERY_MODE)
    # delivery_on_full="backpressure",  # Block, raise, or backpressure when full (or set AICM_DELIVERY_ON_FULL)
)
```

Set the environment variable ``AICM_DELIVERY_MODE=async`` (or pass
``delivery_mode="async"`` as shown above) to use an ``httpx.AsyncClient`` with
non-blocking retries—ideal for eventlet/gevent worker pools.

To change the default behaviour when the queue is full, set
``AICM_DELIVERY_ON_FULL`` to ``block`` or ``raise``.  The default is
``backpressure`` which discards the oldest payload.

When using process-based workers such as Celery or the ``multiprocessing``
module, create the ``CostManager`` inside the worker's initialisation hook.
This ensures the background delivery thread is started for every worker
process and avoids race conditions after forking.

## 👨‍💻 Advanced Usage

### Async Support

```python
from aicostmanager import AsyncCostManager
import openai

async_client = openai.AsyncOpenAI(api_key="your-key")
tracked_async = AsyncCostManager(async_client)

response = await tracked_async.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Custom Configuration

```python
tracked_client = CostManager(
    client,
    aicm_api_key="your-api-key",           # Override env var
    aicm_api_base="https://custom.url",    # Custom API base
    delivery_queue_size=2000,              # Larger queue
    delivery_max_retries=10,               # More retries
    delivery_batch_interval=0.1,           # Custom batch window
    delivery_max_batch_size=50,            # Custom batch size limit
    delivery_on_full="raise",             # Block, raise, or backpressure
)
```

### Manual Usage Tracking (Tracker)

Use the `Tracker` when you need to record custom usage events that are not tied to a wrapped SDK call (e.g., batch jobs, internal services, or custom metrics). It validates payloads against your configuration’s `manual_usage_schema` and delivers them using the same resilient queue:

```python
from aicostmanager import Tracker

tracker = Tracker(
    config_id="your-config-id",
    service_id="your-service-id",
)

tracker.track({
    "tokens": 123,
    "model": "gpt-4o-mini",
})

# Reuse a session or request identifier from the upstream service
# tracker.track({"tokens": 123, "model": "gpt-4o-mini"}, response_id="session123")

# Provide a custom timestamp if you already recorded one
# tracker.track({"tokens": 123, "model": "gpt-4o-mini"}, timestamp="2024-01-01T00:00:00Z")

# Async initialization for web apps
# tracker = await Tracker.create_async("cfg", "svc")
# tracker.close()  # during shutdown
```

See the dedicated guide: [Manual Usage Tracking](docs/tracker.md).

### Querying Usage Events

Access your usage data programmatically:

```python
import requests

def get_recent_usage(aicm_api_key: str, customer_id: str = None):
    headers = {"Authorization": f"Bearer {aicm_api_key}"}
    params = {"limit": 100}
    if customer_id:
        params["customer_id"] = customer_id
    
    resp = requests.get(
        "https://aicostmanager.com/api/v1/usage/events/",
        headers=headers,
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()
```

## 📖 Documentation

### Complete Guides

- **[📖 Documentation Hub](docs/index.md)** - Complete documentation index
- **[🏢 Multi-Tenant Guide](docs/multi-tenant.md)** - Client tracking, cost allocation, and billing
- **[📊 Usage Examples](docs/usage.md)** - API usage and basic examples
- **[🔧 Tracking System](docs/tracking.md)** - How the tracking system works
- **[📐 Manual Usage Tracking](docs/tracker.md)** - Record custom usage events
- **[⚙️ Configuration & Env Vars](docs/configuration.md)** - Environment variables and INI behavior
- **[🌐 REST API Tracking](docs/rest.md)** - Wrap requests or httpx sessions
- **[🧪 Testing Guide](docs/testing.md)** - Running tests and validation

### Quick Reference

| Topic | Description | Link |
|-------|-------------|------|
| **Multi-Tenant** | Track costs per client, project, or department | [Guide](docs/multi-tenant.md) |
| **Basic Usage** | SDK installation and simple examples | [Usage](docs/usage.md) |
| **Tracking** | How usage tracking works under the hood | [Tracking](docs/tracking.md) |
| **Manual Tracking** | Send custom usage records without wrappers | [Tracker](docs/tracker.md) |
| **REST API** | Track raw HTTP requests | [REST Tracking](docs/rest.md) |
| **Testing** | Running tests and validation | [Testing](docs/testing.md) |
| **Configuration** | Env vars, INI, delivery modes | [Configuration](docs/configuration.md) |

### API Reference

The full OpenAPI specification is generated at runtime by the service and is
available from `/api/v1/openapi.json`. No schema file is stored in this
repository.

## 💻 Development & Testing

### Setup

```bash
# Clone and install
git clone https://github.com/aicostmanager/aicostmanager-python.git
cd aicostmanager-python

# Using uv (recommended)
uv sync

# Using pip
pip install -e .
```

### Running Tests

1. Create a `.env` file inside `tests/` with at least `AICM_API_KEY` and any provider keys you wish to use:

   ```env
   AICM_API_KEY=your-aicostmanager-api-key
   OPENAI_API_KEY=your-openai-api-key
   ANTHROPIC_API_KEY=your-anthropic-api-key
   # optional overrides
   # AICM_API_BASE=https://aicostmanager.com
   # AICM_INI_PATH=/path/to/AICM.INI
   ```

2. Install test dependencies:

   ```bash
   uv sync --extra test
   # or with pip:
   pip install -e ".[test]"
   ```

3. Run the test suite:

   ```bash
   pytest
   ```

**🔒 Testing Privacy**: Tests use YOUR provider API keys locally to verify functionality. These keys never leave your machine—they're only used for local testing.

### Queue Health and Metrics

You can inspect background delivery metrics programmatically:

```python
from aicostmanager import get_global_delivery_health

health = get_global_delivery_health()
if health:
    print(health["queue_size"], health["total_discarded"], health["last_error"])
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run the test suite: `pytest`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- **🌐 Website**: [aicostmanager.com](https://aicostmanager.com)
- **📦 PyPI**: [pypi.org/project/aicostmanager](https://pypi.org/project/aicostmanager/)
- **🐙 GitHub**: [github.com/aicostmanager/aicostmanager-python](https://github.com/aicostmanager/aicostmanager-python)
- **📖 Documentation**: [Complete documentation and guides](docs/index.md)
- **🐛 Issues**: [Report bugs and feature requests](https://github.com/aicostmanager/aicostmanager-python/issues)
- **📧 Support**: [support@aicostmanager.com](mailto:support@aicostmanager.com)

## 📈 What's Next?

- **MCP Server Support**: Native Model Context Protocol integration for AI agents
- **Enhanced Analytics**: More detailed cost breakdown and optimization recommendations  
- **Additional Providers**: Expanding support for more AI and API services
- **Enterprise Features**: Advanced access controls and compliance tools

---

**Stop AI costs from becoming surprises. Start tracking, controlling, and optimizing your AI spending today.**

**[Get started free at aicostmanager.com](https://aicostmanager.com)** - No credit card required.
