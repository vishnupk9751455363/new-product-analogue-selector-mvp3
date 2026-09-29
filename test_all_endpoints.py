import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000"

def get(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.read().decode('utf-8')

def post(path, data):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.read().decode('utf-8')

print("Testing Endpoints...")

# 1. Root
s, body = get("/")
print(f"GET / : Status {s}, Length: {len(body)}")
assert s == 200 and "<!DOCTYPE html>" in body

# 2. Style.css
s, body = get("/style.css")
print(f"GET /style.css : Status {s}, Length: {len(body)}")
assert s == 200

# 3. App.js
s, body = get("/app.js")
print(f"GET /app.js : Status {s}, Length: {len(body)}")
assert s == 200

# 4. Products
s, body = get("/api/products?is_historical=0")
data = json.loads(body)
prods = data.get("products", [])
print(f"GET /api/products?is_historical=0 : Status {s}, Products: {len(prods)}")
assert s == 200 and len(prods) > 0
first_sku = prods[0]["product_id"]

# 5. Analogues
s, body = post("/api/analogues", {
    "product_id": first_sku,
    "k": 5,
    "custom_weights": {"category": 0.25, "subcategory": 0.20, "festival": 0.15, "price_tier": 0.15, "pack_size": 0.10, "shelf_life": 0.08, "weather_sensitivity": 0.07},
    "debias_promotions": False
})
data = json.loads(body)
confidence = data.get("forecast", {}).get("confidence_score")
print(f"POST /api/analogues : Status {s}, Analogues count: {len(data.get('analogues', []))}, Confidence: {confidence}")
assert s == 200 and len(data.get('analogues', [])) == 5

# 6. Analogues with Debias
s, body = post("/api/analogues", {
    "product_id": first_sku,
    "k": 5,
    "custom_weights": {"category": 0.25, "subcategory": 0.20, "festival": 0.15, "price_tier": 0.15, "pack_size": 0.10, "shelf_life": 0.08, "weather_sensitivity": 0.07},
    "debias_promotions": True
})
data = json.loads(body)
raw_w1 = data['raw_curve']['W1']
deb_w1 = data['debiased_curve']['W1']
print(f"POST /api/analogues (debiased) : Status {s}, Raw vs Debias curve diff: {raw_w1} vs {deb_w1}")
assert s == 200

# 7. Weights Optimize
s, body = post("/api/weights/optimize", {
    "cv_folds": 3,
    "k": 5,
    "apply_to_engine": False
})
data = json.loads(body)
print(f"POST /api/weights/optimize : Status {s}, CV WAPE: {data.get('optimization_result', {}).get('cv_wape_percentage')}%")
assert s == 200

# 8. Disruptions Simulate
s, body = post("/api/disruptions/simulate", {
    "scenario_type": "supplier_delay",
    "product_id": first_sku,
    "params": {"delay_weeks": 2, "spoilage_rate_pct": 0.05, "shelf_life_days": 60}
})
data = json.loads(body)
print(f"POST /api/disruptions/simulate : Status {s}, Lost Sales: {data.get('lost_sales_units')}")
assert s == 200

# 9. Audit Override
s, body = post("/api/audit/override", {
    "product_id": first_sku,
    "changed_by": "Test Suite Runner",
    "field_changed": "launch_curve_W1",
    "old_value": "100.0",
    "new_value": "125.0",
    "reason": "Automated verification test override"
})
data = json.loads(body)
print(f"POST /api/audit/override : Status {s}, Change ID: {data.get('change_id')}")
assert s == 200

# 10. Audit Trail
s, body = get(f"/api/audit/trail?product_id={first_sku}")
data = json.loads(body)
print(f"GET /api/audit/trail : Status {s}, Trail records: {data.get('total_records')}")
assert s == 200

# 11. Audit Test Tamper
s, body = post("/api/audit/test-tamper?change_id=1", {})
data = json.loads(body)
print(f"POST /api/audit/test-tamper : Status {s}, Blocked: {data.get('trigger_blocked')}, Tamper Successful: {data.get('tamper_successful')}")
assert s == 200 and data.get("trigger_blocked") is True

# 12. Benchmark
s, body = get("/api/benchmark")
data = json.loads(body)
print(f"GET /api/benchmark : Status {s}, Overall Selector WAPE: {data.get('overall', {}).get('selector_wape')}%")
assert s == 200

print("\nALL 12 API ENDPOINTS VERIFIED AND RESPONDING SUCCESSFULLY (100% PASS)!")
