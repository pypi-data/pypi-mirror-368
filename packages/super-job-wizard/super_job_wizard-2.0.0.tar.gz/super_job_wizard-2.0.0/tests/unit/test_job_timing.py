#!/usr/bin/env python3
"""
🧪 跳槽时机分析功能测试脚本
Test Job Timing Analysis Feature
"""

import sys
import os
import json
from datetime import datetime

# 添加src目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
modules_dir = os.path.join(src_dir, 'modules')

sys.path.insert(0, src_dir)
sys.path.insert(0, modules_dir)

def test_job_timing_analysis():
    """测试跳槽时机分析功能"""
    print("🧪 开始测试跳槽时机分析功能...")
    print("=" * 60)
    
    try:
        # 导入模块
        from super_job_wizard import analyze_job_timing
        
        # 准备测试数据
        user_profile = {
            "experience_years": 3,
            "skills": ["Python", "机器学习", "数据分析", "项目管理", "SQL"],
            "current_salary": 180000,
            "job_satisfaction": 4,  # 1-10分，4分表示不太满意
            "emergency_fund_months": 6,  # 有6个月应急资金
            "current_project_phase": "即将完成",
            "bonus_month": 2  # 2月发年终奖
        }
        
        market_context = {
            "industry": "技术",
            "location": "北京", 
            "position_level": "中级"
        }
        
        print("📊 测试数据:")
        print(f"用户画像: {json.dumps(user_profile, ensure_ascii=False, indent=2)}")
        print(f"市场环境: {json.dumps(market_context, ensure_ascii=False, indent=2)}")
        print()
        
        # 执行分析
        print("🔍 执行跳槽时机分析...")
        result = analyze_job_timing(user_profile, market_context)
        
        # 输出结果
        print("✅ 分析完成！结果如下:")
        print("=" * 60)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("=" * 60)
        
        # 验证关键字段
        required_fields = [
            "分析ID", "综合评分", "跳槽建议", "个人准备度", 
            "市场时机", "最佳时间窗口", "风险评估", "行动建议"
        ]
        
        missing_fields = [field for field in required_fields if field not in result]
        
        if missing_fields:
            print(f"❌ 缺少必要字段: {missing_fields}")
            return False
        else:
            print("✅ 所有必要字段都存在")
            
        # 验证评分范围
        score = result.get("综合评分", 0)
        if 0 <= score <= 100:
            print(f"✅ 综合评分在合理范围内: {score}")
        else:
            print(f"❌ 综合评分超出范围: {score}")
            return False
            
        # 验证建议内容
        advice = result.get("跳槽建议", "")
        if advice:
            print(f"✅ 跳槽建议: {advice}")
        else:
            print("❌ 缺少跳槽建议")
            return False
            
        print("\n🎉 跳槽时机分析功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_scenarios():
    """测试不同场景下的分析结果"""
    print("\n🧪 测试不同场景...")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "新手程序员",
            "user_profile": {
                "experience_years": 1,
                "skills": ["Python", "JavaScript"],
                "current_salary": 80000,
                "job_satisfaction": 6,
                "emergency_fund_months": 2,
                "current_project_phase": "进行中",
                "bonus_month": 2
            },
            "market_context": {
                "industry": "技术",
                "location": "深圳",
                "position_level": "初级"
            }
        },
        {
            "name": "资深工程师",
            "user_profile": {
                "experience_years": 8,
                "skills": ["Python", "Java", "架构设计", "团队管理", "机器学习", "云计算"],
                "current_salary": 350000,
                "job_satisfaction": 3,
                "emergency_fund_months": 12,
                "current_project_phase": "即将完成",
                "bonus_month": 2
            },
            "market_context": {
                "industry": "技术",
                "location": "上海",
                "position_level": "高级"
            }
        }
    ]
    
    try:
        from super_job_wizard import analyze_job_timing
        
        for scenario in scenarios:
            print(f"\n📋 场景: {scenario['name']}")
            print("-" * 40)
            
            result = analyze_job_timing(scenario['user_profile'], scenario['market_context'])
            
            print(f"综合评分: {result.get('综合评分', 0)}")
            print(f"跳槽建议: {result.get('跳槽建议', '')}")
            print(f"个人准备度: {result.get('个人准备度', {}).get('总分', 0)}")
            print(f"市场时机: {result.get('市场时机', {}).get('总分', 0)}")
            
            # 显示前3个行动建议
            actions = result.get('行动建议', [])[:3]
            if actions:
                print("主要建议:")
                for action in actions:
                    print(f"  • {action}")
        
        print("\n✅ 不同场景测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 场景测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 启动跳槽时机分析功能测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 基础功能测试
    success1 = test_job_timing_analysis()
    
    # 不同场景测试
    success2 = test_different_scenarios()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 所有测试通过！跳槽时机分析功能正常工作！")
        print("🔥 真nb！功能扩展成功！")
    else:
        print("❌ 部分测试失败，需要检查代码")
        
    print("=" * 60)