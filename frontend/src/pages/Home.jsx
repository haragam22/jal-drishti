import React, { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import RawFeedPanel from '../components/RawFeedPanel';
import SafeModeOverlay from '../components/SafeModeOverlay';
import DetectionOverlay from '../components/DetectionOverlay';
import MaximizedPanel from '../components/MaximizedPanel';
import AlertPanel from '../components/AlertPanel';
import MetricsPanel from '../components/MetricsPanel';
import RiskScoreCircle from '../components/RiskScoreCircle';
import SensorStatusPanel from '../components/SensorStatusPanel';
import InputSourceToggle from '../components/InputSourceToggle';
import LastAlertSnapshot from '../components/LastAlertSnapshot';
import ConnectedViewers from '../components/ConnectedViewers';
import OperatorActionPanel from '../components/OperatorActionPanel';
import EventTimeline from '../components/EventTimeline';
import SnapshotModal from '../components/SnapshotModal';
import { useStream } from '../context/StreamContext';

const Home = () => {
    // Access global stream data + layout context
    const {
        addEvent,
        events,
        systemStatus,
        fps,
        connectionStatus
    } = useStream();

    const { displayFrame, inputSource, setInputSource } = useOutletContext();

    // Local UI state
    const [maximizedPanel, setMaximizedPanel] = useState(null);
    const [snapshotModal, setSnapshotModal] = useState({
        isOpen: false,
        imageData: null,
        timestamp: '',
        alertType: ''
    });
    const [lastAlertSnapshot, setLastAlertSnapshot] = useState(null);

    // Handlers
    const handleCaptureSnapshot = (e) => {
        e?.stopPropagation();
        if (displayFrame.image_data) {
            setSnapshotModal({
                isOpen: true,
                imageData: displayFrame.image_data,
                timestamp: new Date().toLocaleString(),
                alertType: displayFrame.state
            });
        }
    };

    return (
        <div className="home-dashboard" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div className="main-content" style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>

                {/* --- COLUMN 1: LEFT SIDEBAR (Controls) --- */}
                <div className="left-sidebar" style={{ width: '280px', display: 'flex', flexDirection: 'column', gap: '10px', padding: '10px', overflowY: 'auto' }}>
                    <SensorStatusPanel
                        sensors={displayFrame.sensors}
                        fusionState={displayFrame.fusion_state}
                        fusionMessage={displayFrame.fusion_message}
                        timelineMessages={displayFrame.timeline_messages}
                    />
                    <InputSourceToggle
                        currentSource={inputSource}
                        sourceState={displayFrame.sourceState || 'IDLE'}
                        onToggle={(source, state) => setInputSource(source)}
                    />
                    <LastAlertSnapshot snapshot={lastAlertSnapshot} />
                </div>

                {/* --- COLUMN 2: CENTER DASHBOARD (2x2 Grid) --- */}
                <div className="center-dashboard" style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '10px', padding: '10px', minWidth: 0 }}>

                    {/* TOP ROW: VIDEOS */}
                    <div className="video-grid-row" style={{ display: 'flex', gap: '10px', flex: 1, minHeight: 0 }}>
                        {/* Raw Feed Panel */}
                        <div className="video-panel clickable" onClick={() => setMaximizedPanel('raw')} style={{ flex: 1, position: 'relative', background: '#000', borderRadius: '8px', overflow: 'hidden' }}>
                            <div className="video-header" style={{ position: 'absolute', top: 0, left: 0, right: 0, padding: '8px', background: 'rgba(0,0,0,0.7)', zIndex: 10, display: 'flex', justifyContent: 'space-between' }}>
                                <h3 style={{ margin: 0, fontSize: '12px', color: '#fff' }}>Raw Feed (Sensor)</h3>
                                <button className="expand-btn">⛶</button>
                            </div>
                            <div className="video-content" style={{ width: '100%', height: '100%' }}>
                                <RawFeedPanel />
                                <SafeModeOverlay isActive={systemStatus.inSafeMode} message={systemStatus.message} cause={systemStatus.cause} />
                            </div>
                        </div>

                        {/* Enhanced Feed Panel */}
                        <div className="video-panel clickable" onClick={() => setMaximizedPanel('enhanced')} style={{ flex: 1, position: 'relative', background: '#000', borderRadius: '8px', overflow: 'hidden' }}>
                            <div className="video-header" style={{ position: 'absolute', top: 0, left: 0, right: 0, padding: '8px', background: 'rgba(0,0,0,0.7)', zIndex: 10, display: 'flex', justifyContent: 'space-between' }}>
                                <h3 style={{ margin: 0, fontSize: '12px', color: '#fff' }}>Enhanced Feed</h3>
                                <div style={{ display: 'flex', gap: '5px' }}>
                                    <button onClick={handleCaptureSnapshot}>📸</button>
                                    <button>⛶</button>
                                </div>
                            </div>
                            <div className="video-content" style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                <img
                                    src={displayFrame.image_data || "https://placehold.co/640x480/0A0A0A/737373?text=Awaiting+Signal"}
                                    alt="Enhanced Feed"
                                    style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }}
                                />
                                {displayFrame.detections && (
                                    <DetectionOverlay
                                        detections={displayFrame.detections}
                                        systemState={displayFrame.state}
                                        width={640} // Todo: Dynamic sizing
                                        height={480}
                                    />
                                )}
                                <SafeModeOverlay isActive={systemStatus.inSafeMode} message={systemStatus.message} cause={systemStatus.cause} />
                            </div>
                        </div>
                    </div>

                    {/* BOTTOM ROW: LOGS & METRICS */}
                    <div className="data-grid-row" style={{ height: '200px', display: 'flex', gap: '10px' }}>
                        <div className="alert-panel-wrapper" style={{ flex: 1, background: '#121212', borderRadius: '8px', padding: '10px' }}>
                            <AlertPanel
                                currentState={displayFrame.state}
                                detections={displayFrame.detections}
                                maxConfidence={displayFrame.max_confidence}
                                addEvent={addEvent}
                            />
                        </div>
                        <div className="metrics-panel-wrapper" style={{ flex: 1, background: '#121212', borderRadius: '8px', padding: '10px' }}>
                            <MetricsPanel
                                fpsHistory={[]} // Todo: Pass history from context
                                latencyHistory={[]}
                                inSafeMode={systemStatus.inSafeMode}
                                safeModeStartTime={null}
                                currentFps={fps}
                                latency={displayFrame.system?.latency_ms}
                                connectionStatus={connectionStatus}
                                systemState={displayFrame.state}
                            />
                        </div>
                    </div>

                    {/* CENTER OVERLAY: RISK SCORE */}
                    <div className="center-overlay" style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', pointerEvents: 'none' }}>
                        <RiskScoreCircle
                            systemState={displayFrame.state}
                            confidence={displayFrame.max_confidence || 0}
                            isSafeMode={systemStatus.inSafeMode}
                        />
                    </div>
                </div>

                {/* --- COLUMN 3: RIGHT SIDEBAR --- */}
                <div className="right-sidebar" style={{ width: '280px', display: 'flex', flexDirection: 'column', gap: '10px', padding: '10px', overflowY: 'auto' }}>
                    <ConnectedViewers isOperator={true} />
                    <OperatorActionPanel
                        threatPriority={displayFrame.threat_priority}
                        signature={displayFrame.signature}
                        riskScore={displayFrame.risk_score}
                        fusionState={displayFrame.fusion_state}
                        seenBefore={displayFrame.seen_before}
                        occurrenceCount={displayFrame.occurrence_count}
                        explainability={displayFrame.explainability}
                        onDecision={(decision) => console.log('Operator Decision:', decision)}
                    />
                    <div style={{ flex: 1, minHeight: '200px', display: 'flex', flexDirection: 'column' }}>
                        <EventTimeline events={events} />
                    </div>
                </div>
            </div>

            {/* Modals */}
            <MaximizedPanel
                isOpen={maximizedPanel === 'raw'}
                onClose={() => setMaximizedPanel(null)}
                title="Raw Feed (Sensor)"
                badge="RAW"
            >
                <RawFeedPanel />
                <SafeModeOverlay isActive={systemStatus.inSafeMode} message={systemStatus.message} cause={systemStatus.cause} />
            </MaximizedPanel>

            <MaximizedPanel
                isOpen={maximizedPanel === 'enhanced'}
                onClose={() => setMaximizedPanel(null)}
                title="Enhanced Feed"
                badge="AI ENHANCED"
            >
                <img
                    src={displayFrame.image_data || "https://placehold.co/640x480/0A0A0A/737373?text=Awaiting+Signal"}
                    alt="Enhanced Feed"
                    style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                />
                <SafeModeOverlay isActive={systemStatus.inSafeMode} message={systemStatus.message} cause={systemStatus.cause} />
            </MaximizedPanel>

            <SnapshotModal
                isOpen={snapshotModal.isOpen}
                onClose={() => setSnapshotModal({ isOpen: false, imageData: null, type: null })}
                imageData={snapshotModal.imageData}
                timestamp={snapshotModal.timestamp}
                alertType={snapshotModal.alertType}
            />
        </div>
    );
};

export default Home;
