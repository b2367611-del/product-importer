#!/usr/bin/env python3
"""
Test script to debug upload issues
"""
import requests
import os

def test_upload():
    # Test if server is running
    try:
        response = requests.get("http://localhost:8000/")
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        return

    # Test upload endpoint
    if not os.path.exists("sample_products.csv"):
        print("❌ sample_products.csv not found")
        return
    
    try:
        with open("sample_products.csv", "rb") as f:
            files = {"file": ("sample_products.csv", f, "text/csv")}
            response = requests.post("http://localhost:8000/api/v1/import/upload", files=files)
            
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response content: {response.text[:500]}")
        
        if response.status_code == 200:
            print("✅ Upload successful!")
            data = response.json()
            print(f"Task ID: {data.get('task_id')}")
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_upload()