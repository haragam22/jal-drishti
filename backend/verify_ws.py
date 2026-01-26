
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:9000/ws/stream"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected! Waiting for messages...")
            
            # Listen for 5 messages then exit
            for i in range(5):
                message = await websocket.recv()
                data = json.loads(message)
                print(f"Received: {json.dumps(data, indent=2)}")
                
                # Validation
                print(f"Type: {data.get('type')}, Status: {data.get('status')}")
                assert "type" in data
                assert "status" in data
                assert "payload" in data
                
                if data["type"] == "data":
                    payload = data["payload"]
                    assert "frame_id" in payload
                    assert "system" in payload
                
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Ensure the backend server is running: python app/main.py")

if __name__ == "__main__":
    try:
        asyncio.run(test_websocket())
    except KeyboardInterrupt:
        pass
