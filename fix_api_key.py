#!/usr/bin/env python3
"""
Fix ArXiv Agent API Key Configuration
====================================

This script helps set the ANTHROPIC_API_KEY for the ArXiv research agent.
"""

import requests
import json
import sys
import getpass

def set_api_key():
    """Set the ANTHROPIC_API_KEY for the ArXiv agent service"""
    
    print("🔑 ArXiv Agent API Key Configuration")
    print("=" * 50)
    print()
    
    # Get API key from user
    api_key = getpass.getpass("Enter your ANTHROPIC_API_KEY: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return False
    
    if not api_key.startswith('sk-ant-'):
        print("⚠️  Warning: API key doesn't look like a valid Anthropic key (should start with 'sk-ant-')")
        confirm = input("Continue anyway? (y/N): ").strip().lower()
        if confirm != 'y':
            return False
    
    # Update service configuration
    headers = {
        'Authorization': 'Bearer rnd_UYMQ9wFqCU9I5bTdwVREP1P5pQex',
        'Content-Type': 'application/json'
    }
    
    service_id = 'srv-d1agjfqdbo4c73cff7t0'
    
    try:
        # Get current environment variables
        response = requests.get(f'https://api.render.com/v1/services/{service_id}', headers=headers)
        response.raise_for_status()
        
        # Update the ANTHROPIC_API_KEY
        update_data = {
            'envVars': [
                {'key': 'ANTHROPIC_API_KEY', 'value': api_key},
                {'key': 'ARXIV_AGENT_EMAIL_USERNAME', 'value': 'donvon@vonbase.com'},
                {'key': 'ARXIV_AGENT_EMAIL_FROM', 'value': 'donvon@vonbase.com'},
                {'key': 'ARXIV_AGENT_LOG_LEVEL', 'value': 'INFO'},
                {'key': 'ARXIV_OUTPUT_PATH', 'value': '/tmp/arxiv_output'},
                {'key': 'RENDER_SERVICE_TYPE', 'value': 'background_worker'}
            ]
        }
        
        response = requests.patch(f'https://api.render.com/v1/services/{service_id}', 
                                headers=headers, 
                                data=json.dumps(update_data))
        
        if response.status_code == 200:
            print("✅ API key updated successfully!")
            print("🔄 Service will automatically restart with new configuration")
            print("⏱️  Please wait 2-3 minutes for the deployment to complete")
            return True
        else:
            print(f"❌ Failed to update API key: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error updating API key: {e}")
        return False

def check_service_status():
    """Check if the service is running properly"""
    
    headers = {'Authorization': 'Bearer rnd_UYMQ9wFqCU9I5bTdwVREP1P5pQex'}
    service_id = 'srv-d1agjfqdbo4c73cff7t0'
    
    print("\n🔍 Checking service status...")
    
    try:
        # Get recent events
        response = requests.get(f'https://api.render.com/v1/services/{service_id}/events?limit=5', headers=headers)
        events = response.json()
        
        recent_failures = []
        recent_successes = []
        
        for event in events:
            event_data = event['event']
            if event_data['type'] == 'server_failed':
                recent_failures.append(event_data)
            elif event_data['type'] == 'server_available':
                recent_successes.append(event_data)
        
        if recent_successes and not recent_failures:
            print("✅ Service is running successfully!")
        elif recent_failures:
            latest_failure = recent_failures[0]
            details = latest_failure.get('details', {})
            exit_code = details.get('reason', {}).get('nonZeroExit', 'unknown')
            print(f"⚠️  Service failed recently (exit code: {exit_code})")
            if exit_code == 2:
                print("💡 Exit code 2 suggests API authentication issues")
        else:
            print("ℹ️  Service status unclear - check Render dashboard")
            
    except Exception as e:
        print(f"❌ Error checking status: {e}")

if __name__ == "__main__":
    print("🤖 ArXiv Research Agent - API Key Configuration Tool")
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        check_service_status()
    else:
        success = set_api_key()
        if success:
            print("\n⏳ Waiting for service to restart...")
            import time
            time.sleep(10)
            check_service_status()
            
            print("\n📋 Next Steps:")
            print("1. ✅ API key has been configured")
            print("2. 🔄 Service is restarting automatically")
            print("3. 📊 Monitor the service in Render dashboard")
            print("4. 🕐 Check status again in 2-3 minutes")
            print("\n🔗 Dashboard: https://dashboard.render.com/worker/srv-d1agjfqdbo4c73cff7t0")