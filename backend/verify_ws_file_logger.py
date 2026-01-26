
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:9000/ws/stream"
    with open("ws_test_log.txt", "w") as f:
        f.write(f"Connecting to {uri}...\n")
        try:
            async with websockets.connect(uri) as websocket:
                f.write("Connected! Waiting for messages...\n")
                
                # Listen for 3 messages
                for i in range(3):
                    message = await websocket.recv()
                    data = json.loads(message)
                    f.write(f"Received: {json.dumps(data)}\n")
                    
                f.write("SUCCESS: Received 3 messages.\n")
                    
        except Exception as e:
            f.write(f"Connection failed: {e}\n")

if __name__ == "__main__":
    try:
        asyncio.run(test_websocket())
    except Exception as e:
        with open("ws_test_log.txt", "a") as f:
            f.write(f"Fatal Error: {e}\n")
