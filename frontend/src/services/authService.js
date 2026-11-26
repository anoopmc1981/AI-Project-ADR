import { CognitoUserPool, CognitoUser, AuthenticationDetails } from 'amazon-cognito-identity-js';
import { cognito } from '../config/cognito';

const poolData = {
  UserPoolId: cognito.userPoolId,
  ClientId: cognito.clientId,
};

const userPool = new CognitoUserPool(poolData);

export const authService = {
  // Sign up new user
  signUp: (email, password, name) => {
    return new Promise((resolve, reject) => {
      const attributeList = [
        {
          Name: 'email',
          Value: email,
        },
        {
          Name: 'name',
          Value: name,
        },
      ];

      userPool.signUp(email, password, attributeList, null, (err, result) => {
        if (err) {
          reject(err);
        } else {
          resolve(result);
        }
      });
    });
  },

  // Confirm sign up with code
  confirmSignUp: (email, code) => {
    return new Promise((resolve, reject) => {
      const cognitoUser = new CognitoUser({
        Username: email,
        Pool: userPool,
      });

      cognitoUser.confirmRegistration(code, true, (err, result) => {
        if (err) {
          reject(err);
        } else {
          resolve(result);
        }
      });
    });
  },

  // Log in user - FIXED VERSION
  login: (email, password) => {
    return new Promise((resolve, reject) => {
      try {
        const cognitoUser = new CognitoUser({
          Username: email,
          Pool: userPool,
        });

        const authenticationDetails = new AuthenticationDetails({
          Username: email,
          Password: password,
        });

        cognitoUser.authenticateUser(authenticationDetails, {
          onSuccess: (result) => {
            try {
              const tokens = {
                accessToken: result.getAccessToken().getJwtToken(),
                idToken: result.getIdToken().getJwtToken(),
                user: email,
              };
              
              // Try to get refresh token if available
              try {
                tokens.refreshToken = result.getRefreshToken().getToken();
              } catch (e) {
                // Refresh token might not be available
              }
              
              resolve(tokens);
            } catch (e) {
              resolve({
                user: email,
                authenticated: true,
              });
            }
          },
          onFailure: (err) => {
            console.error('Auth error:', err);
            reject(new Error(err.message || 'Login failed'));
          },
        });
      } catch (err) {
        console.error('Login error:', err);
        reject(new Error(err.message || 'Login error'));
      }
    });
  },

  // Log out user
  logout: () => {
    const cognitoUser = userPool.getCurrentUser();
    if (cognitoUser) {
      cognitoUser.signOut();
    }
  },

  // Get current user
  getCurrentUser: () => {
    return userPool.getCurrentUser();
  },

  // Get current user session
  getUserSession: () => {
    return new Promise((resolve, reject) => {
      const cognitoUser = userPool.getCurrentUser();

      if (!cognitoUser) {
        reject(new Error('No user found'));
        return;
      }

      cognitoUser.getSession((err, session) => {
        if (err) {
          reject(err);
        } else if (!session.isValid()) {
          reject(new Error('Session is not valid'));
        } else {
          resolve(session);
        }
      });
    });
  },

  // Check if user is authenticated
  isAuthenticated: async () => {
    try {
      await authService.getUserSession();
      return true;
    } catch {
      return false;
    }
  },

  // Refresh tokens
  refreshTokens: () => {
    return new Promise((resolve, reject) => {
      const cognitoUser = userPool.getCurrentUser();

      if (!cognitoUser) {
        reject(new Error('No user found'));
        return;
      }

      cognitoUser.getSession((err, session) => {
        if (err) {
          reject(err);
        } else {
          const refreshToken = session.getRefreshToken();
          cognitoUser.refreshSession(refreshToken, (err, session) => {
            if (err) {
              reject(err);
            } else {
              resolve({
                accessToken: session.getAccessToken().getJwtToken(),
                idToken: session.getIdToken().getJwtToken(),
              });
            }
          });
        }
      });
    });
  },
};
