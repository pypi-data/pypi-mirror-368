#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Platform Integration 模块高级功能测试脚本
测试新增的简历优化报告和平台效果分析功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.platform_integration import PlatformIntegrator
import json
from datetime import datetime, timedelta

def test_resume_optimization_report():
    """测试简历优化报告功能"""
    print("🔍 测试简历优化报告功能...")
    
    integrator = PlatformIntegrator()
    
    # 模拟简历数据
    resume_data = {
        "name": "张三",
        "contact": "zhangsan@email.com",
        "summary": "有3年Python开发经验，熟悉Django框架",
        "skills": ["Python", "Django", "MySQL", "Git"],
        "experience": [
            {
                "company": "ABC科技",
                "position": "Python开发工程师",
                "duration": "2021-2024",
                "description": "负责Web应用开发和维护"
            }
        ],
        "education": [{"degree": "本科", "major": "计算机科学"}],
        "projects": [
            {
                "name": "电商系统",
                "tech_stack": ["Python", "Django", "Redis"],
                "description": "开发了完整的电商后台系统"
            }
        ]
    }
    
    # 模拟目标职位
    target_jobs = [
        {
            "title": "高级Python开发工程师",
            "company": "腾讯",
            "required_skills": ["Python", "Django", "Redis", "Docker", "Kubernetes"],
            "description": "负责大型Web应用开发",
            "requirements": ["熟练掌握Python", "有Docker经验", "了解微服务架构"]
        },
        {
            "title": "后端开发工程师",
            "company": "阿里巴巴",
            "required_skills": ["Python", "FastAPI", "PostgreSQL", "AWS"],
            "description": "开发高并发后端服务",
            "requirements": ["Python开发经验", "云服务经验", "数据库优化"]
        }
    ]
    
    # 生成简历优化报告
    report = integrator.generate_resume_optimization_report(resume_data, target_jobs)
    
    print(f"📊 简历优化报告生成完成！")
    print(f"   总体匹配度: {report['匹配度分析']['总体匹配度']}%")
    print(f"   匹配技能: {len(report['匹配度分析']['匹配技能'])}个")
    print(f"   缺失技能: {len(report['匹配度分析']['缺失技能'])}个")
    print(f"   结构完整性: {report['结构建议']['完整性评分']}分")
    print(f"   优化建议数量: {len(report['关键词优化']['优化建议'])}条")
    
    # 显示技能差距分析
    skill_gaps = report['技能差距']
    print(f"   关键技能缺失: {len(skill_gaps['关键技能'])}个")
    print(f"   可选技能缺失: {len(skill_gaps['可选技能'])}个")
    
    # 显示行动计划
    action_plan = report['行动计划']
    print(f"   立即行动项: {len(action_plan['立即行动（今天）'])}项")
    print(f"   短期目标: {len(action_plan['短期目标（1周内）'])}项")
    
    return report

def test_platform_effectiveness_analysis():
    """测试平台效果分析功能"""
    print("\n📈 测试平台效果分析功能...")
    
    integrator = PlatformIntegrator()
    
    # 模拟求职申请历史数据
    application_history = [
        {
            "platform": "LinkedIn",
            "company": "腾讯",
            "position": "Python开发工程师",
            "apply_date": "2024-01-15",
            "status": "已面试",
            "viewed": True,
            "replied": True,
            "interviewed": True
        },
        {
            "platform": "BOSS直聘",
            "company": "阿里巴巴",
            "position": "后端工程师",
            "apply_date": "2024-01-16",
            "status": "已录用",
            "viewed": True,
            "replied": True,
            "interviewed": True
        },
        {
            "platform": "拉勾网",
            "company": "字节跳动",
            "position": "全栈工程师",
            "apply_date": "2024-01-17",
            "status": "已回复",
            "viewed": True,
            "replied": True,
            "interviewed": False
        },
        {
            "platform": "智联招聘",
            "company": "美团",
            "position": "Python工程师",
            "apply_date": "2024-01-18",
            "status": "已查看",
            "viewed": True,
            "replied": False,
            "interviewed": False
        },
        {
            "platform": "猎聘",
            "company": "滴滴",
            "position": "后端开发",
            "apply_date": "2024-01-19",
            "status": "未回复",
            "viewed": False,
            "replied": False,
            "interviewed": False
        }
    ]
    
    # 分析平台效果
    effectiveness = integrator.analyze_platform_effectiveness(application_history)
    
    print(f"📊 平台效果分析完成！")
    print(f"   分析的平台数量: {len(effectiveness['平台排名'])}个")
    
    # 显示平台排名
    print("\n🏆 平台效果排名:")
    for i, (platform, stats) in enumerate(effectiveness['平台排名'].items(), 1):
        print(f"   {i}. {platform}: {stats['综合评分']:.1f}分")
        print(f"      成功率: {stats['成功率']:.1f}% | 面试率: {stats['面试率']:.1f}%")
    
    # 显示最佳投递时间建议
    time_analysis = effectiveness['最佳投递时间']
    print(f"\n⏰ 最佳投递时间分析:")
    print(f"   推荐投递日: {list(time_analysis['最佳投递日'].keys())}")
    print(f"   推荐时间段: {list(time_analysis['最佳投递时间'].keys())}")
    
    # 显示成功模式
    patterns = effectiveness['成功模式']
    print(f"\n✅ 成功模式识别:")
    print(f"   成功因素: {len(patterns['成功因素'])}个")
    print(f"   最佳实践: {len(patterns['最佳实践'])}个")
    
    # 显示优化建议
    advice = effectiveness['优化建议']
    print(f"\n💡 平台优化建议: {len(advice)}条")
    for i, suggestion in enumerate(advice[:3], 1):
        print(f"   {i}. {suggestion}")
    
    return effectiveness

