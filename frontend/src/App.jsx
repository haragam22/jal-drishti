import React, { useState, useEffect } from 'react';
import StatusBar from './components/StatusBar';
import VideoPanel from './components/VideoPanel';
import AlertPanel from './components/AlertPanel';
import useLiveStream from './hooks/useLiveStream';
import './App.css';

function App() {
  const { frame, fps, isConnected } = useLiveStream();

  // If waiting for first frame, show loading or initial state
  const currentFrame = frame || {
    detections: [],
    visibility_score: 0,
    image_data: null
  };

  return (
    <div className="app-container">
      <StatusBar
        fps={fps}
        status={isConnected ? "Connected" : "Disconnected"}
        visibilityScore={currentFrame.visibility_score}
      />

      <main className="main-content">
        <VideoPanel
          title="Raw Feed"
          imageSrc="https://placehold.co/640x480/333/FFF?text=Raw+Feed"
          isEnhanced={false}
        />
        <VideoPanel
          title="Enhanced Feed"
          imageSrc={currentFrame.image_data}
          detections={currentFrame.detections}
          isEnhanced={true}
        />
      </main>

      <AlertPanel detections={currentFrame.detections} />
    </div>
  );
}

export default App;
