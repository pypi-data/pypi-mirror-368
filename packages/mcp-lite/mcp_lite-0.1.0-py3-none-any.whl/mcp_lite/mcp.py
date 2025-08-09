import inspect
from typing import Callable

from .tool import Tool


__all__ = ['MCP']


class MCP:
    def __init__(self):
        self._tools = None

    def _tools_is_dict(self) -> bool:
        """Check if tools are a dict"""
        if isinstance(self._tools, dict):
            return True
        else:
            return False

    def _add_tool(self, tool: Tool) -> None:
        """Add tool to the MCP's tools"""
        self._tools[tool.name] = tool

    def tool(self, func: Callable) -> Callable:
        """Decorator to add a function as a tool"""
        new_tool = Tool(
            name=func.__name__,
            description=func.__doc__,
            is_async=inspect.iscoroutinefunction(func),
            func=func
        )
        if not self._tools_is_dict():
            self._tools = {}
        self._add_tool(new_tool)
        return func

    @property
    def tools(self) -> dict:
        """Get the MCP's tools"""
        if self._tools is None:
            return {}
        else:
            return self._tools

    def list_tools(self):
        return self.tools.values()

    async def call_tool(self, name: str, args: dict = None):
        """Call a tool by its name"""
        tool: Tool = self.tools.get(name)
        if tool is None:
            raise ValueError(f"Tool {name} not found")
        if args is None:
            args = {}
        if tool.is_async:
            return await tool.func(**args)
        else:
            return tool.func(**args)
