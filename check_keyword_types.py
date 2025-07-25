#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import os

def check_keyword_types():
    """检查配置文件中的关键词类型"""
    config_dir = "industry_configs"
    
    for f in os.listdir(config_dir):
        if f.endswith('.yaml') and f != 'main_config.yaml':
            file_path = os.path.join(config_dir, f)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    config = yaml.safe_load(file)
                    
                # 检查所有层级的关键词
                sections = ['core_keywords', 'technical_terms', 'application_scenarios', 'related_entities']
                for section in sections:
                    if section in config:
                        for category, keywords in config[section].items():
                            if keywords:
                                for i, kw in enumerate(keywords):
                                    if not isinstance(kw, str):
                                        print(f'{f}: {section}.{category}[{i}] = {kw} ({type(kw).__name__})')
                                    elif kw is None:
                                        print(f'{f}: {section}.{category}[{i}] = None')
                                        
            except Exception as e:
                print(f'{f}: 解析错误 - {e}')

if __name__ == "__main__":
    check_keyword_types()