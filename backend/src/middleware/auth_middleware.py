"""
Authentication Middleware - Verifies Cognito JWT tokens
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import requests
from typing import Dict, Optional
from functools import lru_cache
from src.config import settings


# HTTP Bearer token scheme
security = HTTPBearer()


@lru_cache(maxsize=1)
def get_cognito_jwks() -> Dict:
    """
    Fetch Cognito JSON Web Key Set (JWKS) for token verification
    Cached to avoid repeated requests
    
    Returns:
        JWKS dictionary
    """
    region = settings.cognito_region
    user_pool_id = settings.cognito_user_pool_id
    jwks_url = f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'
    
    try:
        response = requests.get(jwks_url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching JWKS: {e}")
        # Return empty dict for local dev (will fall back to JWT_SECRET)
        return {'keys': []}


def verify_cognito_token(token: str) -> Dict:
    """
    Verify Cognito JWT token using JWKS
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        # Get JWKS from Cognito
        jwks = get_cognito_jwks()
        
        # Decode token header to get kid (key ID)
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')
        
        # Find matching key in JWKS
        key = None
        for jwk_key in jwks.get('keys', []):
            if jwk_key.get('kid') == kid:
                key = jwk_key
                break
        
        if not key:
            # Fallback to local JWT_SECRET for development
            if settings.debug or not settings.cognito_user_pool_id:
                payload = jwt.decode(
                    token,
                    settings.jwt_secret,
                    algorithms=[settings.jwt_algorithm]
                )
                return payload
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: Key not found"
                )
        
        # Verify token with Cognito public key
        payload = jwt.decode(
            token,
            key,
            algorithms=['RS256'],
            options={"verify_aud": False}  # Cognito uses 'client_id' instead of 'aud'
        )
        
        # Verify token_use claim
        if payload.get('token_use') != 'access':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: Wrong token_use"
            )
        
        return payload
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = security) -> Dict:
    """
    Dependency to extract and verify current user from JWT token
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        User info from token payload
    """
    token = credentials.credentials
    payload = verify_cognito_token(token)
    
    # Extract user info from token
    return {
        'user_id': payload.get('sub') or payload.get('username'),
        'email': payload.get('email'),
        'role': payload.get('custom:role', 'candidate'),
        'cognito_username': payload.get('username')
    }


async def require_admin(current_user: Dict = Depends(get_current_user)) -> Dict:
    """
    Dependency to ensure current user is an admin
    
    Args:
        current_user: Current user info from get_current_user
        
    Returns:
        Admin user info
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_candidate(current_user: Dict = Depends(get_current_user)) -> Dict:
    """
    Dependency to ensure current user is a candidate
    
    Args:
        current_user: Current user info from get_current_user
        
    Returns:
        Candidate user info
        
    Raises:
        HTTPException: If user is not a candidate
    """
    if current_user.get('role') != 'candidate':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Candidate access required"
        )
    return current_user


# Import Depends here to avoid circular import
from fastapi import Depends
