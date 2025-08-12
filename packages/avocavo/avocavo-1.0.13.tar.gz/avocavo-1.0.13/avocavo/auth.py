"""
Authentication module for Avocavo Nutrition API
Handles user login, logout, and API key management
Supports both email/password and OAuth browser login
"""

import os
import json
import keyring
import requests
import webbrowser
import time
from typing import Optional, Dict, List
from pathlib import Path
from .models import Account
from .exceptions import ApiError, AuthenticationError

from .auth_supabase import SupabaseAuthManager


class AuthManager:
    """Manages authentication and API key storage"""
    
    SERVICE_NAME = "avocavo-nutrition"
    CONFIG_DIR = Path.home() / ".avocavo"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    
    def __init__(self, base_url: str = "https://app.avocavo.app", verify_ssl: bool = True):
        self.base_url = base_url.rstrip('/')
        self.config_dir = self.CONFIG_DIR
        self.config_file = self.CONFIG_FILE
        self.verify_ssl = verify_ssl
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Configure SSL warnings suppression if SSL verification is disabled
        if not self.verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Initialize Supabase auth manager for unified OAuth
        self.supabase_auth = SupabaseAuthManager(base_url, verify_ssl)
    
    def login(self, email: str = None, password: str = None, provider: str = "google", use_supabase: bool = False) -> Dict:
        """
        Login with email/password or OAuth browser login
        
        Args:
            email: User email (for email/password login)
            password: User password (for email/password login)
            provider: OAuth provider ("google" or "github") for browser login
            use_supabase: Whether to use Supabase OAuth (recommended)
            
        Returns:
            Dictionary with user info and API key
            
        Raises:
            AuthenticationError: If login fails
        """
        # If email and password provided, use traditional login
        if email and password:
            return self._login_with_password(email, password)
        
        # Use Supabase OAuth or legacy OAuth as fallback
        if use_supabase:
            try:
                print("🔐 Using Supabase OAuth...")
                return self.supabase_auth.login(provider)
            except Exception as e:
                print(f"⚠️  Supabase OAuth failed, falling back to legacy OAuth: {e}")
                print("🔐 Using legacy OAuth as fallback...")
                return self._login_with_oauth(provider)
        
        # Legacy OAuth browser login (default - more reliable)
        print("🔐 Using reliable OAuth authentication...")
        try:
            return self._login_with_oauth(provider)
        except Exception as e:
            # If legacy OAuth also fails with datetime error, provide clear message
            if 'datetime' in str(e):
                raise AuthenticationError("Authentication service temporarily unavailable due to backend issues. Please try again later.")
            raise
        
    def _prompt_for_provider(self) -> str:
        """Prompt user to choose OAuth provider"""
        print("\n🔐 Choose OAuth Provider:")
        print("1. Google")
        print("2. GitHub")
        
        while True:
            choice = input("Enter choice (1-2): ").strip()
            if choice == "1":
                return "google"
            elif choice == "2":
                return "github"
            else:
                print("❌ Invalid choice. Please enter 1 or 2.")
                continue
    
    def _login_with_password(self, email: str, password: str) -> Dict:
        """Traditional email/password login"""
        try:
            try:
                response = requests.post(
                    f"{self.base_url}/api/auth/login",
                    json={
                        "email": email,
                        "password": password
                    },
                    timeout=30,
                    verify=self.verify_ssl
                )
            except requests.exceptions.SSLError as ssl_error:
                if self.verify_ssl:
                    # Try with system CA bundle as fallback
                    print("🔧 SSL verification failed, trying system CA bundle...")
                    system_ca_bundle = self._get_system_ca_bundle()
                    if system_ca_bundle:
                        try:
                            response = requests.post(
                                f"{self.base_url}/api/auth/login",
                                json={
                                    "email": email,
                                    "password": password
                                },
                                timeout=30,
                                verify=system_ca_bundle
                            )
                            print("✅ Successfully connected using system CA bundle")
                        except requests.exceptions.SSLError:
                            raise AuthenticationError(f"SSL certificate verification failed with both default and system CA bundles: {ssl_error}")
                    else:
                        raise AuthenticationError(f"SSL certificate verification failed: {ssl_error}")
                else:
                    raise AuthenticationError(f"Unexpected SSL error: {ssl_error}")
            
            if response.status_code == 401:
                raise AuthenticationError("Invalid email or password")
            elif response.status_code != 200:
                raise AuthenticationError(f"Login failed: {response.status_code}")
            
            data = response.json()
            
            if not data.get('success'):
                raise AuthenticationError(data.get('error', 'Login failed'))
            
            # Extract user info and API key
            user_info = data.get('user', {})
            api_key = user_info.get('api_key')
            
            if not api_key:
                raise AuthenticationError("No API key received")
            
            # Store API key securely
            self._store_api_key(email, api_key)
            
            # Store user config
            self._store_user_config({
                'email': email,
                'user_id': user_info.get('id'),
                'api_tier': user_info.get('api_tier', 'developer'),
                'logged_in_at': data.get('timestamp'),
                'login_method': 'password'
            })
            
            return {
                'success': True,
                'email': email,
                'api_tier': user_info.get('api_tier'),
                'api_key': api_key[:12] + "...",  # Masked for display
                'message': 'Successfully logged in'
            }
            
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Connection error: {str(e)}")
    
    def _login_with_oauth(self, provider: str) -> Dict:
        """OAuth browser login with Google or GitHub"""
        try:
            print(f"🔐 Initiating {provider.title()} OAuth login...")
            
            # Step 1: Initiate OAuth flow
            try:
                response = requests.post(
                    f"{self.base_url}/api/auth/login",
                    json={
                        "provider": provider,
                        "skip_supabase": True  # Tell backend to skip Supabase auth.users creation
                    },
                    timeout=30,
                    verify=self.verify_ssl  # Use configurable SSL verification
                )
            except requests.exceptions.SSLError as ssl_error:
                if self.verify_ssl:
                    # Try with system CA bundle as fallback
                    print("🔧 SSL verification failed, trying system CA bundle...")
                    system_ca_bundle = self._get_system_ca_bundle()
                    if system_ca_bundle:
                        try:
                            response = requests.post(
                                f"{self.base_url}/api/auth/login",
                                json={
                                    "provider": provider,
                                    "skip_supabase": True
                                },
                                timeout=30,
                                verify=system_ca_bundle
                            )
                            print("✅ Successfully connected using system CA bundle")
                        except requests.exceptions.SSLError:
                            raise AuthenticationError(f"SSL certificate verification failed with both default and system CA bundles. Please ensure you're connecting to the correct server: {ssl_error}")
                    else:
                        raise AuthenticationError(f"SSL certificate verification failed. Please ensure you're connecting to the correct server: {ssl_error}")
                else:
                    # This shouldn't happen if verify=False, but handle it anyway
                    raise AuthenticationError(f"Unexpected SSL error: {ssl_error}")
            
            if response.status_code != 200:
                data = response.json() if response.content else {}
                raise AuthenticationError(data.get('error', f'Failed to initiate {provider} login'))
            
            auth_data = response.json()
            if not auth_data.get('success'):
                raise AuthenticationError(auth_data.get('error', 'OAuth initiation failed'))
            
            session_id = auth_data.get('session_id')
            oauth_url = auth_data.get('oauth_url')
            
            if not session_id or not oauth_url:
                raise AuthenticationError("Invalid OAuth response from server")
            
            # Step 2: Open browser for user authentication
            print(f"🌐 Opening browser for {provider.title()} authentication...")
            print(f"📋 If browser doesn't open automatically, visit: {oauth_url}")
            
            try:
                webbrowser.open(oauth_url)
            except Exception:
                print("⚠️  Could not open browser automatically")
            
            # Step 3: Poll for completion
            print("⏳ Waiting for authentication to complete...")
            max_attempts = 60  # 5 minutes timeout
            attempt = 0
            
            while attempt < max_attempts:
                try:
                    try:
                        status_response = requests.get(
                            f"{self.base_url}/api/auth/status/{session_id}",
                            timeout=10,
                            verify=self.verify_ssl
                        )
                    except requests.exceptions.SSLError as ssl_error:
                        if self.verify_ssl:
                            # Try with system CA bundle as fallback
                            system_ca_bundle = self._get_system_ca_bundle()
                            if system_ca_bundle:
                                try:
                                    status_response = requests.get(
                                        f"{self.base_url}/api/auth/status/{session_id}",
                                        timeout=10,
                                        verify=system_ca_bundle
                                    )
                                except requests.exceptions.SSLError:
                                    raise AuthenticationError(f"SSL certificate verification failed during OAuth polling with both default and system CA bundles: {ssl_error}")
                            else:
                                raise AuthenticationError(f"SSL certificate verification failed during OAuth polling: {ssl_error}")
                        else:
                            # This shouldn't happen if verify=False, but handle it anyway
                            raise AuthenticationError(f"Unexpected SSL error during OAuth polling: {ssl_error}")
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        
                        if status_data.get('status') in ['completed', 'retrieved']:
                            # Success! Get OAuth token
                            auth_uuid = status_data.get('auth_uuid')
                            user_email = status_data.get('user_email')
                            
                            if auth_uuid and user_email:
                                # Exchange OAuth token for proper JWT token
                                print("🔄 Exchanging authentication tokens...")
                                
                                try:
                                    exchange_headers = {
                                        'Authorization': f'Bearer auth_uuid:{auth_uuid}',
                                        'Content-Type': 'application/json'
                                    }
                                    
                                    # Try token exchange with SSL fallback logic (same as OAuth polling)
                                    exchange_response = None
                                    try:
                                        exchange_response = requests.post(
                                            f"{self.base_url}/api/auth/exchange-token",
                                            headers=exchange_headers,
                                            timeout=30,
                                            verify=self.verify_ssl
                                        )
                                    except requests.exceptions.SSLError as ssl_error:
                                        if self.verify_ssl:
                                            # Try with system CA bundle as fallback
                                            print("🔧 SSL verification failed during token exchange, trying system CA bundle...")
                                            system_ca_bundle = self._get_system_ca_bundle()
                                            if system_ca_bundle:
                                                try:
                                                    exchange_response = requests.post(
                                                        f"{self.base_url}/api/auth/exchange-token",
                                                        headers=exchange_headers,
                                                        timeout=30,
                                                        verify=system_ca_bundle
                                                    )
                                                    print("✅ Token exchange successful using system CA bundle")
                                                except requests.exceptions.SSLError:
                                                    raise AuthenticationError(f"SSL certificate verification failed for token exchange with both default and system CA bundles: {ssl_error}")
                                            else:
                                                raise AuthenticationError(f"SSL certificate verification failed for token exchange: {ssl_error}")
                                        else:
                                            raise AuthenticationError(f"Unexpected SSL error during token exchange: {ssl_error}")
                                    
                                    if exchange_response.status_code != 200:
                                        exchange_data = exchange_response.json() if exchange_response.content else {}
                                        raise AuthenticationError(exchange_data.get('error', 'Token exchange failed'))
                                    
                                    exchange_data = exchange_response.json()
                                    if not exchange_data.get('success'):
                                        raise AuthenticationError(exchange_data.get('error', 'Token exchange failed'))
                                    
                                    jwt_token = exchange_data.get('access_token')
                                    user_info = exchange_data.get('user', {})
                                    
                                    if not jwt_token:
                                        raise AuthenticationError("No JWT token received from token exchange")
                                    
                                    # Store JWT token for identity and key management
                                    self._store_jwt_token(user_email, jwt_token)
                                    
                                    # Store user config with actual tier from server
                                    self._store_user_config({
                                        'email': user_email,
                                        'api_tier': user_info.get('api_tier', 'free'),
                                        'logged_in_at': time.time(),
                                        'login_method': 'oauth',
                                        'oauth_provider': provider
                                    })
                                    
                                    print(f"✅ Login successful! Welcome {user_email}")
                                    print(f"📊 Your tier: {user_info.get('api_tier', 'free')}")
                                    print("💡 Use av.create_api_key() to create an API key for making requests")
                                    
                                    # Break out of the polling loop
                                    return {
                                        'success': True,
                                        'email': user_email,
                                        'api_tier': user_info.get('api_tier', 'free'),
                                        'provider': provider,
                                        'message': f'{provider.title()} OAuth login successful'
                                    }
                                    
                                except requests.exceptions.RequestException as e:
                                    raise AuthenticationError(f"Token exchange failed: {str(e)}")
                            else:
                                raise AuthenticationError("Invalid response from OAuth completion")
                        
                        elif status_data.get('status') == 'error':
                            raise AuthenticationError(status_data.get('error', 'OAuth authentication failed'))
                        
                        # Still pending, continue polling
                        if attempt == 0:
                            print("👆 Please complete authentication in your browser...")
                        elif attempt % 10 == 0:  # Show progress every 10 attempts
                            print("⏳ Still waiting for authentication...")
                    
                    elif status_response.status_code == 404:
                        print(f"❌ Session not found (404). Attempt {attempt + 1}/{max_attempts}")
                        raise AuthenticationError("OAuth session expired. Please try again.")
                    elif status_response.status_code == 410:
                        # Session already retrieved, this is expected
                        print(f"❌ Session already used (410). Attempt {attempt + 1}/{max_attempts}")
                        raise AuthenticationError("OAuth session already used. Please try again.")
                    else:
                        print(f"❌ Unexpected status code: {status_response.status_code}. Response: {status_response.text[:200]}")
                
                except requests.exceptions.RequestException:
                    pass  # Network issues, continue trying
                
                time.sleep(5)  # Wait 5 seconds between polls
                attempt += 1
            
            raise AuthenticationError("OAuth login timed out. Please try again.")
            
        except AuthenticationError:
            raise
        except Exception as e:
            raise AuthenticationError(f"OAuth login failed: {str(e)}")
    
    def _get_system_ca_bundle(self) -> Optional[str]:
        """
        Detect system CA bundle location for automatic SSL fallback
        
        Returns:
            Path to system CA bundle if found, None otherwise
        """
        # Common system CA bundle locations (in order of preference)
        system_ca_paths = [
            '/etc/ssl/certs/ca-certificates.crt',  # Debian/Ubuntu
            '/etc/pki/tls/certs/ca-bundle.crt',    # CentOS/RHEL/Fedora
            '/etc/ssl/ca-bundle.pem',              # openSUSE
            '/usr/share/ssl/certs/ca-bundle.crt',  # Alternative locations
            '/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem',  # Newer RHEL/CentOS
            '/usr/local/share/certs/ca-root-nss.crt',  # FreeBSD
            '/etc/ssl/cert.pem',  # macOS/BSD
        ]
        
        for ca_path in system_ca_paths:
            if os.path.exists(ca_path):
                try:
                    # Verify the file is readable and non-empty
                    with open(ca_path, 'r') as f:
                        content = f.read(100)  # Read first 100 chars to verify
                        if content.strip() and 'BEGIN CERTIFICATE' in content:
                            return ca_path
                except (IOError, OSError):
                    continue
        
        return None
    
    def logout(self) -> Dict:
        """
        Logout current user and clear stored credentials
        
        Returns:
            Success message
        """
        # Log out from Supabase first
        self.supabase_auth.logout()
        
        # Legacy cleanup
        config = self._load_user_config()
        
        if config and config.get('email'):
            # Remove stored API key
            try:
                keyring.delete_password(self.SERVICE_NAME, config['email'])
            except keyring.errors.PasswordDeleteError:
                pass  # Key was already removed
        
        # Remove config file
        if self.config_file.exists():
            self.config_file.unlink()
        
        return {
            'success': True,
            'message': 'Successfully logged out'
        }
    
    def get_current_user(self) -> Optional[Dict]:
        """
        Get current logged-in user info
        
        Returns:
            User info dictionary or None if not logged in
        """
        config = self._load_user_config()
        
        if not config or not config.get('email'):
            return None
        
        # For OAuth users, check if we have a JWT session
        if config.get('login_method') == 'oauth':
            jwt_token = self._get_jwt_token(config['email'])
            if jwt_token:
                return {
                    'email': config['email'],
                    'api_tier': config.get('api_tier'),
                    'user_id': config.get('user_id'),
                    'logged_in_at': config.get('logged_in_at'),
                    'login_method': 'oauth',
                    'provider': config.get('oauth_provider'),
                    'has_jwt': True
                }
        
        # For password users, check for API key
        api_key = self._get_api_key(config['email'])
        if api_key:
            return {
                'email': config['email'],
                'api_tier': config.get('api_tier'),
                'user_id': config.get('user_id'),
                'api_key': api_key,
                'logged_in_at': config.get('logged_in_at'),
                'login_method': 'password'
            }
        
        return None
    
    def get_api_key(self) -> Optional[str]:
        """
        Get stored API key for current user
        
        Returns:
            Selected API key for nutrition calls, or JWT token if no API key selected
        """
        # Check Supabase auth first - JWT tokens work as API keys
        token = self.supabase_auth.get_access_token()
        if token:
            return token
        
        # Fallback to legacy auth
        config = self._load_user_config()
        if not config or not config.get('email'):
            return None
        
        # If user has selected an API key, return that for nutrition calls
        if config.get('selected_api_key'):
            return config['selected_api_key']
        
        # Otherwise return JWT token (for API key management operations)
        return self._get_api_key(config['email'])
    
    def is_logged_in(self) -> bool:
        """Check if user is currently logged in"""
        # Check Supabase auth first
        if self.supabase_auth.is_logged_in():
            return True
        
        # Fallback to legacy check
        return self.get_current_user() is not None
    
    def get_jwt_auth_headers(self) -> Dict[str, str]:
        """Get JWT authentication headers for API key management"""
        config = self._load_user_config()
        if not config or not config.get('email'):
            raise AuthenticationError("Not logged in. Please login first.")
        
        jwt_token = self._get_jwt_token(config['email'])
        if not jwt_token:
            raise AuthenticationError("No JWT token found. Please login again.")
        
        return {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }
    
    def list_api_keys(self) -> Dict:
        """
        List all API keys for the authenticated user
        
        Returns:
            Dictionary with list of API keys and usage information
        """
        try:
            headers = self.get_jwt_auth_headers()
            try:
                response = requests.get(f"{self.base_url}/api/keys", headers=headers, timeout=30, verify=self.verify_ssl)
            except requests.exceptions.SSLError as ssl_error:
                if self.verify_ssl:
                    system_ca_bundle = self._get_system_ca_bundle()
                    if system_ca_bundle:
                        try:
                            response = requests.get(f"{self.base_url}/api/keys", headers=headers, timeout=30, verify=system_ca_bundle)
                        except requests.exceptions.SSLError:
                            raise AuthenticationError(f"SSL certificate verification failed: {ssl_error}")
                    else:
                        raise AuthenticationError(f"SSL certificate verification failed: {ssl_error}")
                else:
                    raise AuthenticationError(f"Unexpected SSL error: {ssl_error}")
            
            if response.status_code == 401:
                raise AuthenticationError("Session expired. Please login again.")
            elif response.status_code != 200:
                raise AuthenticationError(f"Failed to list API keys: {response.status_code}")
            
            return response.json()
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Connection error: {str(e)}")
    
    def create_api_key(self, name: str = "Python Package Key", description: str = None, environment: str = "development") -> Dict:
        """
        Create a new API key
        
        Args:
            name: Name for the API key
            description: Optional description
            environment: Environment tag (development, staging, production)
            
        Returns:
            Dictionary with new API key information (full key shown only once)
        """
        try:
            headers = self.get_jwt_auth_headers()
            data = {
                "key_name": name,
                "description": description or "Created via Python package",
                "environment": environment
            }
            
            try:
                response = requests.post(f"{self.base_url}/api/keys", json=data, headers=headers, timeout=30, verify=self.verify_ssl)
            except requests.exceptions.SSLError as ssl_error:
                if self.verify_ssl:
                    system_ca_bundle = self._get_system_ca_bundle()
                    if system_ca_bundle:
                        try:
                            response = requests.post(f"{self.base_url}/api/keys", json=data, headers=headers, timeout=30, verify=system_ca_bundle)
                        except requests.exceptions.SSLError:
                            raise AuthenticationError(f"SSL certificate verification failed: {ssl_error}")
                    else:
                        raise AuthenticationError(f"SSL certificate verification failed: {ssl_error}")
                else:
                    raise AuthenticationError(f"Unexpected SSL error: {ssl_error}")
            
            if response.status_code == 401:
                raise AuthenticationError("Session expired. Please login again.")
            elif response.status_code not in [200, 201]:
                error_data = response.json() if response.content else {}
                raise AuthenticationError(error_data.get('error', f'Failed to create API key: {response.status_code}'))
            
            result = response.json()
            
            # Automatically store the new API key for use
            if result.get('key', {}).get('api_key'):
                config = self._load_user_config()
                if config and config.get('email'):
                    self._store_api_key(config['email'], result['key']['api_key'])
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Connection error: {str(e)}")
    
    def switch_to_api_key(self, api_key: str) -> Dict:
        """
        Switch to using a specific API key
        
        Args:
            api_key: The API key to switch to
            
        Returns:
            Success confirmation
        """
        config = self._load_user_config()
        if not config or not config.get('email'):
            raise AuthenticationError("Not logged in. Please login first.")
        
        # Store the API key
        self._store_api_key(config['email'], api_key)
        
        return {
            'success': True,
            'message': f'Switched to API key: {api_key[:12]}...',
            'api_key_preview': f'{api_key[:12]}...'
        }
    
    def delete_api_key(self, key_id: int) -> Dict:
        """
        Delete (deactivate) an API key
        
        Args:
            key_id: ID of the key to delete
            
        Returns:
            Dictionary with deletion confirmation
        """
        try:
            headers = self.get_jwt_auth_headers()
            try:
                response = requests.delete(f"{self.base_url}/api/keys/{key_id}", headers=headers, timeout=30, verify=self.verify_ssl)
            except requests.exceptions.SSLError as ssl_error:
                if self.verify_ssl:
                    system_ca_bundle = self._get_system_ca_bundle()
                    if system_ca_bundle:
                        try:
                            response = requests.delete(f"{self.base_url}/api/keys/{key_id}", headers=headers, timeout=30, verify=system_ca_bundle)
                        except requests.exceptions.SSLError:
                            raise AuthenticationError(f"SSL certificate verification failed: {ssl_error}")
                    else:
                        raise AuthenticationError(f"SSL certificate verification failed: {ssl_error}")
                else:
                    raise AuthenticationError(f"Unexpected SSL error: {ssl_error}")
            
            if response.status_code == 401:
                raise AuthenticationError("Session expired. Please login again.")
            elif response.status_code != 200:
                error_data = response.json() if response.content else {}
                raise AuthenticationError(error_data.get('error', f'Failed to delete API key: {response.status_code}'))
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Connection error: {str(e)}")
    
    def _store_api_key(self, email: str, api_key: str) -> None:
        """Store API key securely using keyring"""
        try:
            keyring.set_password(self.SERVICE_NAME, email, api_key)
        except Exception as e:
            # SECURITY: Do not store credentials in plaintext as fallback
            raise AuthenticationError(f"Unable to store API key securely. Please ensure your system keyring is available: {e}")
    
    def _store_jwt_token(self, email: str, jwt_token: str) -> None:
        """Store JWT token securely using keyring"""
        try:
            keyring.set_password(self.SERVICE_NAME, f"jwt_{email}", jwt_token)
        except Exception as e:
            # SECURITY: Do not store credentials in plaintext as fallback
            raise AuthenticationError(f"Unable to store JWT token securely. Please ensure your system keyring is available: {e}")
    
    def _get_api_key(self, email: str) -> Optional[str]:
        """Retrieve API key securely"""
        try:
            return keyring.get_password(self.SERVICE_NAME, email)
        except Exception:
            # SECURITY: No plaintext fallback for credential retrieval
            return None
    
    def _get_jwt_token(self, email: str) -> Optional[str]:
        """Retrieve JWT token securely"""
        try:
            return keyring.get_password(self.SERVICE_NAME, f"jwt_{email}")
        except Exception:
            # SECURITY: No plaintext fallback for credential retrieval
            return None
    
    def list_api_keys(self) -> Dict:
        """List all API keys for the current user using JWT authentication"""
        config = self._load_user_config()
        if not config or not config.get('email'):
            raise AuthenticationError("Not logged in")
        
        email = config['email']
        jwt_token = self._get_jwt_token(email)
        
        if not jwt_token:
            raise AuthenticationError("No valid session. Please login again.")
        
        try:
            response = self._make_jwt_request('GET', '/api/keys', jwt_token)
            if response.get('success'):
                return response  # Return full response with 'keys', 'success', 'total'
            else:
                raise AuthenticationError(response.get('error', 'Failed to list API keys'))
        except Exception as e:
            raise AuthenticationError(f"Failed to list API keys: {str(e)}")
    
    def switch_api_key(self, key_id: int = None) -> str:
        """
        Switch to use a specific API key for nutrition calls
        
        Args:
            key_id: ID of the key to switch to. If None, will show interactive selection.
            
        Returns:
            The full API key value that can be used for nutrition calls
            
        Example:
            # Interactive selection
            api_key = auth.switch_api_key()
            
            # Direct key ID
            api_key = auth.switch_api_key(123)
        """
        try:
            config = self._load_user_config()
            if not config or not config.get('email'):
                raise AuthenticationError("Not logged in. Please login first.")
            
            jwt_token = self._get_jwt_token(config['email'])
            if not jwt_token:
                raise AuthenticationError("JWT token not found. Please login again.")
            
            # If no key_id provided, user needs to select from available keys
            if key_id is None:
                keys_response = self.list_api_keys()
                keys = keys_response.get('keys', [])
                
                if not keys:
                    raise AuthenticationError("No API keys found. Please create an API key first.")
                
                # Show account-level credit info once
                if keys:
                    first_key = keys[0]
                    credits = first_key.get('credits', {})
                    if credits and credits.get('global_balance', 0) > 0:
                        print(f"💰 Account Credits: {credits.get('global_balance', 0)} credits available")
                    
                print("Available API keys:")
                for i, key in enumerate(keys, 1):
                    status = "🟢 ACTIVE" if key.get('is_active') else "🔴 INACTIVE"
                    
                    # Safely display API key with masking
                    api_key = key.get('api_key', 'N/A')
                    masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "****"
                    print(f"   [{i}] {key.get('key_name', 'Unnamed')}: {masked_key} ({status})")
                
                while True:
                    try:
                        choice = input("Select an API key (enter number): ").strip()
                        choice_idx = int(choice) - 1
                        if 0 <= choice_idx < len(keys):
                            key_id = keys[choice_idx]['id']
                            break
                        else:
                            print(f"Please enter a number between 1 and {len(keys)}")
                    except (ValueError, KeyboardInterrupt):
                        raise AuthenticationError("API key selection cancelled")
            
            # Now reveal the full API key using the key_id
            response = self._make_jwt_request('POST', f'/api/keys/{key_id}/reveal', jwt_token)
            
            if response.get('success'):
                full_api_key = response.get('api_key')
                key_name = response.get('key_name', 'Unknown')
                
                # Store the selected API key for future use
                config = self._load_user_config()
                config['selected_api_key'] = full_api_key
                config['selected_key_name'] = key_name
                config['selected_key_id'] = key_id
                self._store_user_config(config)
                
                print(f"✅ Switched to API key: {key_name}")
                return full_api_key
            else:
                raise AuthenticationError(response.get('error', 'Failed to reveal API key'))
                
        except Exception as e:
            raise AuthenticationError(f"Failed to switch API key: {str(e)}")
    
