# Jal-Drishti — Frontend ⇄ Backend ⇄ ML Architecture

## Purpose
A concise single-page reference describing how the Frontend, Backend and ML Engine interact in Phase-2, how to run and test the system, and known issues/troubleshooting steps observed during development.

---

## High-level Architecture

- Raw Video Source (Backend): `backend/app/video/video_reader.py` (alias `VideoReader` / `RawVideoSource`)
  - Reads `dummy.mp4` (or camera), converts frames from BGR → RGB and yields `(frame, frame_id, timestamp)`.

- Scheduler (Backend): `backend/app/scheduler/frame_scheduler.py`
  - Enforces target FPS, computes drift, always emits RAW frames to `raw_callback`, and sends a subset of frames to ML (dropping when behind).
  - Calls `result_callback` with ML outputs or system messages.

- Video Transport (Backend): `backend/app/services/video_stream_manager.py`
  - Encodes RGB frames to JPEG → base64 and broadcasts `RAW_FRAME` messages over `/ws/raw_feed`.

- ML Service (Backend): `backend/app/services/ml_service.py` (or `app.ml.dummy_ml`)
  - Provides `run_inference(frame)` which accepts a single RGB `uint8` frame and returns a fixed JSON payload. Loaded once at startup.

- WebSocket API
  - `/ws/raw_feed` (App-level path): Serves raw frames (from `VideoStreamManager`).
  - `/ws/stream` (ws_server router): Receives ML-connected clients and receives ML result broadcasts created by `result_callback`.

- Frontend
  - `useRawFeed` (hook) connects to `/ws/raw_feed`, receives `RAW_FRAME` messages with contract: `{type: 'RAW_FRAME', frame_id, timestamp, image, resolution}` and shows the raw JPEG.
  - `useLiveStream` (hook) connects to `/ws/stream` and receives ML `data` messages (schema: timestamp, state, detections, image_data, system.{fps, latency_ms}).
  - `RawFeedPanel` renders `useRawFeed` output; `VideoPanel` renders ML-enhanced feed and detections.

---

## Message Contracts (short)

- RAW_FRAME
  - type: "RAW_FRAME"
  - frame_id: int
  - timestamp: float (POSIX)
  - image: base64-jpeg string
  - resolution: [H, W]

- ML data (wrapped by scheduler `result_callback`)
  - type: "data"
  - payload: { frame_id, timestamp, state, detections, image_data (base64 or null), ... }

---

## How to run locally (quick)

1. Backend (in `backend/`):

```powershell
# from repository root
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 9000
```

2. Frontend (in `frontend/`):

```bash
cd frontend
npm run dev
# open the provided URL (default http://localhost:5173)
```

3. Login in the UI (test credentials), you should see two panels:
  - Left: RAW FEED (Sensor) — frames from `/ws/raw_feed`.
  - Right: ENHANCED FEED — frames / results forwarded from ML via `/ws/stream`.

---

## Troubleshooting (observed issues & fixes)

1. No frames in UI (RAW or Enhanced)
   - Cause: Frontend `WS_CONFIG.URL` pointed to `ws://127.0.0.1:8000` while backend runs on `9000`.
   - Fix: Update `frontend/src/constants.js` to point to `ws://127.0.0.1:9000/ws/stream` (done).

2. `UnboundLocalError: frame_index referenced before assignment` in `video_reader.py`
   - Cause: Logging used `frame_index` while variable was `frame_id`.
   - Fix: `video_reader.py` updated to use `frame_id`, yield `(frame, frame_id, timestamp)`, and convert BGR→RGB.

3. Raw feed not broadcast
   - Cause: `FrameScheduler` did not have a `raw_callback` registered in `app.main`.
   - Fix: `app.main` now registers `raw_callback` that schedules `video_stream_manager.broadcast_raw_frame` on the main event loop.

4. WebSocket send errors during rapid reconnects
   - State: `ws_server.broadcast` includes exception handling and uses `asyncio.run_coroutine_threadsafe` with the main event loop. Keep an eye on logs if frequent connects/disconnects occur.

5. Color mismatch (red/blue)
   - Cause: BGR vs RGB confusion between OpenCV and browser images.
   - Fix: `video_reader.py` converts BGR→RGB; `VideoStreamManager` encodes the RGB back to JPEG by converting to BGR first, so the displayed image has correct colors.

---

## Known Limitations & Recommendations

- Latency vs FPS: The scheduler drops frames for ML processing when drift exceeds the frame interval. The RAW feed still emits every frame.
- Single-threaded ML: If ML inference is slow, ML results will drop, but RAW frames continue streaming.
- Production readiness: Add health-check endpoints, graceful shutdown handling, and stronger WS backpressure handling for many clients.

---

## Next steps to verify after these changes

- Start backend and frontend, log messages should show:
  - "[RawVideoSource] Streaming from: ..."
  - "[VideoStreamManager] Client connected"
  - Frequent "RAW_FRAME" messages in browser Network WS tab for `/ws/raw_feed`.
  - ML results forwarded on `/ws/stream` if ML is enabled.

- If any issue remains, collect the backend logs (startup + scheduler) and front-end DevTools WebSocket frames.


---

For more detailed developer docs, see the `ml-engine` and `frontend/docs_helping` folders in the repository.
