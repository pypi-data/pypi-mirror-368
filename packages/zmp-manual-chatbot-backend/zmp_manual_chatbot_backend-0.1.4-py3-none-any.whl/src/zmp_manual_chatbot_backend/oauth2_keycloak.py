"""
OAuth2/Keycloak integration module for ZMP Manual Chatbot Backend.

This module provides comprehensive OAuth2 authentication using Keycloak,
including JWT token validation, public key management, and user authentication.
"""

import logging
import jwt
import requests
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2AuthorizationCodeBearer
from jwt import ExpiredSignatureError, InvalidIssuedAtError, InvalidKeyError, PyJWTError
from jwt.api_jwk import PyJWK
import json
from fastapi.responses import JSONResponse
from typing import Optional

from .auth_models import TokenData
from .config import settings

logger = logging.getLogger("appLogger")

# OAuth2 Algorithm
ALGORITHM = "RS256"

# Export constants for simplified auth module
KEYCLOAK_CLIENT_ID = settings.KEYCLOAK_CLIENT_ID
KEYCLOAK_CLIENT_SECRET = settings.KEYCLOAK_CLIENT_SECRET
KEYCLOAK_REDIRECT_URI = settings.KEYCLOAK_REDIRECT_URI
KEYCLOAK_TOKEN_ENDPOINT = settings.keycloak_token_endpoint
KEYCLOAK_USER_ENDPOINT = settings.keycloak_userinfo_endpoint
HTTP_CLIENT_SSL_VERIFY = settings.HTTP_CLIENT_SSL_VERIFY

# This will be initialized when Keycloak is enabled
PUBLIC_KEY = None
oauth2_scheme = None


def get_public_key():
    """
    Retrieve the public key from Keycloak JWKS endpoint.
    
    Returns:
        The public key for JWT token verification, or None if retrieval fails.
    """
    try:
        logger.info(f"Retrieving public key from: {settings.keycloak_jwks_endpoint}")

        response = requests.get(
            settings.keycloak_jwks_endpoint, 
            verify=settings.HTTP_CLIENT_SSL_VERIFY, 
            timeout=10
        )

        if response.status_code != 200:
            logger.error(f"Failed to retrieve JWKS: Status {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None

        jwks = response.json()
        logger.debug(f"JWKS response: {json.dumps(jwks)}")

        # Validate jwks structure
        if not isinstance(jwks, dict) or not jwks.get("keys"):
            logger.error(f"Invalid JWKS format: {jwks}")
            return None

        # Log the number of keys received
        logger.info(f"Received {len(jwks['keys'])} keys from JWKS endpoint")

        try:
            if jwks.get("keys") and len(jwks["keys"]) > 0:
                # Get the first key for RS256
                key_data = next(
                    (
                        k
                        for k in jwks["keys"]
                        if k.get("alg") == ALGORITHM or k.get("use") == "sig"
                    ),
                    jwks["keys"][0],
                )

                # Log key information for debugging
                logger.debug(
                    f"Using key with kid: {key_data.get('kid')}, alg: {key_data.get('alg')}, use: {key_data.get('use')}"
                )

                # Convert to PyJWK and extract public key
                public_key = PyJWK.from_dict(key_data).key
                logger.info(
                    f"Successfully retrieved public key of type: {type(public_key).__name__}"
                )
                return public_key
            else:
                logger.error("No keys found in JWKS response")
                return None
        except InvalidKeyError as ike:
            logger.error(f"InvalidKeyError: {str(ike)}")
            # Log the problematic key
            if jwks.get("keys") and len(jwks["keys"]) > 0:
                logger.error(f"Problem with key: {json.dumps(jwks['keys'][0])}")
            return None

    except requests.RequestException as re:
        logger.error(f"Request error fetching public key: {str(re)}")
        return None
    except json.JSONDecodeError as jde:
        logger.error(f"JSON decode error: {str(jde)}")
        logger.error(
            f"Response content: {response.text[:500]}"
        )  # Log first 500 chars of response
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching public key: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def verify_token(token: str) -> TokenData:
    """
    Verify and decode a JWT token from Keycloak.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        TokenData object with user information
        
    Raises:
        HTTPException: If token is invalid, expired, or verification fails
    """
    if PUBLIC_KEY is None:
        logger.error("PUBLIC_KEY is None, token verification will fail")
        raise HTTPException(status_code=401, detail="Authentication not configured")

    try:
        # First, do a basic check to ensure the token has the right format
        parts = token.split(".")
        if len(parts) != 3:
            logger.error(
                f"Invalid token format: token has {len(parts)} segments, expected 3"
            )
            raise HTTPException(status_code=401, detail="Invalid token format")

        # Then decode with more relaxed validation for development
        payload = jwt.decode(
            jwt=token,
            key=PUBLIC_KEY,
            algorithms=[ALGORITHM],
            audience=settings.KEYCLOAK_CLIENT_ID,
            options={
                "verify_signature": True,
                "verify_aud": False,  # More relaxed for development
                "verify_iat": False,  # More relaxed for development
                "verify_exp": True,  # Keep expiration check
                "verify_nbf": False,  # More relaxed for development
            },
            leeway=60,
        )

        if payload is None:
            logger.error("Token decoded but payload is None")
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # Extract username and create TokenData
        username = payload.get("preferred_username", payload.get("sub", "unknown"))
        
        # Create TokenData with all available fields
        token_data = TokenData(
            username=username,
            email=payload.get("email"),
            full_name=payload.get("name"),
            roles=payload.get("realm_access", {}).get("roles", []),
            preferred_username=payload.get("preferred_username"),
            exp=payload.get("exp"),
            sub=payload.get("sub"),
            iss=payload.get("iss"),
            aud=payload.get("aud"),
            iat=payload.get("iat")
        )

        # Log successful validation for debugging
        logger.debug(f"Token successfully validated for user: {username}")

        return token_data

    except ExpiredSignatureError as ese:
        logger.error(f"ExpiredSignatureError: {ese}")
        raise HTTPException(status_code=401, detail="Expired token")
    except InvalidIssuedAtError as iiae:
        logger.error(f"InvalidIssuedAtError: {iiae}")
        raise HTTPException(status_code=401, detail="Invalid token timestamp")
    except PyJWTError as jwte:
        logger.error(f"JWTError: {jwte}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")


def exchange_code_for_token(authorization_code: str, redirect_uri: str = None):
    """
    Exchange an authorization code for an access token.
    
    Args:
        authorization_code: The authorization code from OAuth2 callback
        redirect_uri: The redirect URI (optional, uses default if not provided)
        
    Returns:
        Token response from Keycloak or error response
    """
    try:
        # Use the provided redirect_uri or fall back to the default one
        actual_redirect_uri = redirect_uri if redirect_uri else settings.KEYCLOAK_REDIRECT_URI

        logger.info(
            f"Exchanging code for token with redirect URI: {actual_redirect_uri}"
        )

        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "client_id": settings.KEYCLOAK_CLIENT_ID,
            "redirect_uri": actual_redirect_uri,
        }

        # Add client secret if available
        if settings.KEYCLOAK_CLIENT_SECRET:
            data["client_secret"] = settings.KEYCLOAK_CLIENT_SECRET
            logger.debug("Using client secret for token exchange")
        else:
            logger.warning("No client secret available for token exchange")

        # Use basic server-side headers - no CORS issues here
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        # Log request details for debugging
        logger.debug(f"Token exchange request data: {data}")
        logger.debug(f"Token endpoint: {settings.keycloak_token_endpoint}")
        logger.debug(f"Headers: {headers}")

        response = requests.post(
            settings.keycloak_token_endpoint,
            data=data,
            headers=headers,
            verify=settings.HTTP_CLIENT_SSL_VERIFY,
            timeout=10,
        )

        # Log detailed response info for debugging
        logger.info(f"Token exchange response status: {response.status_code}")
        if response.status_code != 200:
            logger.debug(f"Token exchange response headers: {dict(response.headers)}")

        # CORS headers for all responses
        cors_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, Origin, Accept",
        }

        # Handle non-200 responses with more detailed logging
        if response.status_code != 200:
            error_message = (
                f"Failed to exchange code for token: Status {response.status_code}"
            )
            try:
                error_data = response.json()
                logger.error(f"{error_message}, Response: {error_data}")
                return JSONResponse(
                    status_code=response.status_code,
                    content=error_data,
                    headers=cors_headers,
                )
            except Exception:
                logger.error(f"{error_message}, Raw response: {response.text}")
                return JSONResponse(
                    status_code=response.status_code,
                    content={
                        "error": "server_error",
                        "error_description": response.text,
                    },
                    headers=cors_headers,
                )

        try:
            token_response = response.json()
            logger.info("Successfully exchanged authorization code for token")

            # Log token information (excluding the actual token values)
            token_info = {
                k: "***" if k in ["access_token", "refresh_token", "id_token"] else v
                for k, v in token_response.items()
            }
            logger.debug(f"Token response structure: {token_info}")

            return token_response
        except ValueError as json_err:
            logger.error(f"Error parsing token response as JSON: {str(json_err)}")
            logger.error(f"Raw response content: {response.text[:200]}...")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "invalid_response",
                    "error_description": "Invalid response format from authentication server",
                },
                headers=cors_headers,
            )

    except Exception as e:
        logger.error(f"Exception during token exchange: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "server_error", "error_description": str(e)},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Authorization, Content-Type, Origin, Accept",
            },
        )


def refresh_token(refresh_token: str):
    """
    Refresh an access token using a refresh token.
    
    Args:
        refresh_token: The refresh token
        
    Returns:
        New token response from Keycloak
        
    Raises:
        HTTPException: If token refresh fails
    """
    try:
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": settings.KEYCLOAK_CLIENT_ID,
        }

        # Add client secret if available
        if settings.KEYCLOAK_CLIENT_SECRET:
            data["client_secret"] = settings.KEYCLOAK_CLIENT_SECRET

        response = requests.post(
            settings.keycloak_token_endpoint,
            data=data,
            verify=settings.HTTP_CLIENT_SSL_VERIFY,
            timeout=10,
        )

        if response.status_code != 200:
            logger.error(f"Failed to refresh token: Status {response.status_code}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to refresh token",
            )

        token_response = response.json()
        logger.info("Successfully refreshed access token")

        return token_response

    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error refreshing token",
        )


def get_userinfo(access_token: str):
    """
    Get user information using an access token.
    
    Args:
        access_token: The access token
        
    Returns:
        User information from Keycloak
        
    Raises:
        HTTPException: If user info retrieval fails
    """
    try:
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(
            settings.keycloak_userinfo_endpoint,
            headers=headers,
            verify=settings.HTTP_CLIENT_SSL_VERIFY,
            timeout=10,
        )

        if response.status_code != 200:
            logger.error(f"Failed to get user info: Status {response.status_code}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to get user info",
            )

        user_info = response.json()
        logger.info(
            f"Successfully retrieved user info for: {user_info.get('preferred_username')}"
        )

        return user_info

    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting user info",
        )


async def get_token_from_request(request: Request) -> str:
    """
    Get token from Authorization header.
    
    Args:
        request: FastAPI request object
        
    Returns:
        The JWT token from the Authorization header
        
    Raises:
        HTTPException: If Authorization header is missing or invalid
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header.split("Bearer ")[1]
    return token


async def get_current_user(
    request: Request = None, token: str = Depends(oauth2_scheme)
) -> TokenData:
    """
    Authentication function using OAuth2 token.
    This is meant to be used with Security(get_current_user) in routes.
    
    Args:
        request: FastAPI request object (optional)
        token: JWT token from OAuth2 scheme
        
    Returns:
        TokenData object with user information
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # If we have a direct token from oauth2_scheme, use it
        # Otherwise, try to get it from the request
        if not token and request:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split("Bearer ")[1]
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        # Validate the token - note that verify_token is not a coroutine, don't use await
        user = verify_token(token)

        # TokenData is a Pydantic model, not a dict, so access attributes directly
        logger.debug(f"Authenticated user via OAuth2: {user.username}")

        return user
    except HTTPException:
        # Re-raise HTTP exceptions directly
        raise
    except Exception as e:
        logger.warning(f"OAuth2 authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user),
) -> TokenData:
    """
    Get the current active user.
    This function is used as a dependency in routes that require authentication.
    It ensures that the user exists and is active by validating the token.
    
    Args:
        current_user: TokenData from get_current_user dependency
        
    Returns:
        TokenData object for the authenticated user
    """
    # At this point, current_user should already be a valid TokenData object
    # if get_current_user has succeeded (it doesn't return None or raise an exception)
    logger.debug(f"Active user authenticated: {current_user.username}")
    return current_user


def initialize_keycloak():
    """
    Initialize Keycloak authentication system.
    
    This function should be called during application startup to:
    - Retrieve the public key from Keycloak
    - Set up the OAuth2 scheme
    - Validate configuration
    """
    global PUBLIC_KEY, oauth2_scheme
    
    if not settings.keycloak_configured:
        logger.warning("Keycloak is not fully configured - some settings are missing")
        return False

    try:
        logger.info(f"Initializing Keycloak for realm: {settings.KEYCLOAK_REALM}")
        logger.info(f"JWKS endpoint: {settings.keycloak_jwks_endpoint}")

        # Get the public key for token verification
        PUBLIC_KEY = get_public_key()

        if not PUBLIC_KEY:
            logger.error("Failed to retrieve Keycloak public key.")
            return False

        logger.debug(f"Public key type: {type(PUBLIC_KEY).__name__}")

        # Set up the OAuth2 scheme for token retrieval
        try:
            # Log the URLs being used for OAuth2 scheme
            logger.info("Initializing OAuth2 scheme with these URLs:")
            logger.info(f"- Authorization URL: {settings.keycloak_auth_endpoint}")
            logger.info(f"- Token URL: {settings.keycloak_token_endpoint}")
            logger.info(f"- Refresh URL: {settings.keycloak_userinfo_endpoint}")

            # Define basic scopes - but use empty scopes to match the sample
            oauth_scopes = {}

            # Create the OAuth2 scheme with minimal configuration like the sample
            oauth2_scheme = OAuth2AuthorizationCodeBearer(
                authorizationUrl=settings.keycloak_auth_endpoint,
                tokenUrl=settings.keycloak_token_endpoint,
                refreshUrl=settings.keycloak_userinfo_endpoint,
                scopes=oauth_scopes,
                auto_error=True,
            )

            # Verify the URLs in the created scheme
            logger.info(f"Created OAuth2 scheme: {oauth2_scheme}")
            try:
                if hasattr(oauth2_scheme, "flows") and hasattr(
                    oauth2_scheme.flows, "authorization_code"
                ):
                    logger.info(
                        f"Authorization URL in scheme: {oauth2_scheme.flows.authorization_code.auth_url}"
                    )
                    logger.info(
                        f"Token URL in scheme: {oauth2_scheme.flows.authorization_code.token_url}"
                    )
                else:
                    logger.info(
                        "OAuth2 scheme does not have expected attributes for logging"
                    )
            except Exception as attr_ex:
                logger.warning(f"Error accessing OAuth2 scheme properties: {str(attr_ex)}")
        except Exception as oauth_ex:
            logger.error(f"Failed to initialize OAuth2 scheme: {str(oauth_ex)}")
            # Fallback to a simpler scheme if there's an error
            from fastapi.security import OAuth2PasswordBearer

            oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.keycloak_token_endpoint)
            logger.info(
                f"Fallback to OAuth2PasswordBearer with token URL: {settings.keycloak_token_endpoint}"
            )

        logger.info(f"Keycloak integration initialized for realm: {settings.KEYCLOAK_REALM}")
        logger.info(f"Using algorithm: {ALGORITHM}")
        return True

    except Exception as e:
        logger.error(f"Error initializing Keycloak: {str(e)}")
        # Log detailed error information
        import traceback
        logger.error(traceback.format_exc())
        return False


# Optional auth dependency that can be disabled
def optional_get_current_user(request: Request = None) -> Optional[TokenData]:
    """
    Optional authentication dependency that returns None if auth is disabled.
    
    This allows for graceful degradation when authentication is disabled
    via the AUTH_ENABLED setting.
    
    Args:
        request: FastAPI request object
        
    Returns:
        TokenData if authenticated, None if auth disabled or authentication fails
    """
    if not settings.AUTH_ENABLED:
        logger.debug("Authentication is disabled, returning None")
        return None
        
    try:
        if oauth2_scheme is None:
            logger.warning("OAuth2 scheme not initialized, authentication unavailable")
            return None
            
        # Try to get token from request
        auth_header = request.headers.get("Authorization") if request else None
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
            
        token = auth_header.split("Bearer ")[1]
        return verify_token(token)
    except Exception as e:
        logger.debug(f"Optional authentication failed: {str(e)}")
        return None