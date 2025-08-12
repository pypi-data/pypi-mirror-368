#!/usr/bin/env python3
"""
Comprehensive monitoring authentication test for Prometheus Pushgateway and Loki.
This script tests basic auth functionality with configurable credentials.

Environment Variables Required:
- PUSHGATEWAY_HOST: URL of the Pushgateway (e.g., http://localhost:9091)
- LOKI_HOST: URL of the Loki server (e.g., http://localhost:3100)
- MONITORING_AUTH_USER: Username for basic authentication
- MONITORING_AUTH_PASS: Password for basic authentication

Example usage:
    export PUSHGATEWAY_HOST="http://13.234.115.98:5000"
    export LOKI_HOST="http://13.234.115.98:5001"
    export MONITORING_AUTH_USER="your_username"
    export MONITORING_AUTH_PASS="your_password"
    python test_monitoring_auth.py
"""

import asyncio
import os
import requests
import time
from typing import Optional

from pyvetic.instrument.prometheus import (
    REQUEST_COUNTER,
    EXCEPTION_COUNTER,
    REQUEST_LATENCY,
    collect_system_metrics,
    push_metrics,
)
from pyvetic.logger import get_logger, enable_loki

# Get configuration from environment variables
PUSHGATEWAY_HOST = os.getenv("PUSHGATEWAY_HOST", "http://localhost:9091")
LOKI_HOST = os.getenv("LOKI_HOST", "http://localhost:3100")
AUTH_USER = os.getenv("MONITORING_AUTH_USER", "admin")
AUTH_PASS = os.getenv("MONITORING_AUTH_PASS", "admin")

# Configure environment variables for the monitoring system
os.environ.setdefault("APP_NAME", "pyvetic-test")
os.environ.setdefault("PUSHGATEWAY_HOST", PUSHGATEWAY_HOST)
os.environ.setdefault("LOKI_HOST", LOKI_HOST)
os.environ.setdefault("MONITORING_AUTH_USER", AUTH_USER)
os.environ.setdefault("MONITORING_AUTH_PASS", AUTH_PASS)

# Enable Loki logging
enable_loki()

# Get logger
logger = get_logger(__name__)


def test_basic_connectivity():
    """Test basic connectivity to monitoring services."""
    print("=== Testing Basic Connectivity ===")
    
    services = {
        "Pushgateway": PUSHGATEWAY_HOST,
        "Loki": LOKI_HOST
    }
    
    results = {}
    
    for service_name, url in services.items():
        print(f"\n--- Testing {service_name} ---")
        print(f"URL: {url}")
        
        try:
            # Test without authentication
            response = requests.get(url, timeout=10)
            print(f"Status without auth: {response.status_code}")
            
            # Test with authentication
            auth = (AUTH_USER, AUTH_PASS)
            response = requests.get(url, auth=auth, timeout=10)
            print(f"Status with auth: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ {service_name}: SUCCESS")
                results[service_name] = True
            elif response.status_code == 401:
                print(f"❌ {service_name}: UNAUTHORIZED")
                results[service_name] = False
            else:
                print(f"⚠️  {service_name}: UNEXPECTED STATUS ({response.status_code})")
                results[service_name] = False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {service_name}: CONNECTION ERROR - {e}")
            results[service_name] = False
    
    return results


def test_authentication_with_different_credentials():
    """Test authentication with different credential combinations."""
    print("\n=== Testing Authentication with Different Credentials ===")
    
    test_credentials = [
        (AUTH_USER, AUTH_PASS),  # Correct credentials
        (AUTH_USER, "wrong_password"),  # Wrong password
        ("wrong_user", AUTH_PASS),  # Wrong username
        ("admin", "admin"),  # Common default
        ("", ""),  # Empty credentials
        (None, None),  # No credentials
    ]
    
    services = {
        "Pushgateway": PUSHGATEWAY_HOST,
        "Loki": LOKI_HOST
    }
    
    for service_name, base_url in services.items():
        print(f"\n--- Testing {service_name} ---")
        
        for username, password in test_credentials:
            try:
                if username and password:
                    auth = (username, password)
                    response = requests.get(f"{base_url}/", auth=auth, timeout=10)
                else:
                    response = requests.get(f"{base_url}/", timeout=10)
                
                status = response.status_code
                if status == 200:
                    print(f"✅ {username}/{password}: SUCCESS (200)")
                elif status == 401:
                    print(f"❌ {username}/{password}: UNAUTHORIZED (401)")
                elif status == 403:
                    print(f"🚫 {username}/{password}: FORBIDDEN (403)")
                else:
                    print(f"⚠️  {username}/{password}: UNEXPECTED ({status})")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ {username}/{password}: CONNECTION ERROR - {e}")


def test_pushgateway_metrics():
    """Test Pushgateway metrics endpoint."""
    print("\n=== Testing Pushgateway Metrics ===")
    
    url = f"{PUSHGATEWAY_HOST}/metrics"
    auth = (AUTH_USER, AUTH_PASS)
    
    try:
        # Test without authentication
        response = requests.get(url, timeout=10)
        print(f"Status without auth: {response.status_code}")
        
        # Test with authentication
        response = requests.get(url, auth=auth, timeout=10)
        print(f"Status with auth: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully accessed metrics with authentication")
            if "pushgateway" in response.text.lower():
                print("✅ Response contains Pushgateway metrics")
            else:
                print("⚠️  Response doesn't contain expected metrics data")
        else:
            print(f"❌ Failed to access metrics: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")


def test_loki_endpoints():
    """Test Loki endpoints."""
    print("\n=== Testing Loki Endpoints ===")
    
    auth = (AUTH_USER, AUTH_PASS)
    
    # Common Loki endpoints to test
    endpoints = [
        "/ready",
        "/metrics",
        "/loki/api/v1/status/buildinfo",
        "/loki/api/v1/labels",
        "/loki/api/v1/series"
    ]
    
    for endpoint in endpoints:
        url = f"{LOKI_HOST}{endpoint}"
        
        try:
            # Test without authentication
            response = requests.get(url, timeout=10)
            print(f"{endpoint} without auth: {response.status_code}")
            
            # Test with authentication
            response = requests.get(url, auth=auth, timeout=10)
            print(f"{endpoint} with auth: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ {endpoint}: SUCCESS")
            elif response.status_code == 401:
                print(f"❌ {endpoint}: UNAUTHORIZED")
            elif response.status_code == 404:
                print(f"⚠️  {endpoint}: NOT FOUND")
            else:
                print(f"⚠️  {endpoint}: UNEXPECTED ({response.status_code})")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint}: CONNECTION ERROR - {e}")


async def test_prometheus_metrics_push():
    """Test Prometheus metrics push functionality."""
    print("\n=== Testing Prometheus Metrics Push ===")
    
    try:
        # Create test metrics
        REQUEST_COUNTER.labels(
            app="pyvetic-test",
            method="GET",
            endpoint="/auth-test",
            status_code=200
        ).inc()
        
        REQUEST_LATENCY.labels(
            app="pyvetic-test",
            method="GET",
            endpoint="/auth-test",
            status_code=200
        ).observe(0.5)
        
        # Push metrics
        push_metrics()
        print("✅ Metrics pushed successfully")
        
        # Wait a moment and verify
        await asyncio.sleep(2)
        
        # Try to access the metrics endpoint to verify they were pushed
        url = f"{PUSHGATEWAY_HOST}/metrics"
        auth = (AUTH_USER, AUTH_PASS)
        
        response = requests.get(url, auth=auth, timeout=10)
        if response.status_code == 200:
            print("✅ Metrics endpoint accessible")
            if "pyvetic-test" in response.text:
                print("✅ Our test metrics found in response")
            else:
                print("⚠️  Our test metrics not found in response")
        else:
            print(f"❌ Metrics endpoint not accessible: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Metrics push test failed: {e}")


async def test_system_metrics():
    """Test system metrics collection."""
    print("\n=== Testing System Metrics Collection ===")
    
    try:
        # Start system metrics collection for a short period
        metrics_task = asyncio.create_task(
            collect_system_metrics(interval=2)
        )
        
        # Let it run for 6 seconds (3 intervals)
        await asyncio.sleep(6)
        
        # Cancel the task
        metrics_task.cancel()
        try:
            await metrics_task
        except asyncio.CancelledError:
            pass
        
        print("✅ System metrics collection completed")
        return True
    except Exception as e:
        print(f"❌ System metrics collection failed: {e}")
        return False


