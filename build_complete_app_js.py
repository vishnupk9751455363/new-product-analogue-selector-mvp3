"""
scripts/build_complete_app_js.py
Constructs the complete, resilient enterprise app.js incorporating:
- Live FastAPI Backend Integration (connected mode)
- Autonomous Embedded Intelligence Engine (standalone / zero-server mode)
- Dynamic Weighted Gower metric recalculation on slider input
- Promotional de-biasing organic curve computation
- Full disruption scenario simulation suite (supplier delay, capacity, viral spike, weather, festival)
- Complete evaluation benchmark data and search filter
- Real-time immutable audit ledger with trigger security tamper test simulation
- Edge case sandbox with graceful degradation
- Full CSV export functionality
"""

import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMBEDDED_JS_PATH = os.path.join(BASE_DIR, "static", "embedded_data.js")

with open(EMBEDDED_JS_PATH, "r", encoding="utf-8") as f:
    embedded_raw = f.read()

# Extract the JSON object from embedded_data.js
json_text = embedded_raw.split("window.DEMANDLENS_EMBEDDED_DATA = ")[1].rstrip(";\n ")
embedded_data_obj = json.loads(json_text)

# Read the current static/app.js to retain all the UI styling, chart options, and event bindings
with open(os.path.join(BASE_DIR, "static", "app.js"), "r", encoding="utf-8") as f:
    current_app_js = f.read()

print(f"Current app.js size: {len(current_app_js)} bytes.")
