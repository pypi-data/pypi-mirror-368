"""
Supabase-based authentication module for Avocavo Nutrition API
Provides unified OAuth authentication using Supabase native flows
"""

import os
import json
import keyring
import requests
import webbrowser
import time
import datetime
from datetime import datetime as dt
import secrets
import http.server
import socketserver
import threading
from urllib.parse import urlparse, parse_qs
from typing import Optional, Dict, List
from pathlib import Path
from .exceptions import ApiError, AuthenticationError

from supabase import create_client, Client


class SupabaseAuthManager:
    """Manages Supabase OAuth authentication and session storage"""
    
    SERVICE_NAME = "avocavo-nutrition"
    CONFIG_DIR = Path.home() / ".avocavo"
    CONFIG_FILE = CONFIG_DIR / "supabase_config.json"
    
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
        
        # Initialize Supabase client
        self.supabase_config = None
        self.supabase = None
    
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
    
    def _get_supabase_config(self) -> bool:
        """Get Supabase configuration from backend"""
        try:
            # Try with SSL verification first
            try:
                response = requests.get(f"{self.base_url}/api/auth/supabase-config", timeout=10, verify=self.verify_ssl)
            except requests.exceptions.SSLError as ssl_error:
                if self.verify_ssl:
                    # Try with system CA bundle as fallback
                    print("🔧 SSL verification failed, trying system CA bundle...")
                    system_ca_bundle = self._get_system_ca_bundle()
                    if system_ca_bundle:
                        try:
                            response = requests.get(f"{self.base_url}/api/auth/supabase-config", timeout=10, verify=system_ca_bundle)
                            print("✅ Successfully connected using system CA bundle")
                        except requests.exceptions.SSLError:
                            raise AuthenticationError(f"SSL certificate verification failed with both default and system CA bundles: {ssl_error}")
                    else:
                        raise AuthenticationError(f"SSL certificate verification failed: {ssl_error}")
                else:
                    raise AuthenticationError(f"Unexpected SSL error: {ssl_error}")
            
            if response.status_code != 200:
                print(f"❌ Failed to get Supabase config: HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if not data.get('success'):
                print(f"❌ Supabase config error: {data.get('error', 'Unknown error')}")
                return False
            
            self.supabase_config = data['config']
            self.supabase = create_client(
                self.supabase_config['url'],
                self.supabase_config['anon_key']
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Supabase: {e}")
            return False
    
    def login(self, provider: str = "google") -> Dict:
        """
        Login using Supabase OAuth with retry logic for NULL field issues
        
        Args:
            provider: OAuth provider ("google", "github", etc.)
            
        Returns:
            Dictionary with user info and session data
            
        Raises:
            AuthenticationError: If login fails
        """
        
        print(f"🔐 Starting {provider} OAuth login with Supabase...")
        print("⚠️  Note: Supabase may have NULL field scanning issues - will retry if needed")
        
        # Get Supabase configuration
        if not self._get_supabase_config():
            raise AuthenticationError("Failed to get Supabase configuration")
        
        try:
            # Create a temporary local server for OAuth callback
            callback_server = self._create_callback_server()
            callback_url = f"http://localhost:{callback_server.port}/callback"
            
            print("🌐 Opening browser for authentication...")
            
            # Start OAuth flow with Supabase
            response = self.supabase.auth.sign_in_with_oauth({
                "provider": provider,
                "options": {
                    "redirect_to": callback_url,
                    "query_params": {
                        "access_type": "offline",
                        "prompt": "consent"
                    }
                }
            })
            
            if response.url:
                try:
                    webbrowser.open(response.url)
                except Exception:
                    print(f"⚠️  Could not open browser automatically")
                    print(f"Please manually open: {response.url}")
            
            # Wait for callback
            auth_result = callback_server.wait_for_callback()
            callback_server.shutdown()
            
            if auth_result['success']:
                print(f"✅ Login successful! Welcome {auth_result['user']['email']}")
                
                # Store session data
                self._store_session(auth_result['session'])
                
                return {
                    'user': auth_result['user'],
                    'session': auth_result['session'],
                    'provider': provider
                }
            else:
                raise AuthenticationError(f"Login failed: {auth_result['error']}")
                
        except Exception as e:
            raise AuthenticationError(f"OAuth login failed: {str(e)}")
    
    def _create_callback_server(self):
        """Create a local HTTP server to handle OAuth callback"""
        
        class CallbackHandler(http.server.BaseHTTPRequestHandler):
            def __init__(self, auth_manager, *args, **kwargs):
                self.auth_manager = auth_manager
                super().__init__(*args, **kwargs)
            
            def do_GET(self):
                # Parse the callback URL
                parsed_url = urlparse(self.path)
                query_params = parse_qs(parsed_url.query)
                
                if parsed_url.path == '/callback':
                    code = query_params.get('code', [None])[0]
                    access_token = query_params.get('access_token', [None])[0]
                    error = query_params.get('error', [None])[0]
                    error_description = query_params.get('error_description', [None])[0]
                    
                    # Send response to browser
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    # If no query params, send HTML that can extract fragment tokens
                    if not code and not access_token and not error:
                        html = """
                        <html>
                            <head><title>OAuth Callback</title></head>
                            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                                <h2>🔐 Processing Authentication...</h2>
                                <p>Please wait while we complete your login.</p>
                                <script>
                                    // Extract token from URL fragment and send to server
                                    const fragment = window.location.hash.substring(1);
                                    const params = new URLSearchParams(fragment);
                                    const access_token = params.get('access_token');
                                    const error = params.get('error');
                                    
                                    if (access_token) {
                                        // Send token to server as query parameter
                                        fetch('/callback?access_token=' + encodeURIComponent(access_token))
                                            .then(() => {
                                                document.body.innerHTML = '<h2 style="color: green;">✅ Authentication Successful!</h2><p>You can close this window and return to the terminal.</p>';
                                            })
                                            .catch(err => {
                                                document.body.innerHTML = '<h2 style="color: red;">❌ Authentication Failed</h2><p>Could not process token.</p>';
                                            });
                                    } else if (error) {
                                        fetch('/callback?error=' + encodeURIComponent(error))
                                            .then(() => {
                                                document.body.innerHTML = '<h2 style="color: red;">❌ Authentication Failed</h2><p>' + error + '</p>';
                                            });
                                    } else {
                                        document.body.innerHTML = '<h2 style="color: orange;">⚠️ No Authentication Data</h2><p>No token or error found in URL.</p>';
                                    }
                                </script>
                            </body>
                        </html>
                        """
                        self.wfile.write(html.encode())
                        return
                    
                    if error:
                        html = f"""
                        <html>
                            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                                <h2 style="color: red;">❌ Authentication Failed</h2>
                                <p>{error_description or error}</p>
                                <p>You can close this window.</p>
                            </body>
                        </html>
                        """
                        self.wfile.write(html.encode())
                        self.server.callback_result = {'success': False, 'error': error_description or error}
                        
                    elif access_token:
                        html = """
                        <html>
                            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                                <h2 style="color: green;">✅ Authentication Successful!</h2>
                                <p>Token received. You can close this window and return to the terminal.</p>
                            </body>
                        </html>
                        """
                        self.wfile.write(html.encode())
                        
                        try:
                            # Use the access token directly to get user info
                            # Wrap in additional error handling for datetime/NULL issues
                            from supabase import create_client
                            temp_supabase = create_client(self.auth_manager.supabase_config['url'], self.auth_manager.supabase_config['anon_key'])
                            
                            # Try to get user info, but handle Supabase-specific errors
                            try:
                                response = temp_supabase.auth.get_user(access_token)
                            except Exception as supabase_error:
                                # Handle datetime/NULL field errors at the Supabase SDK level
                                error_str = str(supabase_error)
                                if ('datetime' in error_str or 
                                    'converting NULL to string' in error_str or 
                                    'recovery_token' in error_str):
                                    self.server.callback_result = {
                                        'success': False, 
                                        'error': f'Supabase SDK error: {error_str}'
                                    }
                                    return
                                else:
                                    raise supabase_error
                            
                            if response.user:
                                # Create a simple session object with just the needed fields
                                class MockSession:
                                    def __init__(self, access_token, user, expires_at):
                                        self.access_token = access_token
                                        self.user = user
                                        self.expires_at = expires_at
                                        self.refresh_token = None
                                
                                mock_session = MockSession(
                                    access_token=access_token,
                                    user=response.user,
                                    expires_at=int(time.time()) + 3600  # 1 hour from now
                                )
                                self.server.callback_result = {'success': True, 'session': mock_session, 'user': response.user}
                            else:
                                self.server.callback_result = {'success': False, 'error': 'Could not verify token'}
                        except Exception as e:
                            # Check if this is a known Supabase issue
                            error_str = str(e)
                            if ('converting NULL to string' in error_str or 
                                'recovery_token' in error_str or
                                'datetime' in error_str or
                                'name \'datetime\' is not defined' in error_str):
                                self.server.callback_result = {
                                    'success': False, 
                                    'error': f'Known Supabase issue: {error_str}'
                                }
                            else:
                                self.server.callback_result = {'success': False, 'error': str(e)}
                    
                    elif code:
                        html = """
                        <html>
                            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                                <h2 style="color: green;">✅ Authentication Successful!</h2>
                                <p>You can close this window and return to the terminal.</p>
                            </body>
                        </html>
                        """
                        self.wfile.write(html.encode())
                        
                        try:
                            # Exchange code for session using Supabase
                            session_response = self.auth_manager.supabase.auth.exchange_code_for_session(code)
                            
                            if session_response.session:
                                self.server.callback_result = {
                                    'success': True,
                                    'session': session_response.session,
                                    'user': session_response.user
                                }
                            else:
                                self.server.callback_result = {'success': False, 'error': 'Failed to exchange code for session'}
                                
                        except Exception as e:
                            self.server.callback_result = {'success': False, 'error': str(e)}
                    
                    else:
                        html = """
                        <html>
                            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                                <h2 style="color: orange;">⚠️ Incomplete Authentication</h2>
                                <p>No authorization code received.</p>
                            </body>
                        </html>
                        """
                        self.wfile.write(html.encode())
                        self.server.callback_result = {'success': False, 'error': 'No authorization code received'}
                
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                # Suppress server logs
                pass
        
        class CallbackServer:
            def __init__(self, auth_manager):
                self.auth_manager = auth_manager
                self.port = self._find_free_port()
                self.callback_result = None
                
                # Create handler with access to auth_manager
                handler = lambda *args, **kwargs: CallbackHandler(auth_manager, *args, **kwargs)
                
                self.httpd = socketserver.TCPServer(("localhost", self.port), handler)
                self.httpd.callback_result = None
                
                # Start server in background thread
                self.server_thread = threading.Thread(target=self.httpd.serve_forever)
                self.server_thread.daemon = True
                self.server_thread.start()
            
            def _find_free_port(self):
                import socket
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', 0))
                    s.listen(1)
                    return s.getsockname()[1]
            
            def wait_for_callback(self, timeout=10):
                """Wait for OAuth callback with timeout"""
                start_time = time.time()
                
                while time.time() - start_time < timeout:
                    if self.httpd.callback_result is not None:
                        # Shutdown server immediately when we get a result
                        try:
                            self.httpd.shutdown()
                        except:
                            pass
                        return self.httpd.callback_result
                    time.sleep(0.1)  # Check more frequently
                
                return {'success': False, 'error': 'Timeout waiting for authentication'}
            
            def shutdown(self):
                """Shutdown the callback server"""
                self.httpd.shutdown()
                self.server_thread.join(timeout=1)
        
        return CallbackServer(self)
    
    def _store_session(self, session) -> None:
        """Store Supabase session data securely"""
        # Convert expires_at to timestamp if it's a datetime object
        expires_at = session.expires_at
        if hasattr(expires_at, 'timestamp'):
            expires_at = expires_at.timestamp()
        elif expires_at is not None:
            expires_at = int(expires_at)
        
        # Extract user info safely - the user object might have datetime fields
        user_id = getattr(session.user, 'id', None)
        user_email = getattr(session.user, 'email', None)
        
        # If user is a dict-like object, handle it differently
        if hasattr(session.user, '__dict__'):
            user_dict = session.user.__dict__
            user_id = user_dict.get('id') or user_id
            user_email = user_dict.get('email') or user_email
        elif hasattr(session.user, 'get'):
            user_id = session.user.get('id') or user_id
            user_email = session.user.get('email') or user_email
        
        session_data = {
            'user_id': user_id,
            'email': user_email,
            'access_token': session.access_token,
            'refresh_token': session.refresh_token,
            'expires_at': expires_at,
            'login_time': time.time(),
            'provider': 'supabase-oauth'
        }
        
        # Store session data in config file
        with open(self.config_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Store tokens securely in keyring
        try:
            keyring.set_password(self.SERVICE_NAME, f"jwt_{session.user.email}", session.access_token)
            if session.refresh_token:
                keyring.set_password(self.SERVICE_NAME, f"refresh_{session.user.email}", session.refresh_token)
        except Exception as e:
            print(f"⚠️  Could not store tokens securely: {e}")
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        try:
            if not self.config_file.exists():
                return False
            
            with open(self.config_file, 'r') as f:
                session_data = json.load(f)
            
            # Check if session is expired
            if session_data.get('expires_at'):
                if time.time() > session_data['expires_at']:
                    return False
            
            # Check if we have an access token
            return bool(session_data.get('access_token'))
            
        except Exception:
            return False
    
    def get_access_token(self) -> Optional[str]:
        """Get current access token"""
        try:
            if not self.config_file.exists():
                return None
            
            with open(self.config_file, 'r') as f:
                session_data = json.load(f)
            
            email = session_data.get('email')
            if email:
                # Try to get from keyring first
                try:
                    token = keyring.get_password(self.SERVICE_NAME, f"jwt_{email}")
                    if token:
                        return token
                except Exception:
                    pass
            
            # Fallback to config file
            return session_data.get('access_token')
            
        except Exception:
            return None
    
    def get_user_info(self) -> Dict:
        """Get current user information"""
        try:
            if not self.config_file.exists():
                return {}
            
            with open(self.config_file, 'r') as f:
                session_data = json.load(f)
            
            return {
                'id': session_data.get('user_id'),
                'email': session_data.get('email'),
                'provider': session_data.get('provider', 'supabase-oauth')
            }
            
        except Exception:
            return {}
    
    def logout(self) -> None:
        """Logout and clear stored session"""
        try:
            # Sign out from Supabase
            if self.supabase:
                self.supabase.auth.sign_out()
        except Exception as e:
            print(f"⚠️  Could not sign out from Supabase: {e}")
        
        # Remove stored credentials
        user_info = self.get_user_info()
        if user_info.get('email'):
            email = user_info['email']
            try:
                keyring.delete_password(self.SERVICE_NAME, f"jwt_{email}")
                keyring.delete_password(self.SERVICE_NAME, f"refresh_{email}")
            except Exception:
                pass
        
        # Remove config file
        if self.config_file.exists():
            self.config_file.unlink()
        
        print("✅ Successfully logged out")
    
    def get_api_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        token = self.get_access_token()
        if not token:
            raise AuthenticationError("Not logged in. Please login first.")
        
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }