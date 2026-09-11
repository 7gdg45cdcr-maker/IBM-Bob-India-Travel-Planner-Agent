# India Travel Agent 🇮🇳✈️

A full-stack AI travel assistant powered by **IBM watsonx Granite-4** that helps users plan trips across India.

---

## Project Structure

```
travel_agent/
├── backend/
│   ├── app.py              # Flask API server
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── templates/
│   │   └── index.html      # Main UI page
│   └── static/
│       ├── css/style.css   # Styles
│       └── js/app.js       # Frontend logic
├── start.sh                # One-click startup script
└── README.md
```

---

## Quick Start

### 1. Run with the startup script

```bash
chmod +x travel_agent/start.sh
./travel_agent/start.sh
```

Then open **http://localhost:5000** in your browser.

### 2. Run manually

```bash
cd travel_agent/backend
pip install -r requirements.txt
python app.py
```

---

## Features

| Feature | Details |
|---|---|
| 💬 Conversational AI | Multi-turn chat with memory (last 6 turns) |
| 🗺️ Destination Sidebar | Quick-click popular Indian destinations |
| 💡 Suggestion Chips | Pre-built prompts to get started instantly |
| 📱 Responsive Design | Works on desktop and mobile |
| 🔄 IAM Auth | Auto-fetches IBM Cloud IAM tokens |

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Frontend UI |
| `POST` | `/api/chat` | Send a message, get AI reply |
| `GET` | `/api/suggestions` | Fetch suggestion chips |

### POST `/api/chat`

**Request:**
```json
{
  "message": "Plan a 7-day trip to Rajasthan",
  "history": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ]
}
```

**Response:**
```json
{
  "reply": "Here's your 7-day Rajasthan itinerary…"
}
```

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `WATSONX_API_KEY` | (hardcoded) | Override via environment variable |
| `PORT` | `5000` | Flask listens on this port |

To use a different API key:
```bash
export WATSONX_API_KEY="your-key-here"
python app.py
```

---

## Tech Stack

- **Backend:** Python 3.9+, Flask, flask-cors, requests
- **Frontend:** Vanilla HTML/CSS/JavaScript (no build step)
- **AI Model:** IBM watsonx Granite-4-H-Small (`ibm/granite-4-h-small`)
- **Auth:** IBM Cloud IAM token exchange
