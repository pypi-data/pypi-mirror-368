#!/usr/bin/env python3
"""
🧠 Smart Decision 智能决策引擎测试脚本
测试决策分析、风险评估、ROI计算等核心功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.smart_decision import SmartDecisionEngine
import json

def test_job_decision_analysis():
    """测试工作选择决策分析"""
    print("🎯 测试工作选择决策分析功能...")
    
    engine = SmartDecisionEngine()
    
    # 模拟工作选择
    job_options = [
        {
            "company": "腾讯",
            "salary": 350000,
            "bonus_ratio": 0.25,
            "equity_value": 150000,
            "benefits_score": 85,
            "career_growth_score": 8,
            "industry_outlook_score": 9,
            "learning_opportunities": 8,
            "culture_score": 8,
            "workload_score": 6,
            "environment_score": 9,
            "financial_stability": 9,
            "market_position": 9,
            "business_model_score": 8,
            "skill_match_score": 8,
            "interest_match_score": 7,
            "value_match_score": 8,
            "company_size": "large",
            "industry": "互联网",
            "company_reputation": 9,
            "industry_recognition": 9,
            "skill_growth_potential": 8,
            "industry_influence": 8,
            "learning_curve_months": 2
        },
        {
            "company": "字节跳动",
            "salary": 380000,
            "bonus_ratio": 0.3,
            "equity_value": 200000,
            "benefits_score": 80,
            "career_growth_score": 9,
            "industry_outlook_score": 9,
            "learning_opportunities": 9,
            "culture_score": 7,
            "workload_score": 5,  # 工作强度较大
            "environment_score": 8,
            "financial_stability": 8,
            "market_position": 9,
            "business_model_score": 8,
            "skill_match_score": 9,
            "interest_match_score": 8,
            "value_match_score": 7,
            "company_size": "large",
            "industry": "互联网",
            "company_reputation": 8,
            "industry_recognition": 9,
            "skill_growth_potential": 9,
            "industry_influence": 9,
            "learning_curve_months": 3
        },
        {
            "company": "AI创业公司",
            "salary": 320000,
            "bonus_ratio": 0.15,
            "equity_value": 300000,
            "benefits_score": 70,
            "career_growth_score": 9,
            "industry_outlook_score": 10,
            "learning_opportunities": 10,
            "culture_score": 9,
            "workload_score": 6,
            "environment_score": 8,
            "financial_stability": 6,  # 创业公司风险
            "market_position": 7,
            "business_model_score": 7,
            "skill_match_score": 9,
            "interest_match_score": 9,
            "value_match_score": 9,
            "company_size": "startup",
            "industry": "AI",
            "company_reputation": 7,
            "industry_recognition": 8,
            "skill_growth_potential": 10,
            "industry_influence": 7,
            "learning_curve_months": 4
        }
    ]
    
    # 用户画像
    user_profile = {
        "current_salary": 280000,
        "risk_tolerance": "medium",
        "career_focus": "growth",
        "work_style": "innovative",
        "skill_level": 7,
        "learning_ability": 8,
        "network_size": 150,
        "other_opportunities_value": 50000
    }
    
    # 执行决策分析
    result = engine.analyze_job_decision(job_options, user_profile)
    
    print("📊 决策分析完成！")
    print(f"🎭 用户性格类型: {engine._determine_personality_type(user_profile)}")
    
    # 显示决策评分
    print("\n📈 决策评分排名:")
    for company, scores in result["决策分析"].items():
        print(f"   {company}: {scores['总分']}分 ({scores['等级']})")
    
    # 显示风险评估
    print("\n⚠️ 风险评估:")
    for company, risk_data in result["风险评估"].items():
        risk_level = "低风险" if risk_data["总体风险"] < 0.3 else "中等风险" if risk_data["总体风险"] < 0.5 else "高风险"
        print(f"   {company}: {risk_data['总体风险']:.3f} ({risk_level})")
        
        # 显示主要风险
        main_risks = risk_data["主要风险"][:2]
        for risk in main_risks:
            print(f"     - {risk['风险']}: {risk['评分']:.3f}")
    
    # 显示ROI分析
    print("\n💰 ROI分析:")
    for company, roi_data in result["ROI计算"].items():
        print(f"   {company}: {roi_data['净ROI']}% (回报周期: {roi_data['回报周期']})")
        print(f"     年度总收益: ¥{roi_data['直接收益']['年度总收益']:,.0f}")
    
    # 显示决策矩阵
    print("\n🎯 决策矩阵:")
    matrix = result["决策矩阵"]["详细对比"]
    for option in matrix:
        print(f"   排名{option['排名']}: {option['选择']} (综合评分: {option['综合评分']})")
    
    # 显示最终建议
    recommendation = result["最终建议"]
    print(f"\n🏆 推荐选择: {recommendation['推荐选择']}")
    print(f"🔮 决策信心: {recommendation['决策信心']}")
    
    print("✅ 工作选择决策分析测试完成！")
    return result

def test_career_trajectory_prediction():
    """测试职业发展轨迹预测"""
    print("\n🚀 测试职业发展轨迹预测功能...")
    
    engine = SmartDecisionEngine()
    
    # 当前状态
    current_profile = {
        "level": "中级",
        "current_salary": 280000,
        "skill_level": 7,
        "learning_ability": 8,
        "experience_years": 5
    }
    
    # 目标设定
    target_goals = {
        "target_level": "专家",
        "target_salary": 500000,
        "target_timeframe": "5年"
    }
    
    # 执行预测
    prediction = engine.predict_career_trajectory(current_profile, target_goals)
    
    print("📈 职业轨迹预测完成！")
    
    # 显示发展路径
    print("\n🛤️ 发展路径:")
    for i, stage in enumerate(prediction["发展路径"]):
        print(f"   阶段{i+1}: {stage['阶段']} - {stage['描述']}")
        print(f"     关键技能: {', '.join(stage['关键技能'])}")
        print(f"     预期时间: {stage['预期时间']}")
    
    # 显示时间规划
    print(f"\n⏰ 总体时间规划: {prediction['时间规划']['总体时间']}")
    
    # 显示关键里程碑
    print("\n🎯 关键里程碑:")
    for milestone in prediction["关键节点"]:
        print(f"   {milestone['里程碑']} ({milestone['时间点']})")
        print(f"     成功标志: {', '.join(milestone['成功标志'][:2])}")
    
    # 显示风险预警
    print("\n⚠️ 风险预警:")
    for risk in prediction["风险预警"]:
        print(f"   {risk['风险']} (概率: {risk['概率']:.1%})")
        print(f"     缓解措施: {risk['缓解措施']}")
    
    print(f"\n🎲 成功概率: {prediction['成功概率']:.1%}")
    
    print("✅ 职业发展轨迹预测测试完成！")
    return prediction

def test_personalized_advice():
    """测试个性化建议生成"""
    print("\n💡 测试个性化建议生成功能...")
    
    engine = SmartDecisionEngine()
    
    # 用户数据
    user_data = {
        "risk_tolerance": "high",
        "career_focus": "technology",
        "work_style": "innovative",
        "skill_level": 6,
        "network_size": 80,
        "current_salary": 250000,
        "experience_years": 4
    }
    
    # 上下文信息
    context = {
        "market_condition": "good",
        "industry_trend": "growing",
        "personal_situation": "stable"
    }
    
    # 生成建议
    advice = engine.generate_personalized_advice(user_data, context)
    
    print("🎯 个性化建议生成完成！")
    
    # 显示性格特征
    print(f"\n🎭 性格特征: {', '.join(advice['性格特征'])}")
    print(f"🎯 决策偏好: {', '.join(advice['决策偏好'][:2])}")
    
    # 显示短期建议
    print("\n📅 短期建议 (3个月内):")
    for i, suggestion in enumerate(advice["短期建议"], 1):
        print(f"   {i}. {suggestion}")
    
    # 显示中期规划
    print("\n📈 中期规划 (1年内):")
    for i, plan in enumerate(advice["中期规划"], 1):
        print(f"   {i}. {plan}")
    
    # 显示长期目标
    print("\n🎯 长期目标 (3-5年):")
    for i, goal in enumerate(advice["长期目标"], 1):
        print(f"   {i}. {goal}")
    
    # 显示行动计划
    print("\n📋 行动计划:")
    for timeframe, actions in advice["行动计划"].items():
        print(f"   {timeframe}: {', '.join(actions[:2])}")
    
    # 显示优先级排序
    print("\n🔥 优先级排序 (前5项):")
    for i, priority in enumerate(advice["优先级排序"][:5], 1):
        print(f"   {i}. {priority['行动']} ({priority['时间框架']}) - 优先级: {priority['优先级']}")
    
    print("✅ 个性化建议生成测试完成！")
    return advice

def test_decision_quality_evaluation():
    """测试决策质量评估"""
    print("\n📊 测试决策质量评估功能...")
    
    engine = SmartDecisionEngine()
    
    # 模拟决策数据
    decision_data = {
        "predicted_score": 85,
        "predicted_salary": 350000,
        "predicted_satisfaction": 8,
        "predicted_growth": 7
    }
    
    # 模拟实际结果
    outcome_data = {
        "actual_score": 78,
        "actual_salary": 340000,
        "actual_satisfaction": 7,
        "actual_growth": 8
    }
    
    # 执行评估
    evaluation = engine.evaluate_decision_quality(decision_data, outcome_data)
    
    print("📈 决策质量评估完成！")
    
    print(f"\n🎯 决策评分: {evaluation['决策评分']}分")
    
    # 显示预测准确性
    print("\n🔍 预测准确性:")
    for metric, data in evaluation["预测准确性"].items():
        print(f"   {metric}: 预测{data['预测值']} vs 实际{data['实际值']} (准确率: {data['准确率']}%)")
    
    # 显示改进建议
    print("\n💡 改进建议:")
    for i, suggestion in enumerate(evaluation["改进建议"], 1):
        print(f"   {i}. {suggestion}")
    
    # 显示学习要点
    print("\n📚 学习要点:")
    for i, point in enumerate(evaluation["学习要点"], 1):
        print(f"   {i}. {point}")
    
    print("✅ 决策质量评估测试完成！")
    return evaluation

def main():
    """主测试函数"""
    print("🧠 Smart Decision 智能决策引擎 - 综合测试")
    print("=" * 60)
    
    try:
        # 测试各个功能模块
        job_analysis = test_job_decision_analysis()
        career_prediction = test_career_trajectory_prediction()
        personalized_advice = test_personalized_advice()
        quality_evaluation = test_decision_quality_evaluation()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试完成！")
        
        print("\n📋 测试总结:")
        print("   ✅ 工作选择决策分析: 多维度评分和风险评估")
        print("   ✅ 职业发展轨迹预测: 路径规划和成功概率")
        print("   ✅ 个性化建议生成: 基于性格的定制建议")
        print("   ✅ 决策质量评估: 预测准确性和改进建议")
        
        print("\n💡 功能亮点:")
        print("   🎯 智能性格识别和个性化权重调整")
        print("   📊 多维度决策矩阵和综合排名")
        print("   ⚠️ 全面风险评估和缓解建议")
        print("   💰 详细ROI计算和投资回报分析")
        print("   🚀 职业发展路径规划和里程碑设定")
        print("   🔮 基于数据的成功概率预测")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()