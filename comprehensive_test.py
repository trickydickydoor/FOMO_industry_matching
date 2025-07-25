#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合测试套件 - 测试多行业识别准确性
"""

import sys
import os
import logging
from typing import List, Dict, Any, Tuple

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.industry_matcher import IndustryMatcher


class ComprehensiveIndustryTester:
    """综合行业匹配测试器"""
    
    def __init__(self):
        """初始化测试器"""
        self.setup_logging()
        self.matcher = IndustryMatcher()
        
        # 扩展的测试用例集
        self.test_cases = self.load_comprehensive_test_cases()
        
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def load_comprehensive_test_cases(self) -> List[Dict[str, Any]]:
        """加载综合测试用例"""
        return [
            # 半导体行业测试用例
            {
                "name": "半导体制程突破",
                "content": """
                台积电宣布其3nm制程技术取得重大突破，新一代芯片的性能相比5nm制程提升15%，功耗降低30%。
                该技术采用了最先进的EUV光刻工艺，晶圆良率已经达到商业化标准。
                这项技术将首先应用于苹果的A17处理器和高通的下一代骁龙芯片。
                """,
                "expected": ["半导体"],
                "description": "典型半导体技术新闻"
            },
            {
                "name": "芯片设计公司",
                "content": """
                中芯国际发布Q3财报，受益于汽车芯片和物联网芯片需求增长，营收同比增长23%。
                公司在28nm制程产能利用率达到95%，14nm制程也进入量产阶段。
                CEO表示将继续投资先进制程研发，加强与设备厂商ASML和应用材料的合作。
                """,
                "expected": ["半导体"],
                "description": "芯片代工厂商新闻"
            },
            
            # 游戏行业测试用例
            {
                "name": "游戏公司财报",
                "content": """
                米哈游《原神》海外收入突破10亿美元，成为中国游戏出海的标杆产品。
                该游戏采用Unity引擎开发，在移动端和PC端都实现了优秀的3D渲染效果。
                公司表示将继续投资游戏开发技术，计划推出更多原创IP。
                """,
                "expected": ["游戏"],
                "description": "游戏公司和产品新闻"
            },
            {
                "name": "电竞赛事",
                "content": """
                2023年英雄联盟全球总决赛在韩国首尔举行，吸引了全球数千万观众观看。
                电竞产业的快速发展带动了游戏直播、赛事运营、电竞培训等相关业务。
                腾讯游戏作为赛事主办方，展示了其在电竞生态建设方面的实力。
                """,
                "expected": ["游戏"],
                "description": "电竞赛事和生态新闻"
            },
            
            # 人工智能行业测试用例
            {
                "name": "大模型发布",
                "content": """
                百度发布文心大模型4.0版本，在自然语言理解和生成能力上显著提升。
                新模型采用Transformer架构，参数规模达到千亿级别，支持多模态输入。
                该模型已在智能客服、智能写作、代码生成等场景实现商业化应用。
                """,
                "expected": ["人工智能"],
                "description": "AI大模型技术新闻"
            },
            {
                "name": "AI应用落地",
                "content": """
                OpenAI的ChatGPT用户数突破1亿，AIGC技术开始在各行业广泛应用。
                企业级AI应用需求激增，推动了GPU算力、模型训练、推理部署等产业链发展。
                分析师预计，人工智能将成为下一轮技术革命的核心驱动力。
                """,
                "expected": ["人工智能"],
                "description": "AI商业化应用新闻"
            },
            
            # 金融科技行业测试用例
            {
                "name": "移动支付发展",
                "content": """
                央行数字货币试点范围进一步扩大，数字人民币在零售支付场景的应用日趋成熟。
                支付宝和微信支付继续优化用户体验，在跨境支付、小微商户服务等方面发力。
                金融科技的发展正在重塑传统银行业的服务模式和竞争格局。
                """,
                "expected": ["金融科技"],
                "description": "数字支付和央行数字货币新闻"
            },
            {
                "name": "区块链金融",
                "content": """
                蚂蚁集团推出基于区块链技术的供应链金融解决方案，帮助中小企业解决融资难题。
                该平台通过智能合约自动化处理贸易融资流程，大幅提升效率并降低风险。
                区块链在金融领域的应用正从概念验证走向规模化商业部署。
                """,
                "expected": ["金融科技"],
                "description": "区块链金融应用新闻"
            },
            
            # 多行业交叉测试用例
            {
                "name": "AI+游戏",
                "content": """
                英伟达发布专为游戏AI设计的新一代RTX显卡，集成了专用的AI加速单元。
                该显卡不仅能提升游戏画质和性能，还支持实时AI对话、智能NPC等功能。
                游戏行业正在积极探索AI技术的应用，打造更智能、更沉浸的游戏体验。
                """,
                "expected": ["半导体", "游戏", "人工智能"],
                "description": "AI技术在游戏硬件中的应用"
            },
            {
                "name": "金融科技+AI",
                "content": """
                蚂蚁集团利用大模型技术升级智能客服系统，客户问题解决率提升40%。
                该系统基于自然语言处理和机器学习算法，能够理解复杂的金融业务咨询。
                人工智能在金融科技领域的深度应用，正在重新定义用户体验标准。
                """,
                "expected": ["金融科技", "人工智能"],
                "description": "AI技术在金融服务中的应用"
            },
            
            # 负面测试用例（应该不匹配）
            {
                "name": "纯经济新闻",
                "content": """
                国家统计局发布10月份经济数据，CPI同比上涨2.1%，PPI同比下降1.3%。
                专家分析认为，当前通胀压力总体可控，经济运行保持在合理区间。
                下一步将继续实施积极的财政政策和稳健的货币政策。
                """,
                "expected": [],
                "description": "纯宏观经济新闻，不应匹配任何技术行业"
            },
            {
                "name": "股市新闻",
                "content": """
                A股三大指数集体收涨，沪指上涨1.2%，深成指上涨1.8%，创业板指上涨2.1%。
                科技股表现活跃，半导体概念股、AI概念股、游戏概念股均有不错涨幅。
                分析师认为，市场情绪正在回暖，投资者风险偏好有所提升。
                """,
                "expected": [],
                "description": "纯股市新闻，虽然提及概念股但应被排除规则过滤"
            },
            
            # 边界测试用例
            {
                "name": "隐性半导体内容",
                "content": """
                苹果发布M3芯片，采用最新的架构设计，CPU性能提升20%，GPU性能提升40%。
                该芯片集成了160亿个晶体管，支持统一内存架构，最高可配置128GB内存。
                新芯片在视频编解码、机器学习推理等任务上表现出色。
                """,
                "expected": ["半导体"],
                "description": "没有直接提及'半导体'，但通过技术特征应该识别"
            },
            {
                "name": "游戏技术新闻",
                "content": """
                虚幻引擎5正式发布，带来了革命性的Nanite虚拟几何和Lumen全局光照技术。
                该引擎能够实现电影级别的视觉效果，将推动次世代游戏开发的技术边界。
                Epic Games表示，新引擎将大幅降低AAA游戏的开发成本和技术门槛。
                """,
                "expected": ["游戏"],
                "description": "通过游戏引擎技术识别游戏行业"
            }
        ]
    
    def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个测试用例"""
        try:
            content = test_case["content"].strip()
            expected = set(test_case["expected"])
            
            # 执行匹配
            matched_industries = set(self.matcher.match_industries_in_content(content))
            
            # 计算准确性指标
            correct_matches = expected & matched_industries
            false_positives = matched_industries - expected
            false_negatives = expected - matched_industries
            
            # 计算评估指标
            precision = len(correct_matches) / len(matched_industries) if matched_industries else (1.0 if not expected else 0.0)
            recall = len(correct_matches) / len(expected) if expected else (1.0 if not matched_industries else 0.0)
            f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
            
            # 计算准确率（正确预测/总预测）
            total_possible = len(expected) + len(matched_industries) - len(correct_matches)
            accuracy = len(correct_matches) / total_possible if total_possible > 0 else 1.0
            
            return {
                "success": True,
                "matched": list(matched_industries),
                "expected": list(expected),
                "correct_matches": list(correct_matches),
                "false_positives": list(false_positives),
                "false_negatives": list(false_negatives),
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "accuracy": accuracy
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """运行综合测试"""
        self.logger.info("开始运行综合行业匹配测试...")
        
        # 首先确保系统已加载行业数据
        if not self.matcher.load_industry_data():
            self.logger.error("无法加载行业数据，测试终止")
            return {"success": False, "error": "无法加载行业数据"}
        
        self.logger.info(f"已加载行业: {list(self.matcher.industry_configs.keys())}")
        
        results = []
        metrics_sum = {
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "accuracy": 0.0
        }
        successful_tests = 0
        
        # 按行业分类统计
        industry_stats = {
            "半导体": {"total": 0, "correct": 0},
            "游戏": {"total": 0, "correct": 0},
            "人工智能": {"total": 0, "correct": 0},
            "金融科技": {"total": 0, "correct": 0},
            "多行业": {"total": 0, "correct": 0},
            "负面测试": {"total": 0, "correct": 0}
        }
        
        for i, test_case in enumerate(self.test_cases, 1):
            self.logger.info(f"\n--- 测试用例 {i}: {test_case['name']} ---")
            self.logger.info(f"描述: {test_case['description']}")
            
            result = self.run_single_test(test_case)
            
            if result["success"]:
                # 统计各行业测试情况
                expected = set(test_case["expected"])
                if len(expected) == 0:
                    category = "负面测试"
                elif len(expected) > 1:
                    category = "多行业"
                else:
                    category = list(expected)[0] if expected else "负面测试"
                
                if category in industry_stats:
                    industry_stats[category]["total"] += 1
                    if result["f1_score"] >= 0.8:  # F1分数>=0.8认为测试通过
                        industry_stats[category]["correct"] += 1
                
                self.logger.info(f"期望: {result['expected']}")
                self.logger.info(f"实际: {result['matched']}")
                self.logger.info(f"准确率: {result['accuracy']:.3f}")
                self.logger.info(f"精确率: {result['precision']:.3f}")
                self.logger.info(f"召回率: {result['recall']:.3f}")
                self.logger.info(f"F1分数: {result['f1_score']:.3f}")
                
                if result['false_positives']:
                    self.logger.warning(f"误报: {result['false_positives']}")
                if result['false_negatives']:
                    self.logger.warning(f"漏报: {result['false_negatives']}")
                
                # 累计指标
                metrics_sum["precision"] += result['precision']
                metrics_sum["recall"] += result['recall']
                metrics_sum["f1_score"] += result['f1_score']
                metrics_sum["accuracy"] += result['accuracy']
                successful_tests += 1
                
            else:
                self.logger.error(f"测试失败: {result['error']}")
            
            results.append({
                "test_case": test_case['name'],
                "category": category if result["success"] else "failed",
                "result": result
            })
        
        # 计算平均指标
        avg_metrics = {}
        if successful_tests > 0:
            for metric in metrics_sum:
                avg_metrics[metric] = metrics_sum[metric] / successful_tests
        
        # 生成测试报告
        summary = {
            "total_tests": len(self.test_cases),
            "successful_tests": successful_tests,
            "failed_tests": len(self.test_cases) - successful_tests,
            "average_metrics": avg_metrics,
            "industry_stats": industry_stats,
            "results": results
        }
        
        # 打印详细报告
        self.print_test_report(summary)
        
        return summary
    
    def print_test_report(self, summary: Dict[str, Any]):
        """打印测试报告"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("综合测试报告")
        self.logger.info("=" * 60)
        
        # 总体统计
        self.logger.info(f"总测试数: {summary['total_tests']}")
        self.logger.info(f"成功测试数: {summary['successful_tests']}")
        self.logger.info(f"失败测试数: {summary['failed_tests']}")
        
        # 平均指标
        if summary['average_metrics']:
            self.logger.info(f"\n平均性能指标:")
            for metric, value in summary['average_metrics'].items():
                self.logger.info(f"  {metric}: {value:.3f}")
        
        # 各行业统计
        self.logger.info(f"\n各行业测试统计:")
        for industry, stats in summary['industry_stats'].items():
            if stats['total'] > 0:
                success_rate = stats['correct'] / stats['total']
                self.logger.info(f"  {industry}: {stats['correct']}/{stats['total']} ({success_rate:.1%})")
        
        # 整体评估
        overall_f1 = summary['average_metrics'].get('f1_score', 0)
        if overall_f1 >= 0.8:
            self.logger.info(f"\n[EXCELLENT] 系统表现优秀！平均F1分数: {overall_f1:.3f}")
        elif overall_f1 >= 0.7:
            self.logger.info(f"\n[GOOD] 系统表现良好！平均F1分数: {overall_f1:.3f}")
        elif overall_f1 >= 0.6:
            self.logger.info(f"\n[ACCEPTABLE] 系统表现可接受，平均F1分数: {overall_f1:.3f}")
        else:
            self.logger.info(f"\n[NEEDS_IMPROVEMENT] 系统需要改进，平均F1分数: {overall_f1:.3f}")


def main():
    """主函数"""
    tester = ComprehensiveIndustryTester()
    
    # 运行综合测试
    summary = tester.run_comprehensive_test()
    
    if not summary.get("success", True):
        print(f"测试执行失败: {summary.get('error', '未知错误')}")
        return False
    
    # 根据结果判断测试是否通过
    avg_f1 = summary.get('average_metrics', {}).get('f1_score', 0)
    
    if avg_f1 >= 0.7:
        print(f"\n[SUCCESS] 综合测试通过！平均F1分数: {avg_f1:.3f}")
        return True
    else:
        print(f"\n[FAILED] 综合测试未通过。平均F1分数: {avg_f1:.3f}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)