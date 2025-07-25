#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证所有行业配置文件
"""

import os
import yaml
import sys

def validate_all_configs():
    """验证所有配置文件"""
    config_dir = "industry_configs"
    
    # 获取所有配置文件
    config_files = [f for f in os.listdir(config_dir) 
                   if f.endswith('.yaml') and f != 'main_config.yaml']
    
    print(f"发现 {len(config_files)} 个行业配置文件")
    
    valid_count = 0
    invalid_files = []
    
    required_sections = [
        "industry_info",
        "core_keywords", 
        "technical_terms",
        "application_scenarios",
        "related_entities"
    ]
    
    for config_file in config_files:
        file_path = os.path.join(config_dir, config_file)
        industry_id = config_file.replace('.yaml', '')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 检查必需字段
            missing_sections = []
            for section in required_sections:
                if section not in config:
                    missing_sections.append(section)
            
            if missing_sections:
                print(f"X {industry_id}: 缺少 {missing_sections}")
                invalid_files.append(config_file)
            else:
                # 检查行业信息
                industry_info = config.get("industry_info", {})
                if not industry_info.get("name"):
                    print(f"X {industry_id}: 缺少行业名称")
                    invalid_files.append(config_file)
                else:
                    print(f"OK {industry_id}: {industry_info.get('name')}")
                    valid_count += 1
                    
        except Exception as e:
            print(f"X {industry_id}: 解析错误 - {e}")
            invalid_files.append(config_file)
    
    print(f"\n=== 验证结果 ===")
    print(f"有效配置: {valid_count}/{len(config_files)}")
    
    if invalid_files:
        print(f"无效文件: {invalid_files}")
        return False
    else:
        print("所有配置文件验证通过!")
        return True

if __name__ == "__main__":
    if validate_all_configs():
        sys.exit(0)
    else:
        sys.exit(1)