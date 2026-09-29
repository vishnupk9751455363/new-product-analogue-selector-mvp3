import re

with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

btn_ids = re.findall(r'<button[^>]+id=["\']([^"\']+)["\']', html)
print(f"Total button IDs in HTML: {len(btn_ids)}")
for bid in sorted(btn_ids):
    has_listener = (f'"{bid}"' in js or f"'{bid}'" in js)
    print(f"{bid:30}: {'CONNECTED' if has_listener else 'CHECK'}")

inputs = re.findall(r'<(?:input|select|textarea)[^>]+id=["\']([^"\']+)["\']', html)
print(f"\nTotal inputs/selects in HTML: {len(inputs)}")
for iid in sorted(inputs):
    has_ref = (f'"{iid}"' in js or f"'{iid}'" in js)
    print(f"{iid:30}: {'REFERENCED' if has_ref else 'UNREFERENCED'}")
