import React from 'react';
import '../App.css';

const AlertPanel = ({ detections = [] }) => {
    const getBadgeClass = (confidence) => {
        if (confidence > 0.75) return "badge-red";
        if (confidence >= 0.4) return "badge-yellow";
        return "badge-green";
    };

    return (
        <div className="alert-panel">
            <div className="alert-header">
                <h3 className="alert-title">
                    {/* Simple SVG icon inline */}
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ marginRight: '8px', color: '#ef4444' }}>
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    Active Alerts
                </h3>
                <span className="alert-count">{detections.length} Events</span>
            </div>

            <div className="alert-list custom-scrollbar">
                {detections.length === 0 ? (
                    <div className="alert-empty">No active threats detected.</div>
                ) : (
                    detections.map((det, index) => (
                        <div key={index} className="alert-item">
                            <div className="alert-info">
                                <span className="alert-id">#{String(index + 1).padStart(3, '0')}</span>
                                <span className="alert-label">{det.label}</span>
                            </div>

                            <div className="alert-meta">
                                <span className="alert-coords">
                                    [{det.bbox.join(', ')}]
                                </span>
                                <span className={`alert-badge ${getBadgeClass(det.confidence)}`}>
                                    {(det.confidence * 100).toFixed(0)}%
                                </span>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default AlertPanel;
