import requests
import sys

def test_login():
    url = "http://127.0.0.1:8000/api/v1/auth/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Login Successful!")
            print(response.json())
        else:
            print(f"Login Failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login()
