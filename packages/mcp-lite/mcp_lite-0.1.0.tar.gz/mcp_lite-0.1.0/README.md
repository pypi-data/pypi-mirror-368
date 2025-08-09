# mcp-lite
The library for local work with AI tools without running MCP server.

### Installation

```python 
pip install mcp-lite
```

### Import

```python 
from mcp_lite import MCP
```

### Usage

```python 
mcp = MCP()


@mcp.tool
def sync_add(a, b):
    return a + b


@mcp.tool
async def async_mul(a, b):
    return a * b


tools = mcp.list_tools()

# Some code where AI calls some tools :)

for tool_call in tool_calls:
    tool_name = tool_call.get("tool_name")
    tool_args = tool_call.get("args", {})

    tool_result = await mcp.call_tool(tool_name, tool_args)

```
