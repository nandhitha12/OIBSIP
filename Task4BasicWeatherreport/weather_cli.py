"""
Basic Weather App — OIBSIP Task 4 (Beginner Tier)
Author: Nandhitha Reddy

A command-line tool that fetches and displays real-time weather data for a
user-specified city using the OpenWeatherMap API.

Setup:
    1. Get a free API key at https://openweathermap.org/api
    2. Set it below in API_KEY, or as an environment variable OWM_API_KEY

Run:
    python weather_cli.py
"""

import os
from typing import Optional

import requests

# Prefer an environment variable so the key isn't hardcoded in shared code;
# falls back to the placeholder string below if you'd rather edit directly.
API_KEY = os.environ.get("OWM_API_KEY", "YOUR_API_KEY_HERE")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_city_input() -> str:
    """Prompt for a city name, rejecting empty input."""
    while True:
        city = input("Enter a city name: ").strip()
        if not city:
            print("  City name can't be empty. Please try again.")
            continue
        return city


def fetch_weather(city: str) -> Optional[dict]:
    """
    Call the OpenWeatherMap API for the given city.
    Returns the parsed JSON dict on success, or None on failure (after
    printing a helpful error message).
    """
    params = {"q": city, "appid": API_KEY, "units": "metric"}

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
    except requests.exceptions.Timeout:
        print("Error: The request timed out. Check your internet connection and try again.")
        return None
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the weather service. Check your internet connection.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: Something went wrong making the request: {e}")
        return None

    if response.status_code in (401, 403):
        print("Error: Invalid API key. Double-check your OpenWeatherMap API key.")
        return None
    if response.status_code == 404:
        print(f"Error: City '{city}' not found. Check the spelling and try again.")
        return None
    if response.status_code != 200:
        print(f"Error: Weather service returned an unexpected status ({response.status_code}).")
        return None

    try:
        return response.json()
    except ValueError:
        print("Error: Received an unreadable response from the weather service.")
        return None


def display_weather(data: dict) -> None:
    """Print the relevant weather fields in a friendly format."""
    city_name = data.get("name", "Unknown")
    country = data.get("sys", {}).get("country", "")

    main = data.get("main", {})
    temp_c = main.get("temp")
    humidity = main.get("humidity")

    weather_list = data.get("weather", [])
    description = weather_list[0]["description"].title() if weather_list else "N/A"

    wind_speed = data.get("wind", {}).get("speed")

    if temp_c is None:
        print("Error: Weather data is incomplete for this location.")
        return

    temp_f = temp_c * 9 / 5 + 32

    print("-" * 45)
    print(f"Weather in {city_name}, {country}")
    print("-" * 45)
    print(f"Temperature:  {temp_c:.1f}°C  ({temp_f:.1f}°F)")
    print(f"Condition:    {description}")
    print(f"Humidity:     {humidity}%")
    print(f"Wind Speed:   {wind_speed} m/s")
    print("-" * 45)


def main() -> None:
    print("=" * 45)
    print("           Basic Weather App")
    print("=" * 45)

    if API_KEY == "YOUR_API_KEY_HERE":
        print("Warning: No API key set. Add your OpenWeatherMap key to the")
        print("OWM_API_KEY environment variable, or edit API_KEY in this file.\n")

    while True:
        city = get_city_input()
        data = fetch_weather(city)
        if data:
            display_weather(data)

        again = input("\nCheck another city? [y/n]: ").strip().lower()
        if again != "y":
            print("Goodbye!")
            break
        print()


if __name__ == "__main__":
    main()
