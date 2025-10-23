"""
Flask application entry point for the Wix–Stripe–GitHub integration.

This app receives webhooks from Stripe when a payment succeeds and
triggers logic to grant GitHub repository access. It is designed to
run both locally and on Render (or any WSGI-compatible host).
"""

import os
from flask import Flask, request, jsonify
from stripe_webhook import handle_stripe_webhook
from config import logger

app = Flask(__name__)


@app.route("/", methods=["GET"])
def health_check():
    """
    Health check endpoint to verify that the server is running.

    Returns
    -------
    flask.Response
        Simple JSON response confirming server status.
    """
    logger.info("Health check requested.")
    return jsonify({"message": "✅ Server running. Stripe webhook active."}), 200


@app.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    """
    Stripe webhook endpoint for receiving payment notifications.

    Returns
    -------
    flask.Response
        Response from the webhook handler.
    """
    return handle_stripe_webhook(request)


if __name__ == "__main__":
    # Dynamic port for Render compatibility
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port)
