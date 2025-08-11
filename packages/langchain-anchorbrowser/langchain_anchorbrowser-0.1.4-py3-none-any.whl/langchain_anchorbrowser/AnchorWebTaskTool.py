from .AnchorBaseTool import AnchorBaseTool
from langchain_core.tools import BaseToolkit, BaseTool
from pydantic import Field, BaseModel

class SimpleAnchorWebTaskTool(AnchorBaseTool, BaseTool):
    name: str = "simple_anchor_web_task_tool"
    description: str = "Perform a simple web task using Anchor Browser AI"
    client_function_name: str = "perform_web_task"
    
    class SimpleWebTaskInputSchema(BaseModel):
        prompt: str = Field(description="The task prompt to execute")
        url: str = Field(default="https://example.com", description="Starting URL for the task")
    args_schema: type[BaseModel] = SimpleWebTaskInputSchema


class AdvancedAnchorWebTaskTool(AnchorBaseTool, BaseTool):
    name: str = "advanced_anchor_web_task_tool"
    description: str = "Perform an advanced web task using Anchor Browser AI"
    client_function_name: str = "perform_web_task"
    
    class AdvancedWebTaskInputSchema(BaseModel):
        prompt: str = Field(description="The task prompt to execute")
        url: str = Field(default="https://example.com", description="Starting URL for the task")
        output_schema: dict = Field(default={}, description="Output schema for structured results")

    args_schema: type[BaseModel] = AdvancedWebTaskInputSchema

class AnchorWebTaskToolKit(BaseToolkit):
    name: str = "anchor_web_task_tool_kit"
    description: str = "Perform a web task using Anchor Browser AI"

    def get_tools(self) -> list[BaseTool]:
        return [
            SimpleAnchorWebTaskTool(),
            AdvancedAnchorWebTaskTool(),
        ]
