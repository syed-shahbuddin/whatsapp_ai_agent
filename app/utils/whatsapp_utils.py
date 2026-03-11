import logging
from flask import current_app
from twilio.rest import Client
import re

from app.services.gemini_service import generate_response


def send_message(to, body):
    """Send a WhatsApp message via Twilio."""
    client = Client(
        current_app.config["TWILIO_ACCOUNT_SID"],
        current_app.config["TWILIO_AUTH_TOKEN"],
    )

    message = client.messages.create(
        from_=f"whatsapp:{current_app.config['TWILIO_PHONE_NUMBER']}",
        to=f"whatsapp:{to}",
        body=body,
    )

    logging.info(f"Message sent with SID: {message.sid}")
    return message


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    text = re.sub(pattern, "", text).strip()

    # Convert double asterisks to single asterisks (WhatsApp bold format)
    pattern = r"\*\*(.*?)\*\*"
    replacement = r"*\1*"
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def process_whatsapp_message(body):
    """Process an incoming Twilio WhatsApp message and send a response."""
    wa_id = body.get("From", "").replace("whatsapp:", "")
    name = body.get("ProfileName", "User")
    message_body = body.get("Body", "")

    logging.info(f"Message from {name} ({wa_id}): {message_body}")

    # Gemini Integration
    response = generate_response(message_body, wa_id, name)
    response = process_text_for_whatsapp(response)

    send_message(wa_id, response)


def is_valid_whatsapp_message(body):
    """Check if the incoming Twilio webhook has a valid WhatsApp message."""
    return bool(body.get("From") and body.get("Body"))
