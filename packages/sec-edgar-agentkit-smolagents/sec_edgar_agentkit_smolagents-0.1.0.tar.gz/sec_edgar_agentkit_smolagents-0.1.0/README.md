# SEC EDGAR agentkit for smolagents

A lightweight integration of SEC EDGAR data access tools for Hugging Face's [smolagents](https://github.com/huggingface/smolagents) framework.

## Installation

```bash
pip install sec-edgar-agentkit-smolagents
# or
pip install -r requirements.txt
```

## Quick Start

```python
from sec_edgar_smolagents import create_sec_edgar_agent

# Create an agent with all SEC EDGAR tools
agent = create_sec_edgar_agent("gpt-4")

# Ask questions about companies and filings
result = agent.run("What was Apple's revenue last year?")
print(result)
```

## Available Tools

- `CIKLookupTool` - Look up company CIK by name or ticker
- `CompanyInfoTool` - Get detailed company information
- `CompanyFactsTool` - Retrieve XBRL company facts
- `FilingSearchTool` - Search for SEC filings
- `FilingContentTool` - Extract filing content
- `Analyze8KTool` - Analyze 8-K material events
- `FinancialStatementsTool` - Extract financial statements
- `XBRLParseTool` - Parse XBRL data
- `InsiderTradingTool` - Analyze Forms 3/4/5

## Usage Examples

### Basic Company Research

```python
from sec_edgar_smolagents import create_sec_edgar_agent

agent = create_sec_edgar_agent("gpt-4")

# Simple queries
agent.run("Find Microsoft's latest 10-K filing")
agent.run("What were Tesla's material events in the last quarter?")
agent.run("Show me insider trading activity for Apple")
```

### Using Specific Tools

```python
from sec_edgar_smolagents import CIKLookupTool, FilingSearchTool

# Create agent with only specific tools
agent = create_sec_edgar_agent(
    "gpt-4",
    tools=[CIKLookupTool(), FilingSearchTool()]
)

result = agent.run("Find Amazon's CIK and recent filings")
```

### Different Model Providers

```python
# OpenAI
agent = create_sec_edgar_agent("gpt-4")

# Anthropic
agent = create_sec_edgar_agent("claude-3-opus-20240229")

# Hugging Face API
from smolagents import HfApiModel
model = HfApiModel("meta-llama/Llama-3-8b-instruct")
agent = create_sec_edgar_agent(model)

# Local model
from smolagents import TransformersModel
model = TransformersModel("microsoft/Phi-3-mini-4k-instruct")
agent = create_sec_edgar_agent(model)
```

### Financial Analysis

```python
agent = create_sec_edgar_agent("gpt-4")

# Complex multi-step analysis
analysis = agent.run("""
    1. Find Apple's last 3 years of 10-K filings
    2. Extract revenue and net income from each
    3. Calculate year-over-year growth rates
    4. Compare with Microsoft's performance
""")

print(analysis)
```

## MCP Server Configuration

The tools connect to the `sec-edgar-mcp` server. By default, it looks for the server at the `sec-edgar-mcp` command. You can customize this:

```python
from sec_edgar_smolagents import SECEdgarToolkit
from sec_edgar_smolagents.mcp_client import MCPClient

# Custom MCP server command
client = MCPClient(server_command="/path/to/sec-edgar-mcp")
toolkit = SECEdgarToolkit(mcp_client=client)

agent = create_sec_edgar_agent("gpt-4", tools=toolkit.get_tools())
```

## Development

### Running Tests

```bash
pytest integrations/smolagents/__tests__/
```

### Running Examples

```bash
cd integrations/smolagents
python examples/basic_usage.py
python examples/financial_analysis.py
```

## Requirements

- Python 3.8+
- smolagents >= 0.1.0
- sec-edgar-mcp server installed (`pip install sec-edgar-mcp`)

## License

AGPL-3.0 - See [LICENSE](../../LICENSE) for details.

## Author

Stefano Amorelli <stefano@amorelli.tech>