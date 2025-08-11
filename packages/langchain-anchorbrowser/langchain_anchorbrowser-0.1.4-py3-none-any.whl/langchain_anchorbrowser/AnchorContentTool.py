from .AnchorBaseTool import AnchorBaseTool
from langchain_core.tools import BaseTool
from pydantic import Field, BaseModel
from typing import Optional, Literal

class AnchorContentTool(AnchorBaseTool, BaseTool):
    name: str = "anchor_content_tool"
    description: str = "Get the content of a webpage using Anchor Browser"
    client_function_name: str = "fetch_webpage"
    
    class InputSchema(BaseModel):
        url: str = Field(description="The URL of the webpage to get content from")
        format: Optional[Literal['markdown', 'html']] = Field(default='markdown', description="Format of the content")
    
    args_schema: type[BaseModel] = InputSchema
