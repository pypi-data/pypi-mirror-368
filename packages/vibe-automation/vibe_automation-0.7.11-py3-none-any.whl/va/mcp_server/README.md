# MCP Web Automation Server

A Model Context Protocol (MCP) server that provides web automation capabilities using Playwright.

## Features

- **get_page_snapshot**: Get AI-optimized page structure
- **execute_python_command**: Execute Python/Playwright code
- **find_element_by_ref**: Find elements by reference from snapshots
- **get_page_screenshot**: Take page screenshots
- **navigate_to_url**: Navigate to specific URLs

## Installation

**IMPORTANT**: Make sure to follow all installation instructions in the main README.md.

### Claude code

Run the following command. Make sure to replace the path with your own path to the repo:

```shell
# Normal mode
claude mcp add-json vibe-automation '{"command": "uv", "args": ["--directory", "/path/to/vibe-automation", "run", "va", "mcp"]}' 

# Vision mode
claude mcp add-json vibe-automation '{"command": "uv", "args": ["--directory", "/path/to/vibe-automation", "run", "va", "mcp", "--mode=vision-html"]}' 
```

## Usage

Once configured, Claude Code will automatically have access to web automation tools:

1. **Navigate to a page**: `navigate_to_url`
2. **Understand the page**: `get_page_snapshot`
3. **Find elements**: `find_element_by_ref`
4. **Test automation**: `execute_python_command`
5. **Visual verification**: `get_page_screenshot`

## Workflow

The server guides Claude Code to:
1. Start with `get_page_snapshot()` to understand page structure
2. Use `find_element_by_ref()` to get proper locators from refs
3. Test Playwright commands incrementally with `execute_python_command()`
4. Build final automation script from successful commands