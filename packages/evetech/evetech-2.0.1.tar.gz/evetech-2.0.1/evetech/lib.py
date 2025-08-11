from flask import Flask, request, redirect, session, jsonify
import requests
import os
import base64
import json
import threading
import time
from datetime import datetime, timedelta
from urllib.parse import urlencode, quote

class Evetech:
    """EVE Online ESI OAuth handler class"""
    
    def __init__(self, client_id, client_secret, redirect_uri='http://localhost:8000/callback', port=8000, tokens_file='tokens.json'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.port = port
        self.tokens_file = tokens_file
        
        # Token data storage - now supports multiple characters
        self.tokens = {}  # Dictionary with character_id as key
        self.current_character = None  # Currently active character_id
        
        # Load existing tokens on initialization
        self._load_tokens()
        
        # EVE OAuth configuration
        self.oauth_config = {
            'authorization_url': 'https://login.eveonline.com/v2/oauth/authorize/',
            'token_url': 'https://login.eveonline.com/v2/oauth/token/',
            'verify_url': 'https://login.eveonline.com/oauth/verify',
            'esi_base_url': 'https://esi.evetech.net/latest'
        }
        
        # Default scopes - can be customized
        self.scopes = [
            'publicData',
            'esi-characters.read_blueprints.v1',
            'esi-characters.read_corporation_roles.v1',
            'esi-wallet.read_character_wallet.v1',
            'esi-skills.read_skills.v1',
            'esi-assets.read_assets.v1'
        ]
        
        # Flask app setup
        self.app = Flask(__name__)
        self.app.secret_key = os.urandom(24)
        self._setup_routes()
    
    def set_scopes(self, scopes):
        """Set custom EVE SSO scopes"""
        self.scopes = scopes
    
    def _setup_routes(self):
        """Configure Flask routes"""
        
        @self.app.route('/login')
        def login():
            import secrets
            
            # Generate secure state
            state = secrets.token_urlsafe(32)
            session['oauth_state'] = state
            
            params = {
                'response_type': 'code',
                'redirect_uri': self.redirect_uri,
                'client_id': self.client_id,
                'scope': ' '.join(self.scopes),
                'state': state
            }
            
            auth_url = f"{self.oauth_config['authorization_url']}?{urlencode(params)}"
            return redirect(auth_url)
        
        @self.app.route('/callback')
        def eve_oauth_callback():
            # Error handling
            error = request.args.get('error')
            if error:
                error_desc = request.args.get('error_description', 'Unknown error')
                return jsonify({'error': f'EVE SSO error: {error} - {error_desc}'}), 400
            
            # Get authorization code
            code = request.args.get('code')
            state = request.args.get('state')
            
            if not code:
                return jsonify({'error': 'No authorization code received from EVE SSO'}), 400
            
            # Verify state (security)
            stored_state = session.get('oauth_state')
            if not stored_state or state != stored_state:
                return jsonify({'error': 'Invalid state parameter'}), 400
            
            # Clean state from session
            session.pop('oauth_state', None)
            
            try:
                # Exchange code for access token
                token_response = self._exchange_code_for_token(code)
                
                if not token_response:
                    return jsonify({'error': 'Failed to obtain access token from EVE SSO'}), 400
                
                access_token = token_response.get('access_token')
                refresh_token = token_response.get('refresh_token')
                expires_in = token_response.get('expires_in', 1200)
                
                # Verify token and get character info
                character_info = self._verify_eve_token(access_token)
                
                if not character_info:
                    return jsonify({'error': 'Failed to verify token with EVE SSO'}), 400
                
                # Store token data for this character
                character_id = character_info['CharacterID']
                character_name = character_info['CharacterName']
                self.tokens[character_id] = {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_timestamp': datetime.now(),
                    'expires_in': expires_in,
                    'character_id': character_id,
                    'character_name': character_name,
                    'character_owner_hash': character_info['CharacterOwnerHash'],
                    'scopes': character_info.get('Scopes', '').split(' ') if character_info.get('Scopes') else []
                }
                
                # Set as current active character
                self.current_character = character_id
                
                # Save tokens to file
                self._save_tokens()
                
                # Schedule server shutdown after token received
                threading.Thread(target=self._shutdown_server, daemon=True).start()
                
                return jsonify({
                    'message': 'EVE SSO authentication successful - Server will shutdown in 3 seconds',
                    'character': {
                        'id': character_info['CharacterID'],
                        'name': character_info['CharacterName'],
                        'scopes': character_info.get('Scopes', '').split(' ') if character_info.get('Scopes') else []
                    }
                })
                
            except requests.exceptions.RequestException as e:
                return jsonify({'error': f'EVE SSO request failed: {str(e)}'}), 500
            except Exception as e:
                return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
    
    def _exchange_code_for_token(self, code):
        """Exchange authorization code for access token"""
        
        # EVE SSO uses Basic Auth with client_id:client_secret encoded in base64
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'login.eveonline.com'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': code
        }
        
        response = requests.post(self.oauth_config['token_url'], headers=headers, data=data)
        response.raise_for_status()
        
        return response.json()  # Return full token response including refresh_token
    
    def _verify_eve_token(self, access_token):
        """Verify token and get character information"""
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': 'Evetech/1.3'
        }
        
        response = requests.get(self.oauth_config['verify_url'], headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def _shutdown_server(self):
        """Function to shutdown Flask server after receiving token"""
        time.sleep(3)  # Wait 3 seconds for response to be sent
        print("\n=== Token received successfully! ===")
        if self.current_character and self.current_character in self.tokens:
            current_data = self.tokens[self.current_character]
            print(f"Character ID: {current_data['character_id']}")
            print(f"Character Name: {current_data['character_name']}")
            print(f"Access Token: {current_data['access_token'][:20]}...")
        print("Shutting down server...")
        
        # Force shutdown of Flask server
        os._exit(0)
    
    def _load_tokens(self):
        """Load tokens from JSON file if it exists"""
        try:
            if os.path.exists(self.tokens_file):
                with open(self.tokens_file, 'r') as f:
                    data = json.load(f)
                
                # Convert string keys back to integers and datetime strings back to datetime objects
                for char_id_str, token_data in data.get('tokens', {}).items():
                    char_id = int(char_id_str)
                    
                    # Convert timestamp string back to datetime object
                    if token_data.get('token_timestamp'):
                        token_data['token_timestamp'] = datetime.fromisoformat(token_data['token_timestamp'])
                    
                    self.tokens[char_id] = token_data
                
                # Restore current character
                if data.get('current_character'):
                    self.current_character = int(data['current_character'])
                
                print(f"Loaded {len(self.tokens)} character tokens from {self.tokens_file}")
                
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Error loading tokens from {self.tokens_file}: {e}")
            print("Starting with empty token storage")
            self.tokens = {}
            self.current_character = None
        except Exception as e:
            print(f"Unexpected error loading tokens: {e}")
            self.tokens = {}
            self.current_character = None
    
    def _save_tokens(self):
        """Save current tokens to JSON file"""
        try:
            # Prepare data for JSON serialization
            data = {
                'tokens': {},
                'current_character': self.current_character
            }
            
            # Convert datetime objects to ISO format strings and integer keys to strings
            for char_id, token_data in self.tokens.items():
                serializable_data = token_data.copy()
                
                # Convert datetime to ISO format string
                if serializable_data.get('token_timestamp'):
                    serializable_data['token_timestamp'] = serializable_data['token_timestamp'].isoformat()
                
                data['tokens'][str(char_id)] = serializable_data
            
            # Write to file
            with open(self.tokens_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"Saved {len(self.tokens)} character tokens to {self.tokens_file}")
            
        except Exception as e:
            print(f"Error saving tokens to {self.tokens_file}: {e}")
    
    def save_tokens(self):
        """Public method to manually save tokens to file"""
        self._save_tokens()
    
    def get_token_data(self, character_id=None):
        """Retrieve stored token data for a character"""
        if character_id is None:
            character_id = self.current_character
        
        if not character_id or character_id not in self.tokens:
            return {}
        
        return self.tokens[character_id].copy()
    
    def get_all_tokens(self):
        """Get all stored tokens"""
        return {char_id: data.copy() for char_id, data in self.tokens.items()}
    
    def get_character_list(self):
        """Get list of authenticated characters as {character_id: character_name}"""
        return {char_id: data['character_name'] for char_id, data in self.tokens.items()}
    
    def set_current_character(self, character_id):
        """Set the active character for operations"""
        if character_id not in self.tokens:
            available = {char_id: data['character_name'] for char_id, data in self.tokens.items()}
            raise ValueError(f"Character ID '{character_id}' not found. Available: {available}")
        
        self.current_character = character_id
        return True
    
    def get_current_character(self):
        """Get the currently active character ID"""
        return self.current_character
    
    def get_current_character_name(self):
        """Get the currently active character name"""
        if not self.current_character or self.current_character not in self.tokens:
            return None
        return self.tokens[self.current_character]['character_name']
    
    def remove_character(self, character_id):
        """Remove a character's token data"""
        if character_id in self.tokens:
            del self.tokens[character_id]
            if self.current_character == character_id:
                # Set new current character if available
                self.current_character = next(iter(self.tokens.keys())) if self.tokens else None
            
            # Save changes to file
            self._save_tokens()
            return True
        return False
    
    def get_character_id_by_name(self, character_name):
        """Get character ID by character name"""
        for char_id, data in self.tokens.items():
            if data['character_name'] == character_name:
                return char_id
        return None
    
    def get_access_token(self, character_id=None):
        """Get access token for a character"""
        if character_id is None:
            character_id = self.current_character
            
        if not character_id or character_id not in self.tokens:
            return None
            
        return self.tokens[character_id].get('access_token')
    
    def get_refresh_token(self, character_id=None):
        """Get refresh token for a character"""
        if character_id is None:
            character_id = self.current_character
            
        if not character_id or character_id not in self.tokens:
            return None
            
        return self.tokens[character_id].get('refresh_token')
    
    def get_character_info(self, character_id=None):
        """Get character information"""
        if character_id is None:
            character_id = self.current_character
            
        if not character_id or character_id not in self.tokens:
            return {}
            
        token_data = self.tokens[character_id]
        return {
            'character_id': token_data.get('character_id'),
            'character_name': token_data.get('character_name'),
            'character_owner_hash': token_data.get('character_owner_hash')
        }
    
    def is_token_expired(self, character_id=None):
        """Check if a character's token is expired"""
        if character_id is None:
            character_id = self.current_character
            
        if not character_id or character_id not in self.tokens:
            return True
        
        token_data = self.tokens[character_id]
        if not token_data.get('token_timestamp'):
            return True
        
        token_age = datetime.now() - token_data['token_timestamp']
        expires_in_seconds = token_data.get('expires_in', 1200)
        
        return token_age.total_seconds() >= expires_in_seconds
    
    def get_token_expiry_time(self, character_id=None):
        """Get when a character's token will expire"""
        if character_id is None:
            character_id = self.current_character
            
        if not character_id or character_id not in self.tokens:
            return None
        
        token_data = self.tokens[character_id]
        if not token_data.get('token_timestamp'):
            return None
        
        expires_in_seconds = token_data.get('expires_in', 1200)
        return token_data['token_timestamp'] + timedelta(seconds=expires_in_seconds)
    
    def refresh_access_token(self, character_id=None):
        """Use refresh token to get a new access token for a character"""
        if character_id is None:
            character_id = self.current_character
            
        if not character_id or character_id not in self.tokens:
            raise Exception(f'Character ID {character_id} not found')
        
        token_data = self.tokens[character_id]
        refresh_token = token_data.get('refresh_token')
        character_name = token_data.get('character_name', str(character_id))
        
        if not refresh_token:
            raise Exception(f'No refresh token available for {character_name} ({character_id}) - need to re-authenticate')
        
        try:
            # EVE SSO uses Basic Auth with client_id:client_secret encoded in base64
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Host': 'login.eveonline.com'
            }
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
            
            response = requests.post(self.oauth_config['token_url'], headers=headers, data=data)
            response.raise_for_status()
            
            token_response = response.json()
            
            # Update token data with new access token
            self.tokens[character_id].update({
                'access_token': token_response.get('access_token'),
                'refresh_token': token_response.get('refresh_token', refresh_token),  # Sometimes new refresh token
                'token_timestamp': datetime.now(),
                'expires_in': token_response.get('expires_in', 1200)
            })
            
            print(f"Token refreshed successfully for {character_name} ({character_id}) at {datetime.now()}")
            
            # Save updated tokens to file
            self._save_tokens()
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to refresh token for {character_name} ({character_id}): {str(e)}")
            return False
    
    def ensure_valid_token(self, character_id=None):
        """Ensure we have a valid token for a character, refresh if needed"""
        if character_id is None:
            character_id = self.current_character
            
        if not character_id or character_id not in self.tokens:
            raise Exception(f'Character ID {character_id} not authenticated - need to authenticate first')
        
        character_name = self.tokens[character_id].get('character_name', str(character_id))
        
        if self.is_token_expired(character_id):
            print(f"Token expired for {character_name} ({character_id}), attempting to refresh...")
            if not self.refresh_access_token(character_id):
                raise Exception(f'Token expired and refresh failed for {character_name} ({character_id}) - need to re-authenticate')
        
        return True
    
    def get_character_info(self):
        """Get character information"""
        return {
            'character_id': self.token_data.get('character_id'),
            'character_name': self.token_data.get('character_name'),
            'character_owner_hash': self.token_data.get('character_owner_hash')
        }
    
    def is_authenticated(self, character_id=None):
        """Check if we have a valid token for a character"""
        if character_id is None:
            character_id = self.current_character
            
        if not character_id:
            return False
            
        return character_id in self.tokens and self.tokens[character_id].get('access_token') is not None
    
    def has_scope(self, scope, character_id=None):
        """Check if a character's token has specific scope"""
        if character_id is None:
            character_id = self.current_character
            
        if not character_id or character_id not in self.tokens:
            return False
            
        scopes = self.tokens[character_id].get('scopes', [])
        return scope in scopes
    
    def make_esi_request(self, endpoint, character_id=None, method='GET', **kwargs):
        """Make authenticated ESI API request with automatic token refresh"""
        if character_id is None:
            character_id = self.current_character
            
        # Ensure we have a valid token
        self.ensure_valid_token(character_id)
        
        url = f"{self.oauth_config['esi_base_url']}/{endpoint.lstrip('/')}"
        headers = kwargs.setdefault('headers', {})
        headers.update({
            'Authorization': f'Bearer {self.tokens[character_id]["access_token"]}',
            'User-Agent': 'Evetech/1.3'
        })
        
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def start_auth_server(self):
        """Start the Flask server for OAuth flow"""
        print(f"Starting EVE SSO authentication server on port {self.port}")
        print(f"Go to: http://localhost:{self.port}/login")
        print("Waiting for authentication...")
        
        self.app.run(host='localhost', port=self.port, debug=False)

# Example usage:
if __name__ == '__main__':
    # Example usage - you need to set your EVE app credentials
    eve_client_id = os.environ.get('EVE_CLIENT_ID')
    eve_client_secret = os.environ.get('EVE_CLIENT_SECRET')
    
    if not eve_client_id or not eve_client_secret:
        print("Please set EVE_CLIENT_ID and EVE_CLIENT_SECRET environment variables")
        print("Get them from: https://developers.eveonline.com/applications")
        exit(1)
    
    # Create Evetech instance
    evetech = Evetech(eve_client_id, eve_client_secret)
    
    # Optionally customize scopes
    evetech.set_scopes(['publicData', 'esi-wallet.read_character_wallet.v1'])
    
    # Start authentication
    evetech.start_auth_server()
    
    # After authentication completes, you can access the token data:
    # token_data = evetech.get_token_data()  # Current character
    # access_token = evetech.get_access_token()  # Current character
    # character_info = evetech.get_character_info()  # Current character
    
    # Multiple character support:
    # characters = evetech.get_character_list()  # Returns {character_id: character_name}
    # evetech.set_current_character(character_id)
    # token_data = evetech.get_token_data(character_id)
    # 
    # # Helper methods:
    # char_id = evetech.get_character_id_by_name('Character Name')
    # char_name = evetech.get_current_character_name()