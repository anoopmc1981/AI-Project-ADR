import { CognitoUserPool, CognitoUser } from 'amazon-cognito-identity-js';
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

  // Log in user
  login: (email, password) => {
    return new Promise((resolve, reject) => {
      const cognitoUser = new CognitoUser({
        Username: email,
        Pool: userPool,
      });

      const authenticationDetails = {
        Username: email,
        Password: password,
      };

      cognitoUser.authenticateUser(
        authenticationDetails,
        {
          onSuccess: (result) => {
            resolve({
              accessToken: result.getAccessToken().getJwtToken(),
              idToken: result.getIdToken().getJwtToken(),
              refreshToken: result.getRefreshToken().getToken(),
            });
          },
          onFailure: (err) => {
            reject(err);
          },
        }
      );
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
