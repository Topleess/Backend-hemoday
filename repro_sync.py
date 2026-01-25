import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def run_repro():
    # 1. Register
    email = f"test_repro_{int(time.time())}@example.com"
    password = "password123"
    print(f"Registering {email}...")
    
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password
    })
    
    if resp.status_code != 201:
        print(f"Registration failed: {resp.text}")
        return
        
    token = resp.json()["access_token"]
    print("Got token.")
    
    # 2. Push Sync Data
    # Payload matching what mobile might send, including 'chelator'
    payload = {
        "changes": {
            "transfusions": {
                "created": [
                    {
                        "id": "test-uuid-1",
                        "date": "2023-10-27",
                        "volume": 200,
                        "weight": 70.0,
                        "component": "concentrate",
                        "volume_per_kg": 2.8,
                        "hb_before": 90,
                        "hb_after": 100,
                        "delta_hb": 10,
                        "chelator": "Exjade",
                        "created_at": int(time.time()*1000),
                        "updated_at": int(time.time()*1000)
                    }
                ],
                "updated": [],
                "deleted": []
            }
        }
    }
    
    headers = {"Authorization": f"Bearer {token}"}

    # Push data
    print("Pushing data...")
    push_response = getattr(requests, 'post')(
        f"{BASE_URL}/sync",
        json=payload,
        headers=headers
    )
    print(f"Push Status: {push_response.status_code}")
    print(f"Push Response: {push_response.text}")

    # Pull data
    print("\nPulling data...")
    pull_response = getattr(requests, 'get')(
        f"{BASE_URL}/sync",
        params={"last_pulled_at": None},
        headers=headers
    )
    print(f"Pull Status: {pull_response.status_code}")
    print(f"Pull Response: {pull_response.text}")

if __name__ == "__main__":
    try:
        run_repro()
    except Exception as e:
        print(e)
