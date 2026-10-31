import json
import os

base_dir = r"C:\Users\Anshumaan\.gemini\antigravity\scratch\ecommerce-customer-analysis"
json_path = os.path.join(base_dir, "dashboard", "dashboard_data.json")
html_path = os.path.join(base_dir, "dashboard", "ecommerce_dashboard.html")

with open(json_path, 'r', encoding='utf-8') as f:
    json_data = f.read()

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

target = "let DATA = null;"
replacement = f"const EMBEDDED_DATA = {json_data};\n    let DATA = null;"

if target in html:
    html = html.replace(target, replacement, 1)

# Now update loadData to use EMBEDDED_DATA directly if fetch fails or on file://
old_load = """    async function loadData() {
        try {
            const resp = await fetch('dashboard_data.json');
            DATA = await resp.json();
            initDashboard();
        } catch(e) {
            document.querySelector('.main').innerHTML =
                `<div class="loading" style="flex-direction:column;gap:12px;">
                    <p style="color:var(--accent-red);">⚠️ Could not load dashboard_data.json</p>
                    <p style="font-size:12px;">Make sure the file is in the same directory as this HTML file.<br>
                    If opening locally, use a local server: <code>python -m http.server 8080</code></p>
                </div>`;
        }
    }"""

new_load = """    async function loadData() {
        try {
            if (window.location.protocol !== 'file:') {
                const resp = await fetch('dashboard_data.json');
                if (resp.ok) {
                    DATA = await resp.json();
                } else {
                    DATA = EMBEDDED_DATA;
                }
            } else {
                DATA = EMBEDDED_DATA;
            }
        } catch(e) {
            DATA = EMBEDDED_DATA;
        }
        initDashboard();
    }"""

if old_load in html:
    html = html.replace(old_load, new_load, 1)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated dashboard with embedded data successfully.")

