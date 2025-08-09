# RoboSystems Python SDK

[![PyPI version](https://badge.fury.io/py/robosystems-python-sdk.svg)](https://pypi.org/project/robosystems-python-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for the RoboSystems Financial Knowledge Graph API. Access comprehensive financial data including accounting records, SEC filings, and advanced graph analytics through a type-safe, async-ready Python interface.

## Features

- **Type-safe API client** with full type hints and Pydantic models
- **Async/await support** for high-performance applications  
- **Multi-tenant support** with graph-scoped operations
- **Authentication handling** with API key and SSO support
- **Comprehensive error handling** with custom exceptions
- **Pagination support** for large data sets
- **Streaming query support** for memory-efficient processing of large result sets
- **Financial AI Agent** integration for natural language queries

## Installation

```bash
pip install robosystems-python-sdk
```

## Quick Start

```python
from robosystems_client import RoboSystemsClient
from robosystems_client.api.company import list_companies
from robosystems_client.api.query import execute_cypher_query
from robosystems_client.models import CypherQueryRequest

# Initialize the client
client = RoboSystemsClient(
    base_url="https://api.robosystems.ai",
    token="your-api-key",
    auth_header_name="X-API-Key",
    prefix=""  # No prefix needed for API key
)

# Async usage (recommended)
import asyncio

async def main():
    # List companies in your graph
    companies = await list_companies.asyncio(graph_id="your-graph-id", client=client)
    print(f"Found {companies.total} companies")
    
    # Execute a Cypher query
    query = CypherQueryRequest(
        query="MATCH (c:Company)-[:HAS_FILING]->(f:Filing) RETURN c.name, f.form_type, f.filing_date LIMIT 10"
    )
    result = await execute_cypher_query.asyncio(graph_id="your-graph-id", client=client, body=query)
    
    for row in result.data:
        print(f"{row['c.name']} filed {row['f.form_type']} on {row['f.filing_date']}")

asyncio.run(main())
```

## Key API Endpoints

### Authentication & User Management
```python
from robosystems_client.api.auth import login_user, get_current_auth_user
from robosystems_client.api.user import create_user_api_key, get_user_graphs
from robosystems_client.models import LoginRequest, CreateAPIKeyRequest

# Login and manage sessions
login_request = LoginRequest(email="user@example.com", password="your-password")
auth_response = await login_user.asyncio(client=client, body=login_request)

# Get current authenticated user
current_user = await get_current_auth_user.asyncio(client=client)

# API key management
api_key_request = CreateAPIKeyRequest(name="My API Key", key_type="user")
api_key = await create_user_api_key.asyncio(client=client, body=api_key_request)

# List user's graphs
user_graphs = await get_user_graphs.asyncio(client=client)
```

### Company & Financial Data
```python
from robosystems_client.api.company import get_company, create_company, list_companies
from robosystems_client.api.connections import create_connection, sync_connection
from robosystems_client.models import CompanyCreate, ConnectionCreate

# List companies with pagination
companies = await list_companies.asyncio(
    graph_id="your-graph-id", 
    client=client,
    limit=20,
    offset=0
)

# Get specific company details
company = await get_company.asyncio(
    graph_id="your-graph-id", 
    company_id="AAPL", 
    client=client
)

# Create new company
company_data = CompanyCreate(
    identifier="MSFT",
    name="Microsoft Corporation",
    metadata={"industry": "Technology"}
)
new_company = await create_company.asyncio(
    graph_id="your-graph-id", 
    client=client, 
    body=company_data
)

# Data connections (QuickBooks, bank accounts, etc.)
connection_config = ConnectionCreate(
    name="QuickBooks Integration",
    connection_type="quickbooks",
    config={"company_id": "123456"}
)
connection = await create_connection.asyncio(
    graph_id="your-graph-id", 
    client=client, 
    body=connection_config
)
```

### Graph Queries & Analytics
```python
from robosystems_client.api.query import execute_cypher_query, execute_read_only_cypher_query
from robosystems_client.api.graph_analytics import get_graph_metrics
from robosystems_client.models import CypherQueryRequest

# Execute Cypher queries with parameters
query_request = CypherQueryRequest(
    query="""MATCH (c:Company {ticker: $ticker})-[:HAS_METRIC]->(m:Metric)
             WHERE m.fiscal_year >= $start_year
             RETURN m.name, m.value, m.fiscal_year
             ORDER BY m.fiscal_year DESC""",
    parameters={"ticker": "AAPL", "start_year": 2020}
)
results = await execute_cypher_query.asyncio(
    graph_id="your-graph-id", 
    client=client, 
    body=query_request
)

# Read-only queries (for better performance on large datasets)
read_only_result = await execute_read_only_cypher_query.asyncio(
    graph_id="your-graph-id",
    client=client,
    body=query_request
)

# Get graph analytics and metrics
metrics = await get_graph_metrics.asyncio(
    graph_id="your-graph-id", 
    client=client
)
print(f"Total nodes: {metrics.total_nodes}")
print(f"Total relationships: {metrics.total_relationships}")
```

### Financial AI Agent
```python
from robosystems_client.api.agent import query_financial_agent
from robosystems_client.models import AgentQueryRequest

# Natural language financial queries
agent_request = AgentQueryRequest(
    query="What was Apple's revenue growth over the last 3 years?",
    include_reasoning=True,
    max_tokens=1000
)
agent_response = await query_financial_agent.asyncio(
    graph_id="your-graph-id", 
    client=client, 
    body=agent_request
)
print(f"Answer: {agent_response.answer}")
if agent_response.reasoning:
    print(f"Reasoning: {agent_response.reasoning}")
```

### Function Patterns

Every API endpoint provides multiple calling patterns:

- **`asyncio()`** - Async call, returns parsed response (recommended)
- **`asyncio_detailed()`** - Async call, returns full Response object  
- **`sync()`** - Synchronous call, returns parsed response
- **`sync_detailed()`** - Synchronous call, returns full Response object

## Streaming Queries

For large result sets, the SDK supports streaming responses that process data in chunks to minimize memory usage:

```python
from robosystems_client.extensions import asyncio_streaming, sync_streaming
from robosystems_client.models import CypherQueryRequest

# Async streaming for large datasets
async def process_large_dataset():
    query = CypherQueryRequest(
        query="""MATCH (c:Company)-[:HAS_METRIC]->(m:Metric)
                 WHERE m.fiscal_year >= 2020
                 RETURN c.name, m.name, m.value, m.fiscal_year
                 ORDER BY c.name, m.fiscal_year""",
        parameters={}
    )
    
    total_rows = 0
    async for chunk in asyncio_streaming(
        graph_id="your-graph-id",
        client=client,
        body=query
    ):
        # Process chunk with chunk['row_count'] rows
        for row in chunk['data']:
            # Process each row without loading entire dataset
            company = row['c.name']
            metric = row['m.name']
            value = row['m.value']
            year = row['m.fiscal_year']
            # Your processing logic here
            
        total_rows += chunk['row_count']
        
        # Final chunk includes execution metadata
        if chunk.get('final'):
            print(f"Query completed: {total_rows} rows in {chunk['execution_time_ms']}ms")

# Synchronous streaming also available
def process_sync():
    for chunk in sync_streaming(graph_id="your-graph-id", client=client, body=query):
        # Process chunk
        for row in chunk['data']:
            print(f"{row['c.name']}: {row['m.name']} = {row['m.value']}")
```

Streaming is ideal for:
- Exporting large datasets without loading everything into memory
- Real-time processing of query results  
- Building ETL pipelines with controlled memory usage
- Generating reports from millions of rows

## Advanced Features

### Billing & Credit Management
```python
from robosystems_client.api.credits_ import get_credit_summary, check_credit_balance
from robosystems_client.api.billing import get_current_graph_bill, get_graph_usage_details

# Monitor credits and usage
credit_summary = await get_credit_summary.asyncio(client=client)
print(f"Available credits: {credit_summary.available_credits:,}")
print(f"Monthly usage: {credit_summary.used_credits:,}/{credit_summary.total_credits:,}")

# Check credit requirements before operations
from robosystems_client.models import CreditCheckRequest
credit_check_request = CreditCheckRequest(
    operation_type="query",
    estimated_credits=100
)
credit_check = await check_credit_balance.asyncio(
    graph_id="your-graph-id", 
    client=client, 
    body=credit_check_request
)

# Billing information
current_bill = await get_current_graph_bill.asyncio(
    graph_id="your-graph-id", 
    client=client
)

# Detailed usage metrics
usage_details = await get_graph_usage_details.asyncio(
    graph_id="your-graph-id",
    client=client,
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

### MCP Tools Integration
```python
from robosystems_client.api.mcp import list_mcp_tools, call_mcp_tool
from robosystems_client.models import MCPToolCall

# List available MCP tools
tools = await list_mcp_tools.asyncio(client=client)
for tool in tools.tools:
    print(f"{tool.name}: {tool.description}")

# Call an MCP tool
tool_call = MCPToolCall(
    name="analyze_financial_statement",
    arguments={
        "company_id": "AAPL", 
        "statement_type": "income",
        "fiscal_year": 2023
    }
)
tool_result = await call_mcp_tool.asyncio(
    client=client,
    body=tool_call
)
print(f"Analysis result: {tool_result.content}")
```

## Error Handling

```python
from robosystems_client.types import Response
from robosystems_client.errors import UnexpectedStatus
import httpx

try:
    # API calls that might fail
    companies = await list_companies.asyncio(graph_id="your-graph-id", client=client)
except UnexpectedStatus as e:
    # Handle API errors (4xx, 5xx)
    print(f"API error: {e.status_code}")
    print(f"Error details: {e.content}")
    
    # Parse error response if JSON
    if e.status_code == 400:
        error_detail = e.content.decode('utf-8')
        print(f"Validation error: {error_detail}")
    elif e.status_code == 401:
        print("Authentication failed - check your API key")
    elif e.status_code == 403:
        print("Permission denied - check graph access")
    elif e.status_code == 429:
        print("Rate limit exceeded - retry later")
except httpx.TimeoutException:
    print("Request timed out - try again")
except httpx.NetworkError as e:
    print(f"Network error: {e}")
except Exception as e:
    print(f"Unexpected error: {type(e).__name__}: {e}")

# Using detailed responses for better error handling
from robosystems_client.api.company import list_companies

response = await list_companies.asyncio_detailed(
    graph_id="your-graph-id",
    client=client
)

if response.status_code == 200:
    companies = response.parsed
    print(f"Success: {companies.total} companies found")
else:
    print(f"Failed with status {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Content: {response.content}")
```

## Development

This SDK is auto-generated from the RoboSystems OpenAPI specification to ensure it stays in sync with the latest API changes.

### Setup

```bash
just venv
just install
```

### Regenerating the SDK

When the API changes, regenerate the SDK from the OpenAPI spec:

```bash
# From localhost (development)
just generate-sdk http://localhost:8000/openapi.json

# From staging
just generate-sdk https://staging.api.robosystems.ai/openapi.json

# From production
just generate-sdk https://api.robosystems.ai/openapi.json
```

### Testing

```bash
just test
just test-cov
```

### Code Quality

```bash
just lint
just format
just typecheck
```

### Publishing

```bash
just build-package
just publish-package
```
