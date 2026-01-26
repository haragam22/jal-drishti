import { useState, useEffect, useRef } from 'react';

const BACKEND_URL = "ws://127.0.0.1:8000/ws/stream";

const useLiveStream = (token) => {
    const [frame, setFrame] = useState(null);
    const [fps, setFps] = useState(0);
    const [isConnected, setIsConnected] = useState(false);

    const wsRef = useRef(null);
    const frameCountRef = useRef(0);
    const fpsIntervalRef = useRef(null);
    const streamIntervalRef = useRef(null);

    useEffect(() => {
        // Connect to WebSocket
        if (!token) return;

        const connect = () => {
            const ws = new WebSocket(`${BACKEND_URL}?token=${token}`);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log("Connected to AI Backend");
                setIsConnected(true);

                // Start sending dummy frames to drive the backend loop
                // In a real app, this would be camera frames. 
                // Here we send an empty byte array to simulate a stream.
                streamIntervalRef.current = setInterval(() => {
                    if (ws.readyState === WebSocket.OPEN) {
                        // Send a 1-byte dummy frame
                        ws.send(new Uint8Array([0]));
                    }
                }, 66); // ~15 FPS
            };

            ws.onmessage = (event) => {
                try {
                    const response = JSON.parse(event.data);
                    if (response.status === "success") {
                        setFrame(response);
                        frameCountRef.current += 1;
                    }
                } catch (err) {
                    console.error("Error parsing backend data:", err);
                }
            };

            ws.onclose = () => {
                console.log("Disconnected from Backend");
                setIsConnected(false);
                if (streamIntervalRef.current) clearInterval(streamIntervalRef.current);
                // Optional: Reconnect logic could go here
            };

            ws.onerror = (err) => {
                console.error("WebSocket Error:", err);
                ws.close();
            };
        };

        connect();

        // FPS Clock
        fpsIntervalRef.current = setInterval(() => {
            setFps(frameCountRef.current);
            frameCountRef.current = 0;
        }, 1000);

        // Cleanup
        return () => {
            if (wsRef.current) wsRef.current.close();
            if (fpsIntervalRef.current) clearInterval(fpsIntervalRef.current);
            if (streamIntervalRef.current) clearInterval(streamIntervalRef.current);
        };
    }, [token]);

    return { frame, fps, isConnected };
};

export default useLiveStream;
