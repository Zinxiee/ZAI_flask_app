import os
from flask import Flask, request, abort
import requests

app = Flask(__name__)

# Load these from environment for security
MG_API_KEY = os.getenv("MAILGUN_API_KEY")
MG_DOMAIN  = os.getenv("MAILGUN_DOMAIN")  # e.g. "mydomain.com"

if not MG_API_KEY or not MG_DOMAIN:
    raise RuntimeError("Set MAILGUN_API_KEY & MAILGUN_DOMAIN env vars")

def process_request(subject: str, body: str) -> str:
    """
    ZachAI backend processing function.
    """
    # Example: echo the incoming message
    return f"Hello! You wrote:\n\nSubject: {subject}\n\n{body}"

@app.route("/incoming", methods=["POST"])
def incoming_email():
    # Mailgun posts form-encoded data
    sender  = request.form.get("from")
    subject = request.form.get("subject", "")
    body     = request.form.get("body-plain", "")

    if not sender:
        abort(400, "Missing 'from' field")

    # ZachAI backend
    reply_text = process_request(subject, body)

    # Send reply via Mailgun API
    resp = requests.post(
        f"https://api.mailgun.net/v3/{MG_DOMAIN}/messages",
        auth=("api", MG_API_KEY),
        data={
            "from":    f"ZachAI <ZachAI@{MG_DOMAIN}>",
            "to":      sender,
            "subject": f"Re: {subject}",
            "text":    reply_text,
        }
    )
    # Optional: log or handle non-200 responses
    resp.raise_for_status()

    # success
    return ("", 200)

if __name__ == "__main__":
    # Ensure this runs on HTTPS in production!
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))