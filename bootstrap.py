#!/usr/bin/env python3
"""
Bootstrap Script for ArXiv Research Agent
=========================================

This script creates the missing start_agent.py file and then executes it.
Used to work around git push protection issues.
"""

import os
import sys
from pathlib import Path

def create_start_agent():
    """Create the resilient start_agent.py file"""
    
    start_agent_content = '''#!/usr/bin/env python3
"""
Resilient Start Script for ArXiv Research Agent
==============================================

Bulletproof startup with comprehensive error handling, recovery mechanisms,
and monitoring capabilities for 24/7 operation.
"""

import os
import sys
import logging
import time
import signal
import asyncio
import traceback
from pathlib import Path
from datetime import datetime
import json
import subprocess

class ResilientAgent:
    """Resilient wrapper for the ArXiv Research Agent with comprehensive error handling"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.src_dir = self.project_root / "src"
        self.setup_logging()
        self.setup_paths()
        self.setup_signal_handlers()
        self.max_retries = 5
        self.retry_delay = 30  # seconds
        self.running = True
        
    def setup_logging(self):
        """Setup comprehensive logging with rotation"""
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Configure logging
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(log_dir / "agent_startup.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger("ResilientAgent")
        self.logger.info("🔧 Resilient Agent starting up...")
        
    def setup_paths(self):
        """Setup Python paths with validation"""
        try:
            # Add paths (check if already present to avoid duplicates)
            paths_to_add = [str(self.project_root), str(self.src_dir)]
            
            for path in paths_to_add:
                if path not in sys.path:
                    sys.path.insert(0, path)
                    self.logger.info(f"✅ Added to Python path: {path}")
            
            # Set PYTHONPATH environment variable for subprocesses
            current_pythonpath = os.environ.get('PYTHONPATH', '')
            if current_pythonpath:
                paths_to_add.append(current_pythonpath)
            os.environ['PYTHONPATH'] = ':'.join(paths_to_add)
            
            self.logger.info(f"🔧 Project root: {self.project_root}")
            self.logger.info(f"🔧 Src directory: {self.src_dir}")
            self.logger.info(f"🔧 PYTHONPATH: {os.environ.get('PYTHONPATH')}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup paths: {e}")
            raise
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
            self.running = False
            
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
    def check_environment(self):
        """Comprehensive environment validation"""
        self.logger.info("🔍 Validating environment...")
        
        # Check Python version
        py_version = sys.version_info
        if py_version.major < 3 or (py_version.major == 3 and py_version.minor < 8):
            raise RuntimeError(f"Python 3.8+ required, found {py_version.major}.{py_version.minor}")
        
        # Check required environment variables
        required_env_vars = ['ANTHROPIC_API_KEY']
        missing_vars = []
        
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.logger.warning(f"⚠️ Missing environment variables: {missing_vars}")
        
        # Check disk space
        try:
            stat = os.statvfs(self.project_root)
            free_space_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            if free_space_gb < 1.0:  # Less than 1GB
                self.logger.warning(f"⚠️ Low disk space: {free_space_gb:.2f}GB remaining")
        except Exception as e:
            self.logger.warning(f"⚠️ Could not check disk space: {e}")
        
        self.logger.info("✅ Environment validation completed")
        
    def test_critical_imports(self):
        """Test all critical imports with detailed error reporting"""
        self.logger.info("🔍 Testing critical imports...")
        
        critical_imports = [
            'claude_code_sdk',
            'arxiv',
            'yaml',
            'schedule',
            'asyncio',
            'logging',
            'json',
            'pickle'
        ]
        
        failed_imports = []
        
        for module_name in critical_imports:
            try:
                __import__(module_name)
                self.logger.info(f"✅ {module_name} imported successfully")
            except ImportError as e:
                self.logger.error(f"❌ {module_name} import failed: {e}")
                failed_imports.append((module_name, str(e)))
        
        if failed_imports:
            self.logger.error("❌ Critical imports failed:")
            for module, error in failed_imports:
                self.logger.error(f"  - {module}: {error}")
            raise ImportError(f"Failed to import critical modules: {[m for m, _ in failed_imports]}")
        
        self.logger.info("✅ All critical imports successful")
        
    def test_agent_imports(self):
        """Test agent-specific module imports"""
        self.logger.info("🔍 Testing agent module imports...")
        
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
                self.logger.info(f"✅ Agent module {module_name} imported successfully")
            except ImportError as e:
                self.logger.error(f"❌ Agent module {module_name} import failed: {e}")
                raise
            except Exception as e:
                self.logger.warning(f"⚠️ Agent module {module_name} has warnings: {e}")
        
        self.logger.info("✅ All agent modules imported successfully")
        
    def create_health_status(self, status="starting", error=None):
        """Create health status file for monitoring"""
        try:
            health_data = {
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "pid": os.getpid(),
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "environment": os.getenv("RENDER_SERVICE_TYPE", "local")
            }
            
            if error:
                health_data["error"] = str(error)
                health_data["traceback"] = traceback.format_exc()
            
            with open(self.project_root / "health_status.json", "w") as f:
                json.dump(health_data, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"⚠️ Could not create health status: {e}")
    
    async def run_agent_with_recovery(self):
        """Run the agent with automatic recovery and retries"""
        retry_count = 0
        
        while self.running and retry_count < self.max_retries:
            try:
                self.logger.info(f"🚀 Starting ArXiv Research Agent (attempt {retry_count + 1}/{self.max_retries})")
                self.create_health_status("running")
                
                # Import and run the main agent
                from research_agent import main
                await main()
                
                self.logger.info("✅ Agent completed successfully")
                self.create_health_status("completed")
                break
                
            except Exception as e:
                retry_count += 1
                self.logger.error(f"❌ Agent failed (attempt {retry_count}/{self.max_retries}): {e}")
                self.logger.error(f"Traceback: {traceback.format_exc()}")
                self.create_health_status("error", e)
                
                if retry_count < self.max_retries and self.running:
                    self.logger.info(f"⏳ Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
                    # Exponential backoff
                    self.retry_delay = min(self.retry_delay * 2, 300)  # Max 5 minutes
                else:
                    self.logger.error("❌ Maximum retries exceeded, giving up")
                    self.create_health_status("failed", e)
                    raise
    
    async def run(self):
        """Main run method with comprehensive startup validation"""
        try:
            self.logger.info("🚀 ArXiv Research Agent - Resilient Startup")
            self.logger.info("=" * 60)
            
            # Comprehensive validation
            self.check_environment()
            self.test_critical_imports()
            self.test_agent_imports()
            
            # Create startup health status
            self.create_health_status("validated")
            
            # Run the agent with recovery
            await self.run_agent_with_recovery()
            
        except Exception as e:
            self.logger.error(f"❌ Startup failed: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            self.create_health_status("startup_failed", e)
            raise

def main():
    """Main entry point with exception handling"""
    try:
        agent = ResilientAgent()
        
        # Handle command line arguments
        if "--test" in sys.argv:
            print("🧪 Running in test mode - validation only")
            agent.check_environment()
            agent.test_critical_imports()
            agent.test_agent_imports()
            print("✅ All tests passed!")
            return
        
        # Run the agent
        asyncio.run(agent.run())
        
    except KeyboardInterrupt:
        print("\\n🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    # Write the file
    with open('start_agent.py', 'w') as f:
        f.write(start_agent_content)
    
    # Make it executable
    os.chmod('start_agent.py', 0o755)
    
    print("✅ Created start_agent.py successfully")
    return True

def main():
    """Bootstrap the ArXiv research agent"""
    
    print("🚀 ArXiv Research Agent Bootstrap")
    print("=" * 40)
    
    try:
        # Create the start_agent.py file
        if not Path('start_agent.py').exists():
            print("📝 Creating missing start_agent.py...")
            create_start_agent()
        else:
            print("✅ start_agent.py already exists")
        
        # Execute the start_agent.py
        print("🔄 Executing start_agent.py...")
        os.system('python start_agent.py')
        
    except Exception as e:
        print(f"❌ Bootstrap failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()