#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
副业选择建议功能测试脚本
测试四个核心评估维度：时间投入、收益潜力、技能匹配、风险评估
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.smart_decision import create_side_business_analyzer
import json

def test_side_business_analysis():
    """测试副业选择建议分析基础功能"""
    print("=" * 60)
    print("🧪 测试副业选择建议分析功能")
    print("=" * 60)
    
    # 创建分析器
    analyzer = create_side_business_analyzer()
    
    # 测试用户画像
    user_profile = {
        "current_skills": ["Python", "JavaScript", "数据分析", "项目管理"],
        "experience_years": 5,
        "current_salary": 250000,
        "industry": "技术",
        "available_time": 20,  # 每周可用时间
        "side_business_budget": 50000,  # 副业预算
        "risk_tolerance": "medium"  # 风险承受能力
    }
    
    # 测试副业选项
    business_options = [
        {
            "business_name": "在线编程教育",
            "category": "在线教育",
            "weekly_hours": 15,
            "startup_time": 6,  # 启动时间(周)
            "monthly_revenue_potential": 12000,
            "startup_cost": 20000,
            "growth_rate": 25,  # 月增长率%
            "market_size": "large",
            "required_skills": ["Python", "教学能力", "视频制作"],
            "market_stability": "high",
            "competition_level": "medium"
        },
        {
            "business_name": "数据分析咨询",
            "category": "咨询服务",
            "weekly_hours": 12,
            "startup_time": 3,
            "monthly_revenue_potential": 8000,
            "startup_cost": 5000,
            "growth_rate": 15,
            "market_size": "medium",
            "required_skills": ["数据分析", "Python", "商业洞察"],
            "market_stability": "high",
            "competition_level": "low"
        },
        {
            "business_name": "软件开发外包",
            "category": "软件开发",
            "weekly_hours": 25,
            "startup_time": 2,
            "monthly_revenue_potential": 15000,
            "startup_cost": 10000,
            "growth_rate": 30,
            "market_size": "large",
            "required_skills": ["Python", "JavaScript", "项目管理"],
            "market_stability": "medium",
            "competition_level": "high"
        }
    ]
    
    # 执行分析
    print("🔍 正在分析副业选择方案...")
    result = analyzer.analyze_side_business_options(user_profile, business_options)
    
    # 验证结果结构
    assert "分析结果" in result, "缺少分析结果"
    assert "推荐副业" in result, "缺少推荐副业"
    assert "投资建议" in result, "缺少投资建议"
    assert "执行计划" in result, "缺少执行计划"
    
    print("\n📊 副业选择分析结果:")
    print("=" * 40)
    
    # 显示每个副业的详细分析
    for i, business in enumerate(result["分析结果"]):
        print(f"\n🏢 副业 {i+1}: {business['副业名称']}")
        print(f"类型: {business['副业类型']}")
        print(f"综合评分: {business['综合评分']}分 - {business['可行性建议']}")
        
        print(f"\n📅 时间投入:")
        time_info = business['时间投入']
        print(f"  评分: {time_info['评分']}分 - {time_info['时间等级']}")
        print(f"  分析: {time_info['可行性分析']}")
        print(f"  建议: {time_info['时间建议']}")
        
        print(f"\n💰 收益潜力:")
        revenue_info = business['收益潜力']
        print(f"  评分: {revenue_info['评分']}分 - {revenue_info['收益等级']}")
        print(f"  月收益: {revenue_info['月收益预期']}")
        print(f"  回报周期: {revenue_info['投资回报周期']}")
        print(f"  分析: {revenue_info['收益分析']}")
        
        print(f"\n🎯 技能匹配:")
        skill_info = business['技能匹配']
        print(f"  评分: {skill_info['评分']}分 - {skill_info['匹配等级']}")
        print(f"  匹配度: {skill_info['技能匹配度']}")
        print(f"  学习难度: {skill_info['学习难度']}")
        print(f"  建议: {skill_info['技能建议']}")
        
        print(f"\n⚠️ 风险评估:")
        risk_info = business['风险评估']
        print(f"  评分: {risk_info['评分']}分 - {risk_info['风险等级']}")
        print(f"  市场风险: {risk_info['市场风险']}")
        print(f"  财务风险: {risk_info['财务风险']}")
        print(f"  建议: {risk_info['风险建议']}")
        
        # 验证评分范围
        assert 0 <= business['综合评分'] <= 100, f"综合评分超出范围: {business['综合评分']}"
        assert 0 <= time_info['评分'] <= 100, f"时间投入评分超出范围: {time_info['评分']}"
        assert 0 <= revenue_info['评分'] <= 100, f"收益潜力评分超出范围: {revenue_info['评分']}"
        assert 0 <= skill_info['评分'] <= 100, f"技能匹配评分超出范围: {skill_info['评分']}"
        assert 0 <= risk_info['评分'] <= 100, f"风险评估评分超出范围: {risk_info['评分']}"
    
    print(f"\n🎯 推荐副业: {result['推荐副业']}")
    
    print(f"\n💡 投资建议:")
    for advice in result["投资建议"]:
        print(f"  • {advice}")
    
    print(f"\n📋 执行计划:")
    execution_plan = result["执行计划"]
    
    if "启动阶段" in execution_plan:
        print("  启动阶段:")
        for phase in execution_plan["启动阶段"]:
            print(f"    {phase['阶段']}: {phase['任务']} - {phase['重点']} ({phase['时间']})")
    
    if "时间安排" in execution_plan:
        print("  时间安排:")
        time_schedule = execution_plan["时间安排"]
        for key, value in time_schedule.items():
            print(f"    {key}: {value}")
    
    if "资源配置" in execution_plan:
        print("  资源配置:")
        resource_allocation = execution_plan["资源配置"]
        for key, value in resource_allocation.items():
            print(f"    {key}: {value}")
    
    if "里程碑" in execution_plan:
        print("  里程碑:")
        for milestone in execution_plan["里程碑"]:
            print(f"    • {milestone}")
    
    print("\n✅ 副业选择建议分析基础功能测试通过！")
    return True

