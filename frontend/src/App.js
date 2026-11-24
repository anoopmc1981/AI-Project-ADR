import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './components/Login';
import { ProtectedRoute } from './components/ProtectedRoute';
import { authService } from './services/authService';
import './App.css';

function Dashboard() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getUserInfo = async () => {
      try {
        const cognitoUser = authService.getCurrentUser();
        if (cognitoUser) {
          cognitoUser.getUserAttributes((err, attributes) => {
            if (err) {
              console.error(err);
            } else {
              const userInfo = {};
              attributes.forEach((attr) => {
                userInfo[attr.Name] = attr.Value;
              });
              setUser(userInfo);
            }
            setLoading(false);
          });
        }
      } catch (err) {
        console.error('Error fetching user:', err);
        setLoading(false);
      }
    };

    getUserInfo();
  }, []);

  const handleLogout = () => {
    authService.logout();
    window.location.href = '/login';
  };

  if (loading) {
    return <div className="loading">Loading user data...</div>;
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>ADR Scanner Dashboard</h1>
        <div className="user-info">
          {user && <span>Welcome, {user.name || user.email}</span>}
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </header>
      <main className="dashboard-content">
        <div className="card">
          <h2>Market Status</h2>
          <p>Your ADR scanning dashboard will appear here.</p>
        </div>
        <div className="card">
          <h2>Recent Crossings</h2>
          <p>No crossings detected yet.</p>
        </div>
        <div className="card">
          <h2>Settings</h2>
          <p>Configure your ADR scanner preferences here.</p>
        </div>
      </main>
    </div>
  );
}

function LoginPage({ onLoginSuccess }) {
  return <Login onLoginSuccess={onLoginSuccess} />;
}

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    // Check if user is already logged in
    const checkAuth = async () => {
      const isAuth = await authService.isAuthenticated();
      setIsLoggedIn(isAuth);
    };

    checkAuth();
  }, []);

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
  };

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage onLoginSuccess={handleLoginSuccess} />} />
        <Route
          path="/"
          element={isLoggedIn ? <Dashboard /> : <Navigate to="/login" />}
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;
