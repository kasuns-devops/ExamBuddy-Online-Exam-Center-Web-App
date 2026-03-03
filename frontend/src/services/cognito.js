/**
 * Cognito Authentication Service - Using Hosted UI
 * This approach doesn't require SECRET_HASH on frontend
 */

const userPoolId = import.meta.env.VITE_COGNITO_USER_POOL_ID;
const clientId = import.meta.env.VITE_COGNITO_CLIENT_ID;
const region = import.meta.env.VITE_COGNITO_REGION || 'eu-north-1';

// Hosted UI domain
const cognitoDomain =
  import.meta.env.VITE_COGNITO_DOMAIN ||
  `exambuddy-auth.auth.${region}.amazoncognito.com`;

const getSafeHostedUri = (configuredUri, fallbackPath) => {
  const fallbackUri = `${window.location.origin}${fallbackPath}`;
  if (!configuredUri) {
    return fallbackUri;
  }

  try {
    const configured = new URL(configuredUri);
    const current = new URL(window.location.origin);
    const configuredHostIsLocal = configured.hostname === 'localhost' || configured.hostname === '127.0.0.1';
    const currentHostIsLocal = current.hostname === 'localhost' || current.hostname === '127.0.0.1';

    if (configuredHostIsLocal && !currentHostIsLocal) {
      return fallbackUri;
    }

    return configuredUri;
  } catch {
    return fallbackUri;
  }
};

const redirectUri = getSafeHostedUri(
  import.meta.env.VITE_COGNITO_REDIRECT_URI,
  '/auth-callback'
);

const logoutRedirectUri = getSafeHostedUri(
  import.meta.env.VITE_COGNITO_LOGOUT_URI,
  '/login'
);

/**
 * Redirect to Cognito Hosted UI for login
 */
export const loginWithHostedUI = () => {
  if (!clientId || !redirectUri || !cognitoDomain) {
    throw new Error('Cognito configuration missing (clientId, redirectUri, or domain)');
  }

  // Generate random state for CSRF protection
  const state = Math.random().toString(36).substring(2, 15) + 
                Math.random().toString(36).substring(2, 15);
  
  // Store state in sessionStorage for validation on callback
  sessionStorage.setItem('oauth_state', state);
  
  const params = new URLSearchParams({
    client_id: clientId,
    response_type: 'code',
    redirect_uri: redirectUri,
    scope: 'email openid profile',
    state: state,
  });

  const authUrl = `https://${cognitoDomain}/login?${params.toString()}`;
  console.log('Cognito authorize URL:', authUrl);
  sessionStorage.setItem('oauth_authorize_url', authUrl);
  window.location.assign(authUrl);
};

/**
 * Exchange authorization code for tokens (called after redirect from Hosted UI)
 */
export const exchangeCodeForTokens = async (code) => {
  try {
    const params = new URLSearchParams({
      grant_type: 'authorization_code',
      client_id: clientId,
      code: code,
      redirect_uri: redirectUri,
    });

    const response = await fetch(
      `https://${cognitoDomain}/oauth2/token`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: params.toString(),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error_description || 'Token exchange failed');
    }

    const { access_token, id_token, refresh_token } = data;

    // Store tokens
    localStorage.setItem('cognito_access_token', access_token);
    localStorage.setItem('cognito_id_token', id_token);
    if (refresh_token) {
      localStorage.setItem('cognito_refresh_token', refresh_token);
    }

    // Decode and store user info from ID token
    const userInfo = JSON.parse(atob(id_token.split('.')[1]));
    localStorage.setItem('user_email', userInfo.email);

    return {
      success: true,
      accessToken: access_token,
      idToken: id_token,
      refreshToken: refresh_token,
      user: { email: userInfo.email },
    };
  } catch (error) {
    console.error('Token exchange error:', error);
    throw error;
  }
};

/**
 * Logout - revoke tokens and redirect to Hosted UI logout
 */
export const logout = () => {
  localStorage.removeItem('cognito_access_token');
  localStorage.removeItem('cognito_id_token');
  localStorage.removeItem('cognito_refresh_token');
  localStorage.removeItem('user_email');
  sessionStorage.removeItem('oauth_state');

  const params = new URLSearchParams({
    client_id: clientId,
    logout_uri: logoutRedirectUri,
  });

  const logoutUrl = `https://${cognitoDomain}/logout?${params.toString()}`;
  console.log('Cognito logout URL:', logoutUrl);
  window.location.assign(logoutUrl);
};

/**
 * Get current ID token
 */
export const getIdToken = () => {
  return localStorage.getItem('cognito_id_token');
};

/**
 * Get current access token
 */
export const getAccessToken = () => {
  return localStorage.getItem('cognito_access_token');
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = () => {
  return !!getIdToken();
};

/**
 * Get user email from storage
 */
export const getUserEmail = () => {
  return localStorage.getItem('user_email');
};

/**
 * Refresh token using refresh token
 */
export const refreshAccessToken = async () => {
  try {
    const refreshToken = localStorage.getItem('cognito_refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const params = new URLSearchParams({
      grant_type: 'refresh_token',
      client_id: clientId,
      refresh_token: refreshToken,
    });

    const response = await fetch(
      `https://${cognitoDomain}/oauth2/token`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: params.toString(),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error_description || 'Token refresh failed');
    }

    const { access_token, id_token } = data;

    localStorage.setItem('cognito_access_token', access_token);
    localStorage.setItem('cognito_id_token', id_token);

    return {
      success: true,
      accessToken: access_token,
      idToken: id_token,
    };
  } catch (error) {
    console.error('Token refresh error:', error);
    // If refresh fails, user needs to login again
    logout();
    throw error;
  }
};

