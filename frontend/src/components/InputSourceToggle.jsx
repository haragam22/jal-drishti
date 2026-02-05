import React, { useState, useEffect, useCallback } from 'react';
import { API_BASE_URL, SOURCE_STATES } from '../constants';
import '../App.css';

/**
 * InputSourceToggle Component
 * 
 * PHASE-3 CORE: Runtime source switching via backend API.
 * - Fetches server info on mount
 * - Calls POST /api/source/select on toggle
 * - Shows camera URL when camera mode is active
 */
const InputSourceToggle = ({ currentSource, onToggle, sourceState, onReset }) => {
    const [serverInfo, setServerInfo] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const isCamera = currentSource === 'camera';
    const isWaiting = sourceState === SOURCE_STATES.CAMERA_WAITING;
    const isIdle = sourceState === SOURCE_STATES.IDLE;

    // Fetch server info on mount
    useEffect(() => {
        const fetchServerInfo = async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/api/source/info`);
                if (res.ok) {
                    const data = await res.json();
                    setServerInfo(data);
                }
            } catch (err) {
                console.warn('[InputSourceToggle] Failed to fetch server info:', err);
            }
        };
        fetchServerInfo();
    }, []);

    // Handle source toggle with API call
    const handleToggle = useCallback(async (sourceType) => {
        if (isLoading) return;

        setIsLoading(true);
        setError(null);

        try {
            const res = await fetch(`${API_BASE_URL}/api/source/select`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: sourceType })
            });

            const data = await res.json();

            if (data.success) {
                // Reset counters on successful switch
                if (onReset) onReset();
                onToggle(sourceType, data.state);
            } else {
                setError(data.error || 'Failed to switch source');
            }
        } catch (err) {
            setError('Network error');
            console.error('[InputSourceToggle] API error:', err);
        } finally {
            setIsLoading(false);
        }
    }, [isLoading, onToggle, onReset]);

    // Get status text based on state
    const getStatusText = () => {
        if (isLoading) return 'SWITCHING...';
        if (isWaiting) return 'WAITING FOR PHONE';
        if (sourceState === SOURCE_STATES.VIDEO_ACTIVE) return 'VIDEO ACTIVE';
        if (sourceState === SOURCE_STATES.CAMERA_ACTIVE) return 'CAMERA ACTIVE';
        if (sourceState === SOURCE_STATES.ERROR) return 'ERROR';
        if (isIdle) return 'SELECT SOURCE';
        return isCamera ? 'CAMERA' : 'VIDEO';
    };

    // Get status color class
    const getStatusClass = () => {
        if (isLoading || isWaiting) return 'status-waiting';
        if (sourceState === SOURCE_STATES.VIDEO_ACTIVE) return 'status-video';
        if (sourceState === SOURCE_STATES.CAMERA_ACTIVE) return 'status-camera';
        if (sourceState === SOURCE_STATES.ERROR) return 'status-error';
        if (isIdle) return 'status-idle';
        return isCamera ? 'status-camera' : 'status-video';
    };

    return (
        <div className="input-source-toggle-container">
            <div className="toggle-header">
                <span className="toggle-label">INPUT SOURCE CONTROL</span>
                <span className={`toggle-status ${getStatusClass()}`}>
                    {getStatusText()}
                </span>
            </div>

            <div className="toggle-controls">
                <button
                    className={`source-btn ${!isCamera && !isIdle ? 'active' : ''} ${isLoading ? 'disabled' : ''}`}
                    onClick={() => handleToggle('video')}
                    disabled={isLoading}
                    title="Use Pre-recorded Video"
                >
                    <span className="source-icon">🎬</span>
                    <div className="source-info">
                        <span className="source-name">VIDEO FILE</span>
                        <span className="source-detail">RTSP / MP4</span>
                    </div>
                </button>

                <div className="toggle-divider"></div>

                <button
                    className={`source-btn ${isCamera ? 'active' : ''} ${isLoading ? 'disabled' : ''}`}
                    onClick={() => handleToggle('camera')}
                    disabled={isLoading}
                    title="Use Phone Camera"
                >
                    <span className="source-icon">📱</span>
                    <div className="source-info">
                        <span className="source-name">PHONE CAM</span>
                        <span className="source-detail">LIVE STREAM</span>
                    </div>
                </button>
            </div>

            {/* Camera URL Box - shown when camera is selected */}
            {isCamera && serverInfo && (
                <div className="camera-url-box">
                    <span className="url-label">📱 PHONE URL:</span>
                    <a
                        href={serverInfo.camera_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="camera-url"
                    >
                        {serverInfo.camera_url}
                    </a>
                    <span className="url-hint">Open on phone to stream</span>
                </div>
            )}

            {/* Error display */}
            {error && (
                <div className="toggle-error">
                    ⚠️ {error}
                </div>
            )}

            <div className="toggle-footer">
                <div className="signal-strength">
                    <span>STATE:</span>
                    <span className={`state-badge ${isIdle ? 'idle' : 'active'}`}>
                        {sourceState || 'UNKNOWN'}
                    </span>
                </div>
                <span className="source-id">
                    IP: {serverInfo?.ip || '...'}
                </span>
            </div>
        </div>
    );
};

export default InputSourceToggle;

