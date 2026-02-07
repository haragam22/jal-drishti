import React, { useState, useCallback } from 'react';
import { FUSION_STATE_COLORS } from '../constants';
import '../App.css';

/**
 * OperatorActionPanel Component (MILESTONE-4)
 * 
 * Provides explicit operator action controls.
 * AI suggests, operator decides.
 * Every decision is logged.
 * 
 * Key Principle: A system with logged human decisions is deployable.
 */

const PRIORITY_COLORS = {
    LOW: '#22C55E',
    MEDIUM: '#3B82F6',
    HIGH: '#F97316',
    CRITICAL: '#EF4444'
};

const PRIORITY_ICONS = {
    LOW: '🟢',
    MEDIUM: '🔵',
    HIGH: '🟠',
    CRITICAL: '🔴'
};

const OperatorActionPanel = ({
    threatPriority = 'LOW',
    signature = '',
    riskScore = 0,
    fusionState = 'NORMAL',
    seenBefore = false,
    occurrenceCount = 0,
    explainability = [],
    onDecision = () => { },
    isActive = false  // Only show actions when there's an alert
}) => {
    const [lastAction, setLastAction] = useState(null);
    const [actionTime, setActionTime] = useState(null);

    const handleAction = useCallback((action) => {
        const decision = {
            action,
            signature,
            timestamp: new Date().toISOString(),
            riskScore,
            threatPriority,
            fusionState
        };

        setLastAction(action);
        setActionTime(new Date().toLocaleTimeString());
        onDecision(decision);
    }, [signature, riskScore, threatPriority, fusionState, onDecision]);

    const riskPercent = Math.round(riskScore * 100);
    const priorityColor = PRIORITY_COLORS[threatPriority] || PRIORITY_COLORS.LOW;
    const priorityIcon = PRIORITY_ICONS[threatPriority] || PRIORITY_ICONS.LOW;

    // Only show full panel when there's an active alert
    const showActions = fusionState !== 'NORMAL' && riskPercent > 15;

    return (
        <div className="operator-panel-container">
            {/* Header */}
            <div className="operator-panel-header">
                <span className="panel-icon">👤</span>
                <span className="panel-title">OPERATOR DECISION</span>
                <span
                    className="priority-badge"
                    style={{ backgroundColor: `${priorityColor}20`, color: priorityColor }}
                >
                    {priorityIcon} {threatPriority}
                </span>
            </div>

            {/* Context Section */}
            <div className="operator-context">
                {seenBefore && (
                    <div className="context-alert">
                        ⚠️ Similar object detected {occurrenceCount} times recently
                    </div>
                )}

                {/* Explainability - "Why this alert?" */}
                {explainability.length > 0 && (
                    <div className="explainability-section">
                        <div className="explainability-title">Why this alert?</div>
                        <ul className="explainability-list">
                            {explainability.map((reason, idx) => (
                                <li key={idx}>• {reason}</li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>

            {/* Action Buttons */}
            {showActions ? (
                <div className="action-buttons">
                    <button
                        className="action-btn confirm"
                        onClick={() => handleAction('CONFIRM_THREAT')}
                    >
                        ✅ Confirm Threat
                    </button>
                    <button
                        className="action-btn dismiss"
                        onClick={() => handleAction('DISMISS_ALERT')}
                    >
                        ❌ Dismiss
                    </button>
                    <button
                        className="action-btn unknown"
                        onClick={() => handleAction('MARK_UNKNOWN')}
                    >
                        🏷️ Unknown
                    </button>
                    <button
                        className="action-btn monitor"
                        onClick={() => handleAction('MONITOR_ONLY')}
                    >
                        ⏸️ Monitor
                    </button>
                </div>
            ) : (
                <div className="no-action-needed">
                    <span className="idle-icon">✓</span>
                    <span>No action required</span>
                </div>
            )}

            {/* Last Decision Footer */}
            {lastAction && (
                <div className="last-decision">
                    <span className="decision-label">Last Decision:</span>
                    <span className="decision-value">{lastAction.replace('_', ' ')}</span>
                    <span className="decision-time">at {actionTime}</span>
                </div>
            )}

            {/* Accountability Footer */}
            <div className="accountability-footer">
                <span className="footer-text">
                    AI suggests • Operator decides • All actions logged
                </span>
            </div>
        </div>
    );
};

export default OperatorActionPanel;
