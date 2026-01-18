
import sys
import os

def check_req():
    print("Checking requests...")
    try:
        import requests
        print(f"Requests version: {requests.__version__}")
        s = requests.Session()
        print("Session created")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_req()
