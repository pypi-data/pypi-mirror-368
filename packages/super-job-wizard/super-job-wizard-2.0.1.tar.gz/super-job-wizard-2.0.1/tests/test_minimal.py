#!/usr/bin/env python3
"""
最小化测试版本 - 只测试get_supported_countries
"""

from fastmcp import FastMCP
from typing import Dict

# 创建MCP实例
mcp = FastMCP("测试版本")

@mcp.tool()
def get_supported_countries() -> Dict:
    """获取支持的全球国家列表"""
    print("🔍 调试: 最小化测试函数被调用了！")
    
    result = {
        "total_countries": 150,
        "sample_countries": ["China", "USA", "Japan", "Germany", "UK"],
        "status": "✅ 最小化测试版本正常工作"
    }
    print(f"🔍 调试: 返回结果 = {result}")
    return result

@mcp.tool()
def test_simple_function() -> Dict:
    """简单测试函数"""
    return {"message": "Hello World", "status": "OK"}

if __name__ == "__main__":
    print("🚀 启动最小化测试版本...")
    mcp.run()