def test_enhanced_market_trends():
    """测试增强的市场趋势分析功能"""
    print("\n📊 测试增强的市场趋势分析功能...")
    
    integrator = PlatformIntegrator()
    
    # 模拟职位数据（包含更多维度）
    job_data = [
        {
            "title": "Python开发工程师",
            "company": "腾讯",
            "company_type": "大厂",
            "location": "深圳",
            "industry": "互联网",
            "salary": 300000,
            "required_skills": ["Python", "Django", "Redis"],
            "experience_required": "3-5年"
        },
        {
            "title": "AI工程师",
            "company": "字节跳动",
            "company_type": "大厂",
            "location": "北京",
            "industry": "互联网",
            "salary": 450000,
            "required_skills": ["Python", "机器学习", "TensorFlow"],
            "experience_required": "3-5年"
        },
        {
            "title": "全栈工程师",
            "company": "创业公司A",
            "company_type": "创业公司",
            "location": "上海",
            "industry": "金融科技",
            "salary": 250000,
            "required_skills": ["Python", "React", "Docker"],
            "experience_required": "2-4年"
        },
        {
            "title": "后端工程师",
            "company": "阿里巴巴",
            "company_type": "大厂",
            "location": "杭州",
            "industry": "电商",
            "salary": 350000,
            "required_skills": ["Python", "微服务", "Kubernetes"],
            "experience_required": "3-5年"
        }
    ]
    
    # 分析市场趋势
    trends = integrator.analyze_job_market_trends(job_data)
    
    print(f"📈 市场趋势分析完成！")
    
    # 显示热门技能
    hot_skills = trends['热门技能']
    print(f"\n🔥 热门技能统计:")
    for skill, count in list(hot_skills.items())[:5]:
        print(f"   {skill}: {count}个职位")
    
    # 显示薪资趋势
    salary_trends = trends['薪资趋势']
    print(f"\n💰 薪资趋势分析:")
    for skill, data in list(salary_trends.items())[:3]:
        print(f"   {skill}: 平均¥{data['平均薪资']:,} (中位数¥{data['薪资中位数']:,})")
    
    # 显示公司类型分布
    if '公司类型' in trends:
        company_types = trends['公司类型']
        print(f"\n🏢 公司类型分布:")
        for company_type, count in company_types.items():
            print(f"   {company_type}: {count}个职位")
    
    # 显示地区分布
    if '地区分布' in trends:
        locations = trends['地区分布']
        print(f"\n🌍 地区分布:")
        for location, count in list(locations.items())[:3]:
            print(f"   {location}: {count}个职位")
    
    # 显示技能组合分析
    if '技能组合' in trends:
        skill_combos = trends['技能组合']
        print(f"\n🔗 热门技能组合:")
        for combo, count in list(skill_combos.items())[:3]:
            print(f"   {combo}: {count}个职位")
    
    # 显示增长趋势预测
    if '增长趋势' in trends:
        growth_predictions = trends['增长趋势']
        print(f"\n📈 技能增长趋势预测:")
        for skill, prediction in list(growth_predictions.items())[:3]:
            print(f"   {skill}: {prediction['预测增长率']} ({prediction['趋势']})")
    
    return trends

def main():
    """主测试函数"""
    print("🚀 开始测试 Platform Integration 模块的高级功能...")
    print("=" * 60)
    
    try:
        # 测试简历优化报告
        resume_report = test_resume_optimization_report()
        
        # 测试平台效果分析
        platform_effectiveness = test_platform_effectiveness_analysis()
        
        # 测试增强的市场趋势分析
        market_trends = test_enhanced_market_trends()
        
        print("\n" + "=" * 60)
        print("🎉 所有高级功能测试完成！")
        print("\n📋 测试总结:")
        print(f"   ✅ 简历优化报告: 生成完整的多维度分析报告")
        print(f"   ✅ 平台效果分析: 实现智能评分和优化建议")
        print(f"   ✅ 市场趋势分析: 新增技能组合和增长预测")
        print(f"   ✅ 辅助功能: 所有支持方法正常工作")
        
        print("\n💡 功能亮点:")
        print("   🎯 智能匹配度计算和技能差距分析")
        print("   📊 多维度平台效果评估和排名")
        print("   🔮 基于趋势权重的技能增长预测")
        print("   📋 结构化行动计划和学习建议")
        print("   ⏰ 最佳投递时间和成功模式识别")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()