# Removed duplicate create_api_key method - using the one above with environment parameter
    
    def _make_jwt_request(self, method: str, endpoint: str, jwt_token: str, data: Dict = None):
        """Make authenticated request using JWT token"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            def make_request(verify_param):
                if method.upper() == 'GET':
                    return requests.get(url, headers=headers, verify=verify_param)
                elif method.upper() == 'POST':
                    return requests.post(url, headers=headers, json=data, verify=verify_param)
                else:
                    raise ValueError(f"Unsupported method: {method}")
            
            try:
                response = make_request(self.verify_ssl)
            except requests.exceptions.SSLError as ssl_error:
                if self.verify_ssl:
                    # Try with system CA bundle as fallback
                    system_ca_bundle = self._get_system_ca_bundle()
                    if system_ca_bundle:
                        try:
                            response = make_request(system_ca_bundle)
                        except requests.exceptions.SSLError:
                            raise AuthenticationError(f"SSL certificate verification failed with both default and system CA bundles: {ssl_error}")
                    else:
                        raise AuthenticationError(f"SSL certificate verification failed: {ssl_error}")
                else:
                    raise AuthenticationError(f"Unexpected SSL error: {ssl_error}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Request failed: {str(e)}")
    
    def _store_user_config(self, config: Dict) -> None:
        """Store user configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _load_user_config(self) -> Optional[Dict]:
        """Load user configuration"""
        if not self.config_file.exists():
            return None
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None


