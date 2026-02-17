import React from 'react';
import ThermalHeatmap from '../components/ThermalHeatmap';

/**
 * Infrared Analysis Console
 * Mid-range thermal confirmation analysis
 */
const Infrared = () => {
    // Hardcoded realistic IR metrics
    const metrics = {
        heatDelta: 6.4,
        backgroundTemp: 12,
        irConfidence: 64,
        signatureType: 'Metallic Anomaly',
        thermalStability: 'CONSISTENT'
    };

    // Correlation data
    const correlation = {
        sonarDetection: true,
        distance: 120,
        syncStatus: 'ALIGNED',
        riskContribution: 30
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
                    🌡️ INFRARED THERMAL ANALYSIS
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
                    MID-RANGE CONFIRMATION
                </div>
            </div>

            {/* Main Layout */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 350px',
                gap: '20px',
                marginBottom: '20px'
            }}>
                {/* Left: Thermal Heatmap */}
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-start' }}>
                    <ThermalHeatmap />
                </div>

                {/* Right: IR Metrics Panel */}
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
                        IR METRICS
                    </div>

                    {/* Metric Items */}
                    <MetricItem
                        label="Heat Delta"
                        value={`+${metrics.heatDelta}°C`}
                        color="#F97316"
                    />
                    <MetricItem
                        label="Background Temp"
                        value={`${metrics.backgroundTemp}°C`}
                        color="#6B7280"
                    />
                    <MetricItem
                        label="IR Confidence"
                        value={`${metrics.irConfidence}%`}
                        color="#F97316"
                        bar={metrics.irConfidence / 100}
                    />
                    <MetricItem
                        label="Signature Type"
                        value={metrics.signatureType}
                        color="#FB923C"
                    />
                    <MetricItem
                        label="Thermal Stability"
                        value={metrics.thermalStability}
                        color="#22C55E"
                    />

                    {/* Thermal Zones */}
                    <div style={{ marginTop: '10px' }}>
                        <div style={{
                            fontSize: '11px',
                            fontWeight: '700',
                            color: '#737373',
                            marginBottom: '8px',
                            letterSpacing: '0.05em'
                        }}>
                            DETECTED ZONES
                        </div>

                        <div style={{
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
                                    Zone Alpha
                                </span>
                                <span style={{ color: '#EF4444', fontWeight: '700' }}>
                                    HIGH
                                </span>
                            </div>
                            <div style={{ color: '#737373', fontSize: '9px' }}>
                                Temp: 18.4°C • Size: 2.3m²
                            </div>
                        </div>

                        <div style={{
                            background: '#0A0A0A',
                            padding: '8px 10px',
                            borderRadius: '4px',
                            border: '1px solid #262626',
                            fontSize: '10px'
                        }}>
                            <div style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                marginBottom: '4px'
                            }}>
                                <span style={{ color: '#E5E5E5', fontWeight: '600' }}>
                                    Zone Beta
                                </span>
                                <span style={{ color: '#F97316', fontWeight: '700' }}>
                                    MEDIUM
                                </span>
                            </div>
                            <div style={{ color: '#737373', fontSize: '9px' }}>
                                Temp: 16.2°C • Size: 1.8m²
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Bottom: Correlation Panel */}
            <div style={{
                background: '#121212',
                border: '1px solid #262626',
                borderRadius: '8px',
                padding: '20px'
            }}>
                <div style={{
                    fontSize: '12px',
                    fontWeight: '700',
                    color: '#A3A3A3',
                    letterSpacing: '0.05em',
                    marginBottom: '16px',
                    borderBottom: '1px solid #262626',
                    paddingBottom: '10px'
                }}>
                    MULTI-SENSOR CORRELATION
                </div>

                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(4, 1fr)',
                    gap: '20px'
                }}>
                    <CorrelationItem
                        label="Sonar Detection"
                        value={correlation.sonarDetection ? 'YES' : 'NO'}
                        color={correlation.sonarDetection ? '#22C55E' : '#737373'}
                        icon="📡"
                    />
                    <CorrelationItem
                        label="Distance Match"
                        value={`${correlation.distance}m`}
                        color="#6B7280"
                        icon="📏"
                    />
                    <CorrelationItem
                        label="Sync Status"
                        value={correlation.syncStatus}
                        color="#22C55E"
                        icon="🔗"
                    />
                    <CorrelationItem
                        label="Risk Contribution"
                        value={`+${correlation.riskContribution}%`}
                        color="#F97316"
                        icon="⚠️"
                    />
                </div>

                <div style={{
                    marginTop: '16px',
                    padding: '10px 12px',
                    background: 'rgba(249, 115, 22, 0.1)',
                    border: '1px solid rgba(249, 115, 22, 0.2)',
                    borderRadius: '6px',
                    fontSize: '11px',
                    color: '#FB923C'
                }}>
                    <strong>ANALYSIS:</strong> Thermal signature correlates with sonar detection at 120m.
                    Metallic heat pattern suggests mechanical object. Combined confidence elevated to SUSPICION level.
                </div>
            </div>
        </div>
    );
};

// Helper component for metrics
const MetricItem = ({ label, value, color, bar }) => (
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

// Helper component for correlation items
const CorrelationItem = ({ label, value, color, icon }) => (
    <div style={{
        background: '#0A0A0A',
        padding: '12px',
        borderRadius: '6px',
        border: '1px solid #262626',
        textAlign: 'center'
    }}>
        <div style={{ fontSize: '20px', marginBottom: '6px' }}>{icon}</div>
        <div style={{ fontSize: '9px', color: '#737373', marginBottom: '4px', fontWeight: '600' }}>
            {label}
        </div>
        <div style={{ fontSize: '13px', color: color, fontWeight: '700', fontFamily: 'monospace' }}>
            {value}
        </div>
    </div>
);

export default Infrared;
