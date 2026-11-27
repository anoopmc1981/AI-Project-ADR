import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './components/Login';
import { authService } from './services/authService';
import { apiService } from './services/apiService';
import './App.css';

function Dashboard() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [dataLoading, setDataLoading] = useState(true);
  const [dataError, setDataError] = useState(null);
  const [activeTab, setActiveTab] = useState('upper'); // 'upper' or 'lower'

  // Load user info on mount
  useEffect(() => {
    const getUserInfo = async () => {
      try {
        // Try to get from stored tokens first
        let userInfo = authService.getStoredUser();
        
        if (!userInfo) {
          // Try to get from Amplify
          const cognitoUser = await authService.getCurrentUser();
          console.log('getCurrentUser result:', cognitoUser);
          if (cognitoUser) {
            userInfo = {
              email: cognitoUser.signInDetails?.loginWith || cognitoUser.username || 'User',
              name: cognitoUser.username || 'User',
            };
          }
        } else {
          userInfo = {
            email: userInfo.username || 'User',
            name: userInfo.username || 'User',
          };
        }
        
        setUser(userInfo);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching user:', err);
        setUser({
          email: 'User',
          name: 'User',
        });
        setLoading(false);
      }
    };

    getUserInfo();
  }, []);

  // Load dashboard data
  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setDataLoading(true);
        setDataError(null);
        
        const data = await apiService.getDashboardData();
        setDashboardData(data);
      } catch (err) {
        console.error('Error loading dashboard data:', err);
        setDataError(err.message || 'Failed to load dashboard data');
        setDashboardData(null);
      } finally {
        setDataLoading(false);
      }
    };

    loadDashboardData();
    
    // Refresh data every 30 seconds
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleLogout = async () => {
    try {
      await authService.logout();
      window.location.href = '/login';
    } catch (err) {
      console.error('Logout error:', err);
      window.location.href = '/login';
    }
  };

  const handleRefreshData = async () => {
    try {
      setDataLoading(true);
      setDataError(null);
      
      const data = await apiService.getDashboardData();
      setDashboardData(data);
    } catch (err) {
      console.error('Error refreshing dashboard data:', err);
      setDataError(err.message || 'Failed to refresh data');
    } finally {
      setDataLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading user data...</div>;
  }

  const crossings = activeTab === 'upper' 
    ? dashboardData?.upper_crossings || [] 
    : dashboardData?.lower_crossings || [];
  
  const summary = dashboardData?.summary || {
    upper_count: 0,
    lower_count: 0,
    total_count: 0,
  };

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
        {/* Summary Cards */}
        <div className="summary-cards">
          <div className="card summary-card">
            <h3>{summary.total_count}</h3>
            <p>Total Crossings Today</p>
          </div>
          <div className="card summary-card">
            <h3>{summary.upper_count}</h3>
            <p>Upper Crossings</p>
          </div>
          <div className="card summary-card">
            <h3>{summary.lower_count}</h3>
            <p>Lower Crossings</p>
          </div>
        </div>

        {/* Error Message */}
        {dataError && (
          <div className="error-message">
            <p>{dataError}</p>
            <button onClick={handleRefreshData} className="retry-button">Retry</button>
          </div>
        )}

        {/* Crossings Table */}
        <div className="card crossings-card">
          <div className="card-header">
            <h2>{activeTab === 'upper' ? 'Upper' : 'Lower'} Crossings</h2>
            <div className="card-controls">
              <button 
                className={`tab-button ${activeTab === 'upper' ? 'active' : ''}`}
                onClick={() => setActiveTab('upper')}
              >
                Upper
              </button>
              <button 
                className={`tab-button ${activeTab === 'lower' ? 'active' : ''}`}
                onClick={() => setActiveTab('lower')}
              >
                Lower
              </button>
              <button 
                onClick={handleRefreshData}
                disabled={dataLoading}
                className="refresh-button"
              >
                {dataLoading ? 'Loading...' : 'Refresh'}
              </button>
            </div>
          </div>

          {dataLoading ? (
            <div className="loading-message">Loading crossings...</div>
          ) : crossings.length === 0 ? (
            <div className="empty-message">No crossings detected</div>
          ) : (
            <table className="crossings-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>LTP</th>
                  <th>ADR %</th>
                  <th>Level</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {crossings.map((crossing, idx) => (
                  <tr key={idx}>
                    <td className="symbol">{crossing.symbol}</td>
                    <td className="ltp">₹{crossing.ltp?.toFixed(2)}</td>
                    <td className="adr-pct">{crossing.adr_pct?.toFixed(2)}%</td>
                    <td className="level">₹{crossing.level?.toFixed(2)}</td>
                    <td className="time">
                      {new Date(crossing.crossing_time).toLocaleTimeString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
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
  const [checkingAuth, setCheckingAuth] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const checkAuth = async () => {
      try {
        const isAuth = await authService.isAuthenticated();
        console.log('Auth check:', isAuth);
        setIsLoggedIn(isAuth);
      } catch (err) {
        console.error('Auth check error:', err);
        setIsLoggedIn(false);
      } finally {
        setCheckingAuth(false);
      }
    };

    checkAuth();
  }, []);

  const handleLoginSuccess = () => {
    console.log('Login successful, setting isLoggedIn to true');
    setIsLoggedIn(true);
    // Force navigation to home after a brief delay
    setTimeout(() => {
      window.location.href = '/';
    }, 100);
  };

  if (checkingAuth) {
    return <div className="loading">Checking authentication...</div>;
  }

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
