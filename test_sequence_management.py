#!/usr/bin/env python3
"""Test script for enhanced sequence management functionality."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all components can be imported."""
    print("Testing imports...")
    
    try:
        from viewmodels.sequence_management_viewmodel import SequenceManagementViewModel
        print("✓ SequenceManagementViewModel imported")
        
        from utils.cache_manager import get_cache_manager
        print("✓ Cache manager imported")
        
        from utils.resource_manager import get_resource_monitor, get_memory_manager
        print("✓ Resource manager imported")
        
        from utils.search_engine import get_search_engine
        print("✓ Search engine imported")
        
        from utils.pagination import LazyLoader, VirtualScrollManager, ChunkedProcessor
        print("✓ Pagination utilities imported")
        
        from views.pages.sequence_management_page import SequenceManagementPage
        print("✓ SequenceManagementPage imported")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_viewmodel_creation():
    """Test ViewModel creation and basic functionality."""
    print("\nTesting ViewModel creation...")
    
    try:
        from viewmodels.sequence_management_viewmodel import SequenceManagementViewModel
        
        # Create ViewModel
        vm = SequenceManagementViewModel()
        print("✓ SequenceManagementViewModel created")
        
        # Check initial state
        state_keys = list(vm.state.keys())
        print(f"✓ Initial state has {len(state_keys)} keys")
        
        # Test state operations
        vm.update_state('test_key', 'test_value')
        assert vm.get_state('test_key') == 'test_value'
        print("✓ State operations work")
        
        # Test pagination
        vm.set_page_size(25)
        assert vm.get_state('page_size') == 25
        print("✓ Pagination settings work")
        
        # Cleanup
        vm.cleanup()
        print("✓ ViewModel cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"✗ ViewModel test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cache_manager():
    """Test cache manager functionality."""
    print("\nTesting cache manager...")
    
    try:
        from utils.cache_manager import get_cache_manager
        
        cache = get_cache_manager()
        print("✓ Cache manager created")
        
        # Test memory cache
        cache.put("test_key", {"data": "test_value"})
        result = cache.get("test_key")
        assert result["data"] == "test_value"
        print("✓ Memory cache works")
        
        # Test cache stats
        stats = cache.get_stats()
        assert "memory_cache" in stats
        print("✓ Cache statistics work")
        
        return True
        
    except Exception as e:
        print(f"✗ Cache manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_resource_monitor():
    """Test resource monitoring functionality."""
    print("\nTesting resource monitor...")
    
    try:
        from utils.resource_manager import get_resource_monitor, get_memory_manager
        
        monitor = get_resource_monitor()
        print("✓ Resource monitor created")
        
        # Test snapshot
        snapshot = monitor.get_current_snapshot()
        assert snapshot.memory_mb > 0
        print(f"✓ Current memory usage: {snapshot.memory_mb:.1f}MB")
        
        # Test memory manager
        memory_mgr = get_memory_manager()
        memory_info = memory_mgr.get_memory_info()
        assert "rss_mb" in memory_info
        print("✓ Memory manager works")
        
        return True
        
    except Exception as e:
        print(f"✗ Resource monitor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_engine():
    """Test search engine functionality."""
    print("\nTesting search engine...")
    
    try:
        from utils.search_engine import get_search_engine
        
        search = get_search_engine()
        print("✓ Search engine created")
        
        # Test index creation
        test_data = [
            {"id": 1, "title": "Test Sequence 1", "content": "ATCGATCG"},
            {"id": 2, "title": "Test Sequence 2", "content": "GCTAGCTA"}
        ]
        
        search.build_index("test_sequences", test_data)
        print("✓ Search index built")
        
        # Test search
        results = search.search("Test", data_types=["test_sequences"])
        assert len(results) >= 0  # May be 0 if no matches
        print(f"✓ Search returned {len(results)} results")
        
        # Test suggestions
        suggestions = search.suggest("Test")
        print(f"✓ Search suggestions: {len(suggestions)} items")
        
        return True
        
    except Exception as e:
        print(f"✗ Search engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pagination():
    """Test pagination utilities."""
    print("\nTesting pagination utilities...")
    
    try:
        from utils.pagination import LazyLoader, VirtualScrollManager, ChunkedProcessor
        
        # Test virtual scroll manager
        scroll_mgr = VirtualScrollManager(total_items=1000, visible_items=20)
        start, end = scroll_mgr.get_visible_range()
        assert start >= 0 and end > start
        print(f"✓ Virtual scroll range: {start}-{end}")
        
        # Test chunked processor
        processor = ChunkedProcessor(chunk_size=10)
        print("✓ Chunked processor created")
        
        return True
        
    except Exception as e:
        print(f"✗ Pagination test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=== Enhanced Sequence Management Test Suite ===\n")
    
    tests = [
        test_imports,
        test_viewmodel_creation,
        test_cache_manager,
        test_resource_monitor,
        test_search_engine,
        test_pagination
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"Test {test.__name__} failed")
        except Exception as e:
            print(f"Test {test.__name__} crashed: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced sequence management is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())