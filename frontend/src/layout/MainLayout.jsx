import React, { useState } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import StatusBar from '../components/StatusBar';
import ConnectionOverlay from '../components/ConnectionOverlay';
import '../App.css';

// Import StreamContext consumption
import { useStream } from '../context/StreamContext';

const MainLayout = () => {
    const {
        frame,
        fps,
        connectionStatus,
        reconnectAttempt,
        manualReconnect,
        systemStatus,
        lastValidFrame
    } = useStream();

    const [inputSource, setInputSource] = useState('video'); // Managed here or context if global
    // Note: If InputSourceToggle needs to be global, we might need to lift this state to Context
    // For now, keeping visual state here, but real source state is in backend/Context.

    const location = useLocation();

    // Determine display frame
    const displayFrame = frame || lastValidFrame || {
        state: 'SAFE_MODE',
        max_confidence: 0,
        detections: [],
        image_data: null,
        system: { fps: null, latency_ms: null },
        risk_score: 0
    };

    // Helper for active link class
    const getLinkClass = ({ isActive }) =>
        `nav-item ${isActive ? 'active' : ''}`;

    return (
        <div className={`app-container ${systemStatus.inSafeMode ? 'safe-mode-active' : ''}`}>

            {/* Status Bar - Persistent across pages */}
            <StatusBar
                systemState={displayFrame.state}
                maxConfidence={displayFrame.max_confidence}
                latencyMs={displayFrame.system?.latency_ms}
                renderFps={fps}
                mlFps={displayFrame.system?.fps}
                connectionStatus={connectionStatus}
                inputSource={inputSource} // Visual only for now
                uptime="00:00:00" // Todo: Lift uptime state if needed globally
            />

            <div className="main-content-wrapper" style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>

                {/* Sidebar Navigation */}
                <nav className="sidebar-nav" style={{
                    width: '80px',
                    background: '#0D0D0D',
                    borderRight: '1px solid #262626',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    paddingTop: '20px',
                    gap: '20px',
                    zIndex: 100
                }}>
                    <NavLink to="/" className={getLinkClass} title="Fusion Dashboard">
                        <span style={{ fontSize: '24px' }}>🛡️</span>
                        <span style={{ fontSize: '10px', marginTop: '4px' }}>HOME</span>
                    </NavLink>

                    <NavLink to="/sonar" className={getLinkClass} title="Sonar Analysis">
                        <span style={{ fontSize: '24px' }}>📡</span>
                        <span style={{ fontSize: '10px', marginTop: '4px' }}>SONAR</span>
                    </NavLink>

                    <NavLink to="/infrared" className={getLinkClass} title="Infrared/Thermal">
                        <span style={{ fontSize: '24px' }}>🌡️</span>
                        <span style={{ fontSize: '10px', marginTop: '4px' }}>IR</span>
                    </NavLink>

                    {/* Settings / System Health placeholder */}
                    <div style={{ marginTop: 'auto', marginBottom: '20px', opacity: 0.5 }}>
                        <span>⚙️</span>
                    </div>
                </nav>

                {/* Main Page Content */}
                <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
                    <Outlet context={{ displayFrame, systemStatus, inputSource, setInputSource }} />
                </div>
            </div>

            {/* Global Overlays */}
            <ConnectionOverlay
                connectionStatus={connectionStatus}
                reconnectAttempt={reconnectAttempt}
                onRetry={manualReconnect}
            />
        </div>
    );
};

export default MainLayout;
