import React, { createContext, useContext } from 'react';
import useLiveStream from '../hooks/useLiveStream';
import { CONNECTION_STATES, SYSTEM_STATES } from '../constants';

const StreamContext = createContext(null);

/**
 * Global provider for the live stream data.
 * This ensures the WebSocket connection persists during client-side navigation.
 */
export const StreamProvider = ({ children }) => {
    const liveStreamData = useLiveStream(true);

    return (
        <StreamContext.Provider value={liveStreamData}>
            {children}
        </StreamContext.Provider>
    );
};

/**
 * Hook to consume the stream data.
 */
export const useStream = () => {
    const context = useContext(StreamContext);
    if (!context) {
        throw new Error('useStream must be used within a StreamProvider');
    }
    return context;
};
