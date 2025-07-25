from flask import Flask, request, jsonify
import json
import logging
from pathlib import Path

# Flask app setup
app = Flask(__name__)

# Logging setup
log_path = Path("build/logs/paypal_webhook.log")
log_path.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Path to subscribers.json
subscribers_path = Path("subscribers.json")

# PayPal Plan ID to internal tier mapping
PLAN_ID_TO_TIER = {
    "P-111FREEPLAN": "free",
    "P-222BASICTIER": "basic",
    "P-333PROTIER": "pro",
    "P-444EXCLUSIVETIER": "exclusive",
}

def load_subscribers():
    if subscribers_path.exists():
        with open(subscribers_path, 'r') as f:
            return json.load(f)
    return {"free": [], "basic": [], "pro": [], "exclusive": []}

def save_subscribers(subscribers):
    with open(subscribers_path, 'w') as f:
        json.dump(subscribers, f, indent=2)

@app.route('/paypal-webhook', methods=['POST'])
def paypal_webhook():
    try:
        data = request.json
        logging.info(f"Webhook received: {json.dumps(data)}")

        event_type = data.get("event_type")
        resource = data.get("resource", {})

        plan_id = resource.get("plan_id")
        payer_email = resource.get("subscriber", {}).get("email_address")

        if not plan_id or not payer_email:
            logging.warning("Missing plan_id or email in resource")
            return jsonify({"status": "missing data"}), 400

        tier = PLAN_ID_TO_TIER.get(plan_id)
        if not tier:
            logging.warning(f"Unknown plan_id: {plan_id}")
            return jsonify({"status": "unknown plan"}), 400

        subscribers = load_subscribers()
        tier_list = subscribers.setdefault(tier, [])

        if payer_email not in tier_list:
            tier_list.append(payer_email)
            save_subscribers(subscribers)
            logging.info(f"Subscribed {payer_email} to tier '{tier}'")
        else:
            logging.info(f"{payer_email} already subscribed to tier '{tier}'")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logging.error(f"Error processing webhook: {str(e)}")
        return jsonify({"status": "error", "detail": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
