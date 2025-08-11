"""SEC EDGAR agentkit tools for smolagents framework."""

import asyncio
from typing import Any, Dict, List, Optional, Union
from smolagents import Tool
from .mcp_client import get_mcp_client


class BaseSECEdgarTool(Tool):
    """Base class for SEC EDGAR agentkit tools."""
    
    def __init__(self, mcp_client=None):
        super().__init__()
        self.mcp_client = mcp_client or get_mcp_client()
    
    def _run_async(self, coro):
        """Helper to run async code in sync context."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)


class CIKLookupTool(BaseSECEdgarTool):
    name = "sec_edgar_cik_lookup"
    description = "Look up a company's CIK (Central Index Key) by name or ticker symbol"
    inputs = {"query": {"type": "string", "description": "Company name or ticker symbol"}}
    output_type = "string"
    
    def forward(self, query: str) -> str:
        result = self._run_async(
            self.mcp_client.call_tool(self.name, {"query": query})
        )
        if isinstance(result, dict):
            return f"CIK: {result.get('cik', 'Not found')} - {result.get('name', '')} ({result.get('ticker', '')})"
        return str(result)


class CompanyInfoTool(BaseSECEdgarTool):
    name = "sec_edgar_company_info"
    description = "Get detailed information about a company using its CIK"
    inputs = {"cik": {"type": "string", "description": "Company CIK number"}}
    output_type = "string"
    
    def forward(self, cik: str) -> str:
        result = self._run_async(
            self.mcp_client.call_tool(self.name, {"cik": cik})
        )
        if isinstance(result, dict):
            info = []
            for key, value in result.items():
                info.append(f"{key.replace('_', ' ').title()}: {value}")
            return "\n".join(info)
        return str(result)


class CompanyFactsTool(BaseSECEdgarTool):
    name = "sec_edgar_company_facts"
    description = "Retrieve XBRL company facts data"
    inputs = {"cik": {"type": "string", "description": "Company CIK number"}}
    output_type = "string"
    
    def forward(self, cik: str) -> str:
        result = self._run_async(
            self.mcp_client.call_tool(self.name, {"cik": cik})
        )
        return str(result)


class FilingSearchTool(BaseSECEdgarTool):
    name = "sec_edgar_filing_search"
    description = "Search for SEC filings with various filters"
    inputs = {
        "cik": {"type": "string", "description": "Company CIK (optional)"},
        "form_type": {"type": "string", "description": "Form type like 10-K, 8-K (optional)"},
        "limit": {"type": "integer", "description": "Number of results (default 10)"}
    }
    output_type = "string"
    
    def forward(self, cik: str = "", form_type: str = "", limit: int = 10) -> str:
        params = {"limit": limit}
        if cik:
            params["cik"] = cik
        if form_type:
            params["form_type"] = form_type
            
        result = self._run_async(
            self.mcp_client.call_tool(self.name, params)
        )
        
        if isinstance(result, list):
            filings = []
            for filing in result[:limit]:
                filings.append(
                    f"- {filing.get('form', 'N/A')} filed on {filing.get('filing_date', 'N/A')}"
                )
            return "\n".join(filings) if filings else "No filings found"
        return str(result)


class FilingContentTool(BaseSECEdgarTool):
    name = "sec_edgar_filing_content"
    description = "Extract content from a specific SEC filing"
    inputs = {
        "url": {"type": "string", "description": "URL of the filing"},
        "section": {"type": "string", "description": "Specific section to extract (optional)"}
    }
    output_type = "string"
    
    def forward(self, url: str, section: str = "") -> str:
        params = {"url": url}
        if section:
            params["section"] = section
            
        result = self._run_async(
            self.mcp_client.call_tool(self.name, params)
        )
        
        if isinstance(result, dict):
            content = result.get('content', '')
            if len(content) > 1000:
                content = content[:1000] + "..."
            return content
        return str(result)


class Analyze8KTool(BaseSECEdgarTool):
    name = "sec_edgar_analyze_8k"
    description = "Analyze 8-K reports for material events"
    inputs = {"url": {"type": "string", "description": "URL of the 8-K filing"}}
    output_type = "string"
    
    def forward(self, url: str) -> str:
        result = self._run_async(
            self.mcp_client.call_tool(self.name, {"url": url})
        )
        return str(result)


class FinancialStatementsTool(BaseSECEdgarTool):
    name = "sec_edgar_financial_statements"
    description = "Extract financial statements from filings"
    inputs = {
        "cik": {"type": "string", "description": "Company CIK"},
        "form_type": {"type": "string", "description": "Form type (10-K, 10-Q)"},
        "year": {"type": "integer", "description": "Fiscal year (optional)"}
    }
    output_type = "string"
    
    def forward(self, cik: str, form_type: str = "10-K", year: int = None) -> str:
        params = {"cik": cik, "form_type": form_type}
        if year:
            params["year"] = year
            
        result = self._run_async(
            self.mcp_client.call_tool(self.name, params)
        )
        
        if isinstance(result, dict):
            statements = []
            for statement, data in result.items():
                statements.append(f"\n{statement.replace('_', ' ').title()}:")
                if isinstance(data, dict):
                    for key, value in data.items():
                        statements.append(f"  {key}: ${value:,.0f}")
            return "\n".join(statements)
        return str(result)


class XBRLParseTool(BaseSECEdgarTool):
    name = "sec_edgar_xbrl_parse"
    description = "Parse XBRL data for specific financial facts"
    inputs = {
        "url": {"type": "string", "description": "URL of the XBRL document"},
        "fact": {"type": "string", "description": "Specific fact to extract"}
    }
    output_type = "string"
    
    def forward(self, url: str, fact: str) -> str:
        result = self._run_async(
            self.mcp_client.call_tool(self.name, {"url": url, "fact": fact})
        )
        return str(result)


class InsiderTradingTool(BaseSECEdgarTool):
    name = "sec_edgar_insider_trading"
    description = "Analyze insider trading transactions (Forms 3, 4, 5)"
    inputs = {
        "cik": {"type": "string", "description": "Company or insider CIK"},
        "form_type": {"type": "string", "description": "Form type (3, 4, or 5)"},
        "limit": {"type": "integer", "description": "Number of results"}
    }
    output_type = "string"
    
    def forward(self, cik: str, form_type: str = "4", limit: int = 10) -> str:
        result = self._run_async(
            self.mcp_client.call_tool(
                self.name, 
                {"cik": cik, "form_type": form_type, "limit": limit}
            )
        )
        return str(result)


class SECEdgarToolkit:
    """Complete toolkit of SEC EDGAR agentkit tools."""
    
    def __init__(self, mcp_client=None):
        self.mcp_client = mcp_client or get_mcp_client()
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize all available tools."""
        return [
            CIKLookupTool(self.mcp_client),
            CompanyInfoTool(self.mcp_client),
            CompanyFactsTool(self.mcp_client),
            FilingSearchTool(self.mcp_client),
            FilingContentTool(self.mcp_client),
            Analyze8KTool(self.mcp_client),
            FinancialStatementsTool(self.mcp_client),
            XBRLParseTool(self.mcp_client),
            InsiderTradingTool(self.mcp_client),
        ]
    
    def get_tools(self) -> List[Tool]:
        """Get all SEC EDGAR agentkit tools."""
        return self.tools
    
    def get_tool_by_name(self, name: str) -> Optional[Tool]:
        """Get a specific tool by name."""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None