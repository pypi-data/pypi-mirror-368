#!/usr/bin/env python3
"""
测试模块导入
"""
import sys
import os

# 添加模块路径
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_dir = os.path.join(current_dir, 'modules')
if modules_dir not in sys.path:
    sys.path.insert(0, modules_dir)

print(f"🔍 调试: 当前工作目录 = {os.getcwd()}")
print(f"🔍 调试: 脚本目录 = {current_dir}")
print(f"🔍 调试: 模块目录 = {modules_dir}")
print(f"🔍 调试: Python路径 = {sys.path[:3]}")

try:
    from global_data import get_global_countries
    print("✅ 成功导入 get_global_countries")
    
    result = get_global_countries()
    print(f"✅ 成功调用 get_global_countries，支持{result.get('支持国家数', 0)}个国家")
    print(f"🔍 调试: 返回数据类型 = {type(result)}")
    print(f"🔍 调试: 返回数据键 = {list(result.keys())}")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    print(f"🔍 调试: 堆栈跟踪 = {traceback.format_exc()}")