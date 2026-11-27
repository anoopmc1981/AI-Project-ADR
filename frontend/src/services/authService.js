import { Amplify } from 'aws-amplify';
import { signUp, confirmSignUp, signIn, signOut, getCurrentUser, fetchAuthSession } from 'aws-amplify/auth';
import { cognito } from '../config/cognito';

// Configure Amplify
Amplify.configure({
  Auth: {
    Cognito: {
      region: cognito.region,
      userPoolId: cognito.userPoolId,
      userPoolClientId: cognito.clientId,
    },
  },
});

// Custom token storage in localStorage
const tokenStorage = {
  setTokens: (tokens) => {
    console.log('Storing tokens in localStorage');
    localStorage.setItem('auth_tokens', JSON.stringify({
      accessToken: tokens.accessToken,
      idToken: tokens.idToken,
      refreshToken: tokens.refreshToken,
      username: tokens.username,
      timestamp: Date.now(),
    }));
  },

  getTokens: () => {
    const stored = localStorage.getItem('auth_tokens');
    if (stored) {
      try {
        return JSON.parse(stored);
      } catch (e) {
        console.error('Error parsing stored tokens:', e);
        return null;
      }
    }
    return null;
  },

  clearTokens: () => {
    console.log('Clearing tokens from localStorage');
    localStorage.removeItem('auth_tokens');
  },
};

export const authService = {
  // Sign up new user
  signUp: (email, password, name) => {
    console.log('signUp called:', { email, name });
    return signUp({
      username: email,
      password: password,
      options: {
        userAttributes: {
          email: email,
          name: name,
        },
      },
    }).catch((err) => {
      console.error('signUp error:', err);
      throw err;
    });
  },

  // Confirm sign up with code
  confirmSignUp: (email, code) => {
    console.log('confirmSignUp called:', { email });
    return confirmSignUp({
      username: email,
      confirmationCode: code,
    }).catch((err) => {
      console.error('confirmSignUp error:', err);
      throw err;
    });
  },

  // Log in user
  login: (email, password) => {
    console.log('login called:', { email });
    return signIn({
      username: email,
      password: password,
    })
      .then(async (user) => {
        console.log('signIn successful:', user);
        
        // Get the session tokens
        try {
          const session = await fetchAuthSession();
          console.log('Got session:', session);
          
          const tokens = {
            accessToken: session.tokens?.accessToken?.toString() || '',
            idToken: session.tokens?.idToken?.toString() || '',
            refreshToken: session.tokens?.refreshToken?.toString() || session.tokens?.refreshToken || '',
            username: user.username,
          };
          
          console.log('Processed tokens:', {
            hasAccessToken: !!tokens.accessToken,
            hasIdToken: !!tokens.idToken,
            hasRefreshToken: !!tokens.refreshToken,
            username: tokens.username,
          });
          
          // Store tokens in localStorage
          tokenStorage.setTokens(tokens);
          
          return {
            user: user.username,
            authenticated: true,
            ...tokens,
          };
        } catch (err) {
          console.error('Error getting session:', err);
          throw err;
        }
      })
      .catch((err) => {
        console.error('signIn error:', err);
        throw err;
      });
  },

  // Log out user
  logout: () => {
    console.log('logout called');
    tokenStorage.clearTokens();
    return signOut().catch((err) => {
      console.error('logout error:', err);
      tokenStorage.clearTokens();
      throw err;
    });
  },

  // Get current user
  getCurrentUser: () => {
    console.log('getCurrentUser called');
    return getCurrentUser().catch((err) => {
      console.error('getCurrentUser error:', err);
      throw err;
    });
  },

  // Get current user session
  getUserSession: () => {
    return fetchAuthSession().catch((err) => {
      console.error('fetchAuthSession error:', err);
      throw err;
    });
  },

  // Check if user is authenticated
  isAuthenticated: async () => {
    try {
      console.log('Checking authentication...');
      
      // First check localStorage for stored tokens
      const stored = tokenStorage.getTokens();
      if (stored) {
        console.log('Found stored tokens for user:', stored.username);
        return true;
      }
      
      // Then check with Amplify
      await getCurrentUser();
      console.log('User authenticated via Amplify');
      return true;
    } catch (err) {
      console.log('Not authenticated:', err.message);
      return false;
    }
  },

  // Get stored user info
  getStoredUser: () => {
    const tokens = tokenStorage.getTokens();
    if (tokens) {
      return {
        username: tokens.username,
        email: tokens.username,
      };
    }
    return null;
  },

  // Refresh tokens
  refreshTokens: async () => {
    try {
      const session = await fetchAuthSession({ forceRefresh: true });
      const tokens = {
        accessToken: session.tokens?.accessToken?.toString() || '',
        idToken: session.tokens?.idToken?.toString() || '',
        refreshToken: session.tokens?.refreshToken?.toString() || session.tokens?.refreshToken || '',
      };
      tokenStorage.setTokens(tokens);
      return tokens;
    } catch (err) {
      console.error('refreshTokens error:', err);
      throw err;
    }
  },
};

