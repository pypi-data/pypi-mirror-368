#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通过MCP客户端测试面试题库生成器
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 直接导入并测试MCP工具函数
from super_job_wizard import generate_interview_questions_ai

def test_mcp_water_quality_interview():
    """通过MCP工具测试水质监测面试题库生成"""
    print("🎭 MCP面试题库生成器测试 - 水质在线监测")
    print("=" * 50)
    
    try:
        # 调用MCP工具函数
        result = generate_interview_questions_ai(
            position="水质在线监测工程师",
            company="环保科技有限公司",
            experience_level="中级",
            question_types=["技术面试", "行为面试", "案例面试"]
        )
        
        print("✅ MCP工具调用成功！")
        print(f"🎯 功能类型: {result.get('功能类型', 'N/A')}")
        print(f"🔧 引擎版本: {result.get('引擎版本', 'N/A')}")
        print(f"📋 应用场景: {result.get('应用场景', 'N/A')}")
        
        # 分析结果
        analysis_result = result.get("分析结果", {})
        if analysis_result:
            print("\n📊 分析结果概览:")
            
            # 题库概述
            overview = analysis_result.get("面试题库概述", {})
            if overview:
                print(f"  目标职位: {overview.get('目标职位', 'N/A')}")
                print(f"  目标公司: {overview.get('目标公司', 'N/A')}")
                print(f"  经验水平: {overview.get('经验水平', 'N/A')}")
                print(f"  总题目数: {overview.get('总题目数', 0)}")
            
            # 定制化题库
            questions = analysis_result.get("定制化题库", {})
            if questions:
                print("\n📚 生成的题库:")
                for q_type, q_list in questions.items():
                    print(f"  {q_type}: {len(q_list)}题")
                    # 显示前2题作为示例
                    for i, question in enumerate(q_list[:2], 1):
                        print(f"    {i}. {question}")
                    if len(q_list) > 2:
                        print(f"    ... 还有{len(q_list)-2}题")
            
            # 准备建议
            tips = analysis_result.get("准备建议", {})
            if tips:
                print("\n💡 准备建议:")
                for tip_type, tip_content in tips.items():
                    if isinstance(tip_content, list):
                        print(f"  {tip_type}: {', '.join(tip_content[:3])}")
                    else:
                        print(f"  {tip_type}: {tip_content}")
        
        print("\n🎉 水质在线监测面试题库生成测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_mcp_water_quality_interview()