#!/usr/bin/env python3
"""
e-BIS Sahayak - Subsystem Health Check Script
Verifies environment, FastAPI backend status, and configuration.
"""

import sys
import json
import urllib.request
import urllib.error

BACKEND_URL = "http://127.0.0.1:8000"


def check_health():
    print("=" * 60)
    print("e-BIS Sahayak: Phase 1 Health & Subsystem Verification")
    print("=" * 60)

    # 1. Check Root Health
    print(f"\n[1/2] Checking Root Health Endpoint: {BACKEND_URL}/health ...")
    try:
        req = urllib.request.Request(f"{BACKEND_URL}/health", headers={"User-Agent": "eBIS-HealthCheck"})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print(f"  [PASS] Status: {data.get('status')} | Service: {data.get('service')} | Phase: {data.get('phase')}")
            else:
                print(f"  [FAIL] Unexpected HTTP status: {response.status}")
                return False
    except urllib.error.URLError as e:
        print(f"  [FAIL] Could not connect to backend at {BACKEND_URL}: {e}")
        return False

    # 2. Check API v1 Detailed Health
    print(f"\n[2/2] Checking API v1 Health Endpoint: {BACKEND_URL}/api/v1/health ...")
    try:
        req = urllib.request.Request(f"{BACKEND_URL}/api/v1/health", headers={"User-Agent": "eBIS-HealthCheck"})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print(f"  [PASS] Subsystem Status: {data.get('status')}")
                print(f"  Subsystems Detail: {json.dumps(data.get('subsystems', {}), indent=4)}")
            else:
                print(f"  [FAIL] Unexpected HTTP status: {response.status}")
                return False
    except urllib.error.URLError as e:
        print(f"  [FAIL] Error querying API v1 health: {e}")
        return False

    print("\n" + "=" * 60)
    print("ALL API HEALTH CHECKS PASSED.")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = check_health()
    sys.exit(0 if success else 1)
