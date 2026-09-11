import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__, static_folder="../frontend/static", template_folder="../frontend/templates")
CORS(app)

# IBM watsonx configuration
WATSONX_URL = "https://eu-de.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
API_KEY = os.environ.get("WATSONX_API_KEY", "nt11bjOSkNnrmGwS2ChDTcrAIzQ7zS0MjU3y0yzqd23n")
PROJECT_ID = "da184998-b41c-4515-8cf7-25bc2df6c523"
MODEL_ID = "ibm/granite-4-h-small"
IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"

_iam_token_cache = {"token": None}


def get_iam_token():
    """Fetch a fresh IBM Cloud IAM bearer token."""
    resp = requests.post(
        IAM_TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": API_KEY,
        },
        timeout=30,
    )
    resp.raise_for_status()
    _iam_token_cache["token"] = resp.json()["access_token"]
    return _iam_token_cache["token"]


SYSTEM_PROMPT = """You are an expert India Travel Agent. Your sole purpose is to help users plan 
the best travel experiences across India. You have deep knowledge of:
- Popular destinations: Rajasthan, Kerala, Goa, Himachal Pradesh, Uttarakhand, Tamil Nadu, 
  Karnataka, Maharashtra, Ladakh, Andaman & Nicobar, Varanasi, Agra, and more.
- Best travel seasons and weather patterns for each region.
- Budget estimation (budget, mid-range, luxury).
- Transport options: flights, trains, buses, road trips.
- Accommodation: hotels, homestays, heritage properties, camping.
- Local cuisine, cultural tips, and must-do experiences.
- Visa and travel document requirements.
- Safety tips and travel advisories.

Always provide:
1. Specific, actionable travel plans with day-by-day itineraries when asked.
2. Estimated costs in Indian Rupees (INR).
3. Best time to visit recommendations.
4. Practical tips for the specific destination.

Be friendly, enthusiastic, and concise. If a user asks something unrelated to India travel, 
politely redirect them to travel planning."""


def build_prompt(user_message: str, history: list) -> str:
    """Build a conversational prompt from chat history."""
    conversation = ""
    for turn in history[-6:]:  # keep last 6 turns for context
        role = turn.get("role", "user")
        content = turn.get("content", "")
        if role == "user":
            conversation += f"User: {content}\n"
        else:
            conversation += f"Agent: {content}\n"
    conversation += f"User: {user_message}\nAgent:"
    return f"{SYSTEM_PROMPT}\n\n{conversation}"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_message = (data.get("message") or "").strip()
    history = data.get("history", [])

    if not user_message:
        return jsonify({"error": "message is required"}), 400

    try:
        token = get_iam_token()
    except Exception as e:
        return jsonify({"error": f"Authentication failed: {str(e)}"}), 502

    prompt = build_prompt(user_message, history)

    payload = {
        "model_id": MODEL_ID,
        "project_id": PROJECT_ID,
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 800,
            "min_new_tokens": 20,
            "stop_sequences": ["User:", "\n\nUser:"],
            "repetition_penalty": 1.1,
        },
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        resp = requests.post(WATSONX_URL, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        generated = result["results"][0]["generated_text"].strip()
        # Strip any trailing "User:" that might leak from stop sequence
        if generated.endswith("User:"):
            generated = generated[: -len("User:")].strip()
        return jsonify({"reply": generated})
    except requests.HTTPError as e:
        return jsonify({"error": f"watsonx API error: {resp.status_code} - {resp.text}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/suggestions", methods=["GET"])
def suggestions():
    """Return quick-start suggestion prompts."""
    return jsonify({
        "suggestions": [
            "Plan a 7-day trip to Rajasthan in December",
            "Best beaches in Goa for a family vacation",
            "Budget trip from Delhi to Himachal Pradesh",
            "Kerala backwaters — best time and itinerary",
            "Top things to do in Ladakh in summer",
            "Weekend getaways from Mumbai under ₹10,000",
        ]
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
