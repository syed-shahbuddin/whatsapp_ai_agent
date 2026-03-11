import logging

from flask import Blueprint, request, jsonify

from .decorators.security import signature_required
from .utils.whatsapp_utils import (
    process_whatsapp_message,
    is_valid_whatsapp_message,
)

webhook_blueprint = Blueprint("webhook", __name__)


def handle_message():
    """
    Handle incoming webhook events from Twilio WhatsApp API.

    Twilio sends webhook data as form-encoded (not JSON).
    Validates the message and processes it if valid.

    Returns:
        response: A tuple containing a JSON response and an HTTP status code.
    """
    body = request.form.to_dict()

    try:
        if is_valid_whatsapp_message(body):
            process_whatsapp_message(body)
            return jsonify({"status": "ok"}), 200
        else:
            return (
                jsonify({"status": "error", "message": "Not a valid WhatsApp message"}),
                400,
            )
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@webhook_blueprint.route("/webhook", methods=["POST"])
@signature_required
def webhook_post():
    return handle_message()


