import React, { useState, useEffect } from 'react';

/**
 * ThermalHeatmap Component
 * Grid-based thermal visualization with warm zones
 */
const ThermalHeatmap = () => {
    const [heatData, setHeatData] = useState([]);
    const gridSize = 20; // 20x20 grid

    // Generate heatmap data
    useEffect(() => {
        const data = [];
        for (let y = 0; y < gridSize; y++) {
            for (let x = 0; x < gridSize; x++) {
                // Create 2 hot zones
                const dist1 = Math.sqrt(Math.pow(x - 8, 2) + Math.pow(y - 7, 2));
                const dist2 = Math.sqrt(Math.pow(x - 14, 2) + Math.pow(y - 13, 2));

                let intensity = 0;

                // Hot zone 1 (stronger)
                if (dist1 < 4) {
                    intensity = Math.max(intensity, 0.8 - (dist1 / 4) * 0.5);
                }

                // Hot zone 2 (weaker)
                if (dist2 < 3) {
                    intensity = Math.max(intensity, 0.6 - (dist2 / 3) * 0.4);
                }

                // Add some noise
                intensity += Math.random() * 0.1;

                data.push({
                    x,
                    y,
                    intensity: Math.min(1, Math.max(0, intensity))
                });
            }
        }
        setHeatData(data);
    }, []);

    // Get color based on intensity
    const getColor = (intensity) => {
        if (intensity < 0.15) return '#0A1628'; // Dark blue (cool)
        if (intensity < 0.3) return '#1E3A5F'; // Navy
        if (intensity < 0.5) return '#F97316'; // Orange
        if (intensity < 0.7) return '#FB923C'; // Light orange
        return '#EF4444'; // Red (hot)
    };

    const cellSize = 20;
    const width = gridSize * cellSize;
    const height = gridSize * cellSize;

    return (
        <div style={{
            background: '#0A0A0A',
            border: '1px solid #262626',
            borderRadius: '8px',
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '12px'
        }}>
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                width: '100%',
                marginBottom: '8px'
            }}>
                <span style={{ fontSize: '11px', fontWeight: '700', color: '#A3A3A3', letterSpacing: '0.05em' }}>
                    THERMAL SIGNATURE MAP
                </span>
                <span style={{ fontSize: '10px', color: '#F97316', fontWeight: '600' }}>
                    2 ANOMALIES DETECTED
                </span>
            </div>

            <div style={{
                position: 'relative',
                width: `${width}px`,
                height: `${height}px`,
                border: '1px solid #404040',
                borderRadius: '4px',
                overflow: 'hidden'
            }}>
                <svg width={width} height={height}>
                    {heatData.map((cell, idx) => (
                        <rect
                            key={idx}
                            x={cell.x * cellSize}
                            y={cell.y * cellSize}
                            width={cellSize}
                            height={cellSize}
                            fill={getColor(cell.intensity)}
                            opacity={0.9}
                        >
                            <animate
                                attributeName="opacity"
                                values="0.9;0.95;0.9"
                                dur={`${2 + Math.random()}s`}
                                repeatCount="indefinite"
                            />
                        </rect>
                    ))}

                    {/* Grid overlay */}
                    {Array.from({ length: gridSize + 1 }).map((_, i) => (
                        <g key={i}>
                            <line
                                x1={i * cellSize}
                                y1={0}
                                x2={i * cellSize}
                                y2={height}
                                stroke="#262626"
                                strokeWidth="0.5"
                                opacity="0.3"
                            />
                            <line
                                x1={0}
                                y1={i * cellSize}
                                x2={width}
                                y2={i * cellSize}
                                stroke="#262626"
                                strokeWidth="0.5"
                                opacity="0.3"
                            />
                        </g>
                    ))}

                    {/* Hot zone markers */}
                    <circle cx={8 * cellSize + cellSize / 2} cy={7 * cellSize + cellSize / 2} r="30" fill="none" stroke="#EF4444" strokeWidth="2" opacity="0.6">
                        <animate attributeName="r" values="30;35;30" dur="2s" repeatCount="indefinite" />
                    </circle>
                    <circle cx={14 * cellSize + cellSize / 2} cy={13 * cellSize + cellSize / 2} r="20" fill="none" stroke="#F97316" strokeWidth="2" opacity="0.6">
                        <animate attributeName="r" values="20;25;20" dur="2s" repeatCount="indefinite" />
                    </circle>
                </svg>

                {/* Crosshair */}
                <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: '40px',
                    height: '40px',
                    border: '1px solid #22C55E',
                    borderRadius: '50%',
                    opacity: 0.3,
                    pointerEvents: 'none'
                }} />
            </div>

            {/* Temperature Scale */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                width: '100%',
                marginTop: '8px'
            }}>
                <span style={{ fontSize: '9px', color: '#737373', fontWeight: '600' }}>TEMP SCALE:</span>
                <div style={{
                    flex: 1,
                    height: '12px',
                    background: 'linear-gradient(to right, #0A1628, #1E3A5F, #F97316, #FB923C, #EF4444)',
                    borderRadius: '2px',
                    border: '1px solid #262626'
                }} />
                <div style={{ display: 'flex', gap: '12px', fontSize: '9px', color: '#737373' }}>
                    <span>12°C</span>
                    <span style={{ color: '#F97316' }}>18°C</span>
                    <span style={{ color: '#EF4444' }}>24°C</span>
                </div>
            </div>
        </div>
    );
};

export default ThermalHeatmap;
