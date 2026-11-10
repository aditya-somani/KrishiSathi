# KrishiSathi

**Multilingual AI Voice Companion for Indian Farmers — Powered by Gnani.ai Vachana & LiveKit Agents**

KrishiSathi enables farmers to call in over standard voice/telephony channels and receive personalized guidance on crops, mandi prices, weather, pest control, and government schemes in their own regional language—with zero smartphone or app required.

---

## Why Gnani.ai + LiveKit?

- **Gnani Prisma STT (`livekit.plugins.gnani.STT`)**: Real-time WebSocket streaming speech recognition tuned for Indian accents, regional dialects, and bilingual code-switching (`en-IN,hi-IN`, `hi-IN`, `mr-IN`, `kn-IN`, `ta-IN`, `te-IN`, `ml-IN`, `bn-IN`, `gu-IN`, `pa-IN`).
- **Gnani Timbre TTS (`livekit.plugins.gnani.TTS`)**: Low-latency WebSocket synthesis (`timbre-v2.5`) with dynamic mid-call language switching across 10 Indian languages.
- **LiveKit Agents**: Sub-second real-time voice orchestration with Silero VAD, multilingual turn detection, preemptive generation, and room-level telephony hangup.

---

## Architecture

| Component | Technology |
| --- | --- |
| Real-time Voice Transport | LiveKit Agents |
| Speech-to-Text (STT) | Gnani.ai Vachana Prisma (`gnani.STT`, WebSocket streaming) |
| Text-to-Speech (TTS) | Gnani.ai Vachana Timbre (`gnani.TTS`, `timbre-v2.5` over WebSocket) |
| Reasoning LLM | Groq (`openai/gpt-oss-20b`) with Gemini fallback |
| Live Agricultural Search | Optional Gemini with Google Search Grounding |
| Post-Call Summarization | Groq (`openai/gpt-oss-20b`) |
| VAD & Turn Detection | Silero VAD + LiveKit Multilingual Turn Detector |
| Farmer Memory Store | SQLite (`data/krishisathi.db`) |

---

## Project Structure

```text
src/krishisathi/
├── agent.py              # LiveKit entrypoint, Gnani STT/TTS pipeline & call watchdog
├── config.py             # Typed environment configuration & startup validation
├── languages.py          # Indian language registry & Gnani BCP-47 locale mapping
├── main.py               # LiveKit worker CLI & prewarm checks
├── prompts.py            # KrishiSathi persona & returning-farmer prompt builder
├── storage.py            # SQLite repository for farmer profiles & 5-call rolling history
├── handlers/
│   ├── summarizer.py     # Async post-call summarization
│   └── transcript.py     # Conversation item tracker
├── tools/
│   ├── farmer.py         # Farmer registration & profile update tools
│   ├── language.py       # Dynamic language detection synced with Gnani TTS
│   └── search.py         # Grounded agricultural search via Google Search
└── utils/
    └── telephony.py      # Room teardown utility for session timeout hangup
tests/                    # Unit tests for config, languages, storage, tools & handlers
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- API credentials: `GNANI_API_KEY`, `GROQ_API_KEY`, and LiveKit credentials (`LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`)

### Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env
   # Fill in GNANI_API_KEY, GROQ_API_KEY, and LiveKit keys
   ```

3. Download VAD & turn-detector assets and run in development mode:
   ```bash
   uv run python -m krishisathi.main download-files
   uv run python -m krishisathi.main dev
   ```

4. Run unit tests:
   ```bash
   uv run pytest -v
   ```

---

## Docker Deployment

```bash
docker build -t krishisathi .
docker run --env-file .env krishisathi
```

---

## License

MIT

