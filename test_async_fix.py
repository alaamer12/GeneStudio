#!/usr/bin/env python3
"""Test script to verify async operations are working correctly."""

import sys
import os
import time
import threading

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_async_operations():
    """Test async operations without UI."""
    try:
        from viewmodels.dashboard_viewmodel import DashboardViewModel
        
        print("🧪 Testing async operations...")
        
        # Create viewmodel
        viewmodel = DashboardViewModel()
        
        # Track completion
        completed = threading.Event()
        results = {}
        
        def on_state_change(key, value):
            print(f"📊 State changed: {key} = {value}")
            if key == 'statistics':
                results['statistics'] = value
                completed.set()
        
        # Add observer
        viewmodel.add_observer(on_state_change)
        
        # Load dashboard data
        print("🔄 Loading dashboard data...")
        viewmodel.load_dashboard_data()
        
        # Wait for completion (with timeout)
        if completed.wait(timeout=10):
            print("✅ Async operation completed successfully!")
            stats = results.get('statistics', {})
            print(f"📈 Statistics: {stats}")
            return True
        else:
            print("❌ Async operation timed out!")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_project_service_direct():
    """Test project service directly."""
    try:
        from services.project_service import ProjectService
        
        print("🧪 Testing project service directly...")
        
        service = ProjectService()
        
        # Test get_project_statistics
        print("📊 Getting project statistics...")
        success, stats = service.get_project_statistics()
        
        if success:
            print(f"✅ Statistics loaded: {stats}")
            return True
        else:
            print(f"❌ Failed to load statistics: {stats}")
            return False
        
    except Exception as e:
        print(f"❌ Direct test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Async Operation Fixes\n")
    
    success = True
    
    # Test project service directly
    print("=" * 50)
    if not test_project_service_direct():
        success = False
    
    print("\n" + "=" * 50)
    
    # Test async operations
    if not test_async_operations():
        success = False
    
    print("\n" + "=" * 50)
    
    if success:
        print("🎉 All async tests passed!")
    else:
        print("❌ Some async tests failed.")
    
    sys.exit(0 if success else 1)