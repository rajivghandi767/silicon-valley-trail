# backend/game/services/weather.py
import urllib.request
import json
import random
from typing import Tuple
from django.core.cache import cache


def check_marine_conditions(latitude: float, longitude: float) -> Tuple[bool, float]:
    cache_key = f"svt_marine_{latitude}_{longitude}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    url = f"https://marine-api.open-meteo.com/v1/marine?latitude={latitude}&longitude={longitude}&current=wave_height"
    try:
        req = urllib.request.Request(
            url, headers={'User-Agent': 'SiliconValleyTrail/1.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            wave_height: float = float(
                data.get('current', {}).get('wave_height', 0.0))
            is_rough_seas: bool = wave_height >= 1.5 or random.random() < 0.20
            result = (is_rough_seas, wave_height)
            cache.set(cache_key, result, timeout=600)
            return result
    except Exception as e:
        print(f"❌ Marine API Error: {e}")
        return False, 0.0


def check_aviation_conditions(latitude: float, longitude: float) -> Tuple[bool, bool]:
    cache_key = f"svt_aviation_{latitude}_{longitude}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    try:
        req = urllib.request.Request(
            url, headers={'User-Agent': 'SiliconValleyTrail/1.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            weather_code: int = int(
                data.get('current_weather', {}).get('weathercode', 0))
            wind_speed: float = float(
                data.get('current_weather', {}).get('windspeed', 0.0))

            is_thunderstorm: bool = weather_code >= 61 or random.random() < 0.20
            is_turbulent: bool = wind_speed >= 25.0 or random.random() < 0.50

            result = (is_thunderstorm, is_turbulent)
            cache.set(cache_key, result, timeout=600)
            return result
    except Exception as e:
        print(f"❌ Aviation API Error: {e}")
        return False, False
