import React, { useRef, useEffect } from 'react';

const DetectionOverlay = ({ detections = [], width = 640, height = 480 }) => {
    const canvasRef = useRef(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        // Clear previous frame
        ctx.clearRect(0, 0, width, height);

        detections.forEach((det) => {
            const { bbox, label, confidence } = det;
            const [x, y, w, h] = bbox;

            // Determine color based on confidence
            let color = '#22c55e'; // Green (< 0.4)
            if (confidence > 0.75) {
                color = '#ef4444'; // Red
            } else if (confidence >= 0.4) {
                color = '#eab308'; // Yellow
            }

            // Draw bounding box
            ctx.strokeStyle = color;
            ctx.lineWidth = 3;
            ctx.strokeRect(x, y, w, h);

            // Draw label background
            ctx.fillStyle = color;
            const text = `${label} ${(confidence * 100).toFixed(0)}%`;
            const textWidth = ctx.measureText(text).width;

            ctx.fillRect(x, y - 25, textWidth + 10, 25);

            // Draw text
            ctx.fillStyle = '#000000';
            ctx.font = '14px sans-serif';
            ctx.fillText(text, x + 5, y - 7);
        });

    }, [detections, width, height]);

    return (
        <canvas
            ref={canvasRef}
            width={width}
            height={height}
            className="detection-overlay"
        />
    );
};

export default DetectionOverlay;
