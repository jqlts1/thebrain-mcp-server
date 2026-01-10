
import requests
import json
import time

API_KEY = "dummy" # Bearer token needed
BASE_URL = "http://localhost:8000/api"

import os
# Load env to get real key for client convenience script?
# Or just use the one in .env file if running locally.
# Let's assume server is running with env loaded.
# But test script needs key to call API.
# I'll read .env manually or assume I can grep it.
# Actually I can use the existing 'client.py' logic if I import it, but I want to test via API endpoint.

def get_api_key():
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("THEBRAIN_API_KEY="):
                return line.split("=")[1].strip().strip('"')
    return ""

TOKEN = get_api_key()
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def test_structure():
    print(f"Token loaded: {bool(TOKEN)}")
    print("1. Creating Root Thought...")
    resp = requests.post(f"{BASE_URL}/thoughts", headers=HEADERS, json={"name": "Test Structure Root", "kind": 1})
    if resp.status_code != 200:
        print(f"Failed to create root: Status={resp.status_code}, Body='{resp.text}'")
        return
    root = resp.json()
    root_id = root["id"]
    print(f"Root created: {root_id}")

    try:
        print("2. Importing Structure...")
        structure = {
            "name": "Ignored Root Name", # top level is merged or ignored if creating children
            # API endpoint is POST /thoughts/{id}/structure. 
            # If Body is List, adds children. If Body is Dict, adds children defined in it? 
            # create_structure implementation:
            # If data is List -> list of children.
            # If data is Dict -> create thought using dict as props, THEN add its children.
            # Wait, if I call create_structure(parent_id, DataDict), it creates a NEW child based on DataDict.
            # It does NOT merge DataDict into parent_id.
            # So if I want to add children TO parent_id, I should pass a LIST.
            # Let's verify client.py logic.
            # if isinstance(data, list): foreach item create_structure(parent, item). Correct.
            # if isinstance(data, dict): create_thought(name, source_id=parent). Correct.
            
            # So to add multiple children to Root, I must pass a List.
        }
        
        structure_list = [
            "Simple Child",
            {
                "name": "Complex Child",
                "label": "TestTag",
                "color": "#FF0000",
                "children": [
                    "Grandchild A",
                    {"name": "Grandchild B", "note": "## Note Content"}
                ]
            }
        ]
        
        resp = requests.post(f"{BASE_URL}/thoughts/{root_id}/structure", headers=HEADERS, json=structure_list)
        print("Import Response:", resp.text)
        assert resp.status_code == 200
        
        print("3. Verifying children...")
        print("Root details:", requests.get(f"{BASE_URL}/thoughts/{root_id}", headers=HEADERS).json())
        print("Root graph:", requests.get(f"{BASE_URL}/thoughts/{root_id}/graph", headers=HEADERS).json())
        time.sleep(2) # Wait for indexing? Usually fast.
        resp = requests.get(f"{BASE_URL}/thoughts/{root_id}/children", headers=HEADERS)
        children = resp.json()
        names = [c["name"] for c in children]
        
        if "Simple Child" not in names:
            print("❌ Simple Child not found in children!")
            print("Graph data:", json.dumps(children, indent=2))
            
            # Check if orphan
            print("Checking if Simple Child exists as orphan...")
            search_res = requests.post(f"{BASE_URL}/tools/search_thoughts", headers=HEADERS, json={"query": "Simple Child", "n": 1}).json()
            print("Search result:", search_res)


        print("Children found:", names)
        assert "Simple Child" in names
        assert "Complex Child" in names
        
        # Verify Grandchild
        complex_child = next(c for c in children if c["name"] == "Complex Child")
        resp = requests.get(f"{BASE_URL}/thoughts/{complex_child['id']}/children", headers=HEADERS)
        g_children = resp.json()
        g_names = [c["name"] for c in g_children]
        print("Grandchildren found:", g_names)
        assert "Grandchild A" in g_names
        assert "Grandchild B" in g_names
        
        print("✅ Structure test passed!")

    finally:
        print("4. Cleaning up...")
        # Delete root (should delete orphans if brain settings allow, or just root)
        # TheBrain API delete thought usually leaves children processing?
        # Actually API delete usually unlinks or forgets.
        # I'll just delete the root.
        requests.delete(f"{BASE_URL}/thoughts/{root_id}", headers=HEADERS)
        print("Cleaned up.")

if __name__ == "__main__":
    test_structure()
