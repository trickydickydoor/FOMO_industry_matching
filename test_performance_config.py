#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试性能配置优化
"""

import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.config_loader import IndustryConfigLoader

def test_performance_config():
    """测试性能配置"""
    try:
        # 初始化配置加载器
        loader = IndustryConfigLoader()
        
        # 获取性能配置
        performance_config = loader.get_performance_config()
        
        print("=== 性能配置测试 ===")
        print(f"批处理大小: {performance_config.get('batch_size')}")
        print(f"最大线程数: {performance_config.get('max_workers')}")
        print(f"请求延迟: {performance_config.get('request_delay', 0)} 秒")
        print(f"缓存启用: {performance_config.get('cache_enabled')}")
        print(f"超时时间: {performance_config.get('timeout_seconds')} 秒")
        
        # 高级参数
        print("\n=== 高级性能参数 ===")
        print(f"连接池大小: {performance_config.get('db_connection_pool', '未设置')}")
        print(f"重试次数: {performance_config.get('retry_attempts', '未设置')}")
        print(f"退避因子: {performance_config.get('backoff_factor', '未设置')}")
        
        # 模拟智能调整
        print("\n=== 智能调整模拟 ===")
        
        test_cases = [50, 100, 348, 500, 1000, 5000]
        max_workers = performance_config.get("max_workers", 3)
        batch_size = performance_config.get("batch_size", 1000)
        
        for total_news in test_cases:
            adjusted_batch = batch_size
            adjusted_workers = max_workers
            
            if total_news < 100:
                adjusted_batch = min(batch_size, 10)
                adjusted_workers = min(max_workers, 4)
            elif total_news < 500:
                adjusted_batch = min(batch_size, 25)
                adjusted_workers = min(max_workers, 6)
            
            batches = (total_news + adjusted_batch - 1) // adjusted_batch
            print(f"  {total_news:4d} 条 → {adjusted_workers} 线程, {adjusted_batch:2d} 条/批, {batches:2d} 批次")
        
        return True
        
    except Exception as e:
        print(f"性能配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_performance_config():
        print("\n✓ 性能配置测试通过!")
        sys.exit(0)
    else:
        print("\n✗ 性能配置测试失败!")
        sys.exit(1)