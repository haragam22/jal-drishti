import React from 'react';
import DetectionOverlay from './DetectionOverlay';
import '../App.css';

const VideoPanel = ({ title, imageSrc, detections, isEnhanced = false }) => {
    return (
        <div className="video-panel">
            <div className="video-header">
                <h3 className="video-title">{title}</h3>
                {isEnhanced && <span className="badge-live">LIVE AI</span>}
            </div>

            <div className="video-content">
                {/* Feed Image */}
                <img
                    src={imageSrc || "https://placehold.co/640x480/111/FFF?text=No+Signal"}
                    alt={title}
                    className="video-feed"
                />

                {/* Overlay - Only if Enhanced */}
                {isEnhanced && detections && (
                    <DetectionOverlay
                        detections={detections}
                        width={640} // Intrinsic resolution assumption
                        height={480}
                    />
                )}
            </div>
        </div>
    );
};

export default VideoPanel;
