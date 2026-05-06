# VaakSetu (వాక్సేతు) 🎙️

> Automate outbound sales calls with AI. Built with Vapi, Python & Claude — handles greetings, objections, meeting booking & CRM logging out of the box.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Vapi](https://img.shields.io/badge/Vapi-AI%20Voice-purple?style=flat-square)
![Claude](https://img.shields.io/badge/Claude-Anthropic-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## What is VaakSetu?

**VaakSetu** (వాక్సేతు) means *"Voice Bridge"* in Telugu — a bridge between your business and every lead through intelligent, automated sales conversations.

VaakSetu is an AI-powered voice agent that autonomously handles outbound cold calls end-to-end — from the first greeting to booking a meeting or logging the outcome in your CRM. No human needed on your side.

---

## ✨ Features

- 🤖 **AI Sales Agent** — Powered by Claude (Anthropic) for natural, intelligent conversations
- 📞 **Outbound Calling** — Triggers real phone calls via Vapi + Twilio
- 🗣️ **Natural Voice** — ElevenLabs text-to-speech for human-like audio
- 🧠 **Objection Handling** — Trained to handle common sales objections
- 📅 **Meeting Booking** — Books demos and follow-ups automatically
- 📋 **CRM Logging** — Logs call outcomes, notes, and lead quality
- 🔁 **Bulk Dialing** — Parallel async dialing for high-volume campaigns
- 📊 **Webhook Events** — Real-time call event handling via FastAPI
- 📱 **Voicemail Detection** — Leaves custom voicemail messages automatically
- 🔒 **Secure** — All secrets managed via environment variables

---

## 🏗️ Architecture

```
Lead List (CSV/CRM)
      │
      ▼
  agent.py  ──►  Vapi API  ──►  Prospect's Phone
                    │
                    ▼
            Real-time Pipeline
         STT → Claude AI → TTS
                    │
                    ▼
              webhook.py
         (FastAPI webhook server)
                    │
            ┌───────┴────────┐
            ▼                ▼
        tools.py          CRM / Calendar
   (book_meeting,        (HubSpot, Calendly,
    log_outcome,          Google Calendar)
    transfer_call)
```

---

## 🗂️ Project Structure

```
vaaksetu/
├── agent.py          # Outbound call trigger + bulk dialer
├── assistant.py      # Claude system prompt + function tools definition
├── tools.py          # Tool handlers (booking, CRM logging, transfer)
├── webhook.py        # FastAPI server for Vapi event handling
├── test_vapi.py      # Connection test + call trigger debugger
├── .env.example      # Environment variable template
├── requirements.txt  # Python dependencies
└── README.md
```

---

## ⚙️ Prerequisites

- Python 3.10+
- [Vapi account](https://vapi.ai) — $10 free credits on signup
- [Anthropic API key](https://console.anthropic.com)
- [Twilio account](https://twilio.com) — for phone number
- [ngrok](https://ngrok.com) — for local webhook tunnel (dev only)
- [ElevenLabs account](https://elevenlabs.io) — for voice (optional, Vapi includes basic voices)

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/vaaksetu.git
cd vaaksetu
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
VAPI_API_KEY=your_vapi_private_key
VAPI_PHONE_NUMBER_ID=your_vapi_phone_number_id
VAPI_ASSISTANT_ID=your_vapi_assistant_id
ANTHROPIC_API_KEY=your_anthropic_api_key
WEBHOOK_URL=https://your-ngrok-url.ngrok-free.app/webhook
```

### 4. Set up Vapi Assistant

1. Go to [Vapi Dashboard](https://dashboard.vapi.ai/assistants)
2. Create a new assistant → Blank Template
3. Set model to **Anthropic → claude-sonnet-4-20250514**
4. Paste the system prompt from `assistant.py`
5. Set voice to **ElevenLabs → Adam**
6. Add your webhook URL under **Server URL**
7. Add tools: `book_meeting`, `log_outcome`, `transfer_call`
8. Save and copy the **Assistant ID**

### 5. Start the webhook server

```bash
# Terminal 1 — Start ngrok
ngrok http 8000

# Terminal 2 — Start FastAPI webhook server
python -m uvicorn webhook:app --port 8000 --reload
```

### 6. Test the connection

```bash
python test_vapi.py
```

### 7. Make your first call

```bash
# Single call
python agent.py --phone +917013549646 --name "Test Lead"

# With prospect context
python agent.py --phone +917013549646 --name "Jane" --context "SaaS founder, 20 employees"

# Bulk dial all leads in SAMPLE_LEADS
python agent.py --bulk
```

---

## 📞 Call Flow

```
1. VaakSetu dials the prospect
2. Prospect picks up
3. Alex greets: "Hi, is this [Name]? I'm Alex from [Company]..."
4. Qualifying questions → Value pitch → Objection handling
5. Prospect agrees → book_meeting tool fires → Meeting booked ✅
6. Call ends → log_outcome tool fires → CRM updated ✅
```

---

## 🛠️ Customisation

### Change the sales script
Edit `SYSTEM_PROMPT` in `assistant.py` — replace `[Company]` with your company name and tailor the pitch.

### Connect your CRM
Edit `tools.py` → `handle_log_outcome()` — add HubSpot, Salesforce, or Airtable API calls.

### Connect your calendar
Edit `tools.py` → `handle_book_meeting()` — add Calendly or Google Calendar integration.

### Add more leads
Edit `SAMPLE_LEADS` in `agent.py` or load from a CSV:

```python
import csv

with open("leads.csv") as f:
    leads = list(csv.DictReader(f))  # columns: phone, name, context

asyncio.run(dial_leads_parallel(leads, concurrency=10))
```

---

## 📦 Requirements

```
vapi-python
anthropic
fastapi
uvicorn
httpx
requests
python-dotenv
```

Install all:
```bash
pip install vapi-python anthropic fastapi uvicorn httpx requests python-dotenv
```

---

## 🔒 Security

- Never commit your `.env` file — it's in `.gitignore`
- Use **Private Key** from Vapi (not Public Key) for server-side calls
- Rotate API keys immediately if accidentally exposed
- Use environment variables — never hardcode secrets in code

---

## 🗺️ Roadmap

- [ ] CSV lead import
- [ ] Calendly integration
- [ ] HubSpot CRM integration
- [ ] Real-time dashboard for call monitoring
- [ ] A/B testing for opening messages
- [ ] Slack alerts on meeting bookings
- [ ] Retry logic for unanswered calls
- [ ] Call recording transcripts

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

## 🙏 Built With

- [Vapi](https://vapi.ai) — Voice AI infrastructure
- [Anthropic Claude](https://anthropic.com) — AI brain
- [ElevenLabs](https://elevenlabs.io) — Natural voice synthesis
- [FastAPI](https://fastapi.tiangolo.com) — Webhook server
- [Twilio](https://twilio.com) — Telephony

---

<p align="center">
  Built with ❤️ from Hyderabad, India 🇮🇳
  <br/>
  <i>వాక్సేతు — Voice Bridge</i>
</p>
