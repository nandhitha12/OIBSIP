# Task 1 — Voice Assistant

**OIBSIP | Oasis Infobyte Internship**
**Author:** Nandhitha Reddy

A Python-based voice assistant that listens to spoken commands via microphone
and responds using text-to-speech, built for the OIBSIP Task 1 checklist.

---

## Features

### Beginner tier (all complete)
- [x] Captures voice input using `speech_recognition` (microphone)
- [x] Responds to "Hello" with a predefined greeting
- [x] Tells the current time and date on request
- [x] Performs a web search on a user-specified topic (opens browser)
- [x] Graceful error handling — asks the user to repeat if unclear
- [x] Text-to-speech feedback for every response (`pyttsx3`)

### Advanced tier (implemented subset)
- [x] Rule-based natural-language intent parsing (handles free-form sentences,
      e.g. "what's the weather in Hyderabad" rather than exact keywords)
- [x] Timed reminders with an audible alert after a set duration
- [x] Live weather via the OpenWeatherMap API
- [x] Custom commands loaded from `config.json`
- [x] Send email via `smtplib` (dummy/test account only)
- [ ] General knowledge QA API — not implemented in this pass (documented
      here as a known gap; could be added with a Wikipedia summary API)

---

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   Note: `PyAudio` can be tricky to install.
   - Windows: `pip install pyaudio` usually works directly.
   - macOS: `brew install portaudio` first, then `pip install pyaudio`.
   - Linux: `sudo apt install portaudio19-dev python3-pyaudio` first.

2. **Get a free OpenWeatherMap API key** (only needed for the weather
   feature) at https://openweathermap.org/api, then add it to
   `config.json`:
   ```json
   "openweathermap_api_key": "YOUR_KEY_HERE"
   ```

3. **(Optional) Configure email sending.** Use a dummy/test email account,
   never a personal one. For Gmail, generate an
   [App Password](https://myaccount.google.com/apppasswords) and add it to
   `config.json` under `email`.

4. **Run the assistant**
   ```bash
   python voice_assistant.py
   ```

## Example commands
- "Hello"
- "What's the time?"
- "What's today's date?"
- "Search for python tutorials"
- "What's the weather in Hyderabad"
- "Remind me to drink water in 10 minutes"
- "Send an email to test@example.com saying hello there"
- "Exit" / "Quit" / "Bye"

## Custom commands
Edit the `custom_commands` section of `config.json` to add your own
phrase → response pairs without touching the code:
```json
"custom_commands": {
  "open notes": "Sure, opening your notes app placeholder.",
  "your phrase here": "the response you want spoken"
}
```

---

## Privacy considerations

This assistant processes the following data, all of it locally except
where noted:

| Data | How it's processed | Stored? |
|---|---|---|
| Microphone audio | Captured locally, then sent to Google's speech-to-text web API (`recognize_google`) for transcription. Not stored by this app. | No |
| Recognized text | Used in-memory to match intents and generate a response. | No |
| Weather queries (city name) | Sent to the OpenWeatherMap API to fetch current conditions. | No |
| Email content (if used) | Sent via your configured SMTP server (e.g. Gmail) to the recipient you specify. Credentials are read from `config.json` on your machine. | Credentials stored locally in `config.json` (not committed with real secrets — use a `.gitignore` or placeholder values in the repo) |
| API keys / email password | Stored locally in `config.json`. | Yes, locally only |

**Recommendations before pushing to GitHub:** do not commit real API keys
or email passwords. Keep `config.json` with empty placeholder values in
the repo, or add it to `.gitignore` and provide a `config.example.json`
instead.

---

## Tech stack
`Python`, `speech_recognition`, `pyttsx3`, `datetime`, `webbrowser`,
`requests` (OpenWeatherMap), `smtplib` (email), `re` (rule-based intent
parsing), `threading` (reminders)
