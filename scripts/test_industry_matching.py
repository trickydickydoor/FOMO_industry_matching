#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行业匹配测试脚本
验证行业识别系统的准确性和效果
"""

import os
import sys
import logging
from typing import List, Dict, Any, Tuple

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.industry_matcher import IndustryMatcher
from database.config_loader import IndustryConfigLoader


class IndustryMatchingTester:
    """行业匹配测试器"""
    
    def __init__(self):
        """初始化测试器"""
        self.setup_logging()
        self.matcher = IndustryMatcher()
        self.config_loader = IndustryConfigLoader()
        
        # 测试用例
        self.test_cases = self.load_test_cases()
        
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def load_test_cases(self) -> List[Dict[str, Any]]:
        """加载测试用例"""
        return [
            {
                "name": "半导体核心技术",
                "content": """
                台积电宣布其3nm制程技术取得重大突破，新一代芯片的性能相比5nm制程提升15%，功耗降低30%。
                该技术采用了最先进的EUV光刻工艺，晶圆良率已经达到商业化标准。
                这项技术将首先应用于苹果的A17处理器和高通的下一代骁龙芯片。
                业内专家认为，这将进一步巩固台积电在先进制程领域的领导地位。
                """,
                "expected": ["半导体"],
                "description": "包含制程、EUV、晶圆、处理器等典型半导体关键词"
            },
            {
                "name": "半导体产业链",
                "content": """
                中芯国际发布Q3财报，受益于汽车芯片和物联网芯片需求增长，营收同比增长23%。
                公司在28nm制程产能利用率达到95%，14nm制程也进入量产阶段。
                CEO表示将继续投资先进制程研发，加强与设备厂商ASML和应用材料的合作。
                分析师预计，随着国产替代趋势加速，公司有望获得更多订单。
                """,
                "expected": ["半导体"],
                "description": "通过产业链公司、制程、产能等概念识别半导体行业"
            },
            {
                "name": "游戏行业直接描述",
                "content": """
                米哈游《原神》海外收入突破10亿美元，成为中国游戏出海的标杆产品。
                该游戏采用Unity引擎开发，在移动端和PC端都实现了优秀的3D渲染效果。
                公司表示将继续投资游戏开发技术，计划推出更多原创IP。
                电竞产业的快速发展也为游戏公司带来了新的商业模式。
                """,
                "expected": ["游戏"],
                "description": "包含游戏公司、游戏开发、Unity引擎等典型游戏行业特征"
            },
            {
                "name": "AI技术应用",
                "content": """
                百度发布文心大模型4.0版本，在自然语言理解和生成能力上显著提升。
                新模型采用Transformer架构，参数规模达到千亿级别，支持多模态输入。
                该模型已在智能客服、智能写作、代码生成等场景实现商业化应用。
                公司还推出了面向企业的AIGC平台，帮助传统行业实现智能化转型。
                """,
                "expected": ["人工智能"],
                "description": "包含大模型、NLP、Transformer等AI技术特征"
            },
            {
                "name": "隐性半导体内容",
                "content": """
                苹果发布M3芯片，采用了最新的架构设计，CPU性能提升20%，GPU性能提升40%。
                该芯片集成了160亿个晶体管，支持统一内存架构，最高可配置128GB内存。
                新芯片在视频编解码、机器学习推理等任务上表现出色。
                分析师认为，这将推动MacBook和iPad产品线的销量增长。
                """,
                "expected": ["半导体"],
                "description": "没有直接提及'半导体'，但通过芯片、晶体管、架构等概念应该识别出来"
            },
            {
                "name": "非技术新闻",
                "content": """
                国家统计局发布10月份经济数据，CPI同比上涨2.1%，PPI同比下降1.3%。
                专家分析认为，当前通胀压力总体可控，经济运行保持在合理区间。
                下一步将继续实施积极的财政政策和稳健的货币政策。
                预计四季度经济将保持稳中有进的态势。
                """,
                "expected": [],
                "description": "纯经济政策新闻，不应匹配到任何技术行业"
            },
            {
                "name": "混合行业内容",
                "content": """
                英伟达发布新一代RTX 4090显卡，采用4nm制程工艺，专为游戏和AI计算设计。
                该显卡在《赛博朋克2077》等3A游戏中表现优异，同时也能加速机器学习训练。
                游戏开发商普遍认为，新显卡将推动光线追踪技术的普及。
                AI研究者也对其在深度学习模型训练方面的性能表示期待。
                """,
                "expected": ["半导体", "游戏", "人工智能"],
                "description": "同时涉及半导体制造、游戏性能、AI计算，应该匹配多个行业"
            }
        ]
    
    def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个测试用例"""
        try:
            # 加载行业数据
            if not self.matcher.load_industry_data():
                return {
                    "success": False,
                    "error": "无法加载行业数据"
                }
            
            content = test_case["content"].strip()
            expected = test_case["expected"]
            
            # 执行匹配
            matched_industries = self.matcher.match_industries_in_content(content)
            
            # 计算准确性
            expected_set = set(expected)
            matched_set = set(matched_industries)
            
            correct_matches = expected_set & matched_set
            false_positives = matched_set - expected_set
            false_negatives = expected_set - matched_set
            
            precision = len(correct_matches) / len(matched_set) if matched_set else (1.0 if not expected_set else 0.0)
            recall = len(correct_matches) / len(expected_set) if expected_set else (1.0 if not matched_set else 0.0)
            f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
            
            return {
                "success": True,
                "matched": matched_industries,
                "expected": expected,
                "correct_matches": list(correct_matches),
                "false_positives": list(false_positives),
                "false_negatives": list(false_negatives),
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试用例"""
        self.logger.info("开始运行行业匹配测试...")
        
        results = []
        total_precision = 0.0
        total_recall = 0.0
        total_f1 = 0.0
        successful_tests = 0
        
        for i, test_case in enumerate(self.test_cases, 1):
            self.logger.info(f"\n测试用例 {i}: {test_case['name']}")
            self.logger.info(f"描述: {test_case['description']}")
            
            result = self.run_single_test(test_case)
            
            if result["success"]:
                self.logger.info(f"期望结果: {result['expected']}")
                self.logger.info(f"实际结果: {result['matched']}")
                self.logger.info(f"准确率: {result['precision']:.2f}")
                self.logger.info(f"召回率: {result['recall']:.2f}")
                self.logger.info(f"F1分数: {result['f1_score']:.2f}")
                
                if result['false_positives']:
                    self.logger.warning(f"误报: {result['false_positives']}")
                if result['false_negatives']:
                    self.logger.warning(f"漏报: {result['false_negatives']}")
                
                total_precision += result['precision']
                total_recall += result['recall']
                total_f1 += result['f1_score']
                successful_tests += 1
            else:
                self.logger.error(f"测试失败: {result['error']}")
            
            results.append({
                "test_case": test_case['name'],
                "result": result
            })
        
        # 计算平均指标
        avg_precision = total_precision / successful_tests if successful_tests > 0 else 0.0
        avg_recall = total_recall / successful_tests if successful_tests > 0 else 0.0
        avg_f1 = total_f1 / successful_tests if successful_tests > 0 else 0.0
        
        summary = {
            "total_tests": len(self.test_cases),
            "successful_tests": successful_tests,
            "failed_tests": len(self.test_cases) - successful_tests,
            "average_precision": avg_precision,
            "average_recall": avg_recall,
            "average_f1_score": avg_f1,
            "results": results
        }
        
        # 输出总结
        self.logger.info("\n" + "=" * 50)
        self.logger.info("测试总结")
        self.logger.info("=" * 50)
        self.logger.info(f"总测试数: {summary['total_tests']}")
        self.logger.info(f"成功测试数: {summary['successful_tests']}")
        self.logger.info(f"失败测试数: {summary['failed_tests']}")
        self.logger.info(f"平均准确率: {avg_precision:.2f}")
        self.logger.info(f"平均召回率: {avg_recall:.2f}")
        self.logger.info(f"平均F1分数: {avg_f1:.2f}")
        
        return summary
    
    def test_configuration(self):
        """测试配置加载"""
        self.logger.info("测试配置系统...")
        
        # 测试配置加载器
        validation_results = self.config_loader.validate_all_configs()
        self.logger.info(f"配置验证结果: {validation_results}")
        
        # 列出可用行业
        available_industries = self.config_loader.list_available_industries()
        self.logger.info(f"可用行业: {available_industries}")
        
        # 测试半导体配置
        if "semiconductor" in available_industries:
            terms = self.config_loader.get_industry_terms("semiconductor")
            for layer, keywords in terms.items():
                self.logger.info(f"{layer}: {len(keywords)} 个关键词")
    
    def test_detailed_scoring(self, content: str):
        """测试详细评分过程"""
        self.logger.info(f"详细评分测试:")
        self.logger.info(f"测试内容: {content[:100]}...")
        
        if not self.matcher.load_industry_data():
            self.logger.error("无法加载行业数据")
            return
        
        # 对每个行业计算详细得分
        for industry_id in self.matcher.industry_configs:
            score = self.matcher.match_industry_in_content(content, industry_id)
            industry_name = self.matcher.industry_configs[industry_id].get("industry_info", {}).get("name", industry_id)
            self.logger.info(f"{industry_name}: {score:.3f}")


def main():
    """主函数"""
    tester = IndustryMatchingTester()
    
    # 测试配置系统
    print("1. 测试配置系统...")
    tester.test_configuration()
    
    # 运行匹配测试
    print("\n2. 运行匹配测试...")
    summary = tester.run_all_tests()
    
    # 详细评分测试
    print("\n3. 详细评分测试...")
    test_content = """台积电宣布其3nm制程技术取得重大突破，新一代芯片的性能相比5nm制程提升15%。"""
    tester.test_detailed_scoring(test_content)
    
    # 判断测试是否通过
    if summary['average_f1_score'] >= 0.7:
        print(f"\n✅ 测试通过！平均F1分数: {summary['average_f1_score']:.2f}")
        return True
    else:
        print(f"\n❌ 测试未通过。平均F1分数: {summary['average_f1_score']:.2f}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)