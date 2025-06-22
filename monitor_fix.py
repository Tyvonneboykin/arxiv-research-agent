#!/usr/bin/env python3
"""
ArXiv Agent Fix Monitoring Script
================================

Monitors the deployment fix and shows real-time status updates.
"""

import requests
import time
import json
from datetime import datetime

def check_deployment_status():
    """Check the status of the current deployment"""
    
    headers = {'Authorization': 'Bearer rnd_UYMQ9wFqCU9I5bTdwVREP1P5pQex'}
    service_id = 'srv-d1agjfqdbo4c73cff7t0'
    
    print("🔍 ArXiv Agent Fix Status Monitor")
    print("=" * 50)
    
    try:
        # Get latest deployment
        response = requests.get(f'https://api.render.com/v1/services/{service_id}/deploys?limit=1', headers=headers)
        deploys = response.json()
        
        if deploys:
            latest_deploy = deploys[0]
            deploy_status = latest_deploy.get('status', 'unknown')
            deploy_id = latest_deploy.get('id', 'unknown')
            
            print(f"🚀 Latest Deploy: {deploy_id}")
            print(f"📊 Status: {deploy_status}")
            
            if deploy_status == 'build_in_progress':
                print("🏗️  Build in progress - installing dependencies...")
            elif deploy_status == 'build_succeeded':
                print("✅ Build succeeded - starting service...")
            elif deploy_status == 'live':
                print("🎉 Deployment is LIVE!")
            elif deploy_status == 'build_failed':
                print("❌ Build failed - check logs")
            
        # Get recent service events
        response = requests.get(f'https://api.render.com/v1/services/{service_id}/events?limit=5', headers=headers)
        events = response.json()
        
        print(f"\\n📋 Recent Events:")
        print("-" * 20)
        
        for event in events:
            event_data = event['event']
            timestamp = event_data['timestamp']
            event_type = event_data['type']
            
            # Parse timestamp
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime('%H:%M:%S')
            
            if event_type == 'server_failed':
                details = event_data.get('details', {})
                reason = details.get('reason', {})
                exit_code = reason.get('nonZeroExit', 'unknown')
                print(f"❌ {time_str} - Server Failed (exit code: {exit_code})")
            elif event_type == 'server_available':
                print(f"✅ {time_str} - Server Available")
            elif event_type == 'deploy_ended':
                details = event_data.get('details', {})
                status = details.get('deployStatus', 'unknown')
                print(f"🚀 {time_str} - Deploy {status}")
            elif event_type == 'build_ended':
                details = event_data.get('details', {})
                status = details.get('buildStatus', 'unknown')
                print(f"🏗️ {time_str} - Build {status}")
            else:
                print(f"ℹ️  {time_str} - {event_type}")
        
        # Analyze current status
        print(f"\\n💡 Status Analysis:")
        print("-" * 15)
        
        recent_failures = [e for e in events if e['event']['type'] == 'server_failed']
        recent_successes = [e for e in events if e['event']['type'] == 'server_available']
        
        if recent_successes and not recent_failures:
            print("🎯 Status: HEALTHY - Service running successfully!")
            print("✅ All fixes have been applied and are working")
        elif recent_failures:
            latest_failure = recent_failures[0]
            details = latest_failure['event'].get('details', {})
            exit_code = details.get('reason', {}).get('nonZeroExit', 'unknown')
            
            if exit_code == 2:
                print("🔑 Status: API KEY ISSUE - Check ANTHROPIC_API_KEY")
                print("💡 Run: python3 fix_api_key.py")
            elif exit_code == 1:
                print("📦 Status: DEPENDENCY ISSUE - Missing packages")
                print("💡 Deployment should resolve this automatically")
            else:
                print(f"❓ Status: UNKNOWN ISSUE - Exit code {exit_code}")
        else:
            print("⏳ Status: STARTING - Service is initializing")
            
    except Exception as e:
        print(f"❌ Error checking status: {e}")

def watch_deployment():
    """Watch deployment progress in real-time"""
    
    print("👀 Watching deployment progress...")
    print("Press Ctrl+C to stop monitoring")
    print()
    
    try:
        while True:
            check_deployment_status()
            print("\\n" + "="*50)
            print("⏱️  Refreshing in 30 seconds...")
            print("="*50 + "\\n")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\\n🛑 Monitoring stopped by user")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--watch":
        watch_deployment()
    else:
        check_deployment_status()
        print(f"\\n🔧 Available Commands:")
        print("• python3 monitor_fix.py --watch  (continuous monitoring)")
        print("• python3 fix_api_key.py          (set API key)")
        print("• python3 debug_deployment.py     (detailed debugging)")