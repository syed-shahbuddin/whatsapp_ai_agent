from functools import wraps
from flask import current_app, jsonify, request
import logging

from twilio.request_validator import RequestValidator


def validate_twilio_signature(url, post_data, signature):
    """
    Validate the incoming Twilio request signature.
    """
    validator = RequestValidator(current_app.config["TWILIO_AUTH_TOKEN"])
    return validator.validate(url, post_data, signature)


def signature_required(f):
    """
    Decorator to ensure that incoming requests to our webhook
    are valid and signed by Twilio.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        signature = request.headers.get("X-Twilio-Signature", "")
        url = request.url
        post_data = request.form.to_dict()

        if not validate_twilio_signature(url, post_data, signature):
            logging.info("Twilio signature verification failed!")
            return jsonify({"status": "error", "message": "Invalid signature"}), 403
        return f(*args, **kwargs)

    return decorated_function
