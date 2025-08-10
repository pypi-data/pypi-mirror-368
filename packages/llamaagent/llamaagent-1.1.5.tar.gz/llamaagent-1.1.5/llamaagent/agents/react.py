"""
ReactAgent implementation for backward compatibility

This module provides the ReactAgent class that maintains backward compatibility
with existing LlamaAgent implementations while serving as a foundation for
enhanced cognitive agents.

Author: LlamaAgent Development Team
"""

import logging
from typing import Any, Dict, Optional

from .base import AgentConfig, AgentResponse, BaseAgent

logger = logging.getLogger(__name__)


class ReactAgent(BaseAgent):
    """
    ReactAgent implementation for backward compatibility.

    This agent provides the classic ReAct (Reasoning and Acting) pattern
    with basic tool usage and reasoning capabilities.
    """

    def __init__(self, config: AgentConfig, **kwargs: Any) -> None:
        """Initialize ReactAgent"""
        super().__init__(config, **kwargs)
        self.logger = logging.getLogger(f"{__name__}.ReactAgent")
        
        # Store LLM provider and tools if provided
        self.llm_provider = kwargs.get('llm_provider')
        tools = kwargs.get('tools')
        if tools:
            # Override the default ToolManager with provided tools
            self.tools = tools

    async def execute(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Execute a task using ReAct pattern"""
        start_time = self._get_current_time()
        total_tokens = 0

        try:
            # Build messages for LLM
            from llamaagent.types import LLMMessage
            
            messages = [
                LLMMessage(
                    role="system",
                    content=f"You are {self.config.name}, a helpful AI assistant using the ReAct pattern. "
                           f"Available tools: {self._get_tool_names()}"
                ),
                LLMMessage(
                    role="user",
                    content=task
                )
            ]
            
            # Get response from LLM provider
            response = await self.llm_provider.complete(
                messages=messages,
                max_tokens=500,
                temperature=self.config.temperature
            )
            
            content = response.content
            total_tokens = response.tokens_used

            # Update statistics
            execution_time = self._get_current_time() - start_time
            self.stats.update(execution_time, True, total_tokens)

            return AgentResponse(
                content=content,
                success=True,
                execution_time=execution_time,
                tokens_used=total_tokens,
                metadata={"agent_type": "react", "task_type": "llm_completion"},
            )

        except Exception as e:
            execution_time = self._get_current_time() - start_time
            self.stats.update(execution_time, False, 0)

            return AgentResponse(
                content=f"Task execution failed: {str(e)}",
                success=False,
                execution_time=execution_time,
                error=str(e),
                metadata={"agent_type": "react", "error": True},
            )

    def _get_current_time(self) -> float:
        """Get current time for timing calculations"""
        import time

        return time.time()
    
    def _get_tool_names(self) -> str:
        """Get list of tool names from tools object"""
        if not self.tools:
            return "none"
        
        # Handle different tool registry types
        if hasattr(self.tools, 'list_tools'):
            return str(self.tools.list_tools())
        elif hasattr(self.tools, 'list_names'):
            return str(self.tools.list_names())
        elif hasattr(self.tools, '_tools'):
            return str(list(self.tools._tools.keys()))
        elif hasattr(self.tools, 'tools'):
            return str(list(self.tools.tools.keys()))
        else:
            return "none"


__all__ = ["ReactAgent"]
