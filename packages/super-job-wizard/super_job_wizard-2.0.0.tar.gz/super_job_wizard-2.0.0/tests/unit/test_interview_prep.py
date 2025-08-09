#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
面试准备工具测试脚本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.smart_decision import create_interview_preparation_analyzer

def test_interview_preparation():
    """测试面试准备分析器功能"""
    print("🎭 开始测试面试准备分析器...")
    
    try:
        # 创建分析器
        analyzer = create_interview_preparation_analyzer()
        print("✅ 面试准备分析器创建成功")
        
        # 测试数据
        test_data = {
            "position": "Python后端开发工程师",
            "company": "字节跳动",
            "experience_level": "中级",
            "tech_stack": ["Python", "Django", "Redis", "MySQL"],
            "user_profile": {
                "name": "张三",
                "experience": "3年Python开发经验",
                "skills": ["Python", "Django", "Flask", "MySQL", "Redis"],
                "projects": ["电商系统", "用户管理系统"]
            }
        }
        
        # 测试AI面试题库生成
        print("\n📝 测试AI面试题库生成...")
        questions = analyzer.generate_ai_interview_questions(
            position=test_data["position"],
            company=test_data["company"],
            experience_level=test_data["experience_level"],
            tech_stack=test_data["tech_stack"]
        )
        print(f"✅ 生成了 {len(questions.get('technical_questions', []))} 道技术题")
        print(f"✅ 生成了 {len(questions.get('behavioral_questions', []))} 道行为题")
        
        # 测试虚拟面试模拟
        print("\n🎯 测试虚拟面试模拟...")
        interview_data = {
            "questions": ["请介绍一下Python的GIL机制", "描述一次你解决技术难题的经历"],
            "answers": ["GIL是全局解释器锁...", "在项目中遇到性能问题时..."],
            "interview_type": "技术面试"
        }
        simulation = analyzer.simulate_virtual_interview(interview_data)
        print(f"✅ 面试模拟完成，总分: {simulation.get('overall_score', 0)}")
        
        # 测试行为面试答案生成
        print("\n💬 测试行为面试答案生成...")
        behavioral_answer = analyzer.generate_behavioral_interview_answers(
            question="描述一次你在团队中解决冲突的经历",
            user_profile=test_data["user_profile"]
        )
        print("✅ 行为面试答案生成成功")
        
        print("\n🎉 所有测试通过！面试准备工具运行正常！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_interview_preparation()