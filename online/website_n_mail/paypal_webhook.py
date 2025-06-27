
from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

# Where to save subscriber tiers
SUBSCRIPTION_DB = "subscribers.json"

# Load or initialize database
def load_subscribers():
    if os.path.exists(SUBSCRIPTION_DB):
        with open(SUBSCRIPTION_DB, 'r') as f:
            return json.load(f)
    return {"all_subscribers": [], "tiers": {}}

def save_subscribers(data):
    with open(SUBSCRIPTION_DB, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/paypal/webhook', methods=['POST'])
def paypal_webhook():
    event = request.json
    if not event:
        return "Bad Request", 400

    event_type = event.get("event_type")
    resource = event.get("resource", {})

    if event_type in ["BILLING.SUBSCRIPTION.CREATED", "BILLING.SUBSCRIPTION.ACTIVATED"]:
        email = resource.get("subscriber", {}).get("email_address", "unknown@example.com")
        plan_id = resource.get("plan_id", "unknown-plan")

        data = load_subscribers()

        if email not in data["all_subscribers"]:
            data["all_subscribers"].append(email)

        if plan_id not in data["tiers"]:
            data["tiers"][plan_id] = []

        if email not in data["tiers"][plan_id]:
            data["tiers"][plan_id].append(email)

        save_subscribers(data)

        print(f"[{datetime.now()}] Subscribed: {email} to {plan_id}")
        return jsonify({"status": "added", "email": email, "tier": plan_id}), 200

    return jsonify({"status": "ignored", "event_type": event_type}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
