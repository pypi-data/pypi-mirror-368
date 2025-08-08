"""
Authentication data models for OAuth2/Keycloak integration.

This module contains Pydantic models for handling authentication-related data
structures including token data, login requests, and API responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TokenData(BaseModel):
    """
    Model for representing JWT token data from Keycloak.
    
    This model contains user information extracted from validated JWT tokens.
    """
    
    username: str = Field(..., description="Primary username identifier")
    email: Optional[str] = Field(None, description="User's email address")
    full_name: Optional[str] = Field(None, description="User's full display name")
    roles: List[str] = Field(default_factory=list, description="User's assigned roles")
    preferred_username: Optional[str] = Field(None, description="User's preferred username from Keycloak")
    exp: Optional[int] = Field(None, description="Token expiration timestamp")
    
    # Additional token fields that may be present
    sub: Optional[str] = Field(None, description="Subject identifier (user ID)")
    iss: Optional[str] = Field(None, description="Token issuer")
    aud: Optional[str] = Field(None, description="Token audience")
    iat: Optional[int] = Field(None, description="Token issued at timestamp")
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "username": "user123",
                "email": "user@example.com",
                "full_name": "John Doe",
                "roles": ["user", "chatbot_access"],
                "preferred_username": "john.doe",
                "exp": 1640995200,
                "sub": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
            }
        }


class LoginRequest(BaseModel):
    """
    Request model for user login (if needed for direct login flows).
    
    Note: In OAuth2 flow, this may not be used directly as users authenticate
    through Keycloak's login pages.
    """
    
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "username": "user123",
                "password": "secure_password"
            }
        }


class TokenResponse(BaseModel):
    """
    Response model for OAuth2 token exchange.
    
    This model represents the response from Keycloak after successful
    authorization code exchange or token refresh.
    """
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type (typically 'bearer')")
    expires_in: Optional[int] = Field(None, description="Token expiration time in seconds")
    refresh_token: Optional[str] = Field(None, description="Refresh token for obtaining new access tokens")
    scope: Optional[str] = Field(None, description="Token scope")
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "scope": "openid profile email"
            }
        }


class ResponseModel(BaseModel):
    """
    Generic response model for API endpoints.
    
    This model provides a consistent response structure for various
    authentication-related API endpoints.
    """
    
    result: str = Field(default="success", description="Operation result status")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    message: Optional[str] = Field(None, description="Human-readable message")
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "result": "success",
                "data": {"user_id": "123", "session_id": "abc-def"},
                "message": "Authentication successful"
            }
        }


class UserInfoResponse(BaseModel):
    """
    Response model for user information from Keycloak userinfo endpoint.
    
    This model represents the user information returned by Keycloak's
    userinfo endpoint after successful authentication.
    """
    
    sub: str = Field(..., description="Subject identifier (user ID)")
    preferred_username: str = Field(..., description="User's preferred username")
    email: Optional[str] = Field(None, description="User's email address")
    email_verified: Optional[bool] = Field(None, description="Whether email is verified")
    name: Optional[str] = Field(None, description="User's full name")
    given_name: Optional[str] = Field(None, description="User's given name")
    family_name: Optional[str] = Field(None, description="User's family name")
    groups: Optional[List[str]] = Field(None, description="User's group memberships")
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "sub": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "preferred_username": "john.doe",
                "email": "john.doe@example.com",
                "email_verified": True,
                "name": "John Doe",
                "given_name": "John",
                "family_name": "Doe",
                "groups": ["users", "chatbot_access"]
            }
        }


class AuthError(BaseModel):
    """
    Model for authentication error responses.
    
    This model provides structured error information for authentication
    failures and OAuth2 errors.
    """
    
    error: str = Field(..., description="Error code")
    error_description: Optional[str] = Field(None, description="Human-readable error description")
    error_uri: Optional[str] = Field(None, description="URI for more information about the error")
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "error": "invalid_token",
                "error_description": "The access token provided is expired, revoked, malformed, or invalid",
                "error_uri": "https://tools.ietf.org/html/rfc6750#section-3.1"
            }
        }