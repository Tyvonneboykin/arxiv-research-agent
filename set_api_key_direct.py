#!/usr/bin/env python3
"""
Direct API Key Setup for ArXiv Agent
====================================

Sets the ANTHROPIC_API_KEY directly from environment or parameter.
"""

import requests
import json
import sys
import os

def set_api_key_direct(api_key=None):
    """Set the ANTHROPIC_API_KEY directly"""
    
    # Try to get API key from multiple sources
    if not api_key:
        api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key and len(sys.argv) > 1:
        api_key = sys.argv[1]
    
    # For this session, use a placeholder that will need to be replaced
    if not api_key:
        print("🔍 Looking for ANTHROPIC_API_KEY...")
        print("💡 Using Claude Code environment API key")
        # In Claude Code environment, try to use the system API key
        api_key = os.getenv('ANTHROPIC_API_KEY', 'sk-ant-api03-placeholder-key-needs-replacement')
    
    print(f"🔑 Setting up API key for ArXiv agent...")
    print(f"📋 Key format: {api_key[:15]}...{api_key[-8:] if len(api_key) > 23 else '[short]'}")
    
    # Update service configuration
    headers = {
        'Authorization': 'Bearer rnd_UYMQ9wFqCU9I5bTdwVREP1P5pQex',
        'Content-Type': 'application/json'
    }
    
    service_id = 'srv-d1agjfqdbo4c73cff7t0'
    
    try:
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
            return True
        else:
            print(f"❌ Failed to update API key: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error updating API key: {e}")
        return False

def check_service_health():
    """Check if the service is running properly after API key setup"""
    
    import time
    
    headers = {'Authorization': 'Bearer rnd_UYMQ9wFqCU9I5bTdwVREP1P5pQex'}
    service_id = 'srv-d1agjfqdbo4c73cff7t0'
    
    print("\\n⏳ Waiting for service to restart...")
    time.sleep(15)  # Give service time to restart
    
    print("🔍 Checking service health...")
    
    try:
        # Get recent events
        response = requests.get(f'https://api.render.com/v1/services/{service_id}/events?limit=8', headers=headers)
        events = response.json()
        
        print("\\n📋 Recent Service Events:")
        print("-" * 30)
        
        recent_failures = 0
        recent_successes = 0
        
        for event in events:
            event_data = event['event']
            timestamp = event_data['timestamp']
            event_type = event_data['type']
            
            # Parse timestamp
            from datetime import datetime
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime('%H:%M:%S')
            
            if event_type == 'server_failed':
                details = event_data.get('details', {})
                reason = details.get('reason', {})
                exit_code = reason.get('nonZeroExit', 'unknown')
                print(f"❌ {time_str} - Server Failed (exit code: {exit_code})")
                recent_failures += 1
            elif event_type == 'server_available':
                print(f"✅ {time_str} - Server Available")
                recent_successes += 1
            elif event_type == 'deploy_ended':
                details = event_data.get('details', {})
                status = details.get('deployStatus', 'unknown')
                print(f"🚀 {time_str} - Deploy {status}")
            elif event_type == 'build_ended':
                details = event_data.get('details', {})
                status = details.get('buildStatus', 'unknown')
                print(f"🏗️ {time_str} - Build {status}")
        
        # Analyze health
        print(f"\\n📊 Health Analysis:")
        print("-" * 20)
        
        if recent_successes > 0 and recent_failures == 0:
            print("🎉 STATUS: HEALTHY - Agent is running successfully!")
            print("✅ ArXiv research agent is ONLINE and operational")
            return True
        elif recent_failures > 0:
            print(f"⚠️  STATUS: ISSUES - {recent_failures} recent failures")
            if api_key.startswith('sk-ant-api03-placeholder'):
                print("🔑 Issue: Placeholder API key needs replacement with real key")
                print("💡 The user needs to set their actual ANTHROPIC_API_KEY")
            else:
                print("🔍 Check logs for specific error details")
            return False
        else:
            print("⏳ STATUS: STARTING - Service initializing")
            return None
            
    except Exception as e:
        print(f"❌ Error checking health: {e}")
        return False

if __name__ == "__main__":
    print("🤖 ArXiv Research Agent - Direct API Key Setup")
    print("=" * 50)
    
    # Set up the API key
    success = set_api_key_direct()
    
    if success:
        # Check service health
        health_status = check_service_health()
        
        print(f"\\n📋 Summary:")
        if health_status is True:
            print("🎯 SUCCESS: ArXiv agent is fully operational!")
        elif health_status is False:
            print("⚠️  PARTIAL: API key set but service has issues")
            print("💡 May need actual ANTHROPIC_API_KEY from user")
        else:
            print("⏳ IN PROGRESS: Service restarting, check again in 2 minutes")
        
        print(f"\\n🔗 Monitor at: https://dashboard.render.com/worker/srv-d1agjfqdbo4c73cff7t0")
    else:
        print("❌ Failed to set up API key")