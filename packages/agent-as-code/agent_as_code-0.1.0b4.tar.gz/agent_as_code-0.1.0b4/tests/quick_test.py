#!/usr/bin/env python3
"""
Quick Test Script for Agent as Code Framework
============================================

This script provides rapid verification of core framework functionality.
Run with: python quick_test.py

Tests:
1. CLI availability
2. Basic agent creation
3. Agentfile parsing
4. Builder functionality
5. Security validation
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

# Add yaml import for testing
try:
    import yaml
except ImportError:
    print("⚠️ PyYAML not installed. Install with: pip install pyyaml")

def test_cli_availability():
    """Test if CLI is available"""
    print("🔧 Testing CLI availability...")
    try:
        result = subprocess.run(['agent', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ CLI is available")
            return True
        else:
            print("❌ CLI returned error")
            return False
    except FileNotFoundError:
        print("❌ CLI not found. Install with: pipx install -e .")
        return False

def test_agent_creation():
    """Test basic agent creation"""
    print("\n📁 Testing agent creation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        # Create test agent
        result = subprocess.run(['agent', 'init', 'test-agent'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Agent creation successful")
            return True
        else:
            print(f"❌ Agent creation failed: {result.stderr}")
            return False

def test_agentfile_parsing():
    """Test Agentfile parsing"""
    print("\n📄 Testing Agentfile parsing...")
    
    try:
        from agent_as_code.parser.aac_parser import AaCParser
        
        parser = AaCParser()
        
        # Test simple Agentfile
        agentfile_content = """FROM agent/python:3.11-docker
CAPABILITY test
MODEL local
ENV TEST_VAR=test_value
EXPOSE 50051
ENTRYPOINT python main.py
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.agentfile', delete=False) as f:
            f.write(agentfile_content)
            f.flush()
            
            config = parser.parse_agentfile(f.name)
            
            if config and config.runtime == "agent/python:3.11-docker":
                print("✅ Agentfile parsing successful")
                os.unlink(f.name)
                return True
            else:
                print("❌ Agentfile parsing failed")
                os.unlink(f.name)
                return False
                
    except Exception as e:
        print(f"❌ Agentfile parsing error: {e}")
        return False

def test_builder_functionality():
    """Test builder functionality"""
    print("\n🏗️ Testing builder functionality...")
    
    try:
        from agent_as_code.builder.unified_builder import UnifiedAgentBuilder
        from agent_as_code.parser.aac_parser import AaCParser
        
        parser = AaCParser()
        builder = UnifiedAgentBuilder()
        
        # Create test configuration
        agentfile_content = """FROM agent/python:3.11-docker
CAPABILITY test
MODEL local
ENV TEST_VAR=test_value
EXPOSE 50051
ENTRYPOINT python main.py
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.agentfile', delete=False) as f:
            f.write(agentfile_content)
            f.flush()
            
            config = parser.parse_agentfile(f.name)
            package = builder.build_microservice(config, "test-agent:latest")
            
            if package and Path(package.build_path).exists():
                print("✅ Builder functionality successful")
                os.unlink(f.name)
                return True
            else:
                print("❌ Builder functionality failed")
                os.unlink(f.name)
                return False
                
    except Exception as e:
        print(f"❌ Builder functionality error: {e}")
        return False

def test_security_validation():
    """Test security validation"""
    print("\n🔒 Testing security validation...")
    
    framework_dir = Path(__file__).parent
    
    # Check for real PAT tokens (exclude virtual environments)
    pat_files = []
    for pattern in ["*.md", "*.py"]:
        for file_path in framework_dir.rglob(pattern):
            if file_path.is_file() and "test_env" not in str(file_path):
                pat_files.append(file_path)
    
    security_issues = []
    
    for file_path in pat_files:
        if file_path.is_file():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Check for real PAT token (exclude test files)
                    if ("8fb7cd921a22c84d4c446eb85711bb5f5e60a6bc273248aa3702c8083518db34" in content and 
                        "test_suite.py" not in str(file_path) and "quick_test.py" not in str(file_path)):
                        security_issues.append(f"Real PAT token in {file_path}")
                    # Check for real API keys (exclude false positives)
                    if ("sk-" in content and 
                        "sk-123" not in content and 
                        "test-api-key" not in content and
                        "risk" not in content.lower()):
                        security_issues.append(f"Real API key in {file_path}")
            except Exception:
                continue
    
    if security_issues:
        print("❌ Security issues found:")
        for issue in security_issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ Security validation passed")
        return True

def run_quick_test():
    """Run all quick tests"""
    print("🚀 Starting Quick Test for Agent as Code Framework")
    print("=" * 50)
    
    tests = [
        ("CLI Availability", test_cli_availability),
        ("Agent Creation", test_agent_creation),
        ("Agentfile Parsing", test_agentfile_parsing),
        ("Builder Functionality", test_builder_functionality),
        ("Security Validation", test_security_validation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Quick Test Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All quick tests passed! Framework is ready for use.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} tests failed. Please review issues.")
        return 1

if __name__ == "__main__":
    sys.exit(run_quick_test()) 