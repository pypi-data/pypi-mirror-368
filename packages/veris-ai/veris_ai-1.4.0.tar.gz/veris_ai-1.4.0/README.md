# Veris AI Python SDK

A Python package for Veris AI tools with simulation capabilities and FastAPI MCP (Model Context Protocol) integration.

## Quick Reference

**Purpose**: Tool mocking, tracing, and FastAPI MCP integration for AI agent development  
**Core Components**: [`tool_mock`](#function-mocking) • [`jaeger_interface`](#jaeger-trace-interface) • [`braintrust_tracing`](#tracing-integration) • [`fastapi_mcp`](#fastapi-mcp-integration)  
**Deep Dive**: [`Module Architecture`](src/veris_ai/README.md) • [`Testing Guide`](tests/README.md) • [`Usage Examples`](examples/README.md)  
**Source of Truth**: Implementation details in [`src/veris_ai/`](src/veris_ai/) source code

## Installation

```bash
# Base package
uv add veris-ai

# With optional extras
uv add "veris-ai[dev,fastapi,instrument]"
```

**Installation Profiles**:
- `dev`: Development tools (ruff, pytest, mypy) 
- `fastapi`: FastAPI MCP integration
- `instrument`: Braintrust/OpenTelemetry tracing

## Import Patterns

**Semantic Tag**: `import-patterns`

```python
# Core imports (base dependencies only)
from veris_ai import veris, JaegerClient

# Optional features (require extras)
from veris_ai import braintrust_tracing  # Requires [instrument]
```

**Complete Import Strategies**: See [`examples/README.md`](examples/README.md) for five different import approaches, conditional features, and integration patterns.

## Configuration

**Semantic Tag**: `environment-config`

| Variable | Purpose | Default |
|----------|---------|---------|
| `VERIS_ENDPOINT_URL` | Mock server endpoint | *Required* |
| `VERIS_MOCK_TIMEOUT` | Request timeout (seconds) | `90.0` |
| `ENV` | Set to `"simulation"` for mock mode | Production |
| `VERIS_SERVICE_NAME` | Tracing service name | Auto-detected |
| `VERIS_OTLP_ENDPOINT` | OpenTelemetry collector | *Required for tracing* |

**Configuration Details**: See [`src/veris_ai/tool_mock.py`](src/veris_ai/tool_mock.py) for environment handling logic.

## Tracing Integration

**Semantic Tag**: `distributed-tracing`

Parallel tracing to Braintrust and Jaeger/OpenTelemetry for monitoring and evaluation.

```python
from veris_ai import braintrust_tracing

# Enable dual tracing
braintrust_tracing.instrument(service_name="my-service", otlp_endpoint="http://localhost:4317")
```

**Session Management**: Automatic session ID extraction from bearer tokens. Manual session control via `veris.set_session_id()` and `veris.clear_session_id()`.

**Implementation Details**: See [`src/veris_ai/braintrust_tracing.py`](src/veris_ai/braintrust_tracing.py) for instrumentation logic.

## Function Mocking

**Semantic Tag**: `tool-mocking`

### Core Decorators

```python
from veris_ai import veris

# Mock mode: Returns simulated responses in ENV=simulation
@veris.mock()
async def your_function(param1: str, param2: int) -> dict:
    """Function documentation for LLM context."""
    return {"result": "actual implementation"}

# Spy mode: Executes function but logs calls/responses
@veris.mock(mode="spy")
async def monitored_function(data: str) -> dict:
    return process_data(data)

# Stub mode: Returns fixed value in simulation
@veris.stub(return_value={"status": "success"})
async def get_data() -> dict:
    return await fetch_from_api()
```

**Behavior**: In simulation mode, decorators intercept calls to mock endpoints. In production, functions execute normally.

**Implementation**: See [`src/veris_ai/tool_mock.py`](src/veris_ai/tool_mock.py) for decorator logic and API integration.

## FastAPI MCP Integration

**Semantic Tag**: `fastapi-mcp`

Expose FastAPI endpoints as MCP tools for AI agent consumption.

```python
from fastapi import FastAPI
from veris_ai import veris

app = FastAPI()

# Enable MCP integration
veris.set_fastapi_mcp(
    fastapi=app,
    name="My API Server",
    include_operations=["get_users", "create_user"],
    exclude_tags=["internal"]
)
```

**Key Features**:
- **Automatic schema conversion**: FastAPI OpenAPI → MCP tool definitions
- **Session management**: Bearer token → session ID mapping
- **Filtering**: Include/exclude operations and tags
- **Authentication**: OAuth2 integration

**Configuration Reference**: See function signature in [`src/veris_ai/tool_mock.py`](src/veris_ai/tool_mock.py) for all `set_fastapi_mcp()` parameters.

## Utility Functions

**Semantic Tag**: `json-schema-utils`

```python
from veris_ai.utils import extract_json_schema

# Schema extraction from types
user_schema = extract_json_schema(User)  # Pydantic models
list_schema = extract_json_schema(List[str])  # Generics
```

**Supported Types**: Built-in types, generics (List, Dict, Union), Pydantic models, TypedDict, forward references.

**Implementation**: See [`src/veris_ai/utils.py`](src/veris_ai/utils.py) for type conversion logic.

## Development

**Semantic Tag**: `development-setup`

**Requirements**: Python 3.11+, `uv` package manager

```bash
# Install with dev dependencies
uv add "veris-ai[dev]"

# Quality checks
ruff check --fix .    # Lint and format
pytest --cov=veris_ai # Test with coverage
```

**Testing & Architecture**: See [`tests/README.md`](tests/README.md) for test structure, fixtures, and coverage strategies. See [`src/veris_ai/README.md`](src/veris_ai/README.md) for module architecture and implementation flows.

## Module Architecture

**Semantic Tag**: `module-architecture`

**Core Modules**: `tool_mock` (mocking), `jaeger_interface` (trace queries), `braintrust_tracing` (dual tracing), `utils` (schema conversion)

**Complete Architecture**: See [`src/veris_ai/README.md`](src/veris_ai/README.md) for module overview, implementation flows, and configuration details. 

## Jaeger Trace Interface

**Semantic Tag**: `jaeger-query-api`

```python
from veris_ai.jaeger_interface import JaegerClient

client = JaegerClient("http://localhost:16686")
traces = client.search(service="veris-agent", tags={"error": "true"})
```

**Complete Guide**: See [`src/veris_ai/jaeger_interface/README.md`](src/veris_ai/jaeger_interface/README.md) for API reference, filtering strategies, and architecture details.

---

**License**: MIT License - see [LICENSE](LICENSE) file for details. 