"""
Stripe webhook handler for processing payment events.

This module defines a function to handle incoming webhook events from Stripe.
When a successful checkout is completed, it can log transaction data and
grant GitHub repository access to the user based on metadata.

Functions
---------
handle_stripe_webhook(request)
    Main webhook handler function.
add_github_collaborator(username: str)
    Invites the user to the private GitHub repository.
"""

from exceptions import SignatureError

import json
import stripe
import requests
from flask import jsonify
from config import (
    STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET,
    GITHUB_TOKEN,
    REPO_OWNER,
    REPO_NAME,
    logger,
)

stripe.api_key = STRIPE_SECRET_KEY

def add_github_collaborator(
        username: str
) -> None:
    """
    Grant GitHub repository access to a collaborator.

    Parameters
    ----------
    username : str
        The GitHub username to invite as a collaborator.

    Returns
    -------
    None
        Logs the outcome of the GitHub API call.
    """
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/collaborators/{username}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

    response = requests.put(url, headers=headers, json={"permission": "pull"})

    if response.status_code == 201:
        logger.info(f"✅ Invited user '{username}' to repository {REPO_OWNER}/{REPO_NAME}.")
    elif response.status_code == 204:
        logger.info(f"⚠️ User '{username}' already has access to repository.")
    else:
        logger.error(
            f"❌ Failed to invite '{username}'. "
            f"Status: {response.status_code} | Response: {response.text}"
        )


def handle_stripe_webhook(request):
    """
    Handle incoming Stripe webhook events and process payment completions.

    Parameters
    ----------
    request : flask.Request
        The Flask request object containing the webhook payload.

    Returns
    -------
    flask.Response
        JSON response indicating success or failure.
    """
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=STRIPE_WEBHOOK_SECRET,
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return jsonify({"error": "Invalid payload"}), 400
    except SignatureError as e:
        logger.error(f"Invalid signature: {e}")
        return jsonify({"error": "Invalid signature"}), 400

    event_type = event.get("type", "unknown")
    logger.info(f"Received Stripe event: {event_type}")

    # Log full event (optional but useful for debugging)
    logger.debug(json.dumps(event, indent=4))

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session.get("customer_details", {}).get("email")
        metadata = session.get("metadata", {})

        logger.info(f"✅ Payment completed from {customer_email}")
        logger.info(f"🧾 Metadata: {metadata}")

        github_username = metadata.get("github_username")
        if github_username:
            add_github_collaborator(
                username=github_username
            )
        else:
            logger.warning("No GitHub username found in metadata.")

    return jsonify({"status": "success"}), 200
