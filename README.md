# KrishiSathi (कृषिसाथी)

**Bridging the Digital Divide: Delivering Internet Intelligence to Farmers Over Ordinary Phone Calls**

---

### The Mission

Over 140 million Indian farmers power the nation's food supply, yet a vast **digital divide** cuts them off from the benefits of modern AI and the live internet. Most existing agricultural solutions demand smartphones, high-speed mobile data, app downloads, and technical literacy—demands that exclude the very farmers who need timely help the most.

**KrishiSathi dismantles every barrier by turning any regular phone call into a direct conversational gateway to the internet:**

- **No Smartphone or Data Plan Needed:** Works on any basic keypad/feature phone over standard telephone lines (PSTN/SIP). Zero hardware cost for the farmer.
- **Zero Technical Friction:** No apps to install, no passwords, no screens. The farmer simply dials a number and speaks.
- **Breaking the Language Barrier:** Powered by **Gnani.ai's Vachana Speech AI**, KrishiSathi speaks and understands Indian languages natively. It greets in Hindi with a warm, respectful feminine persona (*"Main KrishiSathi hoon, aapki kheti ki digital sathi"*) and understands everyday Hinglish farming loanwords (*mandi, rate, urea, spray, weather*) without breaking conversation flow.
- **Real-Time Internet Grounding:** Connects callers to live agricultural facts—today's mandi prices, crop MSP announcements, localized rain forecasts, and government schemes (PM-KISAN, PMFBY)—retrieved live and synthesized into actionable, spoken advice.
- **Persistent Caller Memory:** Automatically recognizes returning callers by their phone number, remembering their past concerns, location, and crops for personalized continuity.

---

### How It Works

```
  [ Farmer on Basic Phone ]
             │ (Regular Voice Call)
             ▼
    [ LiveKit SIP Telephony ]
             │
             ├──► [ Gnani.ai Prisma STT ] ────► Real-time Indian language speech-to-text
             │
             ├──► [ Groq Reasoning LLM ]  ────► Low-latency conversational intelligence
             │            │
             │            └──► [ Live Web Search ] ──► Real-time mandi rates & weather
             │
             ├──► [ Gnani.ai Timbre TTS ] ────► Natural, warm Indic voice reply
             │
             └──► [ SQLite Caller Memory ] ───► Auto-profiles farmer & call history
```

---

### Architecture & Technology

| Layer | Technology | Role |
| --- | --- | --- |
| **Voice Transport** | **LiveKit Agents** | Sub-second audio orchestration, SIP telephony dispatch & room lifecycle |
| **Speech-to-Text** | **Gnani.ai Prisma STT** (`livekit-plugins-gnani`) | Telephony-grade streaming recognition tuned for Indian accents & code-mixing |
| **Text-to-Speech** | **Gnani.ai Timbre TTS** (`livekit-plugins-gnani`) | Expressive, low-latency Indic voice synthesis (`timbre-v3.0` / `Shivani`) |
| **Reasoning LLM** | **Groq** (`openai/gpt-oss-20b`) | Ultra-fast token generation adhering to strict feminine Indic grammar |
| **Live Grounding** | **Google Search Grounding (`v1beta`)** | Live mandi rates, MSP updates, and instant weather lookups |
| **Memory Store** | **SQLite** (`data/krishisathi.db`) | Per-caller profile persistence & rolling conversation history |

---

### Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Configure environment (copy and fill in .env)
cp .env.example .env

# 3. Run worker locally (or deploy to LiveKit Cloud)
uv run python -m krishisathi.main dev
# Deploy to LiveKit Cloud:
# lk agent deploy --secrets-file .env --ignore-empty-secrets --yes
```

---

### License

MIT — Built for farmers by Aditya Somani.
