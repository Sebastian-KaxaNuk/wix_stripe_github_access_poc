from flask import Flask, request
from stripe_webhook import handle_stripe_event
from config import PORT

#%%

app = Flask(__name__)

#%%
@app.route("/health", methods=["GET"])
def health():
    return "ok", 200

@app.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")
    status, message = handle_stripe_event(
        payload=payload,
        sig_header=sig_header
    )
    return message, status

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