# Global auth manager instance
_auth_manager = AuthManager()


def login(email: str = None, password: str = None, provider: str = "google", base_url: str = "https://app.avocavo.app", verify_ssl: bool = True, use_supabase: bool = False) -> Dict:
    """
    Login to Avocavo and store API key securely
    
    Args:
        email: Your email (for email/password login)
        password: Your password (for email/password login)
        provider: OAuth provider ("google" or "github") for browser login
        base_url: API base URL (defaults to production)
        verify_ssl: Whether to verify SSL certificates (default: True, can disable for development)
        
    Returns:
        Login result with user info
        
    Examples:
        import avocavo as av
        
        # OAuth browser login (recommended)
        result = av.login()                    # Google OAuth (default)
        result = av.login(provider="google")   # Google OAuth (explicit)
        result = av.login(provider="github")   # GitHub OAuth
        
        # Email/password login (legacy)
        result = av.login("user@example.com", "password")
        
        if result['success']:
            print(f"Logged in as {result['email']}")
            
            # Now you can use the API without passing API key
            nutrition = av.analyze_ingredient("2 cups flour")
    """
    global _auth_manager
    _auth_manager = AuthManager(base_url, verify_ssl)
    return _auth_manager.login(email, password, provider, use_supabase)


def logout() -> Dict:
    """
    Logout and clear stored credentials
    
    Returns:
        Logout confirmation
        
    Example:
        result = av.logout()
        print(result['message'])  # "Successfully logged out"
    """
    return _auth_manager.logout()


