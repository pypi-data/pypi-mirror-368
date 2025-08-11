"""Agent creation utilities for SEC EDGAR agentkit with smolagents."""

from typing import List, Optional, Union
from smolagents import Agent, LiteLLMModel, HfApiModel, TransformersModel
from .tools import SECEdgarToolkit


def create_sec_edgar_agent(
    model: Optional[Union[str, LiteLLMModel, HfApiModel, TransformersModel]] = None,
    tools: Optional[List] = None,
    additional_tools: Optional[List] = None,
    **kwargs
) -> Agent:
    """
    Create a smolagents Agent with SEC EDGAR agentkit tools.
    
    Args:
        model: The language model to use. Can be:
            - A string model name (e.g., "gpt-4", "claude-3-opus")
            - A LiteLLMModel instance
            - An HfApiModel instance  
            - A TransformersModel instance
        tools: List of tools to use. If None, uses all SEC EDGAR tools.
        additional_tools: Additional tools to include beyond SEC EDGAR tools.
        **kwargs: Additional arguments to pass to Agent constructor.
    
    Returns:
        Agent: Configured smolagents Agent with SEC EDGAR capabilities.
    
    Examples:
        # Using OpenAI
        agent = create_sec_edgar_agent("gpt-4")
        
        # Using Anthropic
        agent = create_sec_edgar_agent("claude-3-opus-20240229")
        
        # Using local model
        from smolagents import TransformersModel
        model = TransformersModel("microsoft/Phi-3-mini-4k-instruct")
        agent = create_sec_edgar_agent(model)
    """
    # Default to GPT-4 if no model specified
    if model is None:
        model = LiteLLMModel("gpt-4")
    elif isinstance(model, str):
        model = LiteLLMModel(model)
    
    # Get SEC EDGAR tools
    if tools is None:
        toolkit = SECEdgarToolkit()
        tools = toolkit.get_tools()
    
    # Add any additional tools
    if additional_tools:
        tools = tools + additional_tools
    
    # Create and return the agent
    return Agent(
        tools=tools,
        model=model,
        **kwargs
    )