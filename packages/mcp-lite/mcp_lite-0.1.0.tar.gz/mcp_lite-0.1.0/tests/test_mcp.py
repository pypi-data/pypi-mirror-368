import unittest
import asyncio

from mcp_lite import MCP


class TestMCP(unittest.IsolatedAsyncioTestCase):
    def test_tool_init(self):
        mcp = MCP()
        assert mcp._tools is None

    def test_tool_decorator(self):
        mcp = MCP()

        @mcp.tool
        def test_func():
            return 10

        assert test_func.__name__ == 'test_func'
        assert "test_func" in mcp.tools
        assert len(mcp.list_tools()) == 1

    async def test_call_tool_sync(self):
        mcp = MCP()

        @mcp.tool
        def test_func():
            return 2 + 2

        result = await mcp.call_tool("test_func")
        self.assertEqual(result, 4)

    async def test_call_tool_async(self):
        mcp = MCP()

        @mcp.tool
        async def test_func():
            await asyncio.sleep(0)
            return 2 + 2

        result = await mcp.call_tool("test_func")
        self.assertEqual(result, 4)

    async def test_call_tool_non_existent(self):
        mcp = MCP()
        with self.assertRaises(ValueError) as cm:
            await mcp.call_tool("non_existent")
        self.assertEqual(str(cm.exception), "Tool non_existent not found")


if __name__ == "__main__":
    unittest.main()
