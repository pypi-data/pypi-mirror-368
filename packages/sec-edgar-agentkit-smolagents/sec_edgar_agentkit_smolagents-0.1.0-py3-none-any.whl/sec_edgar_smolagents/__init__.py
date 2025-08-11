"""SEC EDGAR agentkit for Hugging Face smolagents framework."""

from .tools import (
    CIKLookupTool,
    CompanyInfoTool,
    CompanyFactsTool,
    FilingSearchTool,
    FilingContentTool,
    Analyze8KTool,
    FinancialStatementsTool,
    XBRLParseTool,
    InsiderTradingTool,
    SECEdgarToolkit,
)
from .agent import create_sec_edgar_agent

__all__ = [
    "CIKLookupTool",
    "CompanyInfoTool", 
    "CompanyFactsTool",
    "FilingSearchTool",
    "FilingContentTool",
    "Analyze8KTool",
    "FinancialStatementsTool",
    "XBRLParseTool",
    "InsiderTradingTool",
    "SECEdgarToolkit",
    "create_sec_edgar_agent",
]

__version__ = "0.1.0"