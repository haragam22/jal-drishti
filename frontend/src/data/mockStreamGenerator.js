/**
 * mockStreamGenerator.js
 * 
 * Simulates an intelligent AI backend.
 * - Maintains state of tracked objects (position, velocity).
 * - Updates positions frame-by-frame.
 * - Randomly adds/removes detections.
 * - Fluctuates confidence levels.
 */

// Simulation constants
const WIDTH = 640;
const HEIGHT = 480;
const MAX_OBJECTS = 5;

// State to persist between frames (simulating backend memory)
let trackedObjects = [
    {
        id: 1,
        label: "Suspicious Object",
        x: 120, // Center x
        y: 80,  // Center y
        w: 180,
        h: 180,
        vx: 2,  // Velocity x
        vy: 1.5,// Velocity y
        confidence: 0.78
    }
];

let frameId = 0;

export const generateNextFrame = () => {
    frameId++;

    // 1. Update existing objects
    trackedObjects.forEach(obj => {
        // Move
        obj.x += obj.vx;
        obj.y += obj.vy;

        // Bounce off walls
        if (obj.x <= 0 || obj.x + obj.w >= WIDTH) obj.vx *= -1;
        if (obj.y <= 0 || obj.y + obj.h >= HEIGHT) obj.vy *= -1;

        // Fluctuate confidence slightly
        obj.confidence += (Math.random() - 0.5) * 0.05;
        obj.confidence = Math.max(0.3, Math.min(0.99, obj.confidence));
    });

    // 2. Randomly add new object
    if (trackedObjects.length < MAX_OBJECTS && Math.random() > 0.98) {
        trackedObjects.push({
            id: Date.now(),
            label: Math.random() > 0.5 ? "Person" : "Bag",
            x: Math.random() * (WIDTH - 100),
            y: Math.random() * (HEIGHT - 100),
            w: 80 + Math.random() * 50,
            h: 100 + Math.random() * 80,
            vx: (Math.random() - 0.5) * 4,
            vy: (Math.random() - 0.5) * 4,
            confidence: 0.5
        });
    }

    // 3. Randomly remove object
    if (trackedObjects.length > 0 && Math.random() > 0.99) {
        trackedObjects.shift();
    }

    // 4. Construct response
    const detections = trackedObjects.map(obj => ({
        label: obj.label,
        confidence: parseFloat(obj.confidence.toFixed(2)),
        // bbox expected format: [x, y, w, h]
        bbox: [Math.floor(obj.x), Math.floor(obj.y), Math.floor(obj.w), Math.floor(obj.h)]
    }));

    // Simulate global visibility
    const visibility = 130 + Math.sin(frameId / 10) * 10;

    return {
        status: "success",
        frame_id: frameId,
        // Using a placeholder that changes slightly to force browser img reload if needed, 
        // though for this task we use static src mostly. 
        // Ideally, image_data would be a base64 string in a real app or a blob URL.
        image_data: `https://placehold.co/640x480/222/FFF?text=Enhanced+Frame+${frameId}`,
        detections: detections,
        visibility_score: parseFloat(visibility.toFixed(1))
    };
};