def get_current_user() -> Optional[Dict]:
    """
    Get current logged-in user information
    
    Returns:
        User info dictionary or None if not logged in
        
    Example:
        user = av.get_current_user()
        if user:
            print(f"Logged in as: {user['email']}")
            print(f"Plan: {user['api_tier']}")
        else:
            print("Not logged in")
    """
    return _auth_manager.get_current_user()


def get_stored_api_key() -> Optional[str]:
    """
    Get stored API key for the current user
    
    Returns:
        API key or None if not logged in
    """
    return _auth_manager.get_api_key()


def is_logged_in() -> bool:
    """
    Check if user is currently logged in
    
    Returns:
        True if logged in, False otherwise
    """
    return _auth_manager.is_logged_in()


# For backwards compatibility with environment variables
def get_api_key_from_env() -> Optional[str]:
    """Get API key from environment variable"""
    return os.environ.get('AVOCAVO_API_KEY')


def get_api_key() -> Optional[str]:
    """
    Get API key from storage or environment
    Priority: logged-in user > environment variable
    """
    # First try logged-in user
    stored_key = get_stored_api_key()
    if stored_key:
        return stored_key
    
    # Fallback to environment variable
    return get_api_key_from_env()


def list_api_keys(base_url: str = "https://app.avocavo.app") -> Dict:
    """
    List all API keys for the authenticated user
    
    Args:
        base_url: API base URL
        
    Returns:
        Dictionary with list of API keys and usage information
        
    Example:
        keys = av.list_api_keys()
        for key in keys['keys']:
            print(f"{key['key_name']}: {key['monthly_usage']}/{key['monthly_limit']}")
    """
    global _auth_manager
    _auth_manager = AuthManager(base_url)
    return _auth_manager.list_api_keys()


