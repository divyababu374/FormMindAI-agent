import requests

print("--- 1. Testing Frontend ---")
try:
    r = requests.get("http://localhost:5173/", timeout=5)
    print("Frontend status:", r.status_code, "HTML title present:", "<title>" in r.text)
except Exception as e:
    print("Frontend error:", e)

print("\n--- 2. Testing Backend Forms List ---")
try:
    r = requests.get("http://127.0.0.1:8000/api/forms/", timeout=5)
    print("Forms list status:", r.status_code)
    forms = r.json()
    print(f"Total forms returned: {len(forms)}")
    for f in forms:
        fid = f.get("id")
        title = f.get("title")
        count = f.get("total_responses_count")
        status = f.get("response_access_status")
        print(f"  Form: {title} ({fid[:8]}...) -> responses: {count}, access: {status}")
except Exception as e:
    print("Backend forms list error:", e)

print("\n--- 3. Testing Form Detail and Analysis ---")
if forms:
    target_id = forms[0]["id"]
    try:
        detail_res = requests.get(f"http://127.0.0.1:8000/api/forms/{target_id}", timeout=5)
        d = detail_res.json()
        print(f"Detail for '{d.get('title')}': questions={d.get('questions_count')}, responses={d.get('total_responses_count')}")
        
        analysis_res = requests.get(f"http://127.0.0.1:8000/api/forms/{target_id}/analysis", timeout=5)
        a = analysis_res.json()
        print("Analysis executive summary:", (a.get("executive_summary") or "")[:120] + "...")
        print("Basic statistics:", a.get("basic_statistics"))
    except Exception as e:
        print("Form detail error:", e)

print("\n--- Verification Complete ---")
