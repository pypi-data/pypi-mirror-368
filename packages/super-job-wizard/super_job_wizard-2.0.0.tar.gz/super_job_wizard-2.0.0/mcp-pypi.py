#!/usr/bin/env python3
"""
🚀 MCP工具开发模板
快速创建MCP工具的精简模板

使用步骤：
1. 填写下方配置信息
2. 替换工具函数为你的功能
3. 运行测试：python MCP_PyPI_template.py
4. 发布到PyPI：参考文件末尾的发布指南
"""

import json
import logging
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# ================================
# 🔧 配置区域 - 请填写以下信息
# ================================

# 基本信息（用于生成setup.py）
PACKAGE_NAME = "my-mcp-tool"  # PyPI包名（小写，用连字符）
TOOL_NAME = "我的MCP工具"  # 工具显示名称
VERSION = "0.1.0"  # 版本号
AUTHOR = "你的名字"  # 作者名
AUTHOR_EMAIL = "your.email@example.com"  # 作者邮箱
DESCRIPTION = "一个强大的MCP工具"  # 简短描述
URL = "https://github.com/yourusername/your-repo"  # 项目主页
LICENSE = "MIT"  # 许可证

# 依赖包列表
REQUIREMENTS = [
    "mcp>=1.0.0",
    "fastmcp>=0.1.0",
    # 在这里添加你的其他依赖
]

# ================================
# 🛠️ MCP工具核心代码
# ================================

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建MCP服务器
mcp = FastMCP(TOOL_NAME)

# ================================
# 🔧 在这里添加你的工具函数
# ================================

@mcp.tool()
def hello_world(name: str = "World") -> str:
    """
    一个简单的问候工具
    
    Args:
        name: 要问候的名字
    
    Returns:
        问候消息
    """
    return f"Hello, {name}! 这是来自 {TOOL_NAME} 的问候。"

@mcp.tool()
def get_current_time() -> str:
    """
    获取当前时间
    
    Returns:
        当前时间字符串
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@mcp.tool()
def calculate_sum(a: float, b: float) -> float:
    """
    计算两个数的和
    
    Args:
        a: 第一个数
        b: 第二个数
    
    Returns:
        两数之和
    """
    return a + b

# ================================
# 🚀 主函数
# ================================

def main():
    """启动MCP服务器"""
    logger.info(f"启动 {TOOL_NAME}...")
    logger.info(f"版本: {VERSION}")
    logger.info(f"作者: {AUTHOR}")
    mcp.run()

if __name__ == "__main__":
    main()

# ================================
# 🧪 本地测试指南
# ================================
"""
🧪 如何在本地测试MCP工具：

1. 直接运行测试：
   ```bash
   # 在当前目录直接运行
   python MCP_PyPI_template.py
   
   # 如果看到类似输出说明启动成功：
   # INFO:__main__:启动 我的MCP工具...
   # INFO:__main__:版本: 0.1.0
   # INFO:__main__:作者: 你的名字
   ```

2. 配置Trae AI客户端测试：
     在Trae AI中，可以直接使用内置的MCP连接功能：
     
     方法1 - 使用Trae AI的MCP面板：
     - 打开Trae AI的MCP连接面板
     - 添加新的MCP服务器
     - 设置命令：python
     - 设置参数：["d:/path/to/your/MCP_PyPI_template.py"]
     - 设置工作目录：d:/path/to/your/directory
     
     方法2 - 使用配置文件（如果支持）：
     ```json
     {
       "mcpServers": {
         "my-test-tool": {
           "command": "python",
           "args": [
             "d:/path/to/your/MCP_PyPI_template.py"
           ],
           "cwd": "d:/path/to/your/directory"
         }
       }
     }
     ```

 3. 连接MCP服务器并测试工具功能

 4. 验证工具是否正常工作：
     - 检查工具是否出现在Trae AI的工具列表中
     - 测试每个工具函数是否返回预期结果
     - 确认MCP连接状态正常，没有错误日志
     - 可以尝试调用hello_world、get_current_time等示例函数
     - 在Trae AI中直接与MCP工具交互测试

 5. 测试成功后再进行PyPI发布！

# ================================
# 📦 PyPI发布指南
# ================================

🚀 如何发布到PyPI：

⚠️ 重要：发布前必须先完成本地测试！

1. 准备项目结构：
   创建以下文件结构：
   my-mcp-tool/
   ├── my_mcp_tool/
   │   ├── __init__.py
   │   └── main.py  (复制本文件内容)
   ├── setup.py
   ├── README.md
   └── requirements.txt

2. 创建setup.py文件：
   ```python
   from setuptools import setup, find_packages
   
   with open("README.md", "r", encoding="utf-8") as fh:
       long_description = fh.read()
   
   setup(
       name="{PACKAGE_NAME}",
       version="{VERSION}",
       author="{AUTHOR}",
       author_email="{AUTHOR_EMAIL}",
       description="{DESCRIPTION}",
       long_description=long_description,
       long_description_content_type="text/markdown",
       url="{URL}",
       packages=find_packages(),
       classifiers=[
           "Development Status :: 3 - Alpha",
           "Intended Audience :: Developers",
           "License :: OSI Approved :: MIT License",
           "Operating System :: OS Independent",
           "Programming Language :: Python :: 3",
           "Programming Language :: Python :: 3.8+",
       ],
       python_requires=">=3.8",
       install_requires=[
           "mcp>=1.0.0",
           "fastmcp>=0.1.0",
       ],
       entry_points={
           "console_scripts": [
               "my-mcp-tool=my_mcp_tool.main:main",
           ],
       },
   )
   ```

3. 创建requirements.txt：
   ```
   mcp>=1.0.0
   fastmcp>=0.1.0
   ```

4. 创建README.md：
   ```markdown
   # {TOOL_NAME}
   
   {DESCRIPTION}
   
   ## 安装
   
   ```bash
   pip install {PACKAGE_NAME}
   ```
   
   ## 使用
   
   ```bash
   {PACKAGE_NAME}
   ```
   ```

5. 构建和上传：
   ```bash
   # 安装构建工具
   pip install build twine
   
   # 构建包
   python -m build
   
   # 上传到PyPI（需要先注册PyPI账号并获取API Token）
   twine upload dist/*
   ```

6. 使用API Token上传，用户必须提供token或用户名密码，否则上传失败，提示用户提供信息：
   ```bash
   # 方法1：环境变量
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=pypi-your-api-token-here
   twine upload dist/*
   
   # 方法2：直接指定
   twine upload -u __token__ -p pypi-your-api-token-here dist/*
   ```

📝 注意事项：
- 用户必须提前注册PyPI账号，并获取API Token
- 包名必须在PyPI上唯一
- 建议先上传到TestPyPI测试：twine upload --repository testpypi dist/*
- API Token比用户名密码更安全，推荐使用
- 每次发布前记得更新版本号

7. 发布后验证：
   ```bash
   # 安装你发布的包
   pip install your-package-name
   
   # 测试命令行工具
   your-package-name
   ```

8. MCP客户端配置（发布后）：
   ```json
   {
     "mcpServers": {
       "your-mcp-server": {
         "command": "uvx",
         "args": [
           "your-mcp-tool"
         ]
       }
     }
   }
   ```

🎉 完整流程总结：
本地开发 → 本地测试 → 构建包 → 上传PyPI → 安装验证 → 配置使用

"""


