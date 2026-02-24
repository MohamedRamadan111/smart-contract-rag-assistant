import requests


try:
    print("Testing API connection...")
    response = requests.post(
        "http://localhost:8000/ask_stream",
        json={"question": "Hello World"} 
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ API is working correctly!")
        print("Response sample:")
        for line in response.iter_lines():
            if line: print(line)
            break
    else:
        print("❌ API Error!")
        print(f"Server Response: {response.text}")

except Exception as e:
    print(f"Connection Failed: {e}")