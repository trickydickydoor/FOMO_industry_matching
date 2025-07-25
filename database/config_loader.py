#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行业配置加载器
动态加载和合并多个YAML配置文件
"""

import os
import yaml
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path


class IndustryConfigLoader:
    """行业配置文件加载器"""
    
    def __init__(self, config_dir: str = None, logger: Optional[logging.Logger] = None):
        """
        初始化配置加载器
        
        Args:
            config_dir: 配置文件目录路径
            logger: 日志记录器
        """
        # 设置配置目录
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # 默认使用项目根目录下的industry_configs
            current_dir = Path(__file__).parent
            self.config_dir = current_dir.parent / "industry_configs"
        
        # 设置日志
        self.logger = logger or logging.getLogger(__name__)
        
        # 缓存配置
        self._main_config = None
        self._industry_configs = {}
        self._merged_config = None
        
    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """
        加载单个YAML文件
        
        Args:
            file_path: YAML文件路径
            
        Returns:
            解析后的配置字典
        """
        try:
            if not file_path.exists():
                self.logger.warning(f"配置文件不存在: {file_path}")
                return {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            
            self.logger.debug(f"成功加载配置文件: {file_path}")
            return config
            
        except yaml.YAMLError as e:
            self.logger.error(f"YAML解析错误 {file_path}: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"加载配置文件失败 {file_path}: {e}")
            return {}
    
    def load_main_config(self) -> Dict[str, Any]:
        """
        加载主配置文件
        
        Returns:
            主配置字典
        """
        if self._main_config is None:
            main_config_path = self.config_dir / "main_config.yaml"
            self._main_config = self._load_yaml_file(main_config_path)
            
            if not self._main_config:
                # 提供默认配置
                self.logger.warning("使用默认主配置")
                self._main_config = self._get_default_main_config()
        
        return self._main_config
    
    def _get_default_main_config(self) -> Dict[str, Any]:
        """获取默认主配置"""
        return {
            "version": "1.0.0",
            "enabled_industries": ["semiconductor"],
            "matching_config": {
                "layer_weights": {
                    "core_keywords": 0.4,
                    "technical_terms": 0.3,
                    "application_scenarios": 0.2,
                    "related_entities": 0.1
                },
                "thresholds": {
                    "high_confidence": 0.8,
                    "low_confidence": 0.5,
                    "fuzzy_similarity": 0.85
                },
                "parameters": {
                    "min_keyword_frequency": 1,
                    "max_industries_per_article": 3,
                    "context_window_size": 50,
                    "boost_factor_nearby": 1.2,
                    "boost_factor_cluster": 1.5
                }
            },
            "performance": {
                "batch_size": 1000,
                "max_workers": 3,
                "cache_enabled": True
            }
        }
    
    def load_industry_config(self, industry_id: str) -> Dict[str, Any]:
        """
        加载特定行业配置
        
        Args:
            industry_id: 行业ID
            
        Returns:
            行业配置字典
        """
        if industry_id not in self._industry_configs:
            config_file = self.config_dir / f"{industry_id}.yaml"
            config = self._load_yaml_file(config_file)
            
            if not config:
                self.logger.warning(f"行业配置为空: {industry_id}")
                return {}
            
            # 验证配置结构
            if not self._validate_industry_config(config, industry_id):
                self.logger.error(f"行业配置验证失败: {industry_id}")
                return {}
            
            self._industry_configs[industry_id] = config
        
        return self._industry_configs[industry_id]
    
    def _validate_industry_config(self, config: Dict[str, Any], industry_id: str) -> bool:
        """
        验证行业配置结构
        
        Args:
            config: 配置字典
            industry_id: 行业ID
            
        Returns:
            验证是否通过
        """
        required_sections = [
            "industry_info",
            "core_keywords", 
            "technical_terms",
            "application_scenarios",
            "related_entities"
        ]
        
        for section in required_sections:
            if section not in config:
                self.logger.error(f"行业配置 {industry_id} 缺少必需部分: {section}")
                return False
        
        # 验证行业信息
        industry_info = config.get("industry_info", {})
        if not industry_info.get("name"):
            self.logger.error(f"行业配置 {industry_id} 缺少行业名称")
            return False
        
        return True
    
    def load_all_industry_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        加载所有启用的行业配置
        
        Returns:
            所有行业配置的字典
        """
        main_config = self.load_main_config()
        enabled_industries = main_config.get("enabled_industries", [])
        
        all_configs = {}
        for industry_id in enabled_industries:
            config = self.load_industry_config(industry_id)
            if config:
                all_configs[industry_id] = config
                self.logger.info(f"已加载行业配置: {industry_id}")
            else:
                self.logger.warning(f"跳过无效的行业配置: {industry_id}")
        
        return all_configs
    
    def get_merged_config(self) -> Dict[str, Any]:
        """
        获取合并后的完整配置
        
        Returns:
            合并后的配置字典
        """
        if self._merged_config is None:
            main_config = self.load_main_config()
            industry_configs = self.load_all_industry_configs()
            
            self._merged_config = {
                "main": main_config,
                "industries": industry_configs
            }
        
        return self._merged_config
    
    def get_industry_terms(self, industry_id: str) -> Dict[str, List[str]]:
        """
        获取特定行业的所有关键词
        
        Args:
            industry_id: 行业ID
            
        Returns:
            分层的关键词字典
        """
        config = self.load_industry_config(industry_id)
        if not config:
            return {}
        
        # 提取所有层次的关键词
        terms = {}
        
        # L1: 核心关键词
        core_keywords = config.get("core_keywords", {})
        terms["core_keywords"] = self._flatten_terms(core_keywords)
        
        # L2: 技术术语
        technical_terms = config.get("technical_terms", {})
        terms["technical_terms"] = self._flatten_terms(technical_terms)
        
        # L3: 应用场景
        application_scenarios = config.get("application_scenarios", {})
        terms["application_scenarios"] = self._flatten_terms(application_scenarios)
        
        # L4: 相关实体
        related_entities = config.get("related_entities", {})
        terms["related_entities"] = self._flatten_terms(related_entities)
        
        return terms
    
    def _flatten_terms(self, terms_dict: Dict[str, Any]) -> List[str]:
        """
        展平嵌套的关键词字典
        
        Args:
            terms_dict: 嵌套的关键词字典
            
        Returns:
            展平后的关键词列表
        """
        flattened = []
        
        for key, value in terms_dict.items():
            if isinstance(value, list):
                flattened.extend(value)
            elif isinstance(value, str):
                flattened.append(value)
            elif isinstance(value, dict):
                flattened.extend(self._flatten_terms(value))
        
        # 去重并过滤空值
        return list(set(filter(None, flattened)))
    
    def get_matching_config(self) -> Dict[str, Any]:
        """
        获取匹配算法配置
        
        Returns:
            匹配配置字典
        """
        main_config = self.load_main_config()
        return main_config.get("matching_config", {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """
        获取性能配置
        
        Returns:
            性能配置字典
        """
        main_config = self.load_main_config()
        return main_config.get("performance", {})
    
    def reload_config(self):
        """重新加载所有配置"""
        self._main_config = None
        self._industry_configs.clear()
        self._merged_config = None
        self.logger.info("配置已重新加载")
    
    def list_available_industries(self) -> List[str]:
        """
        列出所有可用的行业配置文件
        
        Returns:
            可用行业ID列表
        """
        if not self.config_dir.exists():
            return []
        
        industries = []
        for yaml_file in self.config_dir.glob("*.yaml"):
            if yaml_file.name != "main_config.yaml":
                industry_id = yaml_file.stem
                industries.append(industry_id)
        
        return sorted(industries)
    
    def validate_all_configs(self) -> Dict[str, bool]:
        """
        验证所有配置文件
        
        Returns:
            验证结果字典
        """
        results = {}
        
        # 验证主配置
        main_config = self.load_main_config()
        results["main_config"] = bool(main_config)
        
        # 验证所有行业配置
        available_industries = self.list_available_industries()
        for industry_id in available_industries:
            config = self.load_industry_config(industry_id)
            results[industry_id] = bool(config)
        
        return results


def main():
    """测试配置加载器"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 创建配置加载器
    loader = IndustryConfigLoader()
    
    # 测试配置加载
    print("=== 测试配置加载器 ===")
    
    # 验证所有配置
    validation_results = loader.validate_all_configs()
    print(f"配置验证结果: {validation_results}")
    
    # 列出可用行业
    available = loader.list_available_industries()
    print(f"可用行业: {available}")
    
    # 加载主配置
    main_config = loader.load_main_config()
    print(f"主配置版本: {main_config.get('version')}")
    
    # 加载半导体配置
    if "semiconductor" in available:
        semiconductor_config = loader.load_industry_config("semiconductor")
        industry_info = semiconductor_config.get("industry_info", {})
        print(f"半导体行业名称: {industry_info.get('name')}")
        
        # 获取关键词
        terms = loader.get_industry_terms("semiconductor")
        for layer, keywords in terms.items():
            print(f"{layer}: {len(keywords)} 个关键词")


if __name__ == "__main__":
    main()