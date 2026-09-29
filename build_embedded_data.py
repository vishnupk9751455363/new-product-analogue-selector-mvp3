"""
scripts/build_embedded_data.py
Extracts data from db/warehouse.db and compiles into a static JS data bundle
for offline/standalone zero-config frontend execution.
"""

import sqlite3
import json
import os
import sys
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.analogue_selector import AnalogueSelector
from src.baseline import CategoryAverageBaselineForecaster
from src.evaluate import run_benchmark

DB_PATH = os.path.join(BASE_DIR, "db", "warehouse.db")
OUTPUT_PATH = os.path.join(BASE_DIR, "static", "embedded_data.js")
ROOT_OUTPUT_PATH = os.path.join(BASE_DIR, "embedded_data.js")

def main():
    conn = sqlite3.connect(DB_PATH)
    prods_df = pd.read_sql("SELECT * FROM products", conn)
    sales_df = pd.read_sql("SELECT * FROM sales_history", conn)

    selector = AnalogueSelector()
    selector.fit(prods_df, sales_df)

    baseline = CategoryAverageBaselineForecaster(use_price_tier=True)
    baseline.fit(prods_df, sales_df)

    # 1. Cold start products
    cold_start = prods_df[prods_df["is_historical"] == 0].to_dict(orient="records")

    # 2. Historical catalogue
    hist_prods = prods_df[prods_df["is_historical"] == 1].to_dict(orient="records")
    for p in hist_prods:
        pid = str(p["product_id"])
        p["launch_curve"] = selector.historical_curves.get(pid, {})
        p["debiased_curve"] = selector.debiased_curves.get(pid, {})
        p["promo_lift_pct"] = round(selector.product_promo_lifts.get(pid, selector.DEFAULT_PROMO_LIFT_RATIO) * 100.0, 1)
        p["has_promo_activity"] = selector.promo_flags.get(pid, False)

    # 3. Category baseline curves
    cat_baselines = {}
    for p in cold_start:
        cat_key = f"{p['category']}_{p['price_tier']}"
        if cat_key not in cat_baselines:
            cat_baselines[cat_key] = baseline.forecast(p)

    # 4. Benchmark evaluation data
    bench_res = run_benchmark(DB_PATH, k=5, horizon_weeks=8)

    # 5. Audit logs
    cur = conn.cursor()
    cur.execute("SELECT * FROM plan_changes ORDER BY change_id DESC LIMIT 20")
    audit_rows = [dict(sqlite3.Row(cur, r)) for r in cur.fetchall()]
    conn.close()

    embedded_payload = {
        "cold_start_products": cold_start,
        "historical_catalog": hist_prods,
        "category_baselines": cat_baselines,
        "category_promo_lifts": selector.category_promo_lifts,
        "benchmark": {
            "overall": bench_res["overall"],
            "weekly": bench_res["weekly"].to_dict(orient="records"),
            "per_product": bench_res["per_product"].to_dict(orient="records")
        },
        "audit_logs": audit_rows,
        "numeric_ranges": {
            "pack_size": list(selector.numeric_ranges.get("pack_size", (1.0, 12.0))),
            "shelf_life": list(selector.numeric_ranges.get("shelf_life", (4.0, 360.0)))
        },
        "default_weights": selector.DEFAULT_WEIGHTS,
        "optimized_weights": {
            "category": 0.28,
            "subcategory": 0.22,
            "festival": 0.14,
            "price_tier": 0.16,
            "pack_size": 0.08,
            "shelf_life": 0.07,
            "weather_sensitivity": 0.05
        }
    }

    js_code = "// Auto-generated embedded dataset for autonomous client-side execution\n"
    js_code += "window.DEMANDLENS_EMBEDDED_DATA = " + json.dumps(embedded_payload, indent=2) + ";\n"

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(js_code)
    with open(ROOT_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(js_code)

    print(f"Generated {OUTPUT_PATH} and {ROOT_OUTPUT_PATH} successfully ({len(js_code)} bytes).")

if __name__ == "__main__":
    main()
