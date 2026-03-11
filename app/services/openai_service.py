import google.generativeai as genai
import shelve
from dotenv import load_dotenv
import os
import logging

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = (
    "You're a helpful WhatsApp assistant that can assist guests that are staying "
    "in our Paris AirBnb. Use your knowledge to best respond to customer queries. "
    "If you don't know the answer, say simply that you cannot help with the question "
    "and advise to contact the host directly. Be friendly and funny."
)

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=SYSTEM_INSTRUCTION,
)


def check_if_history_exists(wa_id):
    """Check if conversation history exists for a given WhatsApp ID."""
    with shelve.open("chat_history_db") as history_shelf:
        return history_shelf.get(wa_id, None)


def store_history(wa_id, history):
    """Store conversation history for a given WhatsApp ID."""
    with shelve.open("chat_history_db", writeback=True) as history_shelf:
        history_shelf[wa_id] = history


def generate_response(message_body, wa_id, name):
    """Generate a response using Gemini, maintaining conversation history per user."""
    history = check_if_history_exists(wa_id)

    if history is None:
        logging.info(f"Creating new chat for {name} with wa_id {wa_id}")
        chat = model.start_chat(history=[])
    else:
        logging.info(f"Retrieving existing chat for {name} with wa_id {wa_id}")
        chat = model.start_chat(history=history)

    response = chat.send_message(message_body)
    new_message = response.text
    logging.info(f"Generated message: {new_message}")

    # Persist the updated history
    store_history(wa_id, chat.history)

    return new_message
