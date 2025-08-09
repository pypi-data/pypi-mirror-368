import click
import json
import os
from datetime import datetime
from .config import CONFIG_DIR

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

def call_groq_api(api_key, model, messages):
    """Call Groq API with the messages."""
    if not GROQ_AVAILABLE:
        return "❌ Groq library not installed. Please run: pip install groq"
    
    try:
        client = Groq(api_key=api_key)
        
        # Convert messages to the format expected by Groq
        groq_messages = []
        for msg in messages:
            groq_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        completion = client.chat.completions.create(
            model=model,
            messages=groq_messages,
            temperature=0.7,
            max_tokens=8192,
            top_p=1,
            stream=False,
            stop=None
        )
        
        return completion.choices[0].message.content
    
    except Exception as e:
        error_msg = str(e)
        if "Invalid API Key" in error_msg or "401" in error_msg:
            return "❌ Invalid Groq API key. Please update your API key with: hichi key"
        elif "Rate limit" in error_msg:
            return "⏰ Rate limit exceeded. Please try again in a moment."
        elif "Model not found" in error_msg or "model" in error_msg.lower() and "does not exist" in error_msg.lower():
            return f"❌ Model '{model}' not found. Please update your model with: hichi model"
        else:
            return f"❌ API Error: {error_msg}"

def format_message_for_display(role, content, timestamp=None):
    """Format a message for display in the terminal."""
    if role == "user":
        icon = "👤"
        prefix = "You"
    else:
        icon = "🤖"
        prefix = "Hichi"
    
    time_str = ""
    if timestamp:
        time_str = f" [{timestamp}]"
    
    return f"{icon} {prefix}{time_str}: {content}"

def start_chat_session(api_key, model):
    """Start an interactive chat session with only current session memory."""
    
    # Build messages for API (only system message, no persistent history)
    messages = [
        {
            "role": "system", 
            "content": "You are Hichi, a helpful AI assistant. Be friendly, concise, and helpful."
        }
    ]
    
    # Session-only conversation history (not saved to disk)
    session_history = []
    
    while True:
        try:
            # Get user input
            user_input = click.prompt("\n💬", type=str, prompt_suffix=" ")
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                click.echo("👋 Goodbye!")
                break
            
            if user_input.strip() == "":
                continue
            
            # Add user message to current session
            user_message = {
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().strftime("%H:%M")
            }
            
            messages.append({"role": "user", "content": user_input})
            session_history.append(user_message)
            
            # Show user message
            click.echo(format_message_for_display("user", user_input))
            
            # Show thinking indicator
            click.echo("🤔 Thinking...", nl=False)
            
            # Call API
            response = call_groq_api(api_key, model, messages)
            
            # Clear thinking indicator
            click.echo("\r" + " " * 15 + "\r", nl=False)
            
            # Add assistant response to current session
            assistant_message = {
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().strftime("%H:%M")
            }
            
            messages.append({"role": "assistant", "content": response})
            session_history.append(assistant_message)
            
            # Show assistant response
            click.echo(format_message_for_display("assistant", response))
            
        except KeyboardInterrupt:
            click.echo("\n\n👋 Chat interrupted!")
            break
        except EOFError:
            click.echo("\n\n👋 Goodbye!")
            break
        except Exception as e:
            click.echo(f"\n❌ An error occurred: {str(e)}")
            continue
