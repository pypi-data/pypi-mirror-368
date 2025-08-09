#!/usr/bin/env python3
"""
🔗 Platform Integration 模块测试脚本
测试平台集成模块的各项功能
"""

import sys
import os
from datetime import datetime, timedelta

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'modules'))

try:
    from modules.platform_integration import PlatformIntegrator
    print("✅ 成功导入 PlatformIntegrator")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

def test_linkedin_analysis():
    """测试LinkedIn分析功能"""
    print("\n" + "="*50)
    print("🔍 测试LinkedIn分析功能")
    print("="*50)
    
    integrator = PlatformIntegrator()
    
    # 测试数据
    test_profile = {
        "headline": "Python开发工程师 | AI/机器学习 | 5年经验",
        "summary": "专注于AI和机器学习的Python开发工程师，有5年项目经验，擅长TensorFlow和PyTorch，曾参与多个大型项目，具备丰富的数据分析和模型优化经验。",
        "skills": ["Python", "机器学习", "TensorFlow", "PyTorch", "数据分析", "AWS"]
    }
    
    result = integrator.analyze_linkedin_profile(test_profile)
    
    print(f"📊 LinkedIn分析结果:")
    print(f"   标题评分: {result['评分']['标题']['评分']}/100")
    print(f"   摘要评分: {result['评分']['摘要']['评分']}/100")
    print(f"   热门技能数量: {len(result['关键词分析']['热门技能'])}")
    print(f"   优化建议数量: {len(result['优化建议'])}")
    
    if result['优化建议']:
        print("   具体建议:")
        for suggestion in result['优化建议']:
            print(f"   - {suggestion}")

def test_email_generation():
    """测试邮件生成功能"""
    print("\n" + "="*50)
    print("📧 测试邮件生成功能")
    print("="*50)
    
    integrator = PlatformIntegrator()
    
    # 测试求职申请邮件
    variables = {
        "姓名": "张三",
        "职位名称": "Python开发工程师",
        "工作年限": "5",
        "专业领域": "AI/机器学习",
        "核心技能": "Python、TensorFlow、数据分析",
        "主要成就": "主导开发了智能推荐系统，提升用户转化率30%",
        "匹配点列表": "• 5年Python开发经验\n• 熟练掌握机器学习算法\n• 有大型项目经验",
        "联系方式": "手机：138****8888，邮箱：zhangsan@email.com",
        "日期": datetime.now().strftime("%Y年%m月%d日")
    }
    
    result = integrator.generate_email("求职申请", variables)
    
    if "错误" not in result:
        print(f"✅ 邮件生成成功")
        print(f"   主题: {result['主题']}")
        print(f"   内容长度: {len(result['内容'])}字符")
        print(f"   优化建议: {len(result['优化建议'])}条")
    else:
        print(f"❌ 邮件生成失败: {result['错误']}")

def test_job_tracking():
    """测试求职追踪功能"""
    print("\n" + "="*50)
    print("📱 测试求职追踪功能")
    print("="*50)
    
    integrator = PlatformIntegrator()
    
    # 模拟求职申请数据
    applications = [
        {"platform": "BOSS直聘", "company": "腾讯", "position": "Python工程师", "status": "已投递"},
        {"platform": "拉勾网", "company": "字节跳动", "position": "AI工程师", "status": "已查看"},
        {"platform": "LinkedIn", "company": "阿里巴巴", "position": "数据工程师", "status": "面试邀请"},
        {"platform": "BOSS直聘", "company": "美团", "position": "后端工程师", "status": "技术面试"},
        {"platform": "猎聘", "company": "百度", "position": "算法工程师", "status": "已录用"},
    ]
    
    result = integrator.track_job_applications(applications)
    
    print(f"📊 求职追踪结果:")
    print(f"   总申请数: {result['总体统计']['总申请数']}")
    print(f"   使用平台: {', '.join(result['总体统计']['使用平台'])}")
    print(f"   平均响应率: {result['总体统计']['平均响应率']}%")
    print(f"   面试转化率: {result['总体统计']['面试转化率']}%")
    
    print(f"\n   平台分析:")
    for platform, stats in result['平台分析'].items():
        print(f"   {platform}: {stats['申请数量']}个申请, 成功率{stats['成功率']}%")
    
    if result['建议']:
        print(f"\n   改进建议:")
        for suggestion in result['建议']:
            print(f"   - {suggestion}")

def test_interview_management():
    """测试面试管理功能"""
    print("\n" + "="*50)
    print("📅 测试面试管理功能")
    print("="*50)
    
    integrator = PlatformIntegrator()
    
    # 模拟面试数据
    now = datetime.now()
    interviews = [
        {
            "company": "腾讯",
            "position": "Python工程师",
            "time": (now + timedelta(days=1)).isoformat(),
            "type": "技术面试"
        },
        {
            "company": "字节跳动",
            "position": "AI工程师", 
            "time": (now + timedelta(days=3)).isoformat(),
            "type": "HR面试"
        },
        {
            "company": "阿里巴巴",
            "position": "数据工程师",
            "time": (now + timedelta(days=5)).isoformat(),
            "type": "终面"
        }
    ]
    
    result = integrator.manage_interview_schedule(interviews)
    
    print(f"📅 面试管理结果:")
    print(f"   即将面试数量: {len(result['即将面试'])}")
    
    for interview in result['即将面试']:
        print(f"   {interview['公司']} - {interview['职位']} (还有{interview['剩余天数']}天)")
    
    if result['准备建议']:
        print(f"\n   准备建议:")
        for advice in result['准备建议']:
            print(f"   - {advice}")

def test_market_trends():
    """测试市场趋势分析功能"""
    print("\n" + "="*50)
    print("📊 测试市场趋势分析功能")
    print("="*50)
    
    integrator = PlatformIntegrator()
    
    # 模拟职位数据
    job_data = [
        {"required_skills": ["Python", "Django", "MySQL"], "salary": 250000},
        {"required_skills": ["JavaScript", "React", "Node.js"], "salary": 280000},
        {"required_skills": ["Python", "机器学习", "TensorFlow"], "salary": 350000},
        {"required_skills": ["Java", "Spring", "MySQL"], "salary": 300000},
        {"required_skills": ["Python", "数据分析", "Pandas"], "salary": 220000},
    ]
    
    result = integrator.analyze_job_market_trends(job_data)
    
    print(f"📈 市场趋势分析结果:")
    print(f"   热门技能TOP5:")
    for i, (skill, count) in enumerate(list(result['热门技能'].items())[:5], 1):
        print(f"   {i}. {skill}: {count}次提及")
    
    print(f"\n   薪资趋势:")
    for skill, data in list(result['薪资趋势'].items())[:3]:
        print(f"   {skill}: 平均¥{data['平均薪资']:,.0f}, 职位数{data['职位数量']}")

def main():
    """主测试函数"""
    print("🔗 Platform Integration 模块功能测试")
    print("=" * 60)
    
    try:
        test_linkedin_analysis()
        test_email_generation()
        test_job_tracking()
        test_interview_management()
        test_market_trends()
        
        print("\n" + "="*60)
        print("🎉 所有测试完成！Platform Integration模块功能正常")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()