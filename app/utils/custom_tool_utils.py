from typing import List
from langchain.tools import StructuredTool, tool
from langchain_core.tools import ToolException

class CustomToolUtils():
    def _try_except_wrapper(self, func):
        try:
            return func
        except ToolException as e:
            print(f"Error: {e}")

    def enhance_agent_tools(self, agent_tools: List):
        enhanced_agent_tools = [
            StructuredTool(
                name=tool.name,
                description=tool.description,
                args_schema=tool.args_schema,
                func=self._try_except_wrapper(tool._run),
                handle_tool_error=True,
                handle_validation_error=True
            ) for tool in agent_tools
        ]
        return enhanced_agent_tools
