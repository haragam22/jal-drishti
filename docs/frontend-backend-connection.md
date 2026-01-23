# Jal-Drishti: Frontend & Backend Architecture

This document explains how the **Jal-Drishti** system works, how the Frontend (UI) talks to the Backend (Server), and what each part is responsible for.

---

## 1. The Big Picture
Jal-Drishti is a real-time AI dashboard.
- **Frontend**: Shows the video feed, bounding boxes, and alerts.
- **Backend**: Simulates the "AI" that detects objects.
- **Connection**: They talk over a **WebSocket**, which is like a permanent phone line that stays open for fast two-way communication.

---

## 2. Frontend (The Visuals)
**Status**: Built with React + Vite.

### What it does:
*   **Draws the Dashboard**: Displays the dark-mode UI, video panels, and status bars.
*   **Smart Overlay**: Uses a `<canvas>` element to draw colored boxes *on top* of the video feed. It doesn't modify the video itself; it just paints over it based on coordinates it receives.
*   **The "Driver"**: Currently, since we don't have a real camera connected, the Frontend acts as the driver. It sends a "ping" (a small dummy data packet) to the backend 15 times a second (FPS). This tells the backend "Hey, give me the next frame's data."

### Key Files:
*   `src/components/`: The UI building blocks (`VideoPanel`, `AlertPanel`, etc.).
*   `src/hooks/useLiveStream.js`: **The most important file.** This is the bridge. It connects to the backend and manages the stream loop.

---

## 3. Backend (The Brain)
**Status**: Built with Python + FastAPI.

### What it does:
*   **Listens**: It sits waiting at `ws://localhost:8000/ws/stream`.
*   **Simulates AI**: We don't have a heavy ML model loaded yet. Instead, we have a **Dummy ML Service** (`ml_service.py`).
    *   It remembers where "objects" are.
    *   Every time it gets a "ping" from the frontend, it moves the objects slightly (bounces them off walls).
    *   It invents a confidence score (e.g., 88%).
*   **Responds**: It sends back a JSON package containing the frame ID and the list of detections.

### Key Files:
*   `app/api/stream.py`: The door. It accepts the WebSocket connection.
*   `app/services/ml_service.py`: The fake brain. It generates the moving box coordinates.

---

## 4. How They Connect (The Flow)

Here is the exact cycle that happens ~15 times every second:

1.  **FRONTEND**: Connects to `ws://localhost:8000/ws/stream`.
2.  **FRONTEND**: Sends a tiny byte (dummy frame) to the server.
3.  **BACKEND**: Receives the byte.
4.  **BACKEND**: Asks `ml_service`: "Where are the objects now?"
5.  **BACKEND**: Sends back a JSON response:
    ```json
    {
      "status": "success",
      "detections": [{ "label": "Bag", "bbox": [100, 200, 50, 50] }]
    }
    ```
6.  **FRONTEND**: Receives JSON -> React updates the state -> Canvas paints the red box at `[100, 200]`.

---

## Summary for the Team
*   **Frontend developers**: You don't need to worry about ML. Just use the data coming into `useLiveStream.js` to render the UI.
*   **Backend developers**: You don't need to worry about pixels. Just make sure `stream.py` receives bytes and returns the correct JSON structure defined in `schemas/response.py`.
*   **Integration**: As long as the **JSON Structure** stays the same, both teams can work independently!
