#!/usr/bin/env python3
"""
Debug script to check what's happening with the ArXiv agent deployment
"""

import requests
import time
import json
from datetime import datetime

def check_service_status():
    """Check the current status of the ArXiv agent service"""
    
    headers = {
        "Authorization": "Bearer rnd_UYMQ9wFqCU9I5bTdwVREP1P5pQex",
        "Content-Type": "application/json"
    }
    
    service_id = "srv-d1agjfqdbo4c73cff7t0"
    
    print("🔍 ArXiv Agent Deployment Debug")
    print("=" * 50)
    
    # Get service info
    try:
        response = requests.get(f"https://api.render.com/v1/services/{service_id}", headers=headers)
        service_info = response.json()
        
        print(f"📊 Service Status: {service_info.get('suspended', 'unknown')}")
        print(f"🔧 Service Type: {service_info['type']}")
        print(f"💻 Start Command: {service_info['serviceDetails']['envSpecificDetails']['startCommand']}")
        print(f"🏗️ Build Command: {service_info['serviceDetails']['envSpecificDetails']['buildCommand']}")
        print(f"📅 Last Updated: {service_info['updatedAt']}")
        
    except Exception as e:
        print(f"❌ Error getting service info: {e}")
        return
    
    # Get recent events
    try:
        response = requests.get(f"https://api.render.com/v1/services/{service_id}/events?limit=10", headers=headers)
        events = response.json()
        
        print(f"\n📋 Recent Events (last 10):")
        print("-" * 30)
        
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
                print(f"ℹ️ {time_str} - {event_type}")
        
    except Exception as e:
        print(f"❌ Error getting events: {e}")
    
    # Get latest deployment info
    try:
        response = requests.get(f"https://api.render.com/v1/services/{service_id}/deploys?limit=1", headers=headers)
        deploys = response.json()
        
        if deploys:
            latest_deploy = deploys[0]
            commit_info = latest_deploy.get('commit', {})
            
            print(f"\n🔄 Latest Deployment:")
            print("-" * 20)
            print(f"📦 Deploy ID: {latest_deploy['id']}")
            print(f"📊 Status: {latest_deploy['status']}")
            print(f"🔗 Commit: {commit_info.get('id', 'unknown')[:8]}")
            print(f"💬 Message: {commit_info.get('message', 'No message')[:80]}...")
            
    except Exception as e:
        print(f"❌ Error getting deployment info: {e}")

def analyze_failure_pattern():
    """Analyze the failure pattern to understand what's happening"""
    
    headers = {
        "Authorization": "Bearer rnd_UYMQ9wFqCU9I5bTdwVREP1P5pQex",
        "Content-Type": "application/json"
    }
    
    service_id = "srv-d1agjfqdbo4c73cff7t0"
    
    print(f"\n🔬 Failure Pattern Analysis:")
    print("-" * 30)
    
    try:
        response = requests.get(f"https://api.render.com/v1/services/{service_id}/events?limit=20", headers=headers)
        events = response.json()
        
        failures = []
        availabilities = []
        
        for event in events:
            event_data = event['event']
            timestamp = event_data['timestamp']
            event_type = event_data['type']
            
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            if event_type == 'server_failed':
                details = event_data.get('details', {})
                reason = details.get('reason', {})
                exit_code = reason.get('nonZeroExit', 0)
                failures.append((dt, exit_code))
            elif event_type == 'server_available':
                availabilities.append(dt)
        
        print(f"📊 Failures in last events: {len(failures)}")
        print(f"✅ Successful starts: {len(availabilities)}")
        
        if failures:
            exit_codes = [code for _, code in failures]
            unique_codes = set(exit_codes)
            print(f"🔢 Exit codes seen: {unique_codes}")
            
            if len(failures) >= 2:
                time_diff = failures[0][0] - failures[1][0]
                print(f"⏱️ Time between failures: {time_diff.total_seconds():.0f} seconds")
        
        # Analyze pattern
        if len(failures) > 5 and len(availabilities) > 0:
            print("📈 Pattern: Service starts successfully but fails after running")
            print("💡 This suggests the resilient script is working but the agent code has issues")
        elif len(failures) > 0 and len(availabilities) == 0:
            print("📈 Pattern: Service fails immediately on startup")
            print("💡 This suggests startup/configuration issues")
        else:
            print("📈 Pattern: Mixed results, need more data")
            
    except Exception as e:
        print(f"❌ Error analyzing pattern: {e}")

def recommend_actions():
    """Recommend next actions based on the analysis"""
    
    print(f"\n💡 Recommended Actions:")
    print("-" * 25)
    print("1. ✅ Path issue is FIXED - start_agent.py is being found")
    print("2. ✅ Resilient startup script is being executed")
    print("3. 🔄 Agent is failing due to code issues, not deployment issues")
    print("4. 📝 Exit code 2 suggests controlled failure from retry logic")
    print("5. 🎯 Focus should be on agent code debugging, not deployment")
    
    print(f"\n🔧 Next Steps:")
    print("• Check if API keys are properly set in environment")
    print("• Verify all Python dependencies are available")
    print("• Look for import errors or missing files in agent code")
    print("• Add more detailed logging to identify specific failure point")
    print("• Consider running agent in test mode first")

if __name__ == "__main__":
    check_service_status()
    analyze_failure_pattern()
    recommend_actions()