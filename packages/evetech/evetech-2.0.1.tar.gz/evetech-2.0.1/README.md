# Evetech OAuth

A simple Python library for EVE Online ESI OAuth authentication with multi-character support and automatic token refresh.

## Features

- 🚀 Easy EVE Online SSO authentication
- 📦 Simple ESI API requests
- 👥 Multi-character support
- 🔄 Automatic token refresh
- 💾 Persistent token storage (JSON file)

## Installation

```bash
pip install evetech
```

## Quick Start

### 1. Setup your EVE Application

1. Go to [EVE Developers](https://developers.eveonline.com/applications)
2. Create a new application
3. Set redirect URI to: `http://localhost:8000/callback`
4. Note your `Client ID` and `Client Secret`

### 2. Basic Usage

```python
from evetech import Evetech
import os

# Set your EVE app credentials
client_id = "your_eve_client_id"
client_secret = "your_eve_client_secret"

# Create Evetech instance
eve = Evetech(client_id, client_secret)

# Optional: Set custom scopes
eve.set_scopes([
    'publicData',
    'esi-wallet.read_character_wallet.v1',
    'esi-skills.read_skills.v1'
])

# Start authentication (opens browser)
eve.start_auth_server()

# After authentication, tokens are automatically saved
print(f"Authenticated as: {eve.get_current_character_name()}")
```

### 3. Making ESI Requests

```python
# Get current character info
character_info = eve.get_character_info()
character_id = character_info['character_id']

# Make ESI requests (automatic token refresh)
character_data = eve.make_esi_request(f'/characters/{character_id}/')
print(f"Character: {character_data['name']}")

# Get wallet balance (requires wallet scope)
try:
    wallet = eve.make_esi_request(f'/characters/{character_id}/wallet/')
    print(f"Wallet: {wallet:,.2f} ISK")
except Exception as e:
    print(f"Wallet access failed: {e}")

# Get character skills
skills = eve.make_esi_request(f'/characters/{character_id}/skills/')
print(f"Total SP: {skills['total_sp']:,}")
```

### 4. Multi-Character Support

```python
# Authenticate multiple characters
eve = Evetech(client_id, client_secret)

# First character
eve.start_auth_server()  # Login with first character
main_char = eve.get_current_character()

# Second character  
eve.start_auth_server()  # Login with second character
alt_char = eve.get_current_character()

# List all authenticated characters
characters = eve.get_character_list()
print("Authenticated characters:", characters)
# Output: {123456: 'Main Character', 789012: 'Alt Character'}

# Switch between characters
eve.set_current_character(main_char)
main_wallet = eve.make_esi_request(f'/characters/{main_char}/wallet/')

eve.set_current_character(alt_char)
alt_wallet = eve.make_esi_request(f'/characters/{alt_char}/wallet/')

# Or specify character directly
main_skills = eve.make_esi_request(f'/characters/{main_char}/skills/', character_id=main_char)
```

### 5. Token Management

```python
# Check authentication status
if eve.is_authenticated():
    print("Ready to make ESI calls")

# Check token expiration
if eve.is_token_expired():
    print("Token will be refreshed automatically")

# Manual token refresh
eve.refresh_access_token()

# Save tokens manually (automatic by default)
eve.save_tokens()

# Remove a character
eve.remove_character(character_id)
```

## Environment Variables

You can also use environment variables:

```bash
export EVE_CLIENT_ID="your_client_id"
export EVE_CLIENT_SECRET="your_client_secret"
```

```python
import os
from evetech import Evetech

eve = Evetech(
    os.environ['EVE_CLIENT_ID'],
    os.environ['EVE_CLIENT_SECRET']
)
```

## Configuration Options

```python
eve = Evetech(
    client_id="your_id",
    client_secret="your_secret",
    redirect_uri="http://localhost:8000/callback",  # Custom redirect
    port=8000,                                       # Custom port
    tokens_file="my_tokens.json"                     # Custom token file
)
```

## Common ESI Endpoints

```python
character_id = eve.get_character_info()['character_id']

# Character information
char_data = eve.make_esi_request(f'/characters/{character_id}/')

# Wallet balance
wallet = eve.make_esi_request(f'/characters/{character_id}/wallet/')

# Skills
skills = eve.make_esi_request(f'/characters/{character_id}/skills/')

# Assets
assets = eve.make_esi_request(f'/characters/{character_id}/assets/')

# Corporation info
corp_id = char_data['corporation_id']
corp_data = eve.make_esi_request(f'/corporations/{corp_id}/')
```

## Available Scopes

Common EVE SSO scopes you might need:

- `publicData` - Public character information
- `esi-wallet.read_character_wallet.v1` - Wallet balance
- `esi-skills.read_skills.v1` - Character skills
- `esi-assets.read_assets.v1` - Character assets
- `esi-characters.read_corporation_roles.v1` - Corporation roles
- `esi-markets.read_character_orders.v1` - Market orders

[Full list of scopes](https://esi.evetech.net/ui/#/Character)

## Error Handling

```python
try:
    wallet = eve.make_esi_request(f'/characters/{character_id}/wallet/')
    print(f"Balance: {wallet:,.2f} ISK")
except Exception as e:
    if "403" in str(e):
        print("Missing required scope for wallet access")
    elif "token" in str(e).lower():
        print("Authentication issue - try re-authenticating")
    else:
        print(f"API error: {e}")
```

## Requirements

- Python 3.7+
- Flask 2.0+
- Requests 2.25+

## License

GNU License, just say you like me :3

## Contributing

Issues and pull requests welcome on GitHub!

## Disclaimer

This library is not affiliated with CCP Games or EVE Online. EVE Online is a trademark of CCP.