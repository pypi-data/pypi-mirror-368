"""
Simplified authentication router for OAuth2/Keycloak integration.

This module provides a single FastAPI route for OAuth2 authentication callback.
"""

import json
import logging
import os
import sys
from typing import Optional

import requests
from fastapi import APIRouter, HTTPException, Request

from .config import settings

logger = logging.getLogger("appLogger")

# Create the authentication router
router = APIRouter(prefix="/api/manual-chatbot/v1/auth", tags=["authentication"])


def save_token_data(tokens: dict, user_info: Optional[dict] = None):
    """
    Save token data to files in the user's home directory for development convenience.
    
    Args:
        tokens: Token response dictionary
        user_info: Optional user information
    """
    try:
        token_dir = os.path.expanduser("~/.zmp-tokens")
        os.makedirs(token_dir, exist_ok=True)

        # Save the full token response
        with open(os.path.join(token_dir, "token.json"), "w") as f:
            json.dump(
                {
                    "access_token": tokens.get("access_token"),
                    "refresh_token": tokens.get("refresh_token"),
                    "token_type": tokens.get("token_type", "bearer"),
                    "expires_in": tokens.get("expires_in"),
                    "user_info": user_info,
                },
                f,
                indent=2,
            )

        # Save just the access token to a separate file
        with open(os.path.join(token_dir, "access_token.txt"), "w") as f:
            f.write(tokens.get("access_token", ""))

        # Save the bearer token format
        with open(os.path.join(token_dir, "bearer_token.txt"), "w") as f:
            f.write(f"Bearer {tokens.get('access_token', '')}")

        logger.info(f"Token data saved to {token_dir}/")
    except Exception as e:
        logger.warning(f"Failed to save token data: {str(e)}")


def _get_size(obj, seen=None):
    """
    Recursively find the size of objects including nested objects.
    
    Args:
        obj: Object to calculate size for
        seen: Set of already processed object IDs
        
    Returns:
        Total size in bytes
    """
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Mark as seen
    seen.add(obj_id)
    # Recursively add sizes of referred objects
    if isinstance(obj, dict):
        size += sum([_get_size(v, seen) for v in obj.values()])
        size += sum([_get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, "__dict__"):
        size += _get_size(obj.__dict__, seen)
    elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([_get_size(i, seen) for i in obj])
    return size


@router.get("/docs/oauth2-redirect", summary="Keycloak OAuth2 callback for the redirect URI")
def callback(request: Request, code: str):
    """
    Keycloak OAuth2 callback endpoint.
    
    This endpoint handles the OAuth2 authorization code flow callback from Keycloak.
    It exchanges the authorization code for access and refresh tokens.
    
    Args:
        request: FastAPI request object
        code: Authorization code from Keycloak
        
    Returns:
        Token response with access_token, refresh_token, etc.
        
    Raises:
        HTTPException: If token exchange fails
    """
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.KEYCLOAK_REDIRECT_URI,
        "client_id": settings.KEYCLOAK_CLIENT_ID,
        "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    
    logger.debug("Exchanging authorization code for tokens...")
    idp_response = requests.post(
        settings.keycloak_token_endpoint,
        data=data,
        headers=headers,
        verify=settings.HTTP_CLIENT_SSL_VERIFY,
    )

    if idp_response.status_code != 200:
        logger.error(f"Token exchange failed: {idp_response.status_code} - {idp_response.text}")
        raise HTTPException(status_code=401, detail="Invalid token")

    tokens = idp_response.json()
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    # Get user information from Keycloak
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    logger.debug("Fetching user info from Keycloak...")
    idp_response = requests.get(
        settings.keycloak_userinfo_endpoint, headers=headers, verify=settings.HTTP_CLIENT_SSL_VERIFY
    )
    
    if idp_response.status_code != 200:
        logger.error(f"User info fetch failed: {idp_response.status_code} - {idp_response.text}")
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_info = idp_response.json()
    logger.debug(f"user_info: {user_info}")

    # Store in session if sessions are available
    if hasattr(request, 'session'):
        request.session["refresh_token"] = refresh_token
        request.session["user_info"] = user_info

        total_bytes = _get_size(request.session)
        if total_bytes > 4096:
            logger.debug(f"Total bytes: {total_bytes}")
            logger.warning(f"The session data size({total_bytes}) is over than 4kb.")
            raise HTTPException(status_code=401, detail="Session data too large")

    # Save tokens to file system
    save_token_data(tokens, user_info)

    logger.info(f"OAuth2 callback successful for user: {user_info.get('preferred_username', 'unknown')}")
    return tokens


@router.get("/docs/oauth2-redirect", summary="Swagger UI OAuth2 redirect handler")
def swagger_oauth2_redirect():
    """
    Swagger UI OAuth2 redirect handler.
    
    This endpoint is automatically used by Swagger UI for OAuth2 authentication flow.
    It handles the redirect from Keycloak back to Swagger UI.
    """
    # This endpoint is handled by Swagger UI internally
    # We just need to define it so it appears in the OpenAPI schema
    return {"message": "OAuth2 redirect handled by Swagger UI"}