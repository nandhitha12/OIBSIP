# Task 4 — Basic Weather App

**OIBSIP | Oasis Infobyte Internship**
**Author:** Nandhitha Reddy

Two versions are included:
- `weather_cli.py` — beginner tier, command-line
- `weather_gui.py` — advanced tier, GUI with icons, forecasts, unit toggle, auto-location

---

## Features

### Beginner tier — `weather_cli.py` (all complete)
- [x] Prompts for a city name
- [x] Calls the OpenWeatherMap API and parses the JSON response
- [x] Displays temperature (°C and °F), humidity, weather description, wind speed
- [x] Graceful error handling — city not found, timeout, connection error,
      invalid API key, each with a specific message
- [x] Input validation — rejects empty city names

### Advanced tier — `weather_gui.py` (all complete)
- [x] GUI window (tkinter) with a city field, "Get Weather" button, results panel
- [x] Weather icons pulled from OpenWeatherMap's icon URLs, shown for
      current conditions and every forecast card
- [x] Hourly forecast panel — next ~6 hours (two 3-hour steps from the
      free forecast API)
- [x] Daily forecast panel — next 5 days (one entry per day, sampled from
      the 3-hourly forecast data)
- [x] Celsius/Fahrenheit toggle button — re-renders all currently
      displayed data in the new unit without a fresh API call
- [x] Bonus: "Use My Location" button — auto-detects your city via your
      IP address using ipinfo.io, then fetches weather for it
- [x] All errors shown as an in-GUI banner, not terminal print statements

---

## Setup

1. **Get a free OpenWeatherMap API key**
   Sign up at https://openweathermap.org/api (free tier gives 60 calls/minute,
   plenty for this project).

2. **Set your API key** — two options:
   - **Recommended:** set an environment variable so it's never hardcoded:
     ```bash
     # Windows (Command Prompt)
     set OWM_API_KEY=your_key_here

     # Windows (PowerShell)
     $env:OWM_API_KEY="your_key_here"

     # macOS/Linux
     export OWM_API_KEY=your_key_here
     ```
   - **Or:** open `weather_cli.py` / `weather_gui.py` and replace
     `"YOUR_API_KEY_HERE"` directly.

   Note: a brand-new OpenWeatherMap key can take up to a couple of hours to
   activate — if you get an "invalid API key" error right after signing up,
   wait a bit and try again.

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the CLI version**
   ```bash
   python weather_cli.py
   ```

5. **Run the GUI version**
   ```bash
   python weather_gui.py
   ```

## Notes
- The free OpenWeatherMap forecast endpoint returns data in 3-hour steps,
  not true hourly/daily data — the GUI approximates "next 6 hours" (2
  steps) and "next 5 days" (one step per ~24h) from that data, which is
  the standard approach on the free tier.
- The "Use My Location" feature relies on IP-based geolocation via
  ipinfo.io, which is approximate (city-level, not exact address) and can
  be inaccurate on some networks (e.g. VPNs, mobile data).

## Tech stack
`Python`, `requests`, `json` (CLI), `tkinter`, `Pillow` (GUI icons),
OpenWeatherMap API, ipinfo.io API (bonus)
