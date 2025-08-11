from .AnchorBaseTool import AnchorBaseTool
from langchain_core.tools import BaseToolkit, BaseTool
from pydantic import Field, BaseModel
from typing import Literal

class SimpleAnchorWebTaskTool(AnchorBaseTool, BaseTool):
    name: str = "simple_anchor_web_task_tool"
    description: str = "Perform a simple web task using Anchor Browser AI"
    client_function_name: str = "perform_web_task"
    
    class SimpleWebTaskInputSchema(BaseModel):
        prompt: str = Field(description="The task prompt to execute")
        url: str = Field(default="https://example.com", description="Starting URL for the task")

    args_schema: type[BaseModel] = SimpleWebTaskInputSchema

class StandardAnchorWebTaskTool(AnchorBaseTool, BaseTool):
    name: str = "standard_anchor_web_task_tool"
    description: str = "Perform a standard web task using Anchor Browser AI"
    client_function_name: str = "perform_web_task"
    
    class StandardWebTaskInputSchema(BaseModel):
        prompt: str = Field(description="The task prompt to execute")
        url: str = Field(default="https://example.com", description="Starting URL for the task")
        agent: Literal['browser-use', 'openai-cua'] = Field(default='browser-use', description="Agent type to use")
        provider: Literal['openai', 'gemini', 'groq', 'azure'] = Field(default='openai', description="AI provider")
        model: str = Field(default='gpt-4o-mini', description="Model to use")

    args_schema: type[BaseModel] = StandardWebTaskInputSchema

class AdvancedAnchorWebTaskTool(AnchorBaseTool, BaseTool):
    name: str = "advanced_anchor_web_task_tool"
    description: str = "Perform an advanced web task using Anchor Browser AI"
    client_function_name: str = "perform_web_task"
    
    class AdvancedWebTaskInputSchema(BaseModel):
        prompt: str = Field(description="The task prompt to execute")
        url: str = Field(default="https://example.com", description="Starting URL for the task")
        agent: Literal['browser-use', 'openai-cua'] = Field(default='browser-use', description="Agent type to use")
        provider: Literal['openai', 'gemini', 'groq', 'azure'] = Field(default='openai', description="AI provider")
        model: str = Field(default='gpt-4o-mini', description="Model to use")
        highlight_elements: bool = Field(default=False, description="Whether to highlight elements")
        output_schema: str = Field(default='json', description="Output schema for structured results")

    args_schema: type[BaseModel] = AdvancedWebTaskInputSchema

class AnchorWebTaskToolKit(BaseToolkit):
    name: str = "anchor_web_task_tool_kit"
    description: str = "Perform a web task using Anchor Browser AI"

    def get_tools(self) -> list[BaseTool]:
        return [
            SimpleAnchorWebTaskTool(),
            StandardAnchorWebTaskTool(),
            AdvancedAnchorWebTaskTool(),
        ]
