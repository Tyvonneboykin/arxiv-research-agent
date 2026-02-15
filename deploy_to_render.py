#!/usr/bin/env python3
"""
Deploy ArXiv Research Agent to Render
====================================

Deploy directly to Render using manual deployment.
"""

import json
import os
import requests
import logging
import time


def create_render_service():
    """Create Render service for ArXiv Research Agent"""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    api_token = os.getenv("RENDER_API_TOKEN")  # Required: set in environment
    owner_id = "tea-cu9g9vrqf0us73bvh5s0"
    
    # Create a background service (since we don't need web interface)
    service_config = {
        "name": "arxiv-research-agent",
        "type": "background_worker",
        "ownerId": owner_id,
        "serviceDetails": {
            "env": "python",
            "buildCommand": "pip install -r requirements.txt",
            "startCommand": "python src/research_agent.py",
            "plan": "starter",
            "region": "oregon",
            "envVars": [
                {
                    "key": "ANTHROPIC_API_KEY", 
                    "value": "YOUR_ANTHROPIC_API_KEY_HERE"
                },
                {
                    "key": "PYTHONPATH",
                    "value": "/opt/render/project/src"
                },
                {
                    "key": "ARXIV_AGENT_LOG_LEVEL",
                    "value": "INFO"
                }
            ]
        }
    }
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    logger.info("🚀 Creating Render background service...")
    
    try:
        response = requests.post(
            "https://api.render.com/v1/services",
            headers=headers,
            json=service_config,
            timeout=30
        )
        
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 201:
            service = response.json()
            service_id = service["service"]["id"]
            logger.info(f"✅ Service created successfully!")
            logger.info(f"Service ID: {service_id}")
            logger.info(f"Service Name: {service['service']['name']}")
            logger.info(f"Dashboard: https://dashboard.render.com/web/{service_id}")
            return service_id
        else:
            logger.error(f"❌ Failed to create service: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error creating service: {e}")
        return None


def deploy_via_manual_upload():
    """Instructions for manual deployment"""
    
    print("""
🚀 ArXiv Research Agent - Manual Deployment Instructions

Since Render requires Git integration for Python services, here are your options:

OPTION 1 - GitHub Integration (Recommended):
1. Create GitHub repository: https://github.com/new
2. Push code:
   git remote add origin https://github.com/yourusername/arxiv-research-agent.git
   git branch -M main
   git push -u origin main

3. Create Render service:
   - Visit: https://dashboard.render.com
   - Click "New" → "Background Worker"
   - Connect GitHub repository
   - Set build command: pip install -r requirements.txt
   - Set start command: python src/research_agent.py
   - Add environment variables:
     * ANTHROPIC_API_KEY: YOUR_ANTHROPIC_API_KEY_HERE
     * PYTHONPATH: /opt/render/project/src

OPTION 2 - Manual Upload:
1. Create zip file of project
2. Upload to Render dashboard
3. Configure as background worker

The agent will then:
✅ Run 24/7 on Render's infrastructure
✅ Generate daily research digests
✅ Save files to your Windows directory (when accessible)
✅ Cost ~$7/month for hosting + API usage

Next: Visit https://dashboard.render.com to complete deployment!
""")


if __name__ == "__main__":
    print("🤖 ArXiv Research Agent - Render Deployment")
    print("=" * 60)
    
    # Try to create service (will likely need manual GitHub setup)
    service_id = create_render_service()
    
    if not service_id:
        print("\n📝 Manual deployment required:")
        deploy_via_manual_upload()
    else:
        print(f"\n✅ Service created! ID: {service_id}")
        print("🔗 Complete setup at: https://dashboard.render.com")