def switch_api_key(key_id: int = None, base_url: str = "https://app.avocavo.app") -> str:
    """
    Switch to use a specific API key for nutrition calls
    
    Args:
        key_id: ID of the key to switch to. If None, will show interactive selection.
        base_url: API base URL
        
    Returns:
        The full API key value that can be used for nutrition calls
        
    Example:
        import avocavo as av
        
        # First login with OAuth
        av.login()
        
        # Interactive selection of API key
        av.switch_api_key()
        
        # Now nutrition calls will use the selected API key
        result = av.analyze_ingredient("1 cup rice")
    """
    global _auth_manager
    _auth_manager = AuthManager(base_url)
    return _auth_manager.switch_api_key(key_id)


def create_api_key(name: str = "Python Package Key", description: str = None, environment: str = "development", base_url: str = "https://app.avocavo.app") -> Dict:
    """
    Create a new API key and automatically switch to it
    
    Args:
        name: Name for the API key
        description: Optional description
        environment: Environment tag (development, staging, production)
        base_url: API base URL
        
    Returns:
        Dictionary with new API key information (full key shown only once)
        
    Example:
        import avocavo as av
        
        # First login with OAuth
        av.login()
        
        # Create and switch to new API key
        result = av.create_api_key("My App Key", 
                                 description="API key for my application",
                                 environment="production")
        
        # Safely display new API key with masking for security
        new_key = result['key']['api_key']
        masked_key = f"{new_key[:8]}...{new_key[-4:]}" if len(new_key) > 12 else "****"
        print(f"Created key: {masked_key}")
        print("💡 Full API key has been stored securely. Use av.get_current_user() to see active key.")
        
        # Now you can use the nutrition API
        nutrition = av.analyze_ingredient("2 cups flour")
    """
    global _auth_manager
    _auth_manager = AuthManager(base_url)
    return _auth_manager.create_api_key(name, description, environment)


def switch_to_api_key(api_key: str, base_url: str = "https://app.avocavo.app") -> Dict:
    """
    Switch to using a specific API key
    
    Args:
        api_key: The API key to switch to
        base_url: API base URL
        
    Returns:
        Success confirmation
        
    Example:
        av.switch_to_api_key("sk_prod_abc123...")
    """
    global _auth_manager
    _auth_manager = AuthManager(base_url)
    return _auth_manager.switch_to_api_key(api_key)


def delete_api_key(key_id: int, base_url: str = "https://app.avocavo.app") -> Dict:
    """
    Delete (deactivate) an API key
    
    Args:
        key_id: ID of the key to delete
        base_url: API base URL
        
    Returns:
        Dictionary with deletion confirmation
        
    Example:
        av.delete_api_key(123)
    """
    global _auth_manager
    _auth_manager = AuthManager(base_url)
    return _auth_manager.delete_api_key(key_id)


def auto_setup_api_key(base_url: str = "https://app.avocavo.app") -> str:
    """
    Auto-setup API key for seamless nutrition analysis
    
    This function:
    1. Checks if user has a selected API key
    2. If no keys exist, creates one automatically  
    3. If exactly one key exists, selects it automatically
    4. If multiple keys exist, prompts user to choose
    
    Returns:
        The selected API key
        
    Example:
        import avocavo as av
        av.login()
        av.auto_setup_api_key()  # One-time setup
        result = av.analyze_ingredient("1 cup rice")  # Now works!
    """
    global _auth_manager
    _auth_manager = AuthManager(base_url)
    
    # Check if user already has a selected API key
    current_key = _auth_manager.get_api_key()
    if current_key and not current_key.startswith('eyJ'):  # Not a JWT token
        print(f"✅ Using existing API key: {current_key[:12]}...")
        return current_key
    
    # List available API keys
    try:
        keys_response = list_api_keys(base_url)
        keys = keys_response.get('keys', [])
        
        if len(keys) == 0:
            # No API keys - create one automatically
            print("🔧 No API keys found. Creating one for you...")
            result = create_api_key("Python Package Auto-Key", "Auto-created for Python package")
            print(f"✅ Created and selected API key: {result['name']}")
            return result['api_key']
            
        elif len(keys) == 1:
            # Exactly one key - select it automatically
            key = keys[0]
            print(f"🔄 Auto-selecting your API key: {key['name']}")
            selected_key = switch_api_key(key['id'])
            return selected_key
            
        else:
            # Multiple keys - let user choose
            print(f"💡 You have {len(keys)} API keys. Please select one:")
            selected_key = switch_api_key()
            return selected_key
            
    except Exception as e:
        raise AuthenticationError(f"Failed to setup API key: {str(e)}")


if __name__ == "__main__":
    # Demo authentication
    print("🔐 Avocavo Nutrition API Authentication")
    print("=" * 40)
    
    user = get_current_user()
    if user:
        print(f"✅ Logged in as: {user['email']}")
        print(f"📊 Plan: {user['api_tier']}")
        print(f"🔑 API Key: {user.get('api_key', '')[:12]}...")
    else:
        print("❌ Not logged in")
        print("\nTo login:")
        print("  import avocavo as av")
        print('  av.login("your@email.com", "password")')