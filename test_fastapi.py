# Simple test to verify the FastAPI setup works
print("Testing FastAPI setup...")
try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from agent import DebateAgent, DebateJudge
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Note: FastAPI packages may need to be installed first")

print("\nTest completed successfully if no import errors above.")