def test_different_user_scenarios():
    """测试不同用户场景的副业选择分析"""
    print("\n" + "=" * 60)
    print("🧪 测试不同用户场景的副业选择分析")
    print("=" * 60)
    
    analyzer = create_side_business_analyzer()
    
    # 场景1: 时间充足的高级工程师
    scenario1_profile = {
        "current_skills": ["Python", "机器学习", "数据分析"],
        "experience_years": 8,
        "current_salary": 400000,
        "industry": "技术",
        "available_time": 25,
        "side_business_budget": 100000,
        "risk_tolerance": "high"
    }
    
    # 场景2: 时间有限的初级程序员
    scenario2_profile = {
        "current_skills": ["HTML", "CSS", "JavaScript"],
        "experience_years": 2,
        "current_salary": 120000,
        "industry": "技术",
        "available_time": 8,
        "side_business_budget": 15000,
        "risk_tolerance": "low"
    }
    
    business_options = [
        {
            "business_name": "AI咨询服务",
            "category": "咨询服务",
            "weekly_hours": 20,
            "startup_time": 8,
            "monthly_revenue_potential": 20000,
            "startup_cost": 30000,
            "growth_rate": 35,
            "market_size": "large",
            "required_skills": ["机器学习", "Python", "商业分析"],
            "market_stability": "high",
            "competition_level": "medium"
        },
        {
            "business_name": "网站制作服务",
            "category": "网站开发",
            "weekly_hours": 10,
            "startup_time": 2,
            "monthly_revenue_potential": 6000,
            "startup_cost": 5000,
            "growth_rate": 20,
            "market_size": "medium",
            "required_skills": ["HTML", "CSS", "JavaScript"],
            "market_stability": "medium",
            "competition_level": "high"
        }
    ]
    
    # 测试场景1
    print("\n🎭 场景1: 高级工程师")
    print("-" * 40)
    result1 = analyzer.analyze_side_business_options(scenario1_profile, business_options)
    
    print(f"用户信息: {scenario1_profile['experience_years']}年经验, 薪资{scenario1_profile['current_salary']:,}元")
    print(f"当前技能: {scenario1_profile['current_skills']}")
    print(f"可用时间: {scenario1_profile['available_time']}小时/周, 预算: {scenario1_profile['side_business_budget']:,}元")
    print(f"推荐副业: {result1['推荐副业']}")
    
    top_business1 = result1["分析结果"][0]
    print(f"副业评分:")
    for business in result1["分析结果"]:
        print(f"  {business['副业名称']}: {business['综合评分']}分 - {business['可行性建议']}")
    
    print("投资建议:")
    for advice in result1["投资建议"]:
        print(f"  • {advice}")
    
    # 测试场景2
    print("\n🎭 场景2: 初级程序员")
    print("-" * 40)
    result2 = analyzer.analyze_side_business_options(scenario2_profile, business_options)
    
    print(f"用户信息: {scenario2_profile['experience_years']}年经验, 薪资{scenario2_profile['current_salary']:,}元")
    print(f"当前技能: {scenario2_profile['current_skills']}")
    print(f"可用时间: {scenario2_profile['available_time']}小时/周, 预算: {scenario2_profile['side_business_budget']:,}元")
    print(f"推荐副业: {result2['推荐副业']}")
    
    print(f"副业评分:")
    for business in result2["分析结果"]:
        print(f"  {business['副业名称']}: {business['综合评分']}分 - {business['可行性建议']}")
    
    print("投资建议:")
    for advice in result2["投资建议"]:
        print(f"  • {advice}")
    
    # 验证不同场景的结果差异
    assert result1["推荐副业"] != result2["推荐副业"] or \
           result1["分析结果"][0]["综合评分"] != result2["分析结果"][0]["综合评分"], \
           "不同用户场景应该产生不同的分析结果"
    
    print("\n✅ 不同用户场景测试通过！")
    return True

def main():
    """主测试函数"""
    print("🚀 开始副业选择建议功能测试")
    
    try:
        # 测试基础功能
        test_side_business_analysis()
        
        # 测试不同场景
        test_different_user_scenarios()
        
        print("\n" + "=" * 60)
        print("📊 测试结果汇总")
        print("=" * 60)
        print("基础功能测试: ✅ 通过")
        print("不同场景测试: ✅ 通过")
        
        print(f"\n🎯 总体结果: 2/2 测试通过")
        print("🎉 所有测试通过！副业选择建议分析功能正常工作！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()