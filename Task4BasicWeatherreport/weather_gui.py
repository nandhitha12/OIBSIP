"""
Basic Weather App — OIBSIP Task 4 (Advanced Tier)
Author: Nandhitha Reddy

A tkinter GUI weather app using the OpenWeatherMap API. Shows current
conditions with an icon, a 6-hour forecast strip, a 5-day forecast strip,
a Celsius/Fahrenheit toggle, and optional auto-detection of the user's
city via their IP address (ipinfo.io).

Setup:
    1. Get a free API key at https://openweathermap.org/api
    2. Set it as the OWM_API_KEY environment variable, or edit API_KEY below

Run:
    python weather_gui.py
"""

import io
import os
import threading
import tkinter as tk
from tkinter import ttk

import requests
from PIL import Image, ImageTk

API_KEY = os.environ.get("OWM_API_KEY", "YOUR_API_KEY_HERE")
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
ICON_URL = "https://openweathermap.org/img/wn/{icon}@2x.png"
IPINFO_URL = "https://ipinfo.io/json"


def celsius_to_fahrenheit(c: float) -> float:
    return c * 9 / 5 + 32


class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Weather App")
        self.geometry("560x640")
        self.configure(bg="#EFF6FF")
        self.resizable(False, False)

        self.unit = "C"  # or "F"
        self.last_current_data = None  # cache for unit toggle re-render
        self.last_forecast_data = None
        self.icon_cache = {}  # avoid re-downloading the same icon

        self._build_widgets()

        if API_KEY == "YOUR_API_KEY_HERE":
            self._show_error("No API key set. Add OWM_API_KEY as an environment "
                              "variable, or edit API_KEY in weather_gui.py.")

    # ------------------------------------------------------------------
    def _build_widgets(self) -> None:
        top = tk.Frame(self, bg="#EFF6FF")
        top.pack(pady=(16, 8), padx=16, fill="x")

        tk.Label(top, text="Weather App", font=("Segoe UI", 18, "bold"),
                  bg="#EFF6FF").pack(side="left")

        self.unit_btn = tk.Button(top, text="Switch to °F", command=self.on_toggle_unit,
                                    bg="#6366F1", fg="white", relief="flat",
                                    padx=8, pady=4, cursor="hand2")
        self.unit_btn.pack(side="right")

        search_frame = tk.Frame(self, bg="#EFF6FF")
        search_frame.pack(padx=16, fill="x")

        self.city_entry = ttk.Entry(search_frame, font=("Segoe UI", 11))
        self.city_entry.pack(side="left", fill="x", expand=True, ipady=4)
        self.city_entry.bind("<Return>", lambda e: self.on_get_weather())

        tk.Button(search_frame, text="Get Weather", command=self.on_get_weather,
                   bg="#2563EB", fg="white", relief="flat", padx=10, pady=6,
                   cursor="hand2").pack(side="left", padx=(6, 0))

        tk.Button(search_frame, text="📍 Use My Location", command=self.on_auto_locate,
                   bg="#10B981", fg="white", relief="flat", padx=8, pady=6,
                   cursor="hand2").pack(side="left", padx=(6, 0))

        # error banner (hidden until needed)
        self.error_label = tk.Label(self, text="", bg="#FEE2E2", fg="#B91C1C",
                                      font=("Segoe UI", 9), wraplength=520, justify="left")

        # current conditions panel
        self.current_frame = tk.Frame(self, bg="white", relief="flat")
        self.current_frame.pack(pady=12, padx=16, fill="x")

        self.icon_label = tk.Label(self.current_frame, bg="white")
        self.icon_label.pack(side="left", padx=10, pady=10)

        info_frame = tk.Frame(self.current_frame, bg="white")
        info_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        self.city_label = tk.Label(info_frame, text="Search for a city", font=("Segoe UI", 14, "bold"), bg="white")
        self.city_label.pack(anchor="w")
        self.temp_label = tk.Label(info_frame, text="", font=("Segoe UI", 24, "bold"), bg="white")
        self.temp_label.pack(anchor="w")
        self.desc_label = tk.Label(info_frame, text="", font=("Segoe UI", 11), bg="white", fg="#4B5563")
        self.desc_label.pack(anchor="w")
        self.details_label = tk.Label(info_frame, text="", font=("Segoe UI", 9), bg="white", fg="#6B7280")
        self.details_label.pack(anchor="w", pady=(4, 0))

        # hourly forecast
        tk.Label(self, text="Next 6 Hours", font=("Segoe UI", 11, "bold"),
                  bg="#EFF6FF").pack(anchor="w", padx=18, pady=(4, 2))
        self.hourly_frame = tk.Frame(self, bg="#EFF6FF")
        self.hourly_frame.pack(padx=16, fill="x")

        # daily forecast
        tk.Label(self, text="Next 5 Days", font=("Segoe UI", 11, "bold"),
                  bg="#EFF6FF").pack(anchor="w", padx=18, pady=(10, 2))
        self.daily_frame = tk.Frame(self, bg="#EFF6FF")
        self.daily_frame.pack(padx=16, fill="x")

    # ------------------------------------------------------------------
    def _show_error(self, message: str) -> None:
        self.error_label.config(text=f"⚠ {message}")
        self.error_label.pack(pady=(0, 8), padx=16, fill="x")

    def _clear_error(self) -> None:
        self.error_label.pack_forget()

    def _clear_frame(self, frame: tk.Frame) -> None:
        for widget in frame.winfo_children():
            widget.destroy()

    # ------------------------------------------------------------------
    def on_get_weather(self) -> None:
        city = self.city_entry.get().strip()
        if not city:
            self._show_error("Please enter a city name.")
            return
        self._clear_error()
        threading.Thread(target=self._fetch_and_render, args=(city,), daemon=True).start()

    def on_auto_locate(self) -> None:
        self._clear_error()
        threading.Thread(target=self._auto_locate_and_fetch, daemon=True).start()

    def _auto_locate_and_fetch(self) -> None:
        try:
            response = requests.get(IPINFO_URL, timeout=8)
            response.raise_for_status()
            data = response.json()
            city = data.get("city")
            if not city:
                self.after(0, self._show_error, "Could not detect your city from your IP address.")
                return
            self.after(0, lambda: self.city_entry.delete(0, tk.END))
            self.after(0, lambda: self.city_entry.insert(0, city))
            self._fetch_and_render(city)
        except requests.exceptions.RequestException as e:
            self.after(0, self._show_error, f"Could not detect location: {e}")

    def on_toggle_unit(self) -> None:
        self.unit = "F" if self.unit == "C" else "C"
        self.unit_btn.config(text=f"Switch to °{'C' if self.unit == 'F' else 'F'}")
        if self.last_current_data:
            self._render_current(self.last_current_data)
        if self.last_forecast_data:
            self._render_forecasts(self.last_forecast_data)

    # ------------------------------------------------------------------
    def _fetch_and_render(self, city: str) -> None:
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        try:
            current_resp = requests.get(CURRENT_URL, params=params, timeout=10)
            forecast_resp = requests.get(FORECAST_URL, params=params, timeout=10)
        except requests.exceptions.Timeout:
            self.after(0, self._show_error, "Request timed out. Check your internet connection.")
            return
        except requests.exceptions.ConnectionError:
            self.after(0, self._show_error, "Could not connect to the weather service.")
            return
        except requests.exceptions.RequestException as e:
            self.after(0, self._show_error, f"Request failed: {e}")
            return

        if current_resp.status_code in (401, 403):
            self.after(0, self._show_error, "Invalid API key. Check your OpenWeatherMap key.")
            return
        if current_resp.status_code == 404:
            self.after(0, self._show_error, f"City '{city}' not found. Check the spelling.")
            return
        if current_resp.status_code != 200:
            self.after(0, self._show_error, f"Weather service error ({current_resp.status_code}).")
            return

        current_data = current_resp.json()
        forecast_data = forecast_resp.json() if forecast_resp.status_code == 200 else None

        self.last_current_data = current_data
        self.last_forecast_data = forecast_data

        self.after(0, self._clear_error)
        self.after(0, self._render_current, current_data)
        if forecast_data:
            self.after(0, self._render_forecasts, forecast_data)

    # ------------------------------------------------------------------
    def _format_temp(self, temp_c: float) -> str:
        if self.unit == "F":
            return f"{celsius_to_fahrenheit(temp_c):.1f}°F"
        return f"{temp_c:.1f}°C"

    def _get_icon(self, icon_code: str, size=(64, 64)):
        cache_key = (icon_code, size)
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        try:
            resp = requests.get(ICON_URL.format(icon=icon_code), timeout=8)
            image = Image.open(io.BytesIO(resp.content)).resize(size)
            photo = ImageTk.PhotoImage(image)
            self.icon_cache[cache_key] = photo
            return photo
        except Exception:
            return None

    def _render_current(self, data: dict) -> None:
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        main = data.get("main", {})
        temp_c = main.get("temp", 0)
        humidity = main.get("humidity", "N/A")
        wind_speed = data.get("wind", {}).get("speed", "N/A")
        weather_list = data.get("weather", [{}])
        description = weather_list[0].get("description", "N/A").title()
        icon_code = weather_list[0].get("icon", "01d")

        self.city_label.config(text=f"{city_name}, {country}")
        self.temp_label.config(text=self._format_temp(temp_c))
        self.desc_label.config(text=description)
        self.details_label.config(text=f"Humidity: {humidity}%   |   Wind: {wind_speed} m/s")

        icon = self._get_icon(icon_code, (72, 72))
        if icon:
            self.icon_label.config(image=icon)
            self.icon_label.image = icon

    def _render_forecasts(self, forecast_data: dict) -> None:
        entries = forecast_data.get("list", [])

        # --- hourly: API gives 3-hour steps, take the next 6 hours worth (2 entries) shown as up to 6 slots ---
        self._clear_frame(self.hourly_frame)
        hourly_slice = entries[:2]  # each step is 3 hours; 2 steps ≈ next 6 hours
        for entry in hourly_slice:
            self._add_forecast_card(self.hourly_frame, entry, daily=False)

        # --- daily: OpenWeatherMap's free 5-day/3-hour forecast; take one entry per day (~every 8th, which is 24h apart) ---
        self._clear_frame(self.daily_frame)
        daily_slice = entries[::8][:5]
        for entry in daily_slice:
            self._add_forecast_card(self.daily_frame, entry, daily=True)

    def _add_forecast_card(self, parent: tk.Frame, entry: dict, daily: bool) -> None:
        card = tk.Frame(parent, bg="white", padx=8, pady=8)
        card.pack(side="left", padx=4, pady=4)

        label_text = entry.get("dt_txt", "")[5:10] if daily else entry.get("dt_txt", "")[11:16]
        tk.Label(card, text=label_text, bg="white", font=("Segoe UI", 8)).pack()

        weather_list = entry.get("weather", [{}])
        icon_code = weather_list[0].get("icon", "01d")
        icon = self._get_icon(icon_code, (36, 36))
        icon_label = tk.Label(card, bg="white")
        if icon:
            icon_label.config(image=icon)
            icon_label.image = icon
        icon_label.pack()

        temp_c = entry.get("main", {}).get("temp", 0)
        tk.Label(card, text=self._format_temp(temp_c), bg="white",
                  font=("Segoe UI", 9, "bold")).pack()


if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
