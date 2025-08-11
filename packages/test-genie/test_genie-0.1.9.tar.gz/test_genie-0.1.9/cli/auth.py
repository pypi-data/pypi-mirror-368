import click
import os
import json
import requests
from pathlib import Path

CONFIG_DIR = Path.home() / ".testgenie"
CONFIG_FILE = CONFIG_DIR / "config.json"
BACKEND_API_URL = "https://testgenie.fly.dev"


def get_authenticated_user():
    """Check if stored token is valid and return user info"""
    config = load_config()
    token = config.get('token')
    if not token:
        return None

    try:
        response = requests.get(
            f"{BACKEND_API_URL}/cli/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        # print(response)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None


def ensure_config_dir():
    """Ensure the config directory exists"""
    CONFIG_DIR.mkdir(exist_ok=True)

def load_config():
    """Load configuration from file"""
    ensure_config_dir()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    """Save configuration to file"""
    ensure_config_dir()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def link(uri, label=None):
    if label is None:
        label = uri
    parameters = ''
    escape_mask = '\033]8;{};{}\033\\{}\033]8;;\033\\'
    return escape_mask.format(parameters, uri, label)


@click.command()
@click.option('--username', prompt=True)
@click.password_option(confirmation_prompt=False)
def login(username, password):
    """Login to TestGenie API (CLI only)"""
    click.echo(f"Logging in as {username}...")
    
    # Call backend API
    try:
        response = requests.post(
            f"{BACKEND_API_URL}/cli/login",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Save token to config
            config = load_config()
            #print("TOKEN: ", data['access_token'])
            config['token'] = data['access_token']
            config['username'] = data['username']
            config['user_id'] = data['user_id']
            save_config(config)
            
            click.echo("✅ Login successful!")
            click.echo(f"👤 User: {data['username']}")
            click.echo(f"⏰ Token expires in: {data['expires_in_days']} days")
        elif response.status_code == 404:
            print(f"User not found!\nPlease register at {link('https://thetestgenie.com/signup')}\n")
        else:
            # click.echo(f"❌ Login failed: {response.text}")
            try:
                error_msg = response.json().get("detail")
            except ValueError:
                error_msg = response.text
            click.echo(f"❌ {error_msg}")
    
    except requests.RequestException as e:
        click.echo(f"❌ Connection error: {e}")
        # click.echo("Make sure the backend API is running at http://localhost:8000")

@click.command()
def logout():
    """Logout from TestGenie API"""
    config = load_config()
    if 'token' in config:
        del config['token']
        del config['username']
        del config['user_id']
        save_config(config)
        click.echo("✅ Logged out successfully!")
    else:
        click.echo("Not logged in.")

@click.command()
def status():
    """Check authentication status"""
    # config = load_config()
    user = get_authenticated_user()
    if user:
        # click.echo(f"✅ Logged in as: {user.get('email', 'Unknown')}")
        # click.echo(f"🆔 User ID: {user.get('username', 'Unknown')}")
        click.echo(f"✅ Logged in as {user.get('username', 'Unknown')}")
        # click.echo("🔑 Token: [HIDDEN]")
    else:
        click.echo("❌ Not logged in or token is invalid!") 