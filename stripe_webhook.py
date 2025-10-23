import stripe
from config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
from github_service import add_collaborator

#%%

stripe.api_key = STRIPE_SECRET_KEY

#%%

def handle_stripe_event(
        payload: bytes,
        sig_header: str
) -> tuple[int, str]:
    """
    Valida la firma y procesa eventos de Stripe.
    """
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return 400, "Invalid payload"
    except stripe.error.SignatureVerificationError:
        return 400, "Invalid signature"

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        custom_fields = session.get("custom_fields", [])
        github_username = None

        for field in custom_fields:
            if field.get("key") == "github_username":
                github_username = field["text"]["value"].strip()

        if not github_username:
            return 200, "No GitHub username provided."

        ok, msg = add_collaborator(
            github_username=github_username
        )
        return 200, msg if ok else f"Error: {msg}"

    return 200, "Event ignored"
