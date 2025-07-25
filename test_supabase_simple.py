#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

def test_supabase():
    """Test Supabase connection"""
    try:
        from supabase import create_client
        print("Supabase import: OK")
        
        # Test client creation with dummy values
        test_url = "https://test.supabase.co"
        test_key = "test_key"
        
        try:
            client = create_client(test_url, test_key)
            print("Client creation: OK")
        except Exception as e:
            if 'proxy' in str(e):
                print(f"Client creation: FAILED - proxy error: {e}")
                return False
            else:
                print(f"Client creation: OK - expected auth error: {e}")
        
        return True
        
    except Exception as e:
        print(f"Supabase test FAILED: {e}")
        return False

def test_handler():
    """Test database handler"""
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from database.supabase_handler import SupabaseHandler
        
        handler = SupabaseHandler(config_file='dummy.json')
        print("SupabaseHandler import: OK")
        return True
        
    except Exception as e:
        print(f"Handler test FAILED: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing Supabase Fix ===")
    
    result1 = test_supabase()
    result2 = test_handler()
    
    if result1 and result2:
        print("All tests PASSED")
        sys.exit(0)
    else:
        print("Some tests FAILED")
        sys.exit(1)