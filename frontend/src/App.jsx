import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { StreamProvider } from './context/StreamContext';
import MainLayout from './layout/MainLayout';
import Home from './pages/Home';
import Sonar from './pages/Sonar';
import Infrared from './pages/Infrared';
import './App.css';

/**
 * App Component (Refactored for MPA)
 * - Wraps application in StreamProvider (Global WebSocket State)
 * - Sets up Routing via React Router
 */
function App() {
  return (
    <StreamProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Home />} />
            <Route path="sonar" element={<Sonar />} />
            <Route path="infrared" element={<Infrared />} />
            {/* Fallback for unknown routes */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </StreamProvider>
  );
}

export default App;
