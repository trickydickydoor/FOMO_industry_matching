#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的行业匹配测试
"""

import sys
import os

# 设置标准输出编码
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.industry_matcher import IndustryMatcher

def safe_print(text):
    """安全打印函数，处理编码问题"""
    try:
        if isinstance(text, str):
            # 尝试以GBK编码输出（Windows默认）
            try:
                print(text.encode('gbk', errors='replace').decode('gbk'))
            except:
                # 如果GBK失败，回退到安全显示
                print(text.encode('ascii', errors='replace').decode('ascii'))
        else:
            print(text)
    except Exception:
        print(repr(text))

def test_basic_matching():
    """测试基本匹配功能"""
    safe_print("初始化行业匹配器...")
    matcher = IndustryMatcher()
    
    safe_print("加载行业配置数据...")
    if not matcher.load_industry_data():
        safe_print("❌ 加载行业配置失败")
        return False
    
    safe_print(f"成功加载 {len(matcher.industry_configs)} 个行业配置")
    
    # 测试用例
    test_cases = [
        {
            "name": "半导体技术新闻",
            "content": "台积电宣布其3nm制程技术取得重大突破，新一代芯片的性能相比5nm制程提升15%，功耗降低30%。该技术采用了最先进的EUV光刻工艺，晶圆良率已经达到商业化标准。",
            "expected": "半导体"
        },
        {
            "name": "普通经济新闻",
            "content": "国家统计局发布10月份经济数据，CPI同比上涨2.1%，PPI同比下降1.3%。专家分析认为，当前通胀压力总体可控，经济运行保持在合理区间。",
            "expected": None
        }
    ]
    
    safe_print("\n开始测试匹配...")
    for i, test_case in enumerate(test_cases, 1):
        safe_print(f"\n测试 {i}: {test_case['name']}")
        safe_print(f"内容: {test_case['content'][:50]}...")
        
        # 执行匹配
        matched_industries = matcher.match_industries_in_content(test_case['content'])
        safe_print(f"匹配结果: {matched_industries}")
        
        # 检查期望结果
        if test_case['expected']:
            if test_case['expected'] in matched_industries:
                safe_print(f"[OK] 匹配正确，期望: {test_case['expected']}")
            else:
                safe_print(f"[ERROR] 匹配错误，期望: {test_case['expected']}")
        else:
            if not matched_industries:
                safe_print(f"[OK] 正确识别为非技术新闻")
            else:
                safe_print(f"[WARNING] 可能存在误判: {matched_industries}")
    
    return True

if __name__ == "__main__":
    success = test_basic_matching()
    if success:
        safe_print("\n[SUCCESS] 基础测试完成！")
    else:
        safe_print("\n[FAILED] 测试失败")
    
    sys.exit(0 if success else 1)