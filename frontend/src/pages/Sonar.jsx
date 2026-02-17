import React from 'react';
import SonarRadar from '../components/SonarRadar';
import SonarTemporalGraph from '../components/SonarTemporalGraph';

/**
 * Sonar Analysis Console
 * Defence-grade long-range sonar visualization
 */
const Sonar = () => {
    // Hardcoded realistic detection data
    const detections = [
        { distance: 120, confidence: 0.78, angle: 45, label: 'Object A' },
        { distance: 340, confidence: 0.52, angle: 280, label: 'Object B' },
        { distance: 85, confidence: 0.91, angle: 160, label: 'Object C' }
    ];

    const metrics = {
        strongestDetection: 120,
        signalStrength: 0.82,
        noiseLevel: 0.21,
        sonarConfidence: 78,
        objectStability: 'STABLE',
        relativeMovement: 'APPROACHING'
    };

    return (
        <div style={{
            height: '100%',
            padding: '20px',
            overflowY: 'auto',
            background: '#0A0A0A'
        }}>
            {/* Header */}
            <div style={{
                marginBottom: '20px',
                borderBottom: '1px solid #262626',
                paddingBottom: '12px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <h1 style={{
                    color: '#E5E5E5',
                    margin: 0,
                    fontSize: '20px',
                    fontWeight: '700',
                    letterSpacing: '0.05em'
                }}>
                    📡 LONG-RANGE SONAR ANALYSIS
                </h1>

                {/* Status Badge */}
                <div style={{
                    background: 'rgba(249, 115, 22, 0.15)',
                    color: '#F97316',
                    border: '1px solid rgba(249, 115, 22, 0.3)',
                    padding: '6px 14px',
                    borderRadius: '6px',
                    fontSize: '11px',
                    fontWeight: '700',
                    letterSpacing: '0.05em'
                }}>
                    EARLY SUSPICION
                </div>
            </div>

            {/* Main Layout */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 350px',
                gap: '20px',
                marginBottom: '20px'
            }}>
                {/* Left: Radar */}
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                    <SonarRadar detections={detections} />
                </div>

                {/* Right: Metrics Panel */}
                <div style={{
                    background: '#121212',
                    border: '1px solid #262626',
                    borderRadius: '8px',
                    padding: '20px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '16px'
                }}>
                    <div style={{
                        fontSize: '12px',
                        fontWeight: '700',
                        color: '#A3A3A3',
                        letterSpacing: '0.05em',
                        borderBottom: '1px solid #262626',
                        paddingBottom: '10px'
                    }}>
                        SONAR METRICS
                    </div>

                    {/* Metric Items */}
                    <MetricItem
                        label="Strongest Detection"
                        value={`${metrics.strongestDetection}m`}
                        color="#EF4444"
                    />
                    <MetricItem
                        label="Signal Strength"
                        value={(metrics.signalStrength * 100).toFixed(0) + '%'}
                        color="#22C55E"
                        bar={metrics.signalStrength}
                    />
                    <MetricItem
                        label="Noise Level"
                        value={(metrics.noiseLevel * 100).toFixed(0) + '%'}
                        color="#737373"
                        bar={metrics.noiseLevel}
                    />
                    <MetricItem
                        label="Sonar Confidence"
                        value={`${metrics.sonarConfidence}%`}
                        color="#F97316"
                    />
                    <MetricItem
                        label="Object Stability"
                        value={metrics.objectStability}
                        color="#22C55E"
                    />
                    <MetricItem
                        label="Relative Movement"
                        value={metrics.relativeMovement}
                        color="#F97316"
                        icon="↓"
                    />

                    {/* Detection List */}
                    <div style={{ marginTop: '10px' }}>
                        <div style={{
                            fontSize: '11px',
                            fontWeight: '700',
                            color: '#737373',
                            marginBottom: '8px',
                            letterSpacing: '0.05em'
                        }}>
                            ACTIVE DETECTIONS
                        </div>
                        {detections.map((det, idx) => (
                            <div key={idx} style={{
                                background: '#0A0A0A',
                                padding: '8px 10px',
                                borderRadius: '4px',
                                marginBottom: '6px',
                                border: '1px solid #262626',
                                fontSize: '10px'
                            }}>
                                <div style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    marginBottom: '4px'
                                }}>
                                    <span style={{ color: '#E5E5E5', fontWeight: '600' }}>
                                        {det.label || `Object ${idx + 1}`}
                                    </span>
                                    <span style={{
                                        color: det.confidence > 0.8 ? '#EF4444' : det.confidence > 0.6 ? '#F97316' : '#22C55E',
                                        fontWeight: '700'
                                    }}>
                                        {(det.confidence * 100).toFixed(0)}%
                                    </span>
                                </div>
                                <div style={{ color: '#737373', fontSize: '9px' }}>
                                    Range: {det.distance}m • Bearing: {det.angle}°
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Bottom: Temporal Graph */}
            <SonarTemporalGraph />
        </div>
    );
};

// Helper component for metrics
const MetricItem = ({ label, value, color, bar, icon }) => (
    <div>
        <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginBottom: '4px'
        }}>
            <span style={{ fontSize: '10px', color: '#737373', fontWeight: '600' }}>
                {label}
            </span>
            <span style={{
                fontSize: '12px',
                color: color || '#E5E5E5',
                fontWeight: '700',
                fontFamily: 'monospace'
            }}>
                {icon && <span style={{ marginRight: '4px' }}>{icon}</span>}
                {value}
            </span>
        </div>
        {bar !== undefined && (
            <div style={{
                height: '4px',
                background: '#262626',
                borderRadius: '2px',
                overflow: 'hidden'
            }}>
                <div style={{
                    height: '100%',
                    width: `${bar * 100}%`,
                    background: color,
                    transition: 'width 0.3s ease'
                }} />
            </div>
        )}
    </div>
);

export default Sonar;
