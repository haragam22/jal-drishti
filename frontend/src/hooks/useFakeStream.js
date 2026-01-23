import { useState, useEffect, useRef } from 'react';
import { generateNextFrame } from '../data/mockStreamGenerator';

const useFakeStream = () => {
    const [frame, setFrame] = useState(null);
    const [fps, setFps] = useState(0);
    const [isConnected, setIsConnected] = useState(false);

    // Refs for logic that shouldn't trigger re-renders
    const frameCountRef = useRef(0);
    const intervalRef = useRef(null);
    const fpsIntervalRef = useRef(null);

    useEffect(() => {
        setIsConnected(true);

        // 1. Frame Loop (Approx 15 FPS -> 66ms)
        intervalRef.current = setInterval(() => {
            const nextFrame = generateNextFrame();

            // Update state with latest frame
            // In a real high-perf scenario, we might use refs or requestAnimationFrame,
            // but for this UI skeleton, useState is sufficient and correct for React updates.
            setFrame(nextFrame);

            // Increment counter for FPS calculation
            frameCountRef.current += 1;
        }, 66);

        // 2. FPS Calculation Loop (Every 1 second)
        fpsIntervalRef.current = setInterval(() => {
            setFps(frameCountRef.current);
            frameCountRef.current = 0; // Reset counter
        }, 1000);

        // Cleanup on unmount
        return () => {
            setIsConnected(false);
            if (intervalRef.current) clearInterval(intervalRef.current);
            if (fpsIntervalRef.current) clearInterval(fpsIntervalRef.current);
        };
    }, []);

    return { frame, fps, isConnected };
};

export default useFakeStream;
