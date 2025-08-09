#!/usr/bin/env python3
"""
调试AI分析器问题
"""

import sys
import os

# 添加模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from ai_analyzer import AIJobAnalyzer
    
    print("✅ AI分析器导入成功")
    
    # 创建实例
    analyzer = AIJobAnalyzer()
    print("✅ AI分析器实例创建成功")
    
    # 测试方法
    print("\n🔍 测试analyze_market_trends方法...")
    print(f"方法签名: {analyzer.analyze_market_trends.__code__.co_varnames}")
    print(f"参数数量: {analyzer.analyze_market_trends.__code__.co_argcount}")
    
    # 尝试调用
    result = analyzer.analyze_market_trends("水质在线监测", "中国")
    print("✅ 方法调用成功!")
    print(f"结果: {result}")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()