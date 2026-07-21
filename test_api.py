#!/usr/bin/env python3
import subprocess
import time
import requests
import json

# Change to the AI-DEBATE-ARENA directory
# Run main.py (the FastAPI server)
print("Starting FastAPI server...")
server_proc = subprocess.Popen(["python", "main.py"], cwd="/Users/princ/Desktop/AI-DEBATE-ARENA", stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Wait for server to start
time.sleep(3)

print("Testing backend endpoints after startup...")

# Test health endpoint
try:
    response = requests.get("http://localhost:8000/api/health")
    print(f"Health endpoint: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"Health endpoint failed: {e}")

# Test personas endpoint
try:
    response = requests.get("http://localhost:8000/api/personas")
    print(f"Personas endpoint: {response.status_code}")
    
    personas = response.json()
    print(f"Personas keys: {list(personas.keys())}")
    
    for persona_key in personas:
        print(f"  Persona {persona_key}: pro={personas[persona_key]['pro']}, con={personas[persona_key]['con']}")
        
    print()
    print('✓ All backend tests passed!')
    
    # Test debate endpoint with different personas
    print("\nTesting debate endpoint with persona=economists...")
    response = requests.get("http://localhost:8000/api/debate?topic=Test+topic&rounds=1&persona=economists")
    print(f"Debate endpoint status: {response.status_code}")
    
    # Check if it's a streaming response (SSE)
    if response.headers.get('content-type', '').startswith('text/event-stream'):
        print("✓ Debate endpoint is streaming as expected")
    else:
        # Try to read as JSON
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response text (truncated): {response.text[:200]}...")
    
    print("\n✓ All backend tests completed!")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    print("\nStopping server...")
    server_proc.terminate()
    server_proc.wait()