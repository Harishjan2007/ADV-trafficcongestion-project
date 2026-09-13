import sys
import os
import time
import json
import urllib.request
import urllib.error

log_file = os.path.join(os.path.dirname(__file__), "backend_debug.log")

def log(msg):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")
    print(msg)

with open(log_file, "w", encoding="utf-8") as f:
    f.write("=== PROXY & TEST VERIFICATION ===\n")

def check_url(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BackendTest/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.getcode()
            body = response.read().decode("utf-8")
            return status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return e.code, body
    except Exception as e:
        return None, str(e)

# Test Vite Proxy on port 3000
vite_endpoints = [
    "http://127.0.0.1:3000/api/ml/status?city=chennai",
    "http://127.0.0.1:3000/api/ml/predictions?city=chennai&horizon=30min&hour=8",
    "http://127.0.0.1:3000/api/ml/predict/ROAD_ANNA_SALAI_1?city=chennai&hour=8&horizon=30min",
    "http://127.0.0.1:3000/api/ml/status?city=vellore",
    "http://127.0.0.1:3000/api/ml/predict/ROAD_VEL_NH48_1?city=vellore&hour=8&horizon=30min",
    "http://127.0.0.1:3000/api/ml/status?city=coimbatore",
    "http://127.0.0.1:3000/api/ml/predict/ROAD_CBE_AVINASHI_1?city=coimbatore&hour=8&horizon=30min"
]

log("1. Testing Vite dev server proxy at http://127.0.0.1:3000/api/...")
proxy_all_ok = True
for u in vite_endpoints:
    s, b = check_url(u)
    if s == 200:
        log(f"  [PROXY PASS 200] {u}")
    else:
        proxy_all_ok = False
        log(f"  [PROXY FAIL {s}] {u} -> {b[:150]}")

log(f"\nVite Proxy working: {proxy_all_ok}")

# Run full test suite with unittest TextTestRunner
log("\n2. Running platform test suite (tests/run_all_tests.py):")
import unittest
loader = unittest.TestLoader()
suite = loader.discover(os.path.join(os.path.dirname(__file__), "tests"), pattern="test_*.py")
runner = unittest.TextTestRunner(verbosity=1)
result = runner.run(suite)
log(f"Tests run: {result.testsRun}")
log(f"Failures: {len(result.failures)}")
log(f"Errors: {len(result.errors)}")
log(f"Was successful: {result.wasSuccessful()}")

log("\n=== COMPLETED ALL CHECKS ===")
