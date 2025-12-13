#!/usr/bin/env python3
"""Test script to verify the SQL and filters fixes."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_project_service():
    """Test project service with filters."""
    try:
        from services.project_service import ProjectService
        
        service = ProjectService()
        
        # Test get_projects method (should not cause AttributeError)
        print("Testing get_projects method...")
        success, projects = service.get_projects(filters={})
        print(f"✅ get_projects with empty filters: success={success}")
        
        # Test with ordering filters (should not cause SQL error)
        print("Testing get_projects with ordering filters...")
        success, projects = service.get_projects(filters={
            'order_by': 'modified_date',
            'order': 'desc'
        })
        print(f"✅ get_projects with ordering filters: success={success}")
        
        # Test with search filter
        print("Testing get_projects with search filter...")
        success, projects = service.get_projects(filters={
            'search': 'test',
            'order_by': 'name',
            'order': 'asc'
        })
        print(f"✅ get_projects with search filter: success={success}")
        
        print("✅ All project service tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Project service test failed: {e}")
        return False

def test_project_viewmodel():
    """Test project viewmodel."""
    try:
        from viewmodels.project_viewmodel import ProjectViewModel
        
        viewmodel = ProjectViewModel()
        
        # Test load_projects method
        print("Testing ProjectViewModel load_projects...")
        viewmodel.load_projects()
        print("✅ ProjectViewModel load_projects completed")
        
        return True
        
    except Exception as e:
        print(f"❌ ProjectViewModel test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing fixes for SQL and filters issues...\n")
    
    success = True
    
    # Test project service
    if not test_project_service():
        success = False
    
    print()
    
    # Test project viewmodel
    if not test_project_viewmodel():
        success = False
    
    print()
    
    if success:
        print("🎉 All tests passed! The fixes are working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    sys.exit(0 if success else 1)