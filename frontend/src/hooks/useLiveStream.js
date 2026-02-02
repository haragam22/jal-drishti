import { useState, useEffect, useRef, useCallback } from 'react';
import {
    SYSTEM_STATES,
    CONNECTION_STATES,
    RECONNECT_CONFIG,
    WS_CONFIG
} from '../constants';

/**
 * useLiveStream Hook
 * 
 * PHASE-3 OPTIMIZED:
 * - Frontend is PASSIVE subscriber
 * - Backend drives timing, not frontend
 * - Keep last valid frame on disconnect
 * - No pings to backend
 * - requestAnimationFrame decoupling: WS receive rate != render rate
 */
const useLiveStream = (enabled = true) => {
    const [frame, setFrame] = useState(null);
    const [fps, setFps] = useState(0);
    const [connectionStatus, setConnectionStatus] = useState(CONNECTION_STATES.DISCONNECTED);
    const [reconnectAttempt, setReconnectAttempt] = useState(0);

    // Refs for logic that shouldn't trigger re-renders
    const wsRef = useRef(null);
    const frameCountRef = useRef(0);
    const fpsIntervalRef = useRef(null);
    const reconnectTimeoutRef = useRef(null);
    const lastValidFrameRef = useRef(null);
    const lastFrameIdRef = useRef(-1);
    const connectRef = useRef(null);

    // ========== requestAnimationFrame DECOUPLING ==========
    // Store latest frame in ref (fast, no re-render)
    // Only render via requestAnimationFrame (smooth, 60fps max)
    const latestFrameRef = useRef(null);
    const rafIdRef = useRef(null);
    const isRenderingRef = useRef(false);

    const getReconnectDelay = useCallback((attempt) => {
        return Math.min(
            RECONNECT_CONFIG.BASE_DELAY_MS * (2 ** attempt),
            RECONNECT_CONFIG.MAX_DELAY_MS
        );
    }, []);

    const cleanup = useCallback(() => {
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
        }
        if (rafIdRef.current) {
            cancelAnimationFrame(rafIdRef.current);
            rafIdRef.current = null;
        }
    }, []);

    // ========== RENDER LOOP (Decoupled from WS) ==========
    // This runs at display refresh rate (~60fps) but only updates state
    // when there's a new frame in latestFrameRef
    const renderLoop = useCallback(() => {
        if (latestFrameRef.current && !isRenderingRef.current) {
            isRenderingRef.current = true;
            const frameToRender = latestFrameRef.current;
            latestFrameRef.current = null; // Clear buffer

            setFrame(frameToRender);
            lastValidFrameRef.current = frameToRender;
            frameCountRef.current += 1;

            isRenderingRef.current = false;
        }
        rafIdRef.current = requestAnimationFrame(renderLoop);
    }, []);

    // Connect to WebSocket function
    const connect = useCallback(() => {
        if (!enabled) return;

        try {
            const ws = new WebSocket(WS_CONFIG.URL);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log('[WS] Connected to AI Backend');
                setConnectionStatus(CONNECTION_STATES.CONNECTED);
                setReconnectAttempt(0);

                // Start render loop on connect
                if (!rafIdRef.current) {
                    rafIdRef.current = requestAnimationFrame(renderLoop);
                }
            };

            ws.onmessage = (event) => {
                try {
                    const response = JSON.parse(event.data);

                    // Skip system messages
                    if (response.type === 'system') {
                        return;
                    }

                    // Out-of-order detection: ignore stale frames
                    if (response.frame_id !== undefined && response.frame_id <= lastFrameIdRef.current) {
                        return;
                    }
                    lastFrameIdRef.current = response.frame_id || lastFrameIdRef.current;

                    // Normalize image_data to a proper data URL
                    let imageData = response.image_data || null;
                    if (imageData && typeof imageData === 'string' && !imageData.startsWith('data:')) {
                        imageData = `data:image/jpeg;base64,${imageData}`;
                    }

                    const normalizedFrame = {
                        timestamp: response.timestamp || new Date().toISOString(),
                        state: response.state || SYSTEM_STATES.SAFE_MODE,
                        max_confidence: response.max_confidence ?? 0,
                        detections: response.detections || [],
                        visibility_score: response.visibility_score ?? 0,
                        image_data: imageData,
                        frame_id: response.frame_id,
                        system: {
                            fps: response.system?.fps ?? null,
                            latency_ms: response.system?.latency_ms ?? null
                        }
                    };

                    // DECOUPLING: Store in ref, don't call setFrame directly
                    // Render loop will pick it up on next animation frame
                    latestFrameRef.current = normalizedFrame;

                } catch (err) {
                    console.error('[WS] Error parsing response:', err);
                }
            };

            ws.onclose = (event) => {
                console.log('[WS] Connection closed:', event.code);

                // STABILIZATION FIX (Issue 6):
                // DO NOT clear frame on disconnect - keep last valid frame visible
                // Visual continuity > frame accuracy

                // Attempt reconnection if not at max attempts
                setReconnectAttempt((prev) => {
                    const nextAttempt = prev + 1;

                    if (nextAttempt >= RECONNECT_CONFIG.MAX_ATTEMPTS) {
                        console.log('[WS] Max reconnection attempts reached');
                        setConnectionStatus(CONNECTION_STATES.FAILED);
                        return nextAttempt;
                    }

                    setConnectionStatus(CONNECTION_STATES.DISCONNECTED);
                    const delay = getReconnectDelay(nextAttempt);
                    console.log(`[WS] Reconnecting in ${delay}ms (attempt ${nextAttempt}/${RECONNECT_CONFIG.MAX_ATTEMPTS})`);

                    reconnectTimeoutRef.current = setTimeout(() => {
                        if (connectRef.current) {
                            connectRef.current();
                        }
                    }, delay);

                    return nextAttempt;
                });
            };

            ws.onerror = () => {
                // Error will be followed by onclose
            };

        } catch (err) {
            console.error('[WS] Failed to create WebSocket:', err);
            setConnectionStatus(CONNECTION_STATES.FAILED);
        }
    }, [enabled, getReconnectDelay, renderLoop]);

    // Keep the ref updated for timeout callbacks
    useEffect(() => {
        connectRef.current = connect;
    }, [connect]);


    // Manual reconnect (for retry button after FAILED state)
    const manualReconnect = useCallback(() => {
        console.log('[WS] Manual reconnect triggered');
        setReconnectAttempt(0);
        lastFrameIdRef.current = -1;
        connect();
    }, [connect]);

    // Initialize connection and FPS counter
    useEffect(() => {
        connect();

        // FPS calculation loop
        fpsIntervalRef.current = setInterval(() => {
            setFps(frameCountRef.current);
            frameCountRef.current = 0;
        }, 1000);

        return () => {
            cleanup();
            if (fpsIntervalRef.current) {
                clearInterval(fpsIntervalRef.current);
            }
        };
    }, [connect, cleanup]);

    return {
        frame,
        fps,
        connectionStatus,
        reconnectAttempt,
        lastValidFrame: lastValidFrameRef.current,
        manualReconnect
    };
};

export default useLiveStream;
