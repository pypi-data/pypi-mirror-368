import unittest
import inspect


from mcp_lite import Tool


async def async_add(a, b):
    return a + b


def sync_mul(a, b):
    return a * b


class TestToolIsolatedAsyncio(unittest.IsolatedAsyncioTestCase):
    async def test_defaults(self):
        t = Tool()
        self.assertEqual(t.name, "")
        self.assertEqual(t.description, "")
        self.assertFalse(t.is_async)
        self.assertIsNone(t.func)

    async def test_async_func_correct_flag(self):
        t = Tool(name="adder", is_async=True, func=async_add)
        self.assertTrue(t.is_async)
        self.assertIs(t.func, async_add)
        self.assertTrue(inspect.iscoroutinefunction(t.func))

    async def test_sync_func_correct_flag(self):
        t = Tool(name="mult", is_async=False, func=sync_mul)
        self.assertFalse(t.is_async)
        self.assertIs(t.func, sync_mul)
        self.assertFalse(inspect.iscoroutinefunction(t.func))

    async def test_async_func_flag_mismatch_raises(self):
        with self.assertRaises(ValueError):
            Tool(name="wrong", is_async=False, func=async_add)

    async def test_sync_func_flag_mismatch_raises(self):
        with self.assertRaises(ValueError):
            Tool(name="wrong", is_async=True, func=sync_mul)

    async def test_call_async_func(self):
        t = Tool(name="adder", is_async=True, func=async_add)
        result = await t.func(2, 3)
        self.assertEqual(result, 5)

    async def test_call_sync_func(self):
        t = Tool(name="mult", is_async=False, func=sync_mul)
        result = t.func(4, 5)
        self.assertEqual(result, 20)


if __name__ == "__main__":
    unittest.main()
