import React, { useState } from 'react';
import { authService } from '../services/authService';
import '../styles/Login.css';

export function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [confirmCode, setConfirmCode] = useState('');
  const [showConfirmation, setShowConfirmation] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await authService.login(email, password);
      if (result) {
        onLoginSuccess(result);
      }
    } catch (err) {
      console.error('Login error:', err);
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await authService.signUp(email, password, name);
      setShowConfirmation(true);
    } catch (err) {
      setError(err.message || 'Sign up failed');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmSignUp = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await authService.confirmSignUp(email, confirmCode);
      // Now log them in
      const result = await authService.login(email, password);
      onLoginSuccess(result);
    } catch (err) {
      setError(err.message || 'Confirmation failed');
    } finally {
      setLoading(false);
    }
  };

  if (showConfirmation) {
    return (
      <div className="login-container">
        <div className="login-box">
          <h2>Confirm Your Email</h2>
          <p>We sent a confirmation code to {email}</p>
          <form onSubmit={handleConfirmSignUp}>
            <input
              type="text"
              placeholder="Confirmation Code"
              value={confirmCode}
              onChange={(e) => setConfirmCode(e.target.value)}
              disabled={loading}
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Confirming...' : 'Confirm'}
            </button>
          </form>
          {error && <div className="error-message">{error}</div>}
          <button
            type="button"
            onClick={() => {
              setShowConfirmation(false);
              setConfirmCode('');
              setError('');
            }}
            className="secondary-button"
          >
            Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>{isSignUp ? 'Sign Up' : 'Login'}</h2>
        <form onSubmit={isSignUp ? handleSignUp : handleLogin}>
          {isSignUp && (
            <input
              type="text"
              placeholder="Full Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={loading}
              required
            />
          )}
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={loading}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loading}
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Processing...' : isSignUp ? 'Sign Up' : 'Login'}
          </button>
        </form>

        {error && <div className="error-message">{error}</div>}

        <button
          type="button"
          onClick={() => {
            setIsSignUp(!isSignUp);
            setError('');
            setEmail('');
            setPassword('');
            setName('');
          }}
          className="toggle-button"
        >
          {isSignUp ? 'Already have an account? Login' : "Don't have an account? Sign Up"}
        </button>
      </div>
    </div>
  );
}
