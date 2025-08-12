"""
Authentication utilities for HLA-Compass SDK
"""

import os
import json
import logging
from pathlib import Path
from typing import Any
from datetime import datetime, timedelta
import requests
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class AuthError(Exception):
    """Authentication error"""
    pass


class Auth:
    """
    Handle authentication for HLA-Compass platform.
    
    Manages JWT tokens and provides authenticated API access.
    """
    
    # Environment URLs
    URLS = {
        'local': 'http://localhost:3000',  # Local development
        'dev': 'https://q9bc90psji.execute-api.eu-central-1.amazonaws.com/dev',
        'staging': 'https://api-staging.hla-compass.com',
        'prod': 'https://api.hla-compass.com'
    }
    
    def __init__(self, config_dir: str | None = None):
        """
        Initialize authentication handler.
        
        Args:
            config_dir: Directory to store auth tokens (default: ~/.hla-compass)
        """
        if config_dir is None:
            config_dir = Path.home() / '.hla-compass'
        else:
            config_dir = Path(config_dir)
            
        self.config_dir = config_dir
        self.config_dir.mkdir(exist_ok=True)
        self.token_file = self.config_dir / 'tokens.json'
        
        # Check if we're in local development mode
        self.is_local = os.getenv('ENVIRONMENT') == 'local' or os.getenv('HLA_ENV') == 'local'
        self.logger = logging.getLogger(f"{__name__}.Auth")
        
        # Load existing tokens
        self.tokens = self._load_tokens()
    
    def _load_tokens(self) -> dict[str, Any]:
        """Load tokens from disk"""
        if self.token_file.exists():
            try:
                with open(self.token_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load tokens: {e}")
        return {}
    
    def _save_tokens(self):
        """Save tokens to disk"""
        try:
            with open(self.token_file, 'w') as f:
                json.dump(self.tokens, f, indent=2)
            # Set restrictive permissions
            os.chmod(self.token_file, 0o600)
        except Exception as e:
            self.logger.error(f"Failed to save tokens: {e}")
    
    def login(self, 
             email: str, 
             password: str,
             env: str = 'dev') -> dict[str, Any]:
        """
        Login to HLA-Compass platform.
        
        Args:
            email: User email
            password: User password
            env: Environment (local, dev, staging, prod)
            
        Returns:
            Authentication response with tokens
        """
        # Handle local development - generate local JWT
        if env == 'local' or self.is_local:
            logger.info("Using local development authentication")
            
            # Generate a local JWT token
            try:
                from datetime import datetime, timedelta
                import jwt
                
                # Create token payload
                payload = {
                    'sub': os.getenv('LOCAL_USER_ID', 'local-dev-user'),
                    'email': email or os.getenv('LOCAL_USER_EMAIL', 'dev@local'),
                    'name': os.getenv('LOCAL_USER_NAME', 'Local Developer'),
                    'organization_id': os.getenv('LOCAL_ORG_ID', 'test-org'),
                    'organization_name': os.getenv('LOCAL_ORG_NAME', 'Test Organization'),
                    'role': os.getenv('LOCAL_USER_ROLE', 'admin'),
                    'iat': datetime.utcnow(),
                    'exp': datetime.utcnow() + timedelta(hours=24)
                }
                
                # Generate token
                secret = os.getenv('JWT_SECRET', 'local-dev-secret')
                token = jwt.encode(payload, secret, algorithm='HS256')
                
                # Return auth data in same format as real login
                auth_data = {
                    'access_token': token,
                    'refresh_token': token,  # Same token for local dev
                    'expires_in': 86400,  # 24 hours
                    'user': {
                        'id': payload['sub'],
                        'email': payload['email'],
                        'name': payload['name'],
                        'organization_id': payload['organization_id'],
                        'role': payload['role']
                    }
                }
                
                # Store tokens
                self.tokens[env] = {
                    'access_token': token,
                    'refresh_token': token,
                    'expires_at': (
                        datetime.utcnow() + 
                        timedelta(seconds=86400)
                    ).isoformat(),
                    'user': auth_data['user']
                }
                self._save_tokens()
                
                logger.info(f"Successfully logged in to local environment")
                return auth_data
                
            except ImportError:
                logger.warning("PyJWT not installed - install with: pip install pyjwt")
                # Fallback to simple token
                auth_data = {
                    'access_token': 'local-dev-token',
                    'refresh_token': 'local-dev-token',
                    'expires_in': 86400,
                    'user': {
                        'id': 'local-dev-user',
                        'email': email or 'dev@local',
                        'name': 'Local Developer',
                        'organization_id': 'test-org',
                        'role': 'admin'
                    }
                }
                self.tokens[env] = {
                    'access_token': 'local-dev-token',
                    'refresh_token': 'local-dev-token',
                    'expires_at': (
                        datetime.utcnow() + 
                        timedelta(seconds=86400)
                    ).isoformat(),
                    'user': auth_data['user']
                }
                self._save_tokens()
                return auth_data
        
        # Normal login for non-local environments
        url = urljoin(self.URLS[env], '/v1/auth/login')
        
        try:
            response = requests.post(
                url,
                json={'email': email, 'password': password},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                
                # Store tokens
                self.tokens[env] = {
                    'access_token': auth_data.get('access_token'),
                    'refresh_token': auth_data.get('refresh_token'),
                    'expires_at': (
                        datetime.utcnow() + 
                        timedelta(seconds=auth_data.get('expires_in', 3600))
                    ).isoformat(),
                    'user': auth_data.get('user')
                }
                self._save_tokens()
                
                self.logger.info(f"Successfully logged in to {env} environment")
                return auth_data
            else:
                error_msg = response.json().get('error', 'Login failed')
                raise AuthError(f"Login failed: {error_msg}")
                
        except requests.RequestException as e:
            raise AuthError(f"Network error during login: {str(e)}")
    
    def logout(self, env: str = 'dev'):
        """
        Logout from HLA-Compass platform.
        
        Args:
            env: Environment to logout from
        """
        if env in self.tokens:
            token = self.tokens[env].get('access_token')
            if token:
                # Try to logout on server
                try:
                    url = urljoin(self.URLS[env], '/v1/auth/logout')
                    requests.post(
                        url,
                        headers={'Authorization': f'Bearer {token}'}
                    )
                except:
                    pass  # Continue even if server logout fails
            
            # Remove local tokens
            del self.tokens[env]
            self._save_tokens()
            self.logger.info(f"Logged out from {env} environment")
    
    def get_token(self, env: str = 'dev') -> str:
        """
        Get valid access token for environment.
        
        Args:
            env: Environment
            
        Returns:
            Valid access token
            
        Raises:
            AuthError: If not authenticated or token expired
        """
        if env not in self.tokens:
            raise AuthError(f"Not authenticated to {env} environment")
        
        token_data = self.tokens[env]
        
        # Check if token is expired
        expires_at = datetime.fromisoformat(token_data['expires_at'])
        if datetime.utcnow() >= expires_at:
            # Try to refresh
            if 'refresh_token' in token_data:
                self._refresh_token(env)
                token_data = self.tokens[env]
            else:
                raise AuthError("Token expired and no refresh token available")
        
        return token_data['access_token']
    
    def _refresh_token(self, env: str):
        """Refresh access token"""
        refresh_token = self.tokens[env].get('refresh_token')
        if not refresh_token:
            raise AuthError("No refresh token available")
        
        url = urljoin(self.URLS[env], '/v1/auth/refresh')
        
        try:
            response = requests.post(
                url,
                json={'refresh_token': refresh_token},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                
                # Update tokens
                self.tokens[env].update({
                    'access_token': auth_data.get('access_token'),
                    'expires_at': (
                        datetime.utcnow() + 
                        timedelta(seconds=auth_data.get('expires_in', 3600))
                    ).isoformat()
                })
                
                if 'refresh_token' in auth_data:
                    self.tokens[env]['refresh_token'] = auth_data['refresh_token']
                
                self._save_tokens()
                self.logger.info(f"Successfully refreshed token for {env}")
            else:
                # Refresh failed, remove tokens
                del self.tokens[env]
                self._save_tokens()
                raise AuthError("Token refresh failed")
                
        except requests.RequestException as e:
            raise AuthError(f"Network error during token refresh: {str(e)}")
    
    def get_headers(self, env: str = 'dev') -> dict[str, str]:
        """
        Get authenticated headers for API requests.
        
        Args:
            env: Environment
            
        Returns:
            Headers dict with Authorization
        """
        token = self.get_token(env)
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def get_user(self, env: str = 'dev') -> dict[str, Any]:
        """
        Get current user information.
        
        Args:
            env: Environment
            
        Returns:
            User information
        """
        if env in self.tokens and 'user' in self.tokens[env]:
            return self.tokens[env]['user']
        
        # Fetch from API
        url = urljoin(self.URLS[env], '/v1/auth/me')
        headers = self.get_headers(env)
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                if env in self.tokens:
                    self.tokens[env]['user'] = user_data
                    self._save_tokens()
                return user_data
            else:
                raise AuthError("Failed to get user information")
        except requests.RequestException as e:
            raise AuthError(f"Network error: {str(e)}")
    
    def is_authenticated(self, env: str = 'dev') -> bool:
        """
        Check if authenticated to environment.
        
        Args:
            env: Environment
            
        Returns:
            True if authenticated with valid token
        """
        try:
            self.get_token(env)
            return True
        except AuthError:
            return False
    
    def get_api_client(self, env: str = 'dev'):
        """
        Get authenticated API client.
        
        Args:
            env: Environment
            
        Returns:
            API client instance
        """
        from .api_client import APIClient
        
        base_url = self.URLS[env]
        headers = self.get_headers(env)
        
        return APIClient(base_url, headers)