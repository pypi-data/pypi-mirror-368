"""
Authentication service for the ZMP Manual Chatbot Backend.

This service provides a clean interface for authentication operations,
wrapping the OAuth2/Keycloak integration and providing additional
user management functionality.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Request

from .auth_models import TokenData, UserInfoResponse, TokenResponse
from .oauth2_keycloak import (
    get_current_user, 
    get_current_active_user, 
    optional_get_current_user,
    verify_token,
    get_userinfo,
    exchange_code_for_token,
    refresh_token as refresh_access_token,
    initialize_keycloak
)
from .config import settings

logger = logging.getLogger("appLogger")


class AuthService:
    """
    Authentication service for handling user operations and authentication flows.
    
    This service provides a higher-level interface for authentication operations,
    user management, and session handling.
    """

    def __init__(self):
        """Initialize the authentication service."""
        self.initialized = False
        logger.info("AuthService initialized")

    async def initialize(self) -> bool:
        """
        Initialize the authentication service.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            if not settings.AUTH_ENABLED:
                logger.info("Authentication is disabled via AUTH_ENABLED setting")
                self.initialized = True
                return True

            if not settings.keycloak_configured:
                logger.warning("Keycloak configuration is incomplete")
                return False

            # Initialize Keycloak OAuth2 integration
            success = initialize_keycloak()
            if success:
                logger.info("AuthService successfully initialized with Keycloak")
                self.initialized = True
            else:
                logger.error("Failed to initialize Keycloak integration")
            
            return success
        except Exception as e:
            logger.error(f"Error initializing AuthService: {str(e)}")
            return False

    def is_auth_enabled(self) -> bool:
        """Check if authentication is enabled."""
        return settings.AUTH_ENABLED and self.initialized

    def is_keycloak_configured(self) -> bool:
        """Check if Keycloak is properly configured."""
        return settings.keycloak_configured

    async def get_current_user_info(self, token_data: TokenData) -> Dict[str, Any]:
        """
        Get comprehensive user information from token data.
        
        Args:
            token_data: Validated token data
            
        Returns:
            Dictionary with user information
        """
        try:
            user_info = {
                "user_id": token_data.sub or token_data.username,
                "username": token_data.username,
                "preferred_username": token_data.preferred_username,
                "email": token_data.email,
                "full_name": token_data.full_name,
                "roles": token_data.roles,
                "is_authenticated": True,
                "token_expires": token_data.exp
            }
            
            logger.debug(f"Retrieved user info for: {token_data.username}")
            return user_info
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving user information"
            )

    async def validate_user_access(self, token_data: TokenData, required_roles: Optional[list] = None) -> bool:
        """
        Validate if user has required access permissions.
        
        Args:
            token_data: Validated token data
            required_roles: List of required roles (optional)
            
        Returns:
            True if user has access, False otherwise
        """
        try:
            # Basic validation - user must be authenticated
            if not token_data or not token_data.username:
                return False

            # Role-based validation if required
            if required_roles:
                user_roles = set(token_data.roles or [])
                required_roles_set = set(required_roles)
                
                if not user_roles.intersection(required_roles_set):
                    logger.warning(
                        f"User {token_data.username} lacks required roles. "
                        f"Has: {user_roles}, Needs: {required_roles_set}"
                    )
                    return False

            logger.debug(f"Access validated for user: {token_data.username}")
            return True
        except Exception as e:
            logger.error(f"Error validating user access: {str(e)}")
            return False

    async def create_user_session_context(self, token_data: TokenData) -> Dict[str, Any]:
        """
        Create session context for authenticated user.
        
        Args:
            token_data: Validated token data
            
        Returns:
            Dictionary with session context information
        """
        try:
            session_context = {
                "user_id": token_data.sub or token_data.username,
                "username": token_data.username,
                "session_prefix": f"user_{token_data.username}",
                "roles": token_data.roles or [],
                "authenticated_at": token_data.iat,
                "expires_at": token_data.exp
            }
            
            logger.debug(f"Created session context for user: {token_data.username}")
            return session_context
        except Exception as e:
            logger.error(f"Error creating session context: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating user session"
            )

    async def handle_oauth_callback(self, authorization_code: str, redirect_uri: Optional[str] = None) -> TokenResponse:
        """
        Handle OAuth2 authorization callback.
        
        Args:
            authorization_code: Authorization code from OAuth2 provider
            redirect_uri: Redirect URI (optional)
            
        Returns:
            Token response with access token
        """
        try:
            if not self.is_auth_enabled():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Authentication service not available"
                )

            # Exchange authorization code for tokens
            token_response = exchange_code_for_token(authorization_code, redirect_uri)
            
            logger.info("OAuth2 callback handled successfully")
            return token_response
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error handling OAuth callback: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing authentication callback"
            )

    async def refresh_user_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh user's access token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New token response
        """
        try:
            if not self.is_auth_enabled():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Authentication service not available"
                )

            # Refresh the access token
            token_response = refresh_access_token(refresh_token)
            
            logger.info("Token refreshed successfully")
            return token_response
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error refreshing authentication token"
            )

    def get_auth_dependency(self, required_roles: Optional[list] = None):
        """
        Get authentication dependency for FastAPI routes.
        
        Args:
            required_roles: List of required roles (optional)
            
        Returns:
            FastAPI dependency function
        """
        async def auth_dependency(current_user: TokenData = Depends(get_current_active_user)) -> TokenData:
            """Authentication dependency with optional role checking."""
            if not self.is_auth_enabled():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Authentication not available"
                )

            # Validate user access if roles are required
            if required_roles:
                has_access = await self.validate_user_access(current_user, required_roles)
                if not has_access:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Insufficient permissions"
                    )

            return current_user
        
        return auth_dependency

    def get_optional_auth_dependency(self):
        """
        Get optional authentication dependency that doesn't fail if not authenticated.
        
        Returns:
            FastAPI dependency function that returns TokenData or None
        """
        async def optional_auth_dependency(request: Request) -> Optional[TokenData]:
            """Optional authentication dependency."""
            if not self.is_auth_enabled():
                return None
            
            return optional_get_current_user(request)
        
        return optional_auth_dependency


# Create a singleton instance of the auth service
auth_service = AuthService()


# Convenience dependency functions for common use cases
async def require_auth(current_user: TokenData = Depends(get_current_active_user)) -> TokenData:
    """
    Dependency that requires authentication.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        TokenData for authenticated user
        
    Raises:
        HTTPException: If not authenticated or auth not available
    """
    if not auth_service.is_auth_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication not available"
        )
    return current_user


async def require_auth_with_roles(required_roles: list):
    """
    Create a dependency that requires authentication with specific roles.
    
    Args:
        required_roles: List of required roles
        
    Returns:
        Dependency function
    """
    return auth_service.get_auth_dependency(required_roles)


async def optional_auth(request: Request) -> Optional[TokenData]:
    """
    Optional authentication dependency.
    
    Args:
        request: FastAPI request object
        
    Returns:
        TokenData if authenticated, None otherwise
    """
    return await auth_service.get_optional_auth_dependency()(request)