from typing import Optional
from langchain.tools import BaseTool, tool as langchain_tool
from agentmail import AgentMail

from .toolkit import Toolkit
from .tools import Tool


class AgentMailToolkit(Toolkit[BaseTool]):
    def __init__(self, client: Optional[AgentMail] = None):
        super().__init__(client)

    def _build_tool(self, tool: Tool):
        def runnable(**kwargs):
            return self.call_method(tool.method_name, kwargs)

        return langchain_tool(
            name_or_callable=tool.name,
            description=tool.description,
            args_schema=tool.params_schema,
            runnable=runnable,
        )
