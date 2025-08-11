# tests/test_core.py

import unittest
from GeoModelingZ import say_hello, get_current_time_str

class TestCore(unittest.TestCase):
    def test_say_hello(self):
        result = say_hello("测试")
        self.assertEqual(result, "Hello, 测试! Welcome to GeoModelingZ.")
        
    def test_get_current_time_str(self):
        result = get_current_time_str()
        # 简单测试返回的是字符串类型
        self.assertIsInstance(result, str)
        # 检查格式是否正确（包含年-月-日）
        self.assertTrue('-' in result)

if __name__ == "__main__":
    unittest.main()