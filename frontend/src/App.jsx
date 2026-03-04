import { useEffect } from 'react';
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
import ExamPage from './pages/ExamPage';
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const isAuthenticated = useAuth((state) => state.isAuthenticated);

  return isAuthenticated ? children : <Navigate to="/login" />;
};

function AppRoutes() {
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
      <Route
        path="/exam"
        element={
          <ProtectedRoute>
            <ExamPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

function App() {
  const initializeAuth = useAuth((state) => state.initializeAuth);
  const buildVersion = import.meta.env.VITE_APP_VERSION || 'dev-local';

  useEffect(() => {
    // Initialize auth from localStorage on app mount
    initializeAuth();
  }, [initializeAuth]);

  return (
    <>
      <Router>
        <AppRoutes />
      </Router>
      <div className="build-version" title={`Build ${buildVersion}`}>
        Build {String(buildVersion).slice(0, 8)}
      </div>
    </>
  );
}

export default App;
