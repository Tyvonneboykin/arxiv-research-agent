#!/usr/bin/env python3
"""
Setup Script for ArXiv Research Agent
====================================

Quick setup and installation script for the research agent.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path


def setup_logging():
    """Setup basic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def install_dependencies(logger):
    """Install Python dependencies"""
    logger.info("📦 Installing Python dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        logger.info("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install dependencies: {e}")
        return False


def create_directories(logger):
    """Create necessary directories"""
    logger.info("📁 Creating directories...")
    
    directories = [
        "logs",
        "output",
        "cache",
        "backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"📂 Created directory: {directory}")
    
    logger.info("✅ All directories created")


def setup_environment(logger):
    """Setup environment variables"""
    logger.info("🔧 Setting up environment...")
    
    env_file = Path(".env")
    
    if not env_file.exists():
        env_content = """# ArXiv Research Agent Environment Variables
# =============================================

# Required: Anthropic API Key for Claude Code SDK
ANTHROPIC_API_KEY=your_api_key_here

# Optional: Email configuration
ARXIV_AGENT_EMAIL_USERNAME=your_email@example.com
ARXIV_AGENT_EMAIL_PASSWORD=your_app_password
ARXIV_AGENT_EMAIL_FROM=your_email@example.com

# Optional: Discord webhook
ARXIV_AGENT_DISCORD_WEBHOOK=https://discord.com/api/webhooks/...

# Optional: Logging level
ARXIV_AGENT_LOG_LEVEL=INFO
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        logger.info(f"📝 Created environment file: {env_file}")
        logger.warning("⚠️  Please edit .env file with your actual API keys and settings")
    else:
        logger.info("✅ Environment file already exists")


def create_systemd_service(logger):
    """Create systemd service file for 24/7 operation"""
    logger.info("🔧 Creating systemd service...")
    
    current_dir = Path.cwd().absolute()
    python_path = sys.executable
    
    service_content = f"""[Unit]
Description=ArXiv Research Agent
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'research-agent')}
WorkingDirectory={current_dir}
Environment=PATH={os.environ.get('PATH')}
EnvironmentFile={current_dir}/.env
ExecStart={python_path} {current_dir}/src/research_agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = Path("arxiv-research-agent.service")
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    logger.info(f"📝 Created systemd service: {service_file}")
    logger.info("To install as system service:")
    logger.info(f"  sudo cp {service_file} /etc/systemd/system/")
    logger.info("  sudo systemctl daemon-reload")
    logger.info("  sudo systemctl enable arxiv-research-agent")
    logger.info("  sudo systemctl start arxiv-research-agent")


def test_configuration(logger):
    """Test the configuration"""
    logger.info("🧪 Testing configuration...")
    
    try:
        # Test imports
        sys.path.insert(0, str(Path("src")))
        from config_manager import ConfigManager
        
        config = ConfigManager()
        research_config = config.get_research_config()
        
        logger.info(f"✅ Configuration loaded successfully")
        logger.info(f"   Research interests: {len(research_config.interests)}")
        logger.info(f"   arXiv categories: {research_config.arxiv_categories}")
        
        # Check API key
        if os.getenv('ANTHROPIC_API_KEY'):
            logger.info("✅ ANTHROPIC_API_KEY is set")
        else:
            logger.warning("⚠️  ANTHROPIC_API_KEY not set - please add to .env file")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False


def main():
    """Main setup function"""
    logger = setup_logging()
    
    logger.info("🚀 ArXiv Research Agent Setup")
    logger.info("=" * 50)
    
    # Check if we're in the right directory
    if not Path("src").exists() or not Path("config").exists():
        logger.error("❌ Please run setup from the project root directory")
        sys.exit(1)
    
    success = True
    
    # Setup steps
    create_directories(logger)
    setup_environment(logger)
    
    if not install_dependencies(logger):
        success = False
    
    if not test_configuration(logger):
        success = False
    
    create_systemd_service(logger)
    
    # Final instructions
    logger.info("\n" + "=" * 50)
    if success:
        logger.info("✅ Setup completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Edit .env file with your API keys")
        logger.info("2. Customize config/config.yaml for your preferences")
        logger.info("3. Test: python src/research_agent.py --test")
        logger.info("4. Run once: python src/research_agent.py --once")
        logger.info("5. Start agent: python src/research_agent.py")
        logger.info("\nFor 24/7 operation, install the systemd service as shown above.")
    else:
        logger.error("❌ Setup completed with errors - please review and fix issues")
        sys.exit(1)


if __name__ == "__main__":
    main()