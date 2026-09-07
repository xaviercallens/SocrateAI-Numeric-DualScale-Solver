import os
import sys
import pytest
import asyncio
import aiohttp
import subprocess
import time
import socket

# Ensure leanflow_antigravity can be imported
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

@pytest.mark.asyncio
async def test_serverless_concurrency():
    """
    Test Step 4: Serverless Concurrency & PyO3 Audit
    Sends 50 concurrent POST requests to the FastAPI server.
    Asserts that exactly 0 requests return an HTTP 500 or OOM error,
    proving PyO3 releases the GIL cleanly.
    """
    port = get_free_port()
    
    # Start the FastAPI server using uvicorn
    # Make sure we run it from the workspace root so it can find leanflow_antigravity
    env = os.environ.copy()
    env["PYTHONPATH"] = WORKSPACE_ROOT
    
    process = subprocess.Popen(
        ["python3", "-m", "uvicorn", "leanflow_antigravity.api:app", "--host", "127.0.0.1", "--port", str(port)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    url = f"http://127.0.0.1:{port}/step"
    
    try:
        # Wait for the server to start by polling
        async def wait_for_server():
            async with aiohttp.ClientSession() as session:
                for _ in range(30):
                    try:
                        async with session.get(f"http://127.0.0.1:{port}/docs") as resp:
                            if resp.status == 200:
                                return True
                    except aiohttp.ClientConnectorError:
                        pass
                    await asyncio.sleep(0.5)
            return False
            
        is_ready = await wait_for_server()
        assert is_ready, "Server failed to start within 15 seconds"
        
        async def fetch(session, cycle_idx):
            payload = {"cycle_idx": cycle_idx}
            async with session.post(url, json=payload) as response:
                return response.status, await response.text()
                
        async with aiohttp.ClientSession() as session:
            tasks = [fetch(session, i) for i in range(50)]
            results = await asyncio.gather(*tasks)
            
        errors = [status for status, text in results if status == 500 or "OOM" in text or "OutOfMemory" in text]
        
        assert len(errors) == 0, f"Expected 0 HTTP 500 or OOM errors, but got {len(errors)}"
        assert len(results) == 50, "Did not receive exactly 50 responses"
        
    finally:
        process.terminate()
        process.wait(timeout=2.0)
