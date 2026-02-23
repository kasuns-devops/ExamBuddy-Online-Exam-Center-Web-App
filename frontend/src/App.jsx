import { useEffect, useState } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import Login from './pages/Login';
import AuthCallback from './pages/AuthCallback';
import Dashboard from './pages/Dashboard';
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isInitialized } = useAuth();

  if (!isInitialized) {
    return <div className="loading-container">Loading...</div>;
  }

  return isAuthenticated() ? children : <Navigate to="/login" />;
};

function AppContent() {
  const { initializeAuth } = useAuth();
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    // Initialize auth from localStorage on app mount
    initializeAuth();
    setInitialized(true);
  }, [initializeAuth]);

  if (!initialized) {
    return <div className="loading-container">Initializing...</div>;
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/auth-callback" element={<AuthCallback />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
