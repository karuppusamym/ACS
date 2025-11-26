import requests
import json

# Test the connection API endpoint
url = "http://localhost:8000/api/v1/connection/connect"
data = {
    "name": "Python Test Connection",
    "type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "agentic_analyst",
    "username": "postgres",
    "password": "password",
    "description": "Test connection from Python script"
}

print("Testing connection API endpoint...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")
print()

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! Connection saved successfully!")
    else:
        print(f"\n❌ FAILED! Status code: {response.status_code}")
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
