# tools/tool_registry.py
from typing import Dict
from .base_tool import BaseTool

class ToolRegistry:
    """
    A registry to store and retrieve tool instances by name.
    """
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register_tool(self, name: str, tool: BaseTool):
        self._tools[name] = tool

    def get_tool(self, name: str) -> BaseTool:
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found in registry.")
        return tool
