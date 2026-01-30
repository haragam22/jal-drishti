import React from 'react';
import useRawFeed from '../hooks/useRawFeed';

const RawFeedPanel = () => {
    // Determine token usage if needed (currently stateless backend for raw feed, so ignored)
    const { status, frameSrc, resolution } = useRawFeed();

    return (
        <div className="w-full h-full bg-black relative flex items-center justify-center overflow-hidden rounded-b-lg">
            {/* Resolution/Status Overlay (Optional, floating) */}
            <div className="absolute top-2 right-2 flex gap-2 z-10">
                {status === 'STREAMING' && (
                    <span className="flex h-2 w-2 relative mt-1">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
                    </span>
                )}
                <span className={`text-[10px] px-1.5 py-0.5 rounded opacity-80 ${status === 'STREAMING' ? 'bg-green-900 text-green-300' :
                        status === 'CONNECTED' ? 'bg-yellow-900 text-yellow-300' :
                            'bg-red-900 text-red-300'
                    }`}>
                    {status}
                </span>
            </div>

            {/* Video Area */}
            {frameSrc ? (
                <img
                    src={frameSrc}
                    alt="Raw Feed"
                    className="w-full h-full object-contain"
                />
            ) : (
                <div className="flex flex-col items-center justify-center text-gray-500 gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                    </svg>
                    <span className="text-xs font-mono tracking-widest text-gray-600">NO SIGNAL</span>
                </div>
            )}

            {/* Overlay for status if not streaming but connected */}
            {status === 'CONNECTED' && !frameSrc && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                    <span className="text-blue-400 animate-pulse text-xs tracking-wider">WAITING...</span>
                </div>
            )}
        </div>
    );
};

export default RawFeedPanel;
