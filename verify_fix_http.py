
import requests
import time

def test_action_skip():
    print("Testing /action skip...")
    # NOTE: This script assumes the server is ALREADY RUNNING on port 8000.
    # It cannot inject state into the running server easily without an endpoint.
    # But wait, I can restart the game and play until prompt? 
    # That's flaky.
    
    # Alternative: I can use a backdoor or just rely on the fact that 
    # if I start a game, P0 will eventually be asked for input or be the one acting.
    # But to test "Chi" specifically requires setup.
    
    # Actually, I can Import the engine from server.main IF I run this script in python
    # BUT importing it constructs a NEW engine instance, separate from the Uvicorn worker.
    # So I cannot modify the running server's state this way.
    
    # I MUST hit the API.
    # Let's try to hit /action with a dummy payload and see if it 400s or 500s.
    # If it 500s, it proves the crash.
    
    try:
        res = requests.post("http://localhost:8000/action", json={
            "type": "skip",
            "player_idx": 0
        })
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text}")
    except Exception as e:
        print(f"Request Failed: {e}")

if __name__ == "__main__":
    test_action_skip()
