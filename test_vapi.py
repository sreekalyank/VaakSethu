"""
test_vapi.py
------------
Run this to debug your Vapi connection and trigger a test call.
Usage: python test_vapi.py
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")

HEADERS = {
    "Authorization": f"Bearer {VAPI_API_KEY}",
    "Content-Type": "application/json"
}

print("=" * 50)
print("VAPI CONNECTION TEST")
print("=" * 50)

# Step 1: Check env variables
print("\n[1] Checking .env variables...")
print(f"  VAPI_API_KEY     : {'✅ Found' if VAPI_API_KEY else '❌ MISSING'}")
print(f"  PHONE_NUMBER_ID  : {'✅ Found' if PHONE_NUMBER_ID else '❌ MISSING'}")
print(f"  ASSISTANT_ID     : {'✅ Found' if ASSISTANT_ID else '❌ MISSING'}")

# Step 2: Test API key
print("\n[2] Testing API key...")
r = requests.get("https://api.vapi.ai/phone-number", headers=HEADERS)
print(f"  Status Code: {r.status_code}")
if r.status_code == 200:
    print("  ✅ API key is valid!")
    numbers = r.json()
    print(f"  Phone numbers on account: {len(numbers)}")
    for n in numbers:
        print(f"    - {n.get('number')} | ID: {n.get('id')}")
elif r.status_code == 401:
    print("  ❌ API key is INVALID — check your VAPI_API_KEY in .env")
else:
    print(f"  ❌ Unexpected error: {r.text}")

# Step 3: Trigger test call
print("\n[3] Triggering test call to +917013549646 ...")
payload = {
    "phoneNumberId": PHONE_NUMBER_ID,
    "assistantId": ASSISTANT_ID,
    "customer": {
        "number": "+917013549646",
        "name": "Test"
    }
}

r2 = requests.post("https://api.vapi.ai/call/phone", json=payload, headers=HEADERS)
print(f"  Status Code: {r2.status_code}")
print(f"  Response: {r2.text}")

if r2.status_code == 201:
    data = r2.json()
    print(f"\n  ✅ Call triggered successfully!")
    print(f"  Call ID : {data.get('id')}")
    print(f"  Status  : {data.get('status')}")
else:
    print(f"\n  ❌ Call failed — see response above for reason")