async def test_loki_logging():
    """Test Loki logging functionality."""
    print("\n=== Testing Loki Logging ===")
    
    try:
        # Test different log levels
        logger.debug("This is a debug message for Loki")
        logger.info("This is an info message for Loki")
        logger.warning("This is a warning message for Loki")
        logger.error("This is an error message for Loki")
        logger.critical("This is a critical message for Loki")
        
        # Test structured logging
        logger.info("User authentication test", extra={
            "user_id": AUTH_USER,
            "auth_method": "basic",
            "timestamp": time.time()
        })
        
        logger.error("Test error with context", extra={
            "error_code": "AUTH_TEST",
            "component": "monitoring_test"
        })
        
        print("✅ Loki logging test completed")
        return True
    except Exception as e:
        print(f"❌ Loki logging failed: {e}")
        return False


async def test_request_simulation():
    """Test request simulation with metrics collection."""
    print("\n=== Testing Request Simulation ===")
    
    try:
        endpoints = ["/api/users", "/api/posts", "/health", "/metrics"]
        methods = ["GET", "POST", "PUT", "DELETE"]
        status_codes = [200, 201, 400, 401, 403, 404, 500]
        
        for i in range(5):
            endpoint = endpoints[i % len(endpoints)]
            method = methods[i % len(methods)]
            status_code = status_codes[i % len(status_codes)]
            latency = 0.1 + (i * 0.1)  # Varying latency
            
            # Record metrics
            REQUEST_COUNTER.labels(
                app="pyvetic-test",
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                app="pyvetic-test",
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).observe(latency)
            
            # Log the request
            logger.info(f"Test request: {method} {endpoint} - Status: {status_code} - Latency: {latency:.3f}s")
            
            await asyncio.sleep(0.5)
        
        # Push final metrics
        push_metrics()
        print("✅ Request simulation completed")
        return True
    except Exception as e:
        print(f"❌ Request simulation failed: {e}")
        return False


def print_configuration():
    """Print current configuration."""
    print("🔍 Monitoring Authentication Test")
    print("=" * 50)
    print("Configuration:")
    print(f"  Pushgateway: {PUSHGATEWAY_HOST}")
    print(f"  Loki: {LOKI_HOST}")
    print(f"  Username: {AUTH_USER}")
    print(f"  Password: {'*' * len(AUTH_PASS) if AUTH_PASS else 'Not set'}")
    print()


async def main():
    """Main test function."""
    print_configuration()
    
    results = []
    
    # Test 1: Basic connectivity
    print("1. Testing basic connectivity...")
    connectivity_results = test_basic_connectivity()
    results.extend([v for v in connectivity_results.values() if v is not None])
    
    # Test 2: Authentication with different credentials
    print("\n2. Testing authentication with different credentials...")
    test_authentication_with_different_credentials()
    
    # Test 3: Pushgateway metrics
    print("\n3. Testing Pushgateway metrics...")
    test_pushgateway_metrics()
    
    # Test 4: Loki endpoints
    print("\n4. Testing Loki endpoints...")
    test_loki_endpoints()
    
    # Test 5: Prometheus metrics push
    print("\n5. Testing Prometheus metrics push...")
    prometheus_ok = await test_prometheus_metrics_push()
    results.append(prometheus_ok)
    
    # Test 6: System metrics
    print("\n6. Testing system metrics...")
    system_ok = await test_system_metrics()
    results.append(system_ok)
    
    # Test 7: Loki logging
    print("\n7. Testing Loki logging...")
    loki_logging_ok = await test_loki_logging()
    results.append(loki_logging_ok)
    
    # Test 8: Request simulation
    print("\n8. Testing request simulation...")
    request_sim_ok = await test_request_simulation()
    results.append(request_sim_ok)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    test_names = [
        "Pushgateway Connectivity",
        "Loki Connectivity",
        "Prometheus Metrics Push",
        "System Metrics Collection",
        "Loki Logging",
        "Request Simulation"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {name}: {status}")
    
    passed = sum([r for r in results if r is not None])
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your monitoring setup is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    print("\nAccess URLs:")
    print(f"- Pushgateway: {PUSHGATEWAY_HOST}")
    print(f"- Loki: {LOKI_HOST}")
    
    print("\nTo run this test with your credentials:")
    print(f"export PUSHGATEWAY_HOST='{PUSHGATEWAY_HOST}'")
    print(f"export LOKI_HOST='{LOKI_HOST}'")
    print("export MONITORING_AUTH_USER='your_username'")
    print("export MONITORING_AUTH_PASS='your_password'")
    print("python test_monitoring_auth.py")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 