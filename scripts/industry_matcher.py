#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行业匹配器
基于多层次语义分析的全自动行业识别系统
"""

import os
import sys
import json
import logging
import threading
import time
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Set, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import SequenceMatcher

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config_loader import IndustryConfigLoader
from database.supabase_handler import SupabaseHandler


class IndustryMatcher:
    """行业智能匹配器"""
    
    def __init__(self, config_dir: str = None):
        """
        初始化匹配器
        
        Args:
            config_dir: 配置文件目录
        """
        self.setup_logging()
        
        # 加载配置
        self.config_loader = IndustryConfigLoader(config_dir, self.logger)
        self.main_config = self.config_loader.load_main_config()
        self.matching_config = self.config_loader.get_matching_config()
        self.performance_config = self.config_loader.get_performance_config()
        
        # 数据库连接
        self.supabase_handler = None
        
        # 行业配置缓存
        self.industry_configs = {}
        self.industry_terms = {}
        
        # 统计信息
        self.processed_count = 0
        self.matched_count = 0
        self.lock = threading.Lock()
        
        # 匹配缓存
        self.match_cache = {} if self.performance_config.get("cache_enabled", True) else None
        
    def setup_logging(self):
        """设置日志"""
        # 确保日志目录存在
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # 配置日志格式
        log_file = os.path.join(log_dir, f'industry_matching_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def init_supabase(self) -> bool:
        """初始化 Supabase 连接"""
        try:
            # 尝试从环境变量获取配置
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_KEY')
            
            if supabase_url and supabase_key:
                # 使用环境变量配置
                config = {
                    'supabase': {
                        'url': supabase_url,
                        'anon_key': supabase_key,
                        'table_name': 'news_items'
                    }
                }
                # 临时写入配置文件
                config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_config.json')
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f)
                
                self.supabase_handler = SupabaseHandler(config_file=config_path, log_callback=self.logger.info)
                
                # 清理临时配置文件
                os.remove(config_path)
            else:
                # 使用本地配置文件
                self.supabase_handler = SupabaseHandler(log_callback=self.logger.info)
            
            if not self.supabase_handler.client:
                self.logger.error("Supabase 客户端初始化失败")
                return False
            
            # 测试连接
            try:
                # 简单的连接测试
                test_response = self.supabase_handler.client.table('news_items').select('id').limit(1).execute()
                self.logger.info("Supabase 连接测试成功")
            except Exception as e:
                self.logger.error(f"Supabase 连接测试失败: {e}")
                return False
                
            self.logger.info("Supabase 连接初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化 Supabase 连接时出错: {e}")
            return False
    
    def load_industry_data(self) -> bool:
        """加载所有行业配置数据"""
        try:
            self.logger.info("开始加载行业配置数据...")
            
            # 加载所有行业配置
            self.industry_configs = self.config_loader.load_all_industry_configs()
            
            if not self.industry_configs:
                self.logger.error("未加载到任何行业配置")
                return False
            
            # 预处理所有行业的关键词
            for industry_id in self.industry_configs:
                terms = self.config_loader.get_industry_terms(industry_id)
                if terms:
                    # 转换为小写进行匹配
                    processed_terms = {}
                    for layer, keywords in terms.items():
                        processed_terms[layer] = [kw.lower().strip() for kw in keywords if kw]
                    self.industry_terms[industry_id] = processed_terms
            
            self.logger.info(f"成功加载 {len(self.industry_configs)} 个行业配置")
            return True
            
        except Exception as e:
            self.logger.error(f"加载行业配置数据时出错: {e}")
            return False
    
    def get_news_batch(self, offset: int, limit: int) -> List[Dict[str, Any]]:
        """分批获取新闻数据"""
        try:
            response = self.supabase_handler.client.table('news_items')\
                .select('id, content')\
                .range(offset, offset + limit - 1)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            self.logger.error(f"获取新闻数据时出错 (offset={offset}): {e}")
            return []
    
    def calculate_fuzzy_similarity(self, text1: str, text2: str) -> float:
        """计算模糊匹配相似度"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def find_keyword_positions(self, content: str, keywords: List[str]) -> List[Tuple[str, int, int]]:
        """
        找到关键词在文本中的位置
        
        Returns:
            List of (keyword, start_pos, end_pos)
        """
        content_lower = content.lower()
        positions = []
        
        for keyword in keywords:
            if not keyword:
                continue
                
            keyword_lower = keyword.lower()
            start = 0
            
            while True:
                pos = content_lower.find(keyword_lower, start)
                if pos == -1:
                    break
                positions.append((keyword, pos, pos + len(keyword)))
                start = pos + 1
        
        return sorted(positions, key=lambda x: x[1])
    
    def calculate_context_boost(self, content: str, keywords: List[str]) -> float:
        """计算上下文增强因子"""
        if not keywords:
            return 1.0
        
        positions = self.find_keyword_positions(content, keywords)
        if len(positions) < 2:
            return 1.0
        
        window_size = self.matching_config.get("parameters", {}).get("context_window_size", 50)
        nearby_boost = self.matching_config.get("parameters", {}).get("boost_factor_nearby", 1.2)
        cluster_boost = self.matching_config.get("parameters", {}).get("boost_factor_cluster", 1.5)
        
        boost_factor = 1.0
        nearby_pairs = 0
        clusters = 0
        
        # 计算相邻关键词对
        for i in range(len(positions) - 1):
            distance = positions[i + 1][1] - positions[i][2]
            if distance <= window_size:
                nearby_pairs += 1
        
        # 计算关键词聚集
        current_cluster_size = 1
        for i in range(len(positions) - 1):
            distance = positions[i + 1][1] - positions[i][2]
            if distance <= window_size:
                current_cluster_size += 1
            else:
                if current_cluster_size >= 3:
                    clusters += 1
                current_cluster_size = 1
        
        if current_cluster_size >= 3:
            clusters += 1
        
        # 应用增强因子
        if nearby_pairs > 0:
            boost_factor *= (1 + nearby_pairs * (nearby_boost - 1) * 0.1)
        
        if clusters > 0:
            boost_factor *= (1 + clusters * (cluster_boost - 1) * 0.2)
        
        return min(boost_factor, 2.0)  # 限制最大增强到2倍
    
    def calculate_layer_score(self, content: str, keywords: List[str]) -> float:
        """
        计算单层关键词得分 - 改进版
        
        Args:
            content: 文章内容
            keywords: 关键词列表
            
        Returns:
            该层的得分 (0-1)
        """
        if not keywords or not content:
            return 0.0
        
        content_lower = content.lower()
        min_frequency = self.matching_config.get("parameters", {}).get("min_keyword_frequency", 1)
        fuzzy_threshold = self.matching_config.get("thresholds", {}).get("fuzzy_similarity", 0.85)
        
        matched_keywords = []
        total_frequency = 0
        high_value_matches = 0  # 高价值关键词匹配数
        
        # 定义高价值关键词 - 覆盖所有行业
        high_value_keywords = {
            # 半导体行业
            '芯片', '半导体', '集成电路', 'ic', '处理器', 'cpu', 'gpu',
            '制程', '工艺', '光刻', 'euv', '晶圆', '封装', '测试',
            '台积电', 'tsmc', '中芯国际', 'smic',
            
            # 游戏行业
            '游戏', '手游', '电竞', '游戏开发', 'unity', 'unreal',
            '腾讯游戏', '网易游戏', '米哈游', '王者荣耀', '原神',
            
            # 人工智能行业
            '人工智能', 'ai', '机器学习', '深度学习', '神经网络',
            '大模型', 'gpt', 'chatgpt', 'aigc', 'openai',
            
            # 金融科技行业
            '金融科技', 'fintech', '支付', '移动支付', '区块链',
            '数字货币', '比特币', '支付宝', '微信支付', '蚂蚁集团'
        }
        
        for keyword in keywords:
            if not keyword:
                continue
            
            keyword_lower = keyword.lower()
            is_high_value = keyword_lower in high_value_keywords
            
            # 精确匹配
            exact_count = content_lower.count(keyword_lower)
            if exact_count >= min_frequency:
                matched_keywords.append(keyword)
                total_frequency += exact_count
                if is_high_value:
                    high_value_matches += 1
                continue
            
            # 模糊匹配
            words = content_lower.split()
            for word in words:
                if len(word) >= 3 and len(keyword_lower) >= 3:  # 避免短词误匹配
                    similarity = self.calculate_fuzzy_similarity(word, keyword_lower)
                    if similarity >= fuzzy_threshold:
                        matched_keywords.append(keyword)
                        total_frequency += 1
                        if is_high_value:
                            high_value_matches += 1
                        break
        
        if not matched_keywords:
            return 0.0
        
        # 改进的评分算法
        # 1. 匹配质量得分 - 重视实际匹配的关键词
        match_quality = min(len(matched_keywords) / 10.0, 1.0)  # 匹配10个关键词即满分
        
        # 2. 频次得分 - 关键词出现频率
        frequency_score = min(total_frequency / 15.0, 1.0)  # 总频次15即满分
        
        # 3. 高价值加权 - 重要关键词额外加分
        high_value_boost = min(high_value_matches * 0.3, 0.6)  # 每个高价值词+0.3，最高+0.6
        
        # 综合得分
        base_score = (match_quality * 0.4 + frequency_score * 0.6) + high_value_boost
        
        # 应用上下文增强
        context_boost = self.calculate_context_boost(content, matched_keywords)
        final_score = min(base_score * context_boost, 1.0)
        
        return final_score
    
    def match_industry_in_content(self, content: str, industry_id: str) -> float:
        """
        匹配单个行业在内容中的得分
        
        Args:
            content: 文章内容
            industry_id: 行业ID
            
        Returns:
            匹配得分 (0-1)
        """
        if industry_id not in self.industry_terms:
            return 0.0
        
        # 获取缓存键
        cache_key = None
        if self.match_cache is not None:
            content_hash = hash(content + industry_id)
            cache_key = f"{industry_id}_{content_hash}"
            if cache_key in self.match_cache:
                return self.match_cache[cache_key]
        
        terms = self.industry_terms[industry_id]
        weights = self.matching_config.get("layer_weights", {})
        
        # 计算各层得分
        layer_scores = {}
        
        # L1: 核心关键词
        core_keywords = terms.get("core_keywords", [])
        layer_scores["core"] = self.calculate_layer_score(content, core_keywords)
        
        # L2: 技术术语
        technical_terms = terms.get("technical_terms", [])
        layer_scores["technical"] = self.calculate_layer_score(content, technical_terms)
        
        # L3: 应用场景
        application_scenarios = terms.get("application_scenarios", [])
        layer_scores["application"] = self.calculate_layer_score(content, application_scenarios)
        
        # L4: 相关实体
        related_entities = terms.get("related_entities", [])
        layer_scores["entities"] = self.calculate_layer_score(content, related_entities)
        
        # 计算加权总分
        total_score = (
            layer_scores["core"] * weights.get("core_keywords", 0.4) +
            layer_scores["technical"] * weights.get("technical_terms", 0.3) +
            layer_scores["application"] * weights.get("application_scenarios", 0.2) +
            layer_scores["entities"] * weights.get("related_entities", 0.1)
        )
        
        # 应用特殊规则（如果有的话）
        total_score = self.apply_special_rules(content, industry_id, total_score)
        
        # 缓存结果
        if cache_key and self.match_cache is not None:
            self.match_cache[cache_key] = total_score
        
        return total_score
    
    def apply_special_rules(self, content: str, industry_id: str, base_score: float) -> float:
        """
        应用特殊匹配规则
        
        Args:
            content: 文章内容
            industry_id: 行业ID
            base_score: 基础得分
            
        Returns:
            调整后的得分
        """
        if industry_id not in self.industry_configs:
            return base_score
        
        config = self.industry_configs[industry_id]
        special_rules = config.get("special_rules", {})
        
        content_lower = content.lower()
        adjusted_score = base_score
        
        # 排除规则
        exclude_keywords = special_rules.get("exclude_keywords", [])
        for exclude_word in exclude_keywords:
            if exclude_word.lower() in content_lower:
                adjusted_score *= 0.3  # 大幅降低得分
                self.logger.debug(f"应用排除规则: {exclude_word} -> 得分降低")
        
        # 必须配对规则
        required_pairs = special_rules.get("required_pairs", [])
        for pair in required_pairs:
            if len(pair) == 2:
                word1, word2 = pair[0].lower(), pair[1].lower()
                if word1 in content_lower and word2 in content_lower:
                    adjusted_score *= 1.2  # 得分提升
                    self.logger.debug(f"应用配对规则: {pair} -> 得分提升")
        
        # 上下文增强规则
        context_boost_words = special_rules.get("context_boost", [])
        for boost_word in context_boost_words:
            if boost_word.lower() in content_lower:
                adjusted_score *= 1.1  # 轻微提升
        
        return min(adjusted_score, 1.0)
    
    def match_industries_in_content(self, content: str) -> List[str]:
        """
        匹配文章内容中的所有行业
        
        Args:
            content: 文章内容
            
        Returns:
            匹配的行业名称列表
        """
        if not content or not self.industry_configs:
            return []
        
        thresholds = self.matching_config.get("thresholds", {})
        high_confidence = thresholds.get("high_confidence", 0.8)
        low_confidence = thresholds.get("low_confidence", 0.5)
        max_industries = self.matching_config.get("parameters", {}).get("max_industries_per_article", 3)
        
        # 计算所有行业的得分
        industry_scores = []
        for industry_id, config in self.industry_configs.items():
            score = self.match_industry_in_content(content, industry_id)
            if score >= low_confidence:
                industry_name = config.get("industry_info", {}).get("name", industry_id)
                industry_scores.append((industry_name, score))
        
        # 按得分排序
        industry_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 选择匹配的行业
        matched_industries = []
        for industry_name, score in industry_scores[:max_industries]:
            if score >= high_confidence or (len(matched_industries) == 0 and score >= low_confidence):
                matched_industries.append(industry_name)
        
        return matched_industries
    
    def process_news_batch(self, news_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """处理一批新闻数据"""
        results = []
        
        for news in news_batch:
            try:
                news_id = news.get('id')
                content = news.get('content', '')
                
                if not news_id:
                    continue
                
                # 匹配行业
                matched_industries = self.match_industries_in_content(content)
                
                # 准备更新数据
                result = {
                    'id': news_id,
                    'industries': matched_industries
                }
                results.append(result)
                
                # 更新计数器
                with self.lock:
                    self.processed_count += 1
                    if matched_industries:
                        self.matched_count += 1
                
            except Exception as e:
                self.logger.error(f"处理新闻 {news.get('id')} 时出错: {e}")
        
        return results
    
    def update_news_industries(self, updates: List[Dict[str, Any]]) -> int:
        """批量更新新闻的行业字段"""
        if not updates:
            return 0
        
        success_count = 0
        batch_size = self.main_config.get("database", {}).get("batch_update_size", 100)
        
        try:
            # 分批更新
            for i in range(0, len(updates), batch_size):
                batch = updates[i:i + batch_size]
                
                try:
                    # 使用 upsert 进行批量更新
                    for update in batch:
                        self.supabase_handler.client.table('news_items')\
                            .update({'industries': update['industries']})\
                            .eq('id', update['id'])\
                            .execute()
                        success_count += 1
                        
                except Exception as e:
                    self.logger.error(f"批量更新失败，尝试单个更新: {e}")
                    # 如果批量更新失败，尝试单个更新
                    for update in batch:
                        try:
                            self.supabase_handler.client.table('news_items')\
                                .update({'industries': update['industries']})\
                                .eq('id', update['id'])\
                                .execute()
                            success_count += 1
                        except Exception as e2:
                            self.logger.error(f"更新新闻 {update['id']} 失败: {e2}")
            
            return success_count
            
        except Exception as e:
            self.logger.error(f"批量更新新闻行业字段时出错: {e}")
            return success_count
    
    def run_matching(self) -> bool:
        """执行匹配任务"""
        start_time = time.time()
        self.logger.info("=" * 50)
        self.logger.info("开始执行新闻行业关联匹配任务")
        self.logger.info("=" * 50)
        
        # 初始化 Supabase 连接
        if not self.init_supabase():
            self.logger.error("Supabase 连接初始化失败，退出任务")
            return False
        
        # 加载行业配置
        if not self.load_industry_data():
            self.logger.error("加载行业配置失败，退出任务")
            return False
        
        # 获取新闻总数
        try:
            count_response = self.supabase_handler.client.table('news_items')\
                .select('id', count='exact').execute()
            total_news = count_response.count if count_response.count else 0
            self.logger.info(f"数据库中共有 {total_news} 条新闻需要处理")
        except Exception as e:
            self.logger.error(f"获取新闻总数失败: {e}")
            return False
        
        if total_news == 0:
            self.logger.info("没有新闻数据需要处理")
            return True
        
        # 多线程处理配置
        max_workers = self.performance_config.get("max_workers", 3)
        batch_size = self.performance_config.get("batch_size", 1000)
        all_updates = []
        
        self.logger.info(f"使用 {max_workers} 个线程，每批处理 {batch_size} 条新闻")
        
        # 分批处理新闻
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            # 提交所有批次任务
            for offset in range(0, total_news, batch_size):
                future = executor.submit(self._process_batch_worker, offset, batch_size)
                futures.append(future)
            
            # 收集结果
            for future in as_completed(futures):
                try:
                    batch_updates = future.result()
                    all_updates.extend(batch_updates)
                    
                    # 输出进度
                    progress = (self.processed_count / total_news) * 100
                    self.logger.info(f"处理进度: {self.processed_count}/{total_news} ({progress:.1f}%)")
                    
                except Exception as e:
                    self.logger.error(f"处理批次时出错: {e}")
        
        # 批量更新数据库
        self.logger.info(f"开始更新数据库，共 {len(all_updates)} 条记录...")
        updated_count = self.update_news_industries(all_updates)
        
        # 输出统计信息
        end_time = time.time()
        duration = end_time - start_time
        
        self.logger.info("=" * 50)
        self.logger.info("任务执行完成")
        self.logger.info(f"处理时间: {duration:.2f} 秒")
        self.logger.info(f"处理的新闻总数: {self.processed_count}")
        self.logger.info(f"匹配到行业的新闻数: {self.matched_count}")
        self.logger.info(f"未匹配到行业的新闻数: {self.processed_count - self.matched_count}")
        self.logger.info(f"成功更新的记录数: {updated_count}")
        self.logger.info(f"匹配成功率: {(self.matched_count/self.processed_count*100):.1f}%" if self.processed_count > 0 else "0%")
        self.logger.info("=" * 50)
        
        return True
    
    def _process_batch_worker(self, offset: int, batch_size: int) -> List[Dict[str, Any]]:
        """批次处理工作线程"""
        try:
            # 获取这一批的新闻数据
            news_batch = self.get_news_batch(offset, batch_size)
            
            if not news_batch:
                return []
            
            # 处理这一批新闻
            batch_updates = self.process_news_batch(news_batch)
            
            return batch_updates
            
        except Exception as e:
            self.logger.error(f"批次工作线程出错 (offset={offset}): {e}")
            return []


def main():
    """主函数"""
    try:
        matcher = IndustryMatcher()
        success = matcher.run_matching()
        
        if success:
            print("新闻行业关联匹配任务执行成功")
            sys.exit(0)
        else:
            print("新闻行业关联匹配任务执行失败")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("任务被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"任务执行时发生异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()