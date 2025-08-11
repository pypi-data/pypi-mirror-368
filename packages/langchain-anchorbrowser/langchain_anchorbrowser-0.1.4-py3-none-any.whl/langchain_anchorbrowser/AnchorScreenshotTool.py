from .AnchorBaseTool import AnchorBaseTool
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional

class AnchorScreenshotTool(AnchorBaseTool, BaseTool):
    name: str = "anchor_screenshot_tool"
    description: str = "Take a screenshot of a webpage using Anchor Browser"
    client_function_name: str = "screenshot_webpage"

    class InputSchema(BaseModel):
        url: str = Field(description="The URL of the webpage to screenshot")
        width: Optional[int] = Field(default=None, description="Width of the screenshot")
        height: Optional[int] = Field(default=None, description="Height of the screenshot")
        image_quality: Optional[int] = Field(default=None, description="Image quality (1-100)")
        wait: Optional[int] = Field(default=None, description="Wait time in milliseconds")
        scroll_all_content: Optional[bool] = Field(default=None, description="Whether to scroll all content")
        capture_full_height: Optional[bool] = Field(default=None, description="Whether to capture full height")
        s3_target_address: Optional[str] = Field(default=None, description="S3 target address for saving")
    
    args_schema: type[BaseModel] = InputSchema