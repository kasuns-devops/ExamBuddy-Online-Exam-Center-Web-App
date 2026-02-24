# Cognito OAuth Configuration Fix

## Issue
Browser was redirected to Cognito `/error` endpoint with 400 Bad Request instead of showing the login form.

## Root Cause
The Cognito client application had missing OAuth2 configuration:
- ❌ AllowedOAuthFlows: not set
- ❌ AllowedOAuthFlowsUserPoolClient: false
- ❌ AllowedOAuthScopes: not set

This caused Cognito to reject the OAuth2 code flow request from the frontend.

## Solution Applied
Updated Cognito client with complete OAuth2 configuration:

```bash
aws cognito-idp update-user-pool-client \
  --user-pool-id eu-north-1_9EipRo5F7 \
  --client-id 4pptkfjoarjpdcl3aq0j27me6g \
  --region eu-north-1 \
  --callback-urls "http://localhost:{3000,5173,5174,5175}/auth-callback" \
  --logout-urls "http://localhost:{3000,5173,5174,5175}/login" \
  --allowed-o-auth-flows "code" \
  --allowed-o-auth-flows-user-pool-client \
  --allowed-o-auth-scopes "email" "openid" "profile" \
  --explicit-auth-flows "ALLOW_REFRESH_TOKEN_AUTH" "ALLOW_USER_SRP_AUTH" \
  --prevent-user-existence-errors ENABLED
```

## Current Configuration
✅ AllowedOAuthFlows: `["code"]`
✅ AllowedOAuthFlowsUserPoolClient: `true`
✅ AllowedOAuthScopes: `["email", "openid", "profile"]`
✅ CallbackURLs: All localhost ports (3000, 5173, 5174, 5175)
✅ LogoutURLs: All localhost ports (3000, 5173, 5174, 5175)
✅ ExplicitAuthFlows: ALLOW_REFRESH_TOKEN_AUTH, ALLOW_USER_SRP_AUTH

## Expected Behavior
1. User clicks "Sign In with Cognito"
2. ✓ Browser redirects to Cognito Hosted UI (not /error)
3. ✓ Cognito login form displays
4. ✓ User can log in with credentials
5. ✓ Cognito redirects back to localhost:5175/auth-callback?code=XXXXXXXX
6. ✓ Frontend exchanges code for tokens
7. ✓ Dashboard displays with API status healthy

## Testing
Clear browser cache and try login again:
- Open http://localhost:5175
- Click "Sign In with Cognito"
- Should now see Cognito login form
