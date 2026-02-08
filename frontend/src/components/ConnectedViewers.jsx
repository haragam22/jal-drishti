import React, { useState, useEffect, useCallback } from 'react';
import { API_BASE_URL } from '../constants';
import '../App.css';

/**
 * ConnectedViewers Component
 * 
 * PHASE-3 CORE: Operator panel for managing connected viewers.
 * - Shows list of connected dashboards
 * - Toggle allow/block per viewer
 * - Blocked viewers stay connected but receive no frames
 */
const ConnectedViewers = ({ isOperator = true }) => {
    const [viewers, setViewers] = useState([]);
    const [stats, setStats] = useState({ total: 0, allowed: 0, blocked: 0 });
    const [isLoading, setIsLoading] = useState(false);
    const [isExpanded, setIsExpanded] = useState(false);

    // Fetch connected viewers
    const fetchViewers = useCallback(async () => {
        if (!isOperator) return;

        try {
            const res = await fetch(`${API_BASE_URL}/api/viewers/connected`);
            if (res.ok) {
                const data = await res.json();
                setViewers(data.viewers || []);
                setStats({
                    total: data.total || 0,
                    allowed: data.allowed || 0,
                    blocked: data.blocked || 0
                });
            }
        } catch (err) {
            console.warn('[ConnectedViewers] Failed to fetch:', err);
        }
    }, [isOperator]);

    // Poll for updates every 5s
    useEffect(() => {
        fetchViewers();
        const interval = setInterval(fetchViewers, 5000);
        return () => clearInterval(interval);
    }, [fetchViewers]);

    // Toggle viewer permission
    const toggleViewer = async (viewerId, currentlyAllowed) => {
        setIsLoading(true);
        try {
            const endpoint = currentlyAllowed ? 'revoke' : 'allow';
            const res = await fetch(`${API_BASE_URL}/api/viewers/${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ viewer_id: viewerId })
            });

            if (res.ok) {
                // Refresh list
                await fetchViewers();
            }
        } catch (err) {
            console.error('[ConnectedViewers] Toggle error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    // Only show for operators
    if (!isOperator) return null;

    // Get device label (truncate viewer_id for display)
    const getDisplayLabel = (viewer) => {
        if (viewer.label && viewer.label !== 'Unknown Device') {
            return viewer.label;
        }
        return `Device ${viewer.viewer_id.slice(-6)}`;
    };

    return (
        <div className="connected-viewers-container">
            <div
                className="viewers-header"
                onClick={() => setIsExpanded(!isExpanded)}
                style={{ cursor: 'pointer' }}
            >
                <span className="viewers-icon">👥</span>
                <span className="viewers-title">CONNECTED VIEWERS</span>
                <span className="viewers-count">{stats.total}</span>
                <span className={`expand-arrow ${isExpanded ? 'expanded' : ''}`}>▼</span>
            </div>

            {isExpanded && (
                <div className="viewers-content">
                    {viewers.length === 0 ? (
                        <div className="viewers-empty">
                            No viewers connected
                        </div>
                    ) : (
                        <div className="viewers-list">
                            {viewers.map((viewer) => (
                                <div
                                    key={viewer.viewer_id}
                                    className={`viewer-item ${viewer.allowed ? 'allowed' : 'blocked'}`}
                                >
                                    <span className="viewer-status-icon">
                                        {viewer.allowed ? '✔️' : '❌'}
                                    </span>
                                    <span className="viewer-label">
                                        {getDisplayLabel(viewer)}
                                    </span>
                                    <button
                                        className={`viewer-toggle-btn ${viewer.allowed ? 'block' : 'allow'}`}
                                        onClick={() => toggleViewer(viewer.viewer_id, viewer.allowed)}
                                        disabled={isLoading}
                                        title={viewer.allowed ? 'Block this viewer' : 'Allow this viewer'}
                                    >
                                        {viewer.allowed ? 'BLOCK' : 'ALLOW'}
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}

                    <div className="viewers-stats">
                        <span className="stat">
                            <span className="stat-label">Allowed:</span>
                            <span className="stat-value allowed">{stats.allowed}</span>
                        </span>
                        <span className="stat">
                            <span className="stat-label">Blocked:</span>
                            <span className="stat-value blocked">{stats.blocked}</span>
                        </span>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ConnectedViewers;
