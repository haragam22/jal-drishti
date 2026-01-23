import React from 'react';
import '../App.css';

const StatusBar = ({ fps = 0, status = "Disconnected", visibilityScore = 0 }) => {
    const getStatusColor = (s) => {
        if (s === "Connected") return "status-connected";
        if (s === "Connecting") return "status-connecting";
        return "status-disconnected";
    };

    return (
        <div className="status-bar">
            <div className="status-brand">
                <h1 className="brand-title">
                    JAL-DRISHTI
                </h1>
                <span className="brand-version">
                    v1.0.0-RC1
                </span>
            </div>

            <div className="status-metrics">
                {/* Connection Status */}
                <div className="metric-group">
                    <span className={`status-dot ${getStatusColor(status)}`}></span>
                    <span className="status-text">{status.toUpperCase()}</span>
                </div>

                {/* Visibility Score */}
                <div className="metric-group right-align">
                    <span className="metric-label">VISIBILITY</span>
                    <span className="metric-value value-cyan">{visibilityScore.toFixed(1)}</span>
                </div>

                {/* FPS */}
                <div className="metric-group right-align">
                    <span className="metric-label">FPS</span>
                    <span className="metric-value value-green">{fps}</span>
                </div>
            </div>
        </div>
    );
};

export default StatusBar;
