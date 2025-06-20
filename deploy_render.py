#!/usr/bin/env python3
"""
Deploy ArXiv Research Agent to Render
====================================

Deploys the research agent to Render using their API.
"""

import json
import logging
import requests
import time
from pathlib import Path


def setup_logging():
    """Setup logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def create_render_service(api_token: str, logger):
    """Create a new service on Render"""
    
    # Service configuration
    service_config = {
        "type": "web_service",
        "name": "arxiv-research-agent",
        "env": "python",
        "plan": "starter",
        "region": "oregon",
        "repo": None,  # We'll use manual deployment
        "branch": None,
        "buildCommand": "pip install -r requirements.txt && python setup.py",
        "startCommand": "python src/research_agent.py",
        "envVars": [
            {
                "key": "ANTHROPIC_API_KEY",
                "value": "YOUR_ANTHROPIC_API_KEY_HERE"
            },
            {
                "key": "ARXIV_AGENT_EMAIL_USERNAME", 
                "value": "donvon@vonbase.com"
            },
            {
                "key": "ARXIV_AGENT_EMAIL_FROM",
                "value": "donvon@vonbase.com"  
            },
            {
                "key": "ARXIV_AGENT_LOG_LEVEL",
                "value": "INFO"
            },
            {
                "key": "PYTHONPATH",
                "value": "/opt/render/project/src"
            }
        ],
        "autoDeploy": False
    }
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # Create service
    logger.info("🚀 Creating Render service...")
    
    response = requests.post(
        "https://api.render.com/v1/services",
        headers=headers,
        json=service_config
    )
    
    if response.status_code == 201:
        service = response.json()
        service_id = service["service"]["id"]
        logger.info(f"✅ Service created successfully: {service_id}")
        logger.info(f"🔗 Service URL: https://{service['service']['name']}.onrender.com")
        return service_id
    else:
        logger.error(f"❌ Failed to create service: {response.status_code}")
        logger.error(f"Response: {response.text}")
        return None


def upload_files_to_render(service_id: str, api_token: str, logger):
    """Upload files to Render service"""
    
    # For simplicity, we'll create a minimal service that can be deployed
    # In a real scenario, you'd typically use Git integration
    
    logger.info("📁 Preparing deployment files...")
    
    # Create a simple deployment package
    files_to_deploy = [
        "src/research_agent.py",
        "src/arxiv_fetcher.py", 
        "src/claude_analyzer.py",
        "src/digest_generator.py",
        "src/config_manager.py",
        "config/config.yaml",
        "requirements.txt",
        "setup.py"
    ]
    
    # Since Render API doesn't support direct file upload for manual deploys,
    # we'll need to use a different approach
    logger.info("ℹ️  Manual deployment required - files ready for Git push")
    
    return True


def trigger_deployment(service_id: str, api_token: str, logger):
    """Trigger a deployment"""
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # Trigger deploy
    logger.info("⚡ Triggering deployment...")
    
    response = requests.post(
        f"https://api.render.com/v1/services/{service_id}/deploys",
        headers=headers,
        json={}
    )
    
    if response.status_code == 201:
        deploy = response.json()
        deploy_id = deploy["deploy"]["id"]
        logger.info(f"✅ Deployment triggered: {deploy_id}")
        return deploy_id
    else:
        logger.error(f"❌ Failed to trigger deployment: {response.status_code}")
        logger.error(f"Response: {response.text}")
        return None


def wait_for_deployment(service_id: str, deploy_id: str, api_token: str, logger, timeout: int = 600):
    """Wait for deployment to complete"""
    
    headers = {
        "Authorization": f"Bearer {api_token}"
    }
    
    logger.info("⏳ Waiting for deployment to complete...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = requests.get(
            f"https://api.render.com/v1/services/{service_id}/deploys/{deploy_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            deploy = response.json()
            status = deploy["deploy"]["status"]
            
            logger.info(f"📊 Deployment status: {status}")
            
            if status == "live":
                logger.info("✅ Deployment completed successfully!")
                return True
            elif status in ["build_failed", "update_failed"]:
                logger.error("❌ Deployment failed!")
                return False
        
        time.sleep(30)  # Check every 30 seconds
    
    logger.error("⏰ Deployment timeout!")
    return False


def get_service_info(service_id: str, api_token: str, logger):
    """Get service information"""
    
    headers = {
        "Authorization": f"Bearer {api_token}"
    }
    
    response = requests.get(
        f"https://api.render.com/v1/services/{service_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        service = response.json()
        logger.info("📋 Service Information:")
        logger.info(f"  Name: {service['service']['name']}")
        logger.info(f"  URL: https://{service['service']['name']}.onrender.com")
        logger.info(f"  Status: {service['service']['status']}")
        logger.info(f"  Plan: {service['service']['plan']}")
        return service
    else:
        logger.error(f"Failed to get service info: {response.status_code}")
        return None


def main():
    """Main deployment function"""
    logger = setup_logging()
    
    # Configuration
    api_token = "REDACTED_RENDER_TOKEN"
    
    logger.info("🚀 Starting Render deployment...")
    logger.info("=" * 50)
    
    # Create service
    service_id = create_render_service(api_token, logger)
    
    if not service_id:
        logger.error("❌ Failed to create service - aborting deployment")
        return False
    
    # Since Render requires Git integration for automatic deployments,
    # we'll provide instructions for manual setup
    logger.info("\n" + "=" * 50)
    logger.info("📝 MANUAL SETUP REQUIRED")
    logger.info("=" * 50)
    logger.info("Render has been configured, but requires Git integration.")
    logger.info("Please follow these steps:")
    logger.info("")
    logger.info("1. Push this project to a Git repository (GitHub/GitLab)")
    logger.info("2. In Render dashboard, connect your repository")
    logger.info("3. Service will auto-deploy from Git")
    logger.info("")
    logger.info("Alternatively, use Render's manual deploy:")
    logger.info("1. Zip the project files")
    logger.info("2. Upload via Render dashboard")
    logger.info("3. Configure environment variables as shown in render.yaml")
    
    # Get service info
    service_info = get_service_info(service_id, api_token, logger)
    
    logger.info("\n✅ Render service created successfully!")
    logger.info("🔗 Next: Connect Git repository for automatic deployment")
    
    return True


if __name__ == "__main__":
    main()