#!/usr/bin/env python3
"""
Test script to verify the PyPI package works when imported from outside the project.
This script will run from /tmp to ensure we're testing the installed package, not local dev version.
"""

import subprocess
import sys
import tempfile
import os

def test_pypi_package():
    """Test the dextrades package from PyPI in a clean environment."""
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Testing from clean directory: {tmpdir}")
        
        # Test basic import
        cmd = [
            "uv", "run", "--with", "dextrades", 
            "python", "-c", "import dextrades; print('✅ Import successful')"
        ]
        
        try:
            result = subprocess.run(cmd, cwd=tmpdir, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Basic import test: PASSED")
                print(f"Output: {result.stdout.strip()}")
            else:
                print("❌ Basic import test: FAILED") 
                print(f"Error: {result.stderr.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Basic import test: TIMEOUT")
            return False
        except Exception as e:
            print(f"❌ Basic import test: EXCEPTION - {e}")
            return False
        
        # Test functionality
        cmd = [
            "uv", "run", "--with", "dextrades",
            "python", "-c", 
            """
import dextrades
config = dextrades.PyConfigBuilder()
print('✅ PyConfigBuilder works')
print(f'✅ Available functions: {len([x for x in dir(dextrades) if not x.startswith("_")])}')
"""
        ]
        
        try:
            result = subprocess.run(cmd, cwd=tmpdir, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Functionality test: PASSED")
                print(f"Output: {result.stdout.strip()}")
            else:
                print("❌ Functionality test: FAILED")
                print(f"Error: {result.stderr.strip()}")
                return False
                
        except Exception as e:
            print(f"❌ Functionality test: EXCEPTION - {e}")
            return False
        
        # Test CLI
        cmd = ["uv", "run", "--with", "dextrades", "dextrades", "--help"]
        
        try:
            result = subprocess.run(cmd, cwd=tmpdir, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and "usage: dextrades" in result.stdout:
                print("✅ CLI test: PASSED")
            else:
                print("❌ CLI test: FAILED")
                print(f"Error: {result.stderr.strip()}")
                return False
                
        except Exception as e:
            print(f"❌ CLI test: EXCEPTION - {e}")
            return False
        
        return True

if __name__ == "__main__":
    print("🧪 Testing dextrades PyPI package from external directory...")
    print("=" * 60)
    
    success = test_pypi_package()
    
    print("=" * 60)
    if success:
        print("🎉 All tests PASSED! The PyPI package works correctly.")
    else:
        print("💥 Some tests FAILED! There may be an issue with the PyPI package.")
        sys.exit(1)