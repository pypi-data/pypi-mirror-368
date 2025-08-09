#!/usr/bin/env python3
"""
测试 get_global_countries 函数
"""

import sys
import os

# 添加模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

try:
    # 尝试导入函数
    from global_data import get_global_countries
    print("✅ 成功导入 get_global_countries")
    
    # 尝试调用函数
    result = get_global_countries()
    print(f"✅ 成功调用 get_global_countries，返回类型: {type(result)}")
    
    if isinstance(result, dict):
        print(f"✅ 返回字典，包含键: {list(result.keys())}")
        if 'supported_countries' in result:
            countries = result['supported_countries']
            print(f"✅ 支持的国家数量: {len(countries)}")
            print(f"✅ 前5个国家: {countries[:5]}")
    
    print("🎉 get_global_countries 函数工作正常！")
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
except Exception as e:
    print(f"❌ 调用失败: {e}")
    import traceback
    traceback.print_exc()