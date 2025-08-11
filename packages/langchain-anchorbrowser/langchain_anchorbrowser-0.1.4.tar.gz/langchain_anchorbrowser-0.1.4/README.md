# LangChain Anchor Browser Integration

A LangChain integration for Anchor Browser, providing tools to interact with web pages programmatically through AI-driven automation.

## Features

- **Content Extraction**: Extract text content from web pages
- **Screenshot Capture**: Take screenshots of web pages
- **AI Web Tasks**: Perform intelligent web tasks using AI (Simple, Standard, Advanced modes)

## Installation

```bash
pip install langchain-anchorbrowser
```

## Quick Start

### 1. Set up your API key

You can set your API key in advance, or you'll be prompted for it when you first run a tool.
```bash
export ANCHORBROWSER_API_KEY="your_api_key_here"
```
don't have Anchor's API Key yet? [register here](https://anchorbrowser.io/).


### 2. Running tutorial-demo.py

```bash
from langchain_anchorbrowser import AnchorContentTool
# Use content tool
content_result = AnchorContentTool().invoke({
    "url": "https://www.anchorbrowser.io",
    "format": "markdown"
})

print(content_result)
```

## Testing

See tests/README.md


