import { useState, useEffect, useRef, useCallback } from 'react';
import { WS_CONFIG } from '../constants';

const useRawFeed = (token) => {
    const [status, setStatus] = useState('DISCONNECTED');
    const [resolution, setResolution] = useState(null);
    const imageRef = useRef(null); // Ref to the image string or Blob URL

    // We use a ref for the renderer to avoid re-renders on every frame
    // But we might want to expose a 'latestFrame' state if the consuming component renders via <img> src
    const [frameSrc, setFrameSrc] = useState(null);

    const wsRef = useRef(null);
    const lastFrameIdRef = useRef(-1);

    const connect = useCallback(() => {
        // Construct WS URL - explicitly triggering the raw_feed endpoint
        // Assuming WS_CONFIG.URL is base like "ws://localhost:8000/ws" 
        // We need to parse/modify it to "ws://localhost:8000/ws/raw_feed"

        // Parse the Configured URL
        // WS_CONFIG.URL is typically "ws://localhost:9000/ws/stream"
        // We need "ws://localhost:9000/ws/raw_feed"

        try {
            // Use URL object for robust parsing
            // Note: 'ws' protocol might need 'http' for URL constructor if environment is weird, 
            // but standard browsers handle ws/wss in URL object nowadays.
            // If not, we can treat it as string.

            const rawConfigUrl = WS_CONFIG.URL;
            let finalUrl;

            if (rawConfigUrl.includes('/ws/stream')) {
                finalUrl = rawConfigUrl.replace('/ws/stream', '/ws/raw_feed');
            } else if (rawConfigUrl.endsWith('/ws')) {
                finalUrl = `${rawConfigUrl}/raw_feed`;
            } else {
                // Fallback: URL might be just host
                const wsUrl = rawConfigUrl.endsWith('/') ? rawConfigUrl.slice(0, -1) : rawConfigUrl;
                finalUrl = `${wsUrl}/raw_feed`;
            }

            console.log(`[RawFeed] Connecting to ${finalUrl}`);
            const ws = new WebSocket(finalUrl);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log('[RawFeed] Connected');
                setStatus('CONNECTED');
                lastFrameIdRef.current = -1;
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    if (data.type === 'RAW_FRAME') {
                        // Out-of-order check
                        if (data.frame_id <= lastFrameIdRef.current) {
                            return; // Drop old frame
                        }
                        lastFrameIdRef.current = data.frame_id;

                        if (data.resolution) {
                            setResolution(data.resolution);
                        }

                        // Decode base64 
                        const src = `data:image/jpeg;base64,${data.image}`;
                        setFrameSrc(src);

                        // If we were waiting for signal, update status
                        setStatus('STREAMING');
                    }
                } catch (err) {
                    console.error('[RawFeed] Parse error', err);
                }
            };

            ws.onclose = () => {
                console.log('[RawFeed] Disconnected');
                setStatus('DISCONNECTED');
                setFrameSrc(null);
            };

            ws.onerror = (err) => {
                console.error('[RawFeed] Error', err);
                setStatus('ERROR');
            };

        } catch (e) {
            console.error("[RawFeed] URL Construction Error", e);
            setStatus('ERROR');
        }
    }, []);

    useEffect(() => {
        connect();
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [connect]);

    return {
        status,
        frameSrc,
        resolution
    };
}
    export default useRawFeed;
