#!/usr/bin/env python3
"""
Simple deployment test to verify our debugging changes are active
"""
import os
import sys
from pathlib import Path

def test_deployment():
    print("🧪 DEPLOYMENT TEST")
    print("=" * 50)
    
    # Check current working directory
    print(f"📁 Current directory: {os.getcwd()}")
    
    # Check if build files exist
    build_files = [
        'build_summary.txt',
        'cli_works.txt', 
        'claude_cli_path.txt',
        'npm_global_bin.txt',
        'node_version.txt'
    ]
    
    print("\n📋 Build files status:")
    files_found = 0
    for file in build_files:
        if os.path.exists(file):
            try:
                with open(file, 'r') as f:
                    content = f.read().strip()
                print(f"  ✅ {file}: {content}")
                files_found += 1
            except Exception as e:
                print(f"  ❌ {file}: Error - {e}")
        else:
            print(f"  ❌ {file}: NOT FOUND")
    
    # Check environment variables
    print(f"\n🔍 Environment variables:")
    env_vars = ['CLAUDE_CLI_PATH', 'PATH', 'NVM_DIR', 'HOME']
    for var in env_vars:
        value = os.getenv(var, 'NOT SET')
        if var == 'PATH':
            paths = value.split(':')[:3] if value != 'NOT SET' else []
            print(f"  - {var}: {':'.join(paths)}...")
        else:
            print(f"  - {var}: {value}")
    
    # Test Claude CLI detection
    print(f"\n🤖 Claude CLI detection:")
    import shutil
    claude_path = shutil.which('claude')
    if claude_path:
        print(f"  ✅ Found in PATH: {claude_path}")
    else:
        print(f"  ❌ Not found in PATH")
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"  - Build files found: {files_found}/{len(build_files)}")
    print(f"  - Claude CLI in PATH: {'Yes' if claude_path else 'No'}")
    print(f"  - CLAUDE_CLI_PATH set: {'Yes' if os.getenv('CLAUDE_CLI_PATH') else 'No'}")
    
    if files_found == 0:
        print(f"\n❌ DEPLOYMENT ISSUE: No build files found - enhanced debugging didn't run")
        return False
    else:
        print(f"\n✅ DEPLOYMENT OK: Build debugging appears to have run")
        return True

if __name__ == "__main__":
    test_deployment()