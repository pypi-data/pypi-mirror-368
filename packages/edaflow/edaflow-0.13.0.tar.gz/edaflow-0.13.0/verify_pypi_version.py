#!/usr/bin/env python3
"""
Verify PyPI Package Version and Cache Status
"""

import requests
import json
from datetime import datetime

def check_pypi_version():
    """Check the current version information on PyPI"""
    try:
        print("🔍 Checking PyPI API for edaflow package...")
        response = requests.get('https://pypi.org/pypi/edaflow/json')
        response.raise_for_status()
        
        data = response.json()
        
        print(f"📦 Package: {data['info']['name']}")
        print(f"🏷️  Current Version: {data['info']['version']}")
        print(f"📅 Upload Date: {data['info']['upload_time'] if 'upload_time' in data['info'] else 'N/A'}")
        print(f"📝 Description: {data['info']['summary']}")
        
        # Check recent versions
        versions = list(data['releases'].keys())
        recent_versions = sorted(versions, key=lambda x: [int(i) for i in x.split('.')], reverse=True)[:5]
        
        print(f"\n🔄 Recent Versions:")
        for version in recent_versions:
            release_info = data['releases'][version]
            if release_info:
                upload_time = release_info[0]['upload_time'] if release_info else "Unknown"
                print(f"   • {version} - {upload_time}")
        
        print(f"\n✅ PyPI shows version {data['info']['version']} as the latest!")
        return data['info']['version']
        
    except requests.RequestException as e:
        print(f"❌ Error checking PyPI: {e}")
        return None

def check_badge_services():
    """Check various badge services"""
    badge_services = [
        ("Badge Fury", "https://badge.fury.io/py/edaflow.svg"),
        ("Shields.io PyPI", "https://img.shields.io/pypi/v/edaflow.svg"),
        ("PyPI Badge", "https://badge.fury.io/py/edaflow.svg")
    ]
    
    print("\n🎯 Checking Badge Services:")
    for service_name, url in badge_services:
        try:
            response = requests.get(url, timeout=10)
            print(f"   • {service_name}: Status {response.status_code} ({'OK' if response.status_code == 200 else 'Error'})")
        except Exception as e:
            print(f"   • {service_name}: Error - {e}")

def force_cache_refresh():
    """Try to force cache refresh on badge services"""
    print("\n🔄 Attempting to refresh badge caches...")
    
    # Try multiple cache-busting strategies
    import time
    timestamp = str(int(time.time()))
    
    cache_bust_urls = [
        f"https://badge.fury.io/py/edaflow.svg?v={timestamp}",
        f"https://img.shields.io/pypi/v/edaflow.svg?v={timestamp}",
    ]
    
    for url in cache_bust_urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"   • Cache-bust request: Status {response.status_code}")
        except Exception as e:
            print(f"   • Cache-bust failed: {e}")

if __name__ == "__main__":
    print("🚀 edaflow v0.12.31 - PyPI Version Verification")
    print("=" * 50)
    
    # Check PyPI API
    version = check_pypi_version()
    
    # Check badge services
    check_badge_services()
    
    # Try cache refresh
    force_cache_refresh()
    
    print("\n" + "=" * 50)
    if version == "0.12.31":
        print("✅ SUCCESS: PyPI correctly shows v0.12.31")
        print("   The badge showing 0.12.21 is likely cached and should update within 1-24 hours.")
        print("   Try refreshing the page or clearing browser cache.")
    else:
        print(f"⚠️  WARNING: PyPI shows version {version}, expected 0.12.31")
    
    print("\n🔗 Direct Links:")
    print("   • PyPI Package: https://pypi.org/project/edaflow/")
    print("   • Latest Version: https://pypi.org/project/edaflow/0.12.31/")
    print("   • Badge Fury: https://badge.fury.io/py/edaflow")
