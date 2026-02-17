import React, { useState, useEffect } from 'react';

/**
 * SonarTemporalGraph Component
 * Shows distance over time (last 10 seconds)
 */
const SonarTemporalGraph = () => {
    const [dataPoints, setDataPoints] = useState([]);

    // Generate realistic approaching trend
    useEffect(() => {
        const initialDistance = 140;
        const points = Array.from({ length: 10 }, (_, i) => ({
            time: i,
            distance: initialDistance - (i * 2) + Math.random() * 3 // Approaching with noise
        }));
        setDataPoints(points);

        // Animate new points
        const interval = setInterval(() => {
            setDataPoints(prev => {
                const newPoints = [...prev.slice(1)];
                const lastDistance = prev[prev.length - 1].distance;
                newPoints.push({
                    time: prev[prev.length - 1].time + 1,
                    distance: Math.max(100, lastDistance - 2 + Math.random() * 3)
                });
                return newPoints;
            });
        }, 1000);

        return () => clearInterval(interval);
    }, []);

    const width = 400;
    const height = 120;
    const padding = 30;
    const graphWidth = width - padding * 2;
    const graphHeight = height - padding * 2;

    // Scale distance to Y coordinate
    const scaleY = (distance) => {
        const minDist = 100;
        const maxDist = 150;
        return height - padding - ((distance - minDist) / (maxDist - minDist)) * graphHeight;
    };

    // Scale time to X coordinate
    const scaleX = (index) => {
        return padding + (index / 9) * graphWidth;
    };

    // Generate path
    const pathData = dataPoints.map((point, idx) => {
        const x = scaleX(idx);
        const y = scaleY(point.distance);
        return idx === 0 ? `M ${x} ${y}` : `L ${x} ${y}`;
    }).join(' ');

    return (
        <div style={{
            background: '#0A0A0A',
            border: '1px solid #262626',
            borderRadius: '8px',
            padding: '16px',
            width: '100%'
        }}>
            <div style={{ marginBottom: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '11px', fontWeight: '700', color: '#A3A3A3', letterSpacing: '0.05em' }}>
                    TEMPORAL ANALYSIS
                </span>
                <span style={{ fontSize: '10px', color: '#22C55E', fontWeight: '600' }}>
                    ↓ APPROACHING
                </span>
            </div>

            <svg width={width} height={height}>
                {/* Grid lines */}
                {[100, 110, 120, 130, 140, 150].map(dist => {
                    const y = scaleY(dist);
                    return (
                        <g key={dist}>
                            <line
                                x1={padding}
                                y1={y}
                                x2={width - padding}
                                y2={y}
                                stroke="#262626"
                                strokeWidth="1"
                                opacity="0.3"
                            />
                            <text
                                x={padding - 5}
                                y={y + 3}
                                fill="#737373"
                                fontSize="9"
                                textAnchor="end"
                            >
                                {dist}m
                            </text>
                        </g>
                    );
                })}

                {/* Area fill */}
                <path
                    d={`${pathData} L ${width - padding} ${height - padding} L ${padding} ${height - padding} Z`}
                    fill="#22C55E"
                    fillOpacity="0.1"
                />

                {/* Line */}
                <path
                    d={pathData}
                    fill="none"
                    stroke="#22C55E"
                    strokeWidth="2"
                    opacity="0.8"
                />

                {/* Data points */}
                {dataPoints.map((point, idx) => {
                    const x = scaleX(idx);
                    const y = scaleY(point.distance);
                    return (
                        <circle
                            key={idx}
                            cx={x}
                            cy={y}
                            r="3"
                            fill="#22C55E"
                            opacity={idx === dataPoints.length - 1 ? 1 : 0.5}
                        />
                    );
                })}

                {/* Axes */}
                <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#404040" strokeWidth="1" />
                <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="#404040" strokeWidth="1" />

                {/* X-axis label */}
                <text x={width / 2} y={height - 5} fill="#737373" fontSize="9" textAnchor="middle">
                    Time (seconds)
                </text>
            </svg>
        </div>
    );
};

export default SonarTemporalGraph;
