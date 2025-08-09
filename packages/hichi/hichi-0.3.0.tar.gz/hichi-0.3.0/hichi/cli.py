import click
import getpass
import json
import os
import base64
from .config import get_config, save_config, DEFAULT_MODEL
from .crypto import encrypt, decrypt
from .chat import start_chat_session

HARDCODED_PASSWORD = "jai_shree_ram"

def verify_password():
    """Verify the hardcoded password."""
    password = getpass.getpass("Enter password: ")
    if password != HARDCODED_PASSWORD:
        click.echo("❌ Incorrect password!")
        exit(1)
    return True

def get_or_setup_api_key():
    """Get API key from config or prompt user to enter it."""
    config = get_config()
    
    if config.get("encrypted_api_key"):
        try:
            # Decrypt existing API key
            encrypted_key = base64.b64decode(config["encrypted_api_key"])
            api_key = decrypt(encrypted_key)
            return api_key
        except Exception:
            click.echo("⚠️  Error decrypting API key. Please re-enter it.")
    
    # First time or error - ask for API key
    click.echo("🔑 Setting up Groq API key...")
    api_key = getpass.getpass("Enter your Groq API key: ")
    
    # Encrypt and save the API key
    encrypted_key = encrypt(api_key)
    config["encrypted_api_key"] = base64.b64encode(encrypted_key).decode()
    save_config(config)
    
    click.echo("✅ API key saved securely!")
    return api_key

@click.group()
def main():
    """
    Hichi - A CLI tool for interacting with Groq AI.
    """
    pass

@main.command()
def hi():
    """Initialize hichi with password verification and API key setup."""
    verify_password()
    click.echo("🙏 Welcome to Hichi!")
    
    # Setup or verify API key
    api_key = get_or_setup_api_key()
    config = get_config()
    
    click.echo(f"📋 Current model: {config.get('model', DEFAULT_MODEL)}")
    click.echo("✨ Hichi is ready to use!")
    click.echo("\nAvailable commands:")
    click.echo("  hichi chat    - Start a chat session")
    click.echo("  hichi key     - Update API key")
    click.echo("  hichi model   - Change model")

@main.command()
def key():
    """Update the Groq API key."""
    verify_password()
    
    click.echo("🔑 Updating Groq API key...")
    api_key = getpass.getpass("Enter your new Groq API key: ")
    
    # Encrypt and save the new API key
    config = get_config()
    encrypted_key = encrypt(api_key)
    config["encrypted_api_key"] = base64.b64encode(encrypted_key).decode()
    save_config(config)
    
    click.echo("✅ API key updated successfully!")

@main.command()
@click.argument('model_name', required=False)
def model(model_name):
    """Update the model. If no model name provided, shows current model."""
    verify_password()
    
    config = get_config()
    
    if not model_name:
        click.echo(f"📋 Current model: {config.get('model', DEFAULT_MODEL)}")
        click.echo("\nTo change model, use: hichi model <model_name>")
        click.echo("Example: hichi model 'Qwen3 480b Coder'")
        return
    
    config["model"] = model_name
    save_config(config)
    click.echo(f"✅ Model updated to: {model_name}")

@main.command()
def chat():
    """Start an interactive chat session with the AI."""
    verify_password()
    
    # Get API key and model
    api_key = get_or_setup_api_key()
    config = get_config()
    model = config.get('model', DEFAULT_MODEL)
    
    click.echo(f"💬 Starting chat session with {model}")
    click.echo("🔄 Session-only memory (no chat history saved)")
    click.echo("Type 'exit' or 'quit' to end the session")
    click.echo("-" * 50)
    
    start_chat_session(api_key, model)

if __name__ == "__main__":
    main()