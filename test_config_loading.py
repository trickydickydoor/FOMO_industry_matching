#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试配置加载功能
"""

import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.config_loader import IndustryConfigLoader

def test_config_loading():
    """测试配置加载功能"""
    try:
        # 初始化配置加载器
        loader = IndustryConfigLoader()
        
        # 加载主配置
        main_config = loader.load_main_config()
        enabled_industries = main_config.get("enabled_industries", [])
        
        print(f"启用的行业数量: {len(enabled_industries)}")
        print("启用的行业列表:")
        for i, industry in enumerate(enabled_industries, 1):
            print(f"  {i:2d}. {industry}")
        
        # 加载所有行业配置
        print("\n开始加载行业配置...")
        all_configs = loader.load_all_industry_configs()
        
        print(f"\n=== 加载结果 ===")
        print(f"成功加载: {len(all_configs)} 个行业配置")
        
        # 显示每个行业的基本信息
        for industry_id, config in all_configs.items():
            industry_info = config.get("industry_info", {})
            name = industry_info.get("name", "未知")
            priority = industry_info.get("priority", "未设置")
            print(f"  {industry_id}: {name} (优先级: {priority})")
        
        return len(all_configs) == 39
        
    except Exception as e:
        print(f"配置加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_config_loading():
        print("\n✓ 配置加载测试通过!")
        sys.exit(0)
    else:
        print("\n✗ 配置加载测试失败!")
        sys.exit(1)