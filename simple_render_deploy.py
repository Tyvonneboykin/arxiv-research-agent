#!/usr/bin/env python3
"""
Simple Render Deployment Script
==============================

Creates a web service on Render for the ArXiv Research Agent.
"""

import json
import requests
import logging


def deploy_to_render():
    """Deploy to Render using API"""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    api_token = "REDACTED_RENDER_TOKEN"
    
    # Service configuration - simplified for web service
    service_data = {
        "name": "arxiv-research-agent",
        "type": "web_service",
        "ownerId": "tea-cu9g9vrqf0us73bvh5s0",
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
                    "key": "ARXIV_AGENT_EMAIL_USERNAME",
                    "value": "donvon@vonbase.com"
                },
                {
                    "key": "ARXIV_AGENT_EMAIL_FROM", 
                    "value": "donvon@vonbase.com"
                },
                {
                    "key": "PYTHONPATH",
                    "value": "/opt/render/project/src"
                }
            ]
        }
    }
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    logger.info("🚀 Creating Render service...")
    
    try:
        response = requests.post(
            "https://api.render.com/v1/services",
            headers=headers,
            json=service_data,
            timeout=30
        )
        
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response: {response.text}")
        
        if response.status_code == 201:
            service = response.json()
            logger.info("✅ Service created successfully!")
            logger.info(f"Service ID: {service.get('id', 'N/A')}")
            return True
        else:
            logger.error(f"❌ Failed to create service: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error creating service: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Deploying ArXiv Research Agent to Render...")
    success = deploy_to_render()
    
    if success:
        print("✅ Deployment initiated!")
        print("📝 Note: You'll need to connect a Git repository for the actual deployment")
        print("🔗 Visit https://dashboard.render.com to complete setup")
    else:
        print("❌ Deployment failed - check logs above")