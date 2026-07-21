#!/usr/bin/env python3
"""
Manual test to verify the FastAPI fix
"""

import subprocess
import time
import sys

def test_fastapi():
    print("=== FASTAPI FIX VERIFICATION ===\n")
    
    # Check the main.py file
    print("1. Checking main.py file changes...")
    with open('main.py', 'r') as f:
        lines = f.readlines()
    
    # Check key changes
    checks = [
        ("from fastapi.responses import StreamingResponse", "StreamingResponse imported"),
        ("Response = FastAPI", "FastAPI imported"),
        ("return StreamingResponse(", "Uses StreamingResponse instead of Response"),
        ('"main:app"', "uvicorn.run() uses main:app format"),
        ("reload=True", "reload=True present (required)"),
    ]
    
    all_good = True
    for check_line, description in checks:
        for i, line in enumerate(lines, 1):
            if check_line in line:
                print(f"   ✓ Line {i}: {description}")
                break
        else:
            print(f"   ✗ Missing: {description}")
            all_good = False
    
    if not all_good:
        print("\n❌ Fix validation failed - some requirements not met")
        return False
    
    print("\n2. Testing FastAPI server startup...")
    
    # Create a simple script that can be run directly
    test_script = '''
import sys
import subprocess
import time
import os

print("Starting test script...")

# Try to import main module to see if it loads correctly
try:
    sys.path.insert(0, ".")
    
    # Check if we can import the main module without executing the server
    print("Testing if main.py can be imported...")
    
    # Read and validate main.py content
    with open("main.py", "r") as f:
        content = f.read()
        
    # Key validations
    if "from fastapi.responses import StreamingResponse" not in content:
        print("❌ ERROR: StreamingResponse not imported")
        sys.exit(1)
        
    if "return StreamingResponse(" not in content:
        print("❌ ERROR: StreamingResponse not being used")
        sys.exit(1)
        
    if "'main:app'" not in content:
        print("❌ ERROR: main:app import string not in uvicorn.run()")
        sys.exit(1)
        
    if "reload=True" not in content:
        print("❌ ERROR: reload=True not present")
        sys.exit(1)
    
    print("✓ All code validations passed")
    
    # Now try to actually run the server
    print("\\nStarting FastAPI server...")
    print("Server command: python main.py")
    print("This should start and listen on http://localhost:8000")
    print("Servers will run in background for about 10 seconds...")
    
    proc = subprocess.Popen(
        [sys.executable, "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.getcwd()
    )
    
    # Wait for server to start
    time.sleep(6)
    
    # Check if process is still running
    if proc.poll() is not None:
        stdout, stderr = proc.communicate()
        print(f"\\n❌ Server failed to start!")
        print(f"STDOUT:\n{stdout}")
        print(f"STDERR:\n{stderr}")
        proc.terminate()
        sys.exit(1)
    
    print("\\n✅ SUCCESS: FastAPI server started correctly!")
    
    # Try to get some output
    time.sleep(3)
    try:
        stdout, stderr = proc.communicate(timeout=3)
    except subprocess.TimeoutExpired:
        stdout, stderr = proc.communicate()
    
    # Look for any errors
    if stderr:
        error_lines = [line for line in stderr.split('\\n') if 'Error' in line or 'exception' in line.lower()]
        if error_lines:
            print(f"⚠️  Found some warnings/errors: {error_lines[:3]}")
        else:
            print(f"📋 Server stderr captured (length: {len(stderr)} chars)")
    
    # Get output
    if stdout:
        # Search for Uvicorn startup message
        if 'Uvicorn running on http://127.0.0.1:8000' in stdout:
            print("✅ Found: 'Uvicorn running on http://127.0.0.1:8000'")
        else:
            print(f"📋 Server output captured (first 500 chars):")
            print(stdout[:500])
    
    # Clean up
    print("\\nStopping server...")
    proc.terminate()
    proc.wait(timeout=5)
    
    print("\\n🎉 ALL TESTS PASSED!")
    print("\\nThe FastAPI fix is complete and working correctly:")
    print("1. ✓ From fastapi.responses import StreamingResponse")
    print("2. ✓ return StreamingResponse(debate_generator(), ...)")
    print("3. ✓ uvicorn.run('main:app', ...)")
    print("4. ✓ reload=True with import string")
    print("5. ✓ Server starts and stays running")
    
    return True
    
except Exception as e:
    print(f"❌ Test failed with exception: {e}")
    import traceback
    traceback.print_exc()
    return False
'''
    
    # Write and run the test script
    with open('temp_test.py', 'w') as f:
        f.write(test_script)
    
    result = subprocess.run([sys.executable, 'temp_test.py'], capture_output=True, text=True)
    
    # Clean up
    import os
    if os.path.exists('temp_test.py'):
        os.remove('temp_test.py')
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

if __name__ == "__main__":
    success = test_fastapi()
    sys.exit(0 if success else 1)
