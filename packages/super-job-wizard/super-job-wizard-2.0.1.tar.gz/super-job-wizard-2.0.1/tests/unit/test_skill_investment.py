#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能投资决策分析功能测试脚本
测试技能投资决策分析器的各项功能
"""

import sys
import os
import json
from typing import Dict, List

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

def setup_test_environment():
    """设置测试环境"""
    print("🔧 设置测试环境...")
    
    # 确保模块路径正确
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    print(f"✅ 项目根目录: {project_root}")
    print(f"✅ 源码路径: {src_path}")
    print(f"✅ Python路径: {sys.path[:3]}")

def test_skill_investment_analysis():
    """测试技能投资决策分析基础功能"""
    print("\n" + "="*60)
    print("🧪 测试技能投资决策分析基础功能")
    print("="*60)
    
    try:
        # 导入测试函数
        from super_job_wizard import analyze_skill_investment
        
        # 准备测试数据
        user_profile = {
            "current_skills": ["Python", "JavaScript", "HTML", "CSS"],
            "experience_years": 3,
            "current_salary": 180000,
            "industry": "技术",
            "career_goal": "高级工程师",
            "learning_capacity": "高",
            "time_budget": 12,  # 每周12小时
            "budget": 8000  # 学习预算8000元
        }
        
        skill_options = [
            {
                "skill_name": "React",
                "category": "前端框架",
                "difficulty": "中等",
                "learning_time": 100,
                "cost": 3000,
                "market_demand": 88,
                "salary_impact": 25000
            },
            {
                "skill_name": "机器学习",
                "category": "AI",
                "difficulty": "困难",
                "learning_time": 200,
                "cost": 5000,
                "market_demand": 95,
                "salary_impact": 40000
            },
            {
                "skill_name": "Vue",
                "category": "前端框架",
                "difficulty": "中等",
                "learning_time": 80,
                "cost": 2500,
                "market_demand": 75,
                "salary_impact": 20000
            }
        ]
        
        print("📊 用户画像:")
        print(f"  当前技能: {user_profile['current_skills']}")
        print(f"  工作经验: {user_profile['experience_years']}年")
        print(f"  当前薪资: {user_profile['current_salary']:,}元")
        print(f"  职业目标: {user_profile['career_goal']}")
        print(f"  学习能力: {user_profile['learning_capacity']}")
        print(f"  时间预算: {user_profile['time_budget']}小时/周")
        print(f"  学习预算: {user_profile['budget']:,}元")
        
        print("\n🎯 技能选项:")
        for i, skill in enumerate(skill_options, 1):
            print(f"  {i}. {skill['skill_name']} ({skill['category']})")
            print(f"     难度: {skill['difficulty']}, 学习时间: {skill['learning_time']}小时")
            print(f"     成本: {skill['cost']:,}元, 市场需求: {skill['market_demand']}")
            print(f"     预期薪资提升: {skill['salary_impact']:,}元")
        
        # 执行分析
        print("\n🔍 执行技能投资决策分析...")
        result = analyze_skill_investment(user_profile, skill_options)
        
        # 验证结果
        print("\n📋 分析结果验证:")
        
        # 检查必要字段
        required_fields = ["分析结果", "推荐技能", "投资建议", "学习路径"]
        for field in required_fields:
            if field in result:
                print(f"  ✅ {field}: 存在")
            else:
                print(f"  ❌ {field}: 缺失")
                return False
        
        # 检查分析结果
        analysis_results = result["分析结果"]
        if len(analysis_results) == len(skill_options):
            print(f"  ✅ 分析结果数量: {len(analysis_results)} (正确)")
        else:
            print(f"  ❌ 分析结果数量: {len(analysis_results)} (应为{len(skill_options)})")
            return False
        
        # 检查评分范围
        for skill_result in analysis_results:
            score = skill_result.get("综合评分", 0)
            if 0 <= score <= 100:
                print(f"  ✅ {skill_result['技能名称']} 评分: {score} (合理范围)")
            else:
                print(f"  ❌ {skill_result['技能名称']} 评分: {score} (超出范围)")
                return False
        
        # 显示详细结果
        print("\n🎯 推荐技能:", result["推荐技能"])
        
        print("\n📊 各技能详细分析:")
        for skill_result in analysis_results:
            print(f"\n  🔸 {skill_result['技能名称']} (综合评分: {skill_result['综合评分']})")
            print(f"    市场需求度: {skill_result['市场需求度']['评分']} - {skill_result['市场需求度']['需求等级']}")
            print(f"    学习难度: {skill_result['学习难度']['评分']} - {skill_result['学习难度']['难度等级']}")
            print(f"    ROI预期: {skill_result['ROI预期']['评分']} - {skill_result['ROI预期']['投资回报等级']}")
            print(f"    个人匹配度: {skill_result['个人匹配度']['评分']} - {skill_result['个人匹配度']['匹配等级']}")
            print(f"    投资建议: {skill_result['投资建议']}")
        
        print("\n💡 投资建议:")
        for advice in result["投资建议"]:
            print(f"  • {advice}")
        
        print("\n📅 学习路径:")
        learning_path = result["学习路径"]
        print(f"  推荐顺序: {learning_path.get('推荐顺序', [])}")
        
        if "学习阶段" in learning_path:
            print("  学习阶段:")
            for phase in learning_path["学习阶段"]:
                print(f"    {phase['阶段']}: {phase['技能']} - {phase['重点']} ({phase['时间']})")
        
        if "时间规划" in learning_path:
            time_plan = learning_path["时间规划"]
            print(f"  时间规划: {time_plan.get('每周总投入', 'N/A')}")
            print(f"  建议分配: {time_plan.get('建议分配', 'N/A')}")
        
        if "预算分配" in learning_path:
            budget_plan = learning_path["预算分配"]
            print(f"  预算分配: {budget_plan.get('总预算', 'N/A')}")
            print(f"  分配建议: {budget_plan.get('分配建议', 'N/A')}")
        
        print("\n✅ 技能投资决策分析基础功能测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_different_user_scenarios():
    """测试不同用户场景的技能投资分析"""
    print("\n" + "="*60)
    print("🧪 测试不同用户场景的技能投资分析")
    print("="*60)
    
    try:
        from super_job_wizard import analyze_skill_investment
        
        # 定义不同用户场景
        scenarios = [
            {
                "name": "新手程序员",
                "user_profile": {
                    "current_skills": ["HTML", "CSS"],
                    "experience_years": 1,
                    "current_salary": 80000,
                    "industry": "技术",
                    "career_goal": "全栈工程师",
                    "learning_capacity": "中",
                    "time_budget": 8,
                    "budget": 3000
                },
                "skill_options": [
                    {
                        "skill_name": "JavaScript",
                        "category": "编程语言",
                        "difficulty": "中等",
                        "learning_time": 120,
                        "cost": 2000,
                        "market_demand": 90,
                        "salary_impact": 30000
                    },
                    {
                        "skill_name": "Python",
                        "category": "编程语言",
                        "difficulty": "简单",
                        "learning_time": 100,
                        "cost": 1500,
                        "market_demand": 85,
                        "salary_impact": 25000
                    }
                ]
            },
            {
                "name": "资深工程师",
                "user_profile": {
                    "current_skills": ["Python", "JavaScript", "React", "Node.js", "SQL"],
                    "experience_years": 8,
                    "current_salary": 350000,
                    "industry": "技术",
                    "career_goal": "技术专家",
                    "learning_capacity": "高",
                    "time_budget": 15,
                    "budget": 15000
                },
                "skill_options": [
                    {
                        "skill_name": "Kubernetes",
                        "category": "架构",
                        "difficulty": "困难",
                        "learning_time": 150,
                        "cost": 8000,
                        "market_demand": 92,
                        "salary_impact": 50000
                    },
                    {
                        "skill_name": "机器学习",
                        "category": "AI",
                        "difficulty": "困难",
                        "learning_time": 200,
                        "cost": 10000,
                        "market_demand": 95,
                        "salary_impact": 60000
                    }
                ]
            }
        ]
        
        for scenario in scenarios:
            print(f"\n🎭 场景: {scenario['name']}")
            print("-" * 40)
            
            user_profile = scenario['user_profile']
            skill_options = scenario['skill_options']
            
            print(f"用户信息: {user_profile['experience_years']}年经验, 薪资{user_profile['current_salary']:,}元")
            print(f"当前技能: {user_profile['current_skills']}")
            print(f"学习预算: {user_profile['budget']:,}元, 时间预算: {user_profile['time_budget']}小时/周")
            
            # 执行分析
            result = analyze_skill_investment(user_profile, skill_options)
            
            # 显示关键结果
            print(f"推荐技能: {result['推荐技能']}")
            
            # 显示各技能评分
            print("技能评分:")
            for skill_result in result["分析结果"]:
                print(f"  {skill_result['技能名称']}: {skill_result['综合评分']}分 - {skill_result['投资建议']}")
            
            # 显示投资建议
            print("投资建议:")
            for advice in result["投资建议"][:3]:  # 显示前3条建议
                print(f"  • {advice}")
        
        print("\n✅ 不同用户场景测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 技能投资决策分析功能测试")
    print("="*60)
    
    # 设置测试环境
    setup_test_environment()
    
    # 执行测试
    test_results = []
    
    # 测试1: 基础功能
    print("\n📋 开始测试...")
    test_results.append(("基础功能测试", test_skill_investment_analysis()))
    
    # 测试2: 不同场景
    test_results.append(("不同场景测试", test_different_user_scenarios()))
    
    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！技能投资决策分析功能正常工作！")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)