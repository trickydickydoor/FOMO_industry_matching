#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Supabase 连接修复
验证新版本 SDK 是否能正常工作
"""

import os
import sys

def test_supabase_import():
    """测试 Supabase 包导入"""
    try:
        from supabase import create_client, Client
        print("OK Supabase package import successful")
        
        # 检查版本
        import supabase
        print(f"Supabase 版本: {getattr(supabase, '__version__', '未知')}")
        return True
    except ImportError as e:
        print(f"✗ Supabase 包导入失败: {e}")
        return False

def test_client_creation():
    """测试客户端创建"""
    try:
        from supabase import create_client
        
        # 使用测试URL和KEY
        test_url = "https://test.supabase.co"
        test_key = "test_key"
        
        try:
            client = create_client(test_url, test_key)
            print("✓ create_client 函数可以正常调用")
            return True
        except Exception as e:
            # 这里应该是认证错误而不是参数错误
            if 'proxy' in str(e):
                print(f"✗ 仍然存在 proxy 参数问题: {e}")
                return False
            else:
                print(f"✓ create_client 函数参数正常（预期的认证错误: {e}）")
                return True
                
    except Exception as e:
        print(f"✗ 客户端创建测试失败: {e}")
        return False

def test_database_handler():
    """测试数据库处理器"""
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from database.supabase_handler import SupabaseHandler
        
        # 测试初始化（不连接真实数据库）
        handler = SupabaseHandler(config_file='non_existent_config.json')
        print("✓ SupabaseHandler 类可以正常导入和初始化")
        return True
        
    except Exception as e:
        print(f"✗ SupabaseHandler 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=== Supabase 连接修复测试 ===\n")
    
    tests = [
        ("Supabase 包导入", test_supabase_import),
        ("客户端创建", test_client_creation),
        ("数据库处理器", test_database_handler),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"测试: {test_name}")
        if test_func():
            passed += 1
        print()
    
    print("=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("✓ 所有测试通过，修复成功")
        return True
    else:
        print("✗ 部分测试失败，需要进一步修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)