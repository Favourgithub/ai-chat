```python
import os
import json
from datetime import datetime
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Configure Gemini API
# Priority: GitHub Codespaces Secrets → .env file → error
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("\n❌ ERROR: GEMINI_API_KEY not found!")
    print("\nSetup options:")
    print("1. GitHub Codespaces (Recommended):")
    print("   - Go to repo → Settings → Secrets and variables → Codespaces")
    print("   - Add secret: GEMINI_API_KEY=<your_key>")
    print("   - Recreate the Codespace")
    print("\n2. Local .env file:")
    print("   - Copy .env.example to .env")
    print("   - Add your API key: GEMINI_API_KEY=<your_key>")
    print("\nGet your free API key: https://ai.google.dev\n")
    raise ValueError("GEMINI_API_KEY not configured")

genai.configure(api_key=api_key)

# Constants
MODEL_NAME = "gemini-pro"
LOG_FILE = "chatbot_logs.json"
SYSTEM_PROMPT = """You are a medical information chatbot assistant. Your role is to provide general, 
educational information about symptoms and health topics.

IMPORTANT GUIDELINES:
1. You are NOT a doctor and cannot provide medical diagnosis or treatment plans.
2. Always include a disclaimer that users should consult healthcare professionals.
3. Provide general information about possible causes, but stress uncertainty.
4. Recommend seeking professional medical care, especially for:
   - Severe or worsening symptoms
   - Symptoms lasting more than a few days
   - Accompanying high fever, chest pain, difficulty breathing, or other concerning signs
5. Be empathetic but clear about your limitations.
6. Never prescribe medications or treatments.
7. Suggest over-the-counter options only as general information, not recommendations.
8. Keep responses concise and clear.

Format responses with:
- A brief acknowledgment of their symptoms
- General educational information
- Clear warning signs that warrant immediate medical attention
- A recommendation to consult a healthcare professional"""

# Initialize conversation history for context
conversation_history = []

def load_logs():
    """Load existing logs if they exist."""
    if Path(LOG_FILE).exists():
        with open(LOG_FILE, 'r') as f:
            return json.load(f)
    return []

def save_logs(logs):
    """Save logs to file."""
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)

def log_interaction(user_input, bot_response):
    """Log user query and bot response with timestamp."""
    logs = load_logs()
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "bot_response": bot_response
    })
    save_logs(logs)

def get_bot_response(user_input):
    """Get response from Gemini API using conversation history."""
    global conversation_history
    
    # Add user message to history
    conversation_history.append({
        "role": "user",
        "parts": [user_input]
    })
    
    try:
        model = genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_PROMPT)
        response = model.generate_content(conversation_history)
        bot_response = response.text
        
        # Add bot response to history
        conversation_history.append({
            "role": "model",
            "parts": [bot_response]
        })
        
        # Log the interaction
        log_interaction(user_input, bot_response)
        
        return bot_response
    
    except Exception as e:
        error_msg = f"Error communicating with Gemini API: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return error_msg

def display_disclaimer():
    """Display medical disclaimer."""
    disclaimer = """
╔════════════════════════════════════════════════════════════════════════╗
║                    MEDICAL DISCLAIMER                                  ║
╠════════════════════════════════════════════════════════════════════════╣
║ This chatbot provides GENERAL EDUCATIONAL INFORMATION ONLY.            ║
║                                                                        ║
║ ⚠️  THIS IS NOT A MEDICAL DIAGNOSIS OR TREATMENT RECOMMENDATION       ║
║ ⚠️  THIS DOES NOT REPLACE PROFESSIONAL MEDICAL ADVICE                 ║
║                                                                        ║
║ ALWAYS consult with a qualified healthcare professional for:          ║
║ • Medical diagnosis                                                   ║
║ • Treatment planning                                                  ║
║ • Emergency symptoms (chest pain, difficulty breathing, etc.)        ║
║                                                                        ║
║ In case of emergency, call emergency services immediately.            ║
╚════════════════════════════════════════════════════════════════════════╝
    """
    print(disclaimer)

def display_welcome():
    """Display welcome message."""
    welcome = """
╔════════════════════════════════════════════════════════════════════════╗
║            Medical Symptom Information Chatbot                          ║
║                  Powered by Google Gemini AI                           ║
╚════════════════════════════════════════════════════════════════════════╝

Welcome! This chatbot provides general medical information about symptoms.

Commands:
  • Type your symptoms to get general information
  • Type 'quit' or 'exit' to end the conversation
  • Type 'clear' to start a new conversation
  • Type 'logs' to see interaction statistics
    """
    print(welcome)

def display_logs_stats():
    """Display statistics about logged interactions."""
    logs = load_logs()
    if logs:
        print(f"\n📊 Chatbot Statistics:")
        print(f"   Total interactions: {len(logs)}")
        print(f"   First interaction: {logs[0]['timestamp']}")
        print(f"   Latest interaction: {logs[-1]['timestamp']}")
        print(f"   Log file: {LOG_FILE}\n")
    else:
        print("\n📊 No interactions logged yet.\n")

def chat():
    """Main chat loop."""
    display_welcome()
    display_disclaimer()
    
    print("\n🩺 Describe your symptoms, and I'll provide general information:")
    print("(Type 'quit' to exit, 'clear' to reset conversation, 'logs' to see stats)\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit']:
                print("\n👋 Thank you for using the Medical Symptom Checker. Take care!")
                break
            
            elif user_input.lower() == 'clear':
                global conversation_history
                conversation_history = []
                print("\n🔄 Conversation cleared. Starting fresh.\n")
                continue
            
            elif user_input.lower() == 'logs':
                display_logs_stats()
                continue
            
            # Get and display bot response
            print("\nBot: ", end="", flush=True)
            response = get_bot_response(user_input)
            print(response)
            print()
        
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Thank you for using the chatbot!")
            break
        except Exception as e:
            print(f"\n[ERROR] An unexpected error occurred: {str(e)}")
            print("Please try again or type 'quit' to exit.\n")

if __name__ == "__main__":
    chat()
```
