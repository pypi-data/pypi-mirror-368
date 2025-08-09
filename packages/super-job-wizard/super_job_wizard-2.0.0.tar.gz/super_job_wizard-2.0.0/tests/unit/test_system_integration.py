#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统完整性测试脚本
测试所有核心模块的协同工作
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, 'src')

from super_job_wizard import SuperJobWizard, UniversalJobAnalyzer, BigDataAnalyzer, AIJobAnalyzer

def test_system_integration():
    """测试系统完整性"""
    print('🚀 开始系统完整性测试...')
    
    try:
        # 1. 测试主系统
        print('\n📋 测试1: 主系统状态检查')
        wizard = SuperJobWizard()
        status = wizard.get_system_status()
        print(f'✅ 主系统状态: {status["状态"]}')
        print(f'   版本: {status["版本"]}')
        print(f'   模块数量: {len(status["模块状态"])}')
        
        # 2. 测试通用职位分析器
        print('\n📋 测试2: 通用职位分析器')
        universal = UniversalJobAnalyzer()
        job_result = universal.analyze_any_job('Python工程师', '深圳', 3)
        print(f'✅ 通用分析器: {job_result["职位信息"]["职位"]} - {job_result["职位信息"]["城市"]}')
        print(f'   预估年薪: {job_result["薪资分析"]["预估年薪"]}元')
        
        # 3. 测试大数据分析器
        print('\n📋 测试3: 大数据分析器')
        big_data = BigDataAnalyzer()
        company_result = big_data.get_company_analysis('腾讯')
        print(f'✅ 大数据分析器: {company_result["company_name"]} - {company_result["basic_info"]["行业"]}')
        print(f'   公司规模: {company_result["basic_info"]["规模"]}')
        
        # 4. 测试AI分析器
        print('\n📋 测试4: AI分析器')
        ai_analyzer = AIJobAnalyzer()
        salary_result = ai_analyzer.predict_salary_range('机器学习工程师', 4, ['Python', 'TensorFlow'], '北京')
        salary_range = salary_result["salary_range"]
        print(f'✅ AI分析器: 薪资预测 ¥{salary_range[0]:,.0f} - ¥{salary_range[1]:,.0f}')
        print(f'   置信度: {salary_result["confidence"]*100:.1f}%')
        
        # 5. 测试行业报告功能
        print('\n📋 测试5: 行业报告功能')
        industry_result = big_data.get_industry_report('AI/机器学习')
        print(f'✅ 行业报告: {industry_result["行业名称"]} - 平均薪资 ¥{industry_result["市场概况"]["平均薪资"]:,}')
        print(f'   年增长率: {industry_result["市场概况"]["年增长率"]}')
        
        print('\n🎉 所有核心功能测试通过！系统运行正常！')
        return True
        
    except Exception as e:
        print(f'\n❌ 测试失败: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_system_integration()
    sys.exit(0 if success else 1)