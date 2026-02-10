/**
 * Header Component - Navigation header with role-based menu
 */
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import './Header.css';

const Header = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout, isAdmin, isCandidate } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="header">
      <div className="header-container">
        <Link to="/" className="header-logo">
          <h1>ExamBuddy</h1>
        </Link>

        <nav className="header-nav">
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="nav-link">
                Dashboard
              </Link>

              {isAdmin() && (
                <>
                  <Link to="/projects" className="nav-link">
                    Projects
                  </Link>
                  <Link to="/questions" className="nav-link">
                    Questions
                  </Link>
                  <Link to="/results-admin" className="nav-link">
                    All Results
                  </Link>
                </>
              )}

              {isCandidate() && (
                <>
                  <Link to="/exams" className="nav-link">
                    Take Exam
                  </Link>
                  <Link to="/history" className="nav-link">
                    My History
                  </Link>
                </>
              )}

              <div className="header-user">
                <span className="user-email">{user?.email}</span>
                <span className="user-role">{user?.role}</span>
                <button onClick={handleLogout} className="btn-logout">
                  Logout
                </button>
              </div>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">
                Login
              </Link>
              <Link to="/register" className="nav-link">
                Register
              </Link>
            </>
          )}
        </nav>

        {/* Mobile menu toggle (implement in future) */}
        <button className="mobile-menu-toggle" aria-label="Toggle menu">
          ☰
        </button>
      </div>
    </header>
  );
};

export default Header;
