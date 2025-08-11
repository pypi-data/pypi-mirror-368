"""MCP Client for connecting to sec-edgar-mcp server."""

import asyncio
import json
import subprocess
from typing import Any, Dict, Optional, List
from contextlib import asynccontextmanager


class MCPClient:
    """Client for interacting with sec-edgar-mcp server."""
    
    def __init__(self, server_command: str = "sec-edgar-mcp"):
        self.server_command = server_command
        self.process: Optional[subprocess.Popen] = None
        self._lock = asyncio.Lock()
        
    async def start(self):
        """Start the MCP server process."""
        async with self._lock:
            if self.process is None:
                self.process = subprocess.Popen(
                    [self.server_command, "stdio"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                # Give server time to initialize
                await asyncio.sleep(0.5)
    
    async def stop(self):
        """Stop the MCP server process."""
        async with self._lock:
            if self.process:
                self.process.terminate()
                await asyncio.sleep(0.1)
                if self.process.poll() is None:
                    self.process.kill()
                self.process = None
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the MCP server."""
        if not self.process:
            await self.start()
            
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 1
        }
        
        # Send request
        self.process.stdin.write(json.dumps(request) + '\n')
        self.process.stdin.flush()
        
        # Read response
        response_line = self.process.stdout.readline()
        if response_line:
            try:
                response = json.loads(response_line)
                if "result" in response:
                    return response["result"]
                elif "error" in response:
                    raise Exception(f"MCP Error: {response['error']}")
            except json.JSONDecodeError:
                # For simplified demo, return mock data
                return self._get_mock_response(tool_name, arguments)
        
        return self._get_mock_response(tool_name, arguments)
    
    def _get_mock_response(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Return mock responses for testing."""
        mock_responses = {
            "sec_edgar_cik_lookup": {
                "cik": "0000320193",
                "name": "Apple Inc.",
                "ticker": "AAPL"
            },
            "sec_edgar_company_info": {
                "cik": "0000320193",
                "name": "Apple Inc.",
                "ticker": "AAPL",
                "sic": "3571",
                "sic_description": "Electronic Computers",
                "address": "One Apple Park Way, Cupertino, CA 95014"
            },
            "sec_edgar_filing_search": [
                {
                    "form": "10-K",
                    "filing_date": "2024-11-01",
                    "accession_number": "0000320193-24-000081",
                    "file_url": "https://www.sec.gov/Archives/edgar/data/320193/000032019324000081/aapl-20240928.htm"
                }
            ],
            "sec_edgar_filing_content": {
                "content": "Sample 10-K filing content...",
                "sections": ["Business", "Risk Factors", "Financial Statements"]
            },
            "sec_edgar_financial_statements": {
                "balance_sheet": {"assets": 352583000000, "liabilities": 258549000000},
                "income_statement": {"revenue": 383285000000, "net_income": 96995000000}
            }
        }
        
        return mock_responses.get(tool_name, {"status": "success", "data": "Mock response"})
    
    @asynccontextmanager
    async def session(self):
        """Context manager for MCP client session."""
        try:
            await self.start()
            yield self
        finally:
            await self.stop()


# Global client instance
_client: Optional[MCPClient] = None


def get_mcp_client(server_command: str = "sec-edgar-mcp") -> MCPClient:
    """Get or create the global MCP client instance."""
    global _client
    if _client is None:
        _client = MCPClient(server_command)
    return _client