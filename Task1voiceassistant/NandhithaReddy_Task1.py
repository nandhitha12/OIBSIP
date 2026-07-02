"""
Voice Assistant — OIBSIP Task 1
Author: Nandhitha Reddy

A Python voice assistant that listens for spoken commands and responds
with useful actions (speech + on-screen text).

BEGINNER TIER (all implemented):
  - Capture voice input via microphone (speech_recognition)
  - Respond to greetings
  - Tell current time/date
  - Web search on a spoken topic (opens browser)
  - Graceful error handling (asks user to repeat if unclear)
  - Text-to-speech feedback for every response (pyttsx3)

ADVANCED TIER (implemented subset — see README for details/privacy notes):
  - Lightweight intent parsing from free-form sentences (not just exact
    keyword matches) using a simple rule-based NLU layer
  - Timed reminders that trigger an audible alert
  - Live weather lookup via OpenWeatherMap (needs a free API key)
  - Custom commands loaded from a config file (config.json)
  - Send email via smtplib (uses a dummy/test account you configure)

Run:
    python voice_assistant.py

Requires a working microphone and speakers. See README.md for setup.
"""

import datetime
import json
import os
import re
import smtplib
import ssl
import threading
import time
import webbrowser
from email.mime.text import MIMEText

import pyttsx3
import speech_recognition as sr

try:
    import requests
except ImportError:
    requests = None  # weather feature will warn if this is missing


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


# --------------------------------------------------------------------------
# Setup: text-to-speech engine
# --------------------------------------------------------------------------
engine = pyttsx3.init()
engine.setProperty("rate", 175)


def speak(text: str) -> None:
    """Speak text aloud and print it, so the interaction is visible too."""
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()


# --------------------------------------------------------------------------
# Setup: speech recognition
# --------------------------------------------------------------------------
recognizer = sr.Recognizer()


def listen() -> str:
    """
    Capture audio from the default microphone and return recognized text
    (lowercased). Returns an empty string if nothing could be understood,
    so callers can handle that gracefully instead of crashing.
    """
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            speak("I didn't hear anything. Could you say that again?")
            return ""

    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that. Could you please repeat?")
        return ""
    except sr.RequestError:
        speak("Speech recognition service is unavailable right now.")
        return ""


# --------------------------------------------------------------------------
# Config: custom commands (advanced tier)
# --------------------------------------------------------------------------
def load_config() -> dict:
    """
    Load user-defined custom commands and API keys from config.json.
    If the file doesn't exist yet, create a starter one.
    """
    default_config = {
        "openweathermap_api_key": "",
        "email": {
            "sender_address": "",
            "sender_app_password": "",
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
        },
        "custom_commands": {
            "open notes": "Sure, opening your notes app placeholder.",
            "tell me a joke": "Why do programmers prefer dark mode? "
                               "Because light attracts bugs!",
        },
    }
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)
        return default_config

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


config = load_config()


# --------------------------------------------------------------------------
# Feature: current time / date
# --------------------------------------------------------------------------
def tell_time() -> None:
    now = datetime.datetime.now()
    speak(f"The current time is {now.strftime('%I:%M %p')}.")


def tell_date() -> None:
    today = datetime.date.today()
    speak(f"Today's date is {today.strftime('%B %d, %Y')}.")


# --------------------------------------------------------------------------
# Feature: web search
# --------------------------------------------------------------------------
def web_search(query: str) -> None:
    if not query:
        speak("What would you like me to search for?")
        query = listen()
        if not query:
            return
    speak(f"Searching the web for {query}.")
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)


# --------------------------------------------------------------------------
# Feature: weather (advanced tier — needs OpenWeatherMap API key)
# --------------------------------------------------------------------------
def get_weather(city: str) -> None:
    api_key = config.get("openweathermap_api_key", "")
    if not api_key:
        speak("Weather lookup needs an OpenWeatherMap API key. "
              "Please add one to config.json.")
        return
    if requests is None:
        speak("The requests library isn't installed, so I can't fetch weather.")
        return

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if response.status_code != 200:
            speak(f"I couldn't find weather for {city}.")
            return
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        speak(f"It's currently {temp} degrees Celsius with {desc} in {city}.")
    except Exception:
        speak("Sorry, I couldn't reach the weather service right now.")


# --------------------------------------------------------------------------
# Feature: timed reminders (advanced tier)
# --------------------------------------------------------------------------
def set_reminder(minutes: float, message: str) -> None:
    speak(f"Okay, I'll remind you to {message} in {minutes} minutes.")

    def alert():
        time.sleep(minutes * 60)
        speak(f"Reminder: {message}")

    threading.Thread(target=alert, daemon=True).start()


# --------------------------------------------------------------------------
# Feature: send email (advanced tier — uses a dummy/test account)
# --------------------------------------------------------------------------
def send_email(recipient: str, subject: str, body: str) -> None:
    email_cfg = config.get("email", {})
    sender = email_cfg.get("sender_address", "")
    password = email_cfg.get("sender_app_password", "")

    if not sender or not password:
        speak("Email isn't configured yet. Please add sender credentials "
              "to config.json using a test account, not your main one.")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(email_cfg.get("smtp_server", "smtp.gmail.com"),
                           email_cfg.get("smtp_port", 587)) as server:
            server.starttls(context=context)
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        speak("Email sent successfully.")
    except Exception as e:
        speak("Sorry, I couldn't send that email.")
        print(f"Email error: {e}")


# --------------------------------------------------------------------------
# Lightweight intent parsing (advanced tier)
# Rule-based NLU: pulls out an intent + entities from a free-form sentence
# instead of requiring exact keyword matches.
# --------------------------------------------------------------------------
INTENT_PATTERNS = [
    ("greeting", re.compile(r"\b(hello|hi|hey)\b")),
    ("time", re.compile(r"\bwhat('?s| is)?\s*(the)?\s*time\b|\btime is it\b")),
    ("date", re.compile(r"\bwhat('?s| is)?\s*(the)?\s*date\b|\btoday'?s date\b")),
    ("search", re.compile(r"\bsearch (for )?(?P<query>.+)")),
    ("weather", re.compile(r"\bweather (in|for)?\s*(?P<city>[\w\s]+)")),
    ("reminder", re.compile(
        r"\bremind me to (?P<message>.+?) in (?P<minutes>\d+(\.\d+)?) minutes?"
    )),
    ("email", re.compile(
        r"\bsend (an )?email to (?P<recipient>\S+@\S+)"
        r"(?: (saying|with subject) (?P<body>.+))?"
    )),
    ("exit", re.compile(r"\b(exit|quit|stop|goodbye|bye)\b")),
]


def parse_intent(text: str):
    """Return (intent_name, match_object) for the first pattern that fits."""
    for name, pattern in INTENT_PATTERNS:
        match = pattern.search(text)
        if match:
            return name, match

    # fall back to custom commands from config.json
    for phrase, response in config.get("custom_commands", {}).items():
        if phrase in text:
            return "custom", response

    return None, None


# --------------------------------------------------------------------------
# Main dispatch loop
# --------------------------------------------------------------------------
def handle_command(text: str) -> bool:
    """
    Process one recognized utterance. Returns False if the assistant
    should stop listening (user asked to exit).
    """
    if not text:
        return True

    intent, match = parse_intent(text)

    if intent == "greeting":
        speak("Hello! How can I help you today?")
    elif intent == "time":
        tell_time()
    elif intent == "date":
        tell_date()
    elif intent == "search":
        web_search(match.group("query"))
    elif intent == "weather":
        get_weather(match.group("city").strip())
    elif intent == "reminder":
        set_reminder(float(match.group("minutes")), match.group("message"))
    elif intent == "email":
        recipient = match.group("recipient")
        body = match.group("body") or "This is a test message from your voice assistant."
        send_email(recipient, subject="Voice Assistant Message", body=body)
    elif intent == "custom":
        speak(match)  # match is the configured response string
    elif intent == "exit":
        speak("Goodbye! Have a great day.")
        return False
    else:
        speak("I'm not sure how to help with that yet. "
              "Try asking for the time, date, weather, or a web search.")

    return True


def main() -> None:
    speak("Voice assistant is ready. Say 'hello' to get started, "
          "or say 'exit' anytime to stop.")
    running = True
    while running:
        text = listen()
        running = handle_command(text)


if __name__ == "__main__":
    main()
