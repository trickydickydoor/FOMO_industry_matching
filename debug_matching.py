#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试匹配过程
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.industry_matcher import IndustryMatcher

def debug_matching():
    """调试匹配过程"""
    print("=== 调试行业匹配 ===")
    
    matcher = IndustryMatcher()
    
    if not matcher.load_industry_data():
        print("无法加载行业数据")
        return
    
    print(f"已加载行业: {list(matcher.industry_configs.keys())}")
    
    # 测试内容
    test_content = "台积电宣布其3nm制程技术取得重大突破，新一代芯片的性能相比5nm制程提升15%，功耗降低30%。该技术采用了最先进的EUV光刻工艺，晶圆良率已经达到商业化标准。"
    
    print(f"\n测试内容: {test_content[:50]}...")
    
    # 查看配置
    print(f"\n匹配配置:")
    print(f"权重: {matcher.matching_config.get('layer_weights', {})}")
    print(f"阈值: {matcher.matching_config.get('thresholds', {})}")
    
    # 对每个行业计算详细得分
    for industry_id in matcher.industry_configs:
        print(f"\n=== {industry_id} 行业分析 ===")
        
        terms = matcher.industry_terms.get(industry_id, {})
        for layer, keywords in terms.items():
            print(f"{layer}: {len(keywords)} 个关键词")
            # 显示前5个关键词
            print(f"  示例: {keywords[:5]}")
        
        # 计算总得分
        score = matcher.match_industry_in_content(test_content, industry_id)
        print(f"\n总得分: {score:.3f}")
        
        # 计算各层得分
        content_lower = test_content.lower()
        
        # L1: 核心关键词
        core_keywords = terms.get("core_keywords", [])
        core_score = matcher.calculate_layer_score(test_content, core_keywords)
        print(f"L1 核心关键词得分: {core_score:.3f}")
        
        # 检查哪些关键词匹配了
        matched_core = []
        for kw in core_keywords:
            if kw.lower() in content_lower:
                matched_core.append(kw)
        print(f"  匹配的核心关键词: {matched_core}")
        
        # L2: 技术术语
        technical_terms = terms.get("technical_terms", [])
        tech_score = matcher.calculate_layer_score(test_content, technical_terms)
        print(f"L2 技术术语得分: {tech_score:.3f}")
        
        # 检查匹配的技术术语
        matched_tech = []
        for kw in technical_terms:
            if kw.lower() in content_lower:
                matched_tech.append(kw)
        print(f"  匹配的技术术语: {matched_tech}")
        
        # 检查阈值
        high_threshold = matcher.matching_config.get("thresholds", {}).get("high_confidence", 0.8)
        low_threshold = matcher.matching_config.get("thresholds", {}).get("low_confidence", 0.5)
        
        print(f"\n阈值检查:")
        print(f"  高置信度阈值: {high_threshold}")
        print(f"  低置信度阈值: {low_threshold}")
        print(f"  当前得分: {score:.3f}")
        
        if score >= high_threshold:
            print(f"  结果: 高置信度匹配")
        elif score >= low_threshold:
            print(f"  结果: 低置信度匹配")
        else:
            print(f"  结果: 不匹配")

if __name__ == "__main__":
    debug_matching()