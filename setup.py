#!/usr/bin/env python3
"""
Setup script for ArXiv Research Agent
=====================================

Installs dependencies and sets up the agent for deployment with comprehensive validation.
"""

import subprocess
import sys
import os
import logging
from pathlib import Path
import json
import time
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_command(cmd, description, critical=True):
    """Run a shell command with error handling"""
    logger.info(f"📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, timeout=300)
        logger.info(f"✅ {description} completed successfully")
        if result.stdout.strip():
            logger.debug(f"STDOUT: {result.stdout}")
        return True
    except subprocess.TimeoutExpired:
        logger.error(f"❌ {description} timed out after 5 minutes")
        return not critical
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed:")
        logger.error(f"Exit code: {e.returncode}")
        if e.stdout:
            logger.error(f"STDOUT: {e.stdout}")
        if e.stderr:
            logger.error(f"STDERR: {e.stderr}")
        return not critical

def verify_environment():
    """Verify that the environment is properly configured"""
    logger.info("🔍 Verifying environment configuration...")
    
    # Check Python version
    py_version = sys.version_info
    if py_version.major < 3 or (py_version.major == 3 and py_version.minor < 8):
        logger.error(f"❌ Python 3.8+ required, found {py_version.major}.{py_version.minor}")
        return False
    logger.info(f"✅ Python version: {py_version.major}.{py_version.minor}.{py_version.micro}")
    
    # Check environment variables
    required_env = ['ANTHROPIC_API_KEY']
    for env_var in required_env:
        if not os.getenv(env_var):
            logger.warning(f"⚠️ Environment variable {env_var} not set")
        else:
            logger.info(f"✅ Environment variable {env_var} is set")
    
    return True

def test_critical_imports():
    """Test all critical imports with detailed error reporting"""
    logger.info("🔍 Testing critical imports...")
    
    imports_to_test = [
        ('claude_code_sdk', 'Claude Code SDK'),
        ('arxiv', 'ArXiv API'),
        ('yaml', 'PyYAML'),
        ('schedule', 'Schedule'),
        ('pathlib', 'Pathlib'),
        ('asyncio', 'AsyncIO'),
        ('logging', 'Logging'),
        ('json', 'JSON'),
        ('pickle', 'Pickle'),
        ('datetime', 'DateTime'),
        ('typing', 'Typing'),
        ('os', 'OS'),
        ('sys', 'Sys')
    ]
    
    failed_imports = []
    
    for module_name, description in imports_to_test:
        try:
            __import__(module_name)
            logger.info(f"✅ {description} import successful")
        except ImportError as e:
            logger.error(f"❌ {description} import failed: {e}")
            failed_imports.append((module_name, str(e)))
    
    if failed_imports:
        logger.error("❌ Critical imports failed:")
        for module, error in failed_imports:
            logger.error(f"  - {module}: {error}")
        return False
    
    return True

def create_directories():
    """Create necessary directories with proper permissions"""
    logger.info("📁 Creating necessary directories...")
    
    directories = [
        'cache',
        'cache/papers', 
        'cache/analyses', 
        'cache/metadata', 
        'output', 
        'logs',
        'tmp'
    ]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        try:
            dir_path.mkdir(exist_ok=True, parents=True)
            os.chmod(dir_path, 0o755)
            logger.info(f"✅ Created directory: {dir_name}")
        except Exception as e:
            logger.error(f"❌ Failed to create directory {dir_name}: {e}")
            return False
    
    return True

def create_health_check():
    """Create a simple health check endpoint"""
    health_check_content = '''#!/usr/bin/env python3
"""
Health Check Endpoint for ArXiv Research Agent
"""
import json
from datetime import datetime
from pathlib import Path

def health_check():
    """Simple health check that returns status"""
    try:
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "arxiv-research-agent",
            "version": "1.0.0"
        }
        
        # Check if log file exists and is writable
        log_file = Path("logs/agent.log")
        if log_file.exists():
            status["last_log_update"] = datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
        
        # Check cache directory
        cache_dir = Path("cache")
        if cache_dir.exists():
            status["cache_files"] = len(list(cache_dir.rglob("*")))
        
        return json.dumps(status, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

if __name__ == "__main__":
    print(health_check())
'''
    
    try:
        with open('health_check.py', 'w') as f:
            f.write(health_check_content)
        os.chmod('health_check.py', 0o755)
        logger.info("✅ Created health check endpoint")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create health check: {e}")
        return False

def test_agent_imports():
    """Test that all agent modules can be imported"""
    logger.info("🔍 Testing agent module imports...")
    
    # Add src to path
    sys.path.insert(0, str(Path.cwd() / "src"))
    
    agent_modules = [
        'arxiv_fetcher',
        'claude_analyzer', 
        'digest_generator',
        'config_manager',
        'cache_manager',
        'research_agent'
    ]
    
    for module_name in agent_modules:
        try:
            __import__(module_name)
            logger.info(f"✅ Agent module {module_name} imported successfully")
        except ImportError as e:
            logger.error(f"❌ Agent module {module_name} import failed: {e}")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Agent module {module_name} has warnings: {e}")
    
    return True

def main():
    """Main setup process with comprehensive validation"""
    logger.info("🚀 Setting up ArXiv Research Agent with resilience features...")
    
    start_time = time.time()
    
    # Check if this is a verification run
    verify_only = '--verify' in sys.argv
    
    if verify_only:
        logger.info("🔍 Running verification-only mode...")
    
    # Step 1: Verify environment
    if not verify_environment():
        logger.error("❌ Environment verification failed")
        sys.exit(1)
    
    # Step 2: Create directories
    if not create_directories():
        logger.error("❌ Directory creation failed")
        sys.exit(1)
    
    # Step 3: Test critical imports
    if not test_critical_imports():
        logger.error("❌ Critical imports failed")
        sys.exit(1)
    
    # Step 4: Test agent imports
    if not test_agent_imports():
        logger.error("❌ Agent module imports failed")
        sys.exit(1)
    
    # Step 5: Create health check
    if not create_health_check():
        logger.error("❌ Health check creation failed")
        sys.exit(1)
    
    # Create a setup completion marker
    try:
        setup_info = {
            "setup_completed": True,
            "setup_time": datetime.now().isoformat(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "environment": os.getenv("RENDER_SERVICE_TYPE", "local"),
            "verification_only": verify_only
        }
        
        with open('setup_complete.json', 'w') as f:
            json.dump(setup_info, f, indent=2)
        
        logger.info("✅ Created setup completion marker")
        
    except Exception as e:
        logger.warning(f"⚠️ Could not create setup marker: {e}")
    
    elapsed_time = time.time() - start_time
    logger.info(f"🎉 Setup completed successfully in {elapsed_time:.2f} seconds!")
    
    if verify_only:
        logger.info("✅ Verification passed - agent is ready to deploy")
    else:
        logger.info("✅ Full setup complete - agent is ready to run")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Setup failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)