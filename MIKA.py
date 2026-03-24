import json
import os
import time
from google import genai
from google.genai import types

# --- 1. SETUP ---
API_KEY = "AIzaSyDo88xlD0oVLK5vQLbG4C2kZ9tLSK37HDs"  # Replace with your actual key
BOT_NAME = "Mika"
MEMORY_FILE = "mika_memory.json"

client = genai.Client(api_key=API_KEY)

# --- 2. THE BRAIN (Identity & Memory) ---
def load_memory():
    """Load past conversations from a file."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_memory(history):
    """Save the current conversation to a file."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def start_mika():
    # Load past chat history
    past_history = load_memory()
    
    # Start the chat session with memory
    chat = client.chats.create(
        model="gemini-2.0-flash", 
        config=types.GenerateContentConfig(
            system_instruction=f"You are {BOT_NAME}, a clever Python-built assistant. Remember the user's name if they tell you.",
        ),
        history=past_history
    )

    print(f"=== {BOT_NAME.upper()} IS ONLINE (Memory Loaded) ===")
    
    if not past_history:
        print(f"{BOT_NAME}: Hi! I don't think we've met. What's your name?")
    else:
        print(f"{BOT_NAME}: Welcome back! How can I help you today?")

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ["exit", "quit", "bye"]:
            # Save the history before leaving
            save_memory(chat._history) 
            print(f"{BOT_NAME}: History saved. See ya!")
            break

        print(f"{BOT_NAME} is thinking...", end="\r")

        try:
            # Send message to Gemini
            response = chat.send_message(user_input)
            print(" " * 30, end="\r") # Clear thinking line
            print(f"{BOT_NAME}: {response.text}")
            
            # Save memory after every message just in case the app crashes
            save_memory(chat._history)

        except Exception as e:
            print(f"\n[Error]: {e}")

if __name__ == "__main__":
    start_mika()