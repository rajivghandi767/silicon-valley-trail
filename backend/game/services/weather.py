# backend/game/services/weather.py
import urllib.request
import json
import random
from typing import Tuple, cast
from django.core.cache import cache
from ..engine.constants import (
    WEATHER_CACHE_TTL,
    EXTERNAL_HTTP_TIMEOUT,
    MARINE_ROUGH_WAVE_HEIGHT_M,
    MARINE_ROUGH_RANDOM_CHANCE,
    AVIATION_THUNDERSTORM_CODE,
    AVIATION_THUNDERSTORM_RANDOM_CHANCE,
    AVIATION_TURBULENT_WIND_SPEED,
    AVIATION_TURBULENT_RANDOM_CHANCE,
)


def check_marine_conditions(latitude: float, longitude: float) -> Tuple[bool, float]:
    cache_key = f"svt_marine_{latitude}_{longitude}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cast(Tuple[bool, float], cached)

    url = f"https://marine-api.open-meteo.com/v1/marine?latitude={latitude}&longitude={longitude}&current=wave_height"
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "SiliconValleyTrail/1.0"}
        )
        with urllib.request.urlopen(req, timeout=EXTERNAL_HTTP_TIMEOUT) as response:
            data = json.loads(response.read().decode())
            wave_height: float = float(data.get("current", {}).get("wave_height", 0.0))
            is_rough_seas: bool = (
                wave_height >= MARINE_ROUGH_WAVE_HEIGHT_M
                or random.random() < MARINE_ROUGH_RANDOM_CHANCE
            )
            result = (is_rough_seas, wave_height)
            cache.set(cache_key, result, timeout=WEATHER_CACHE_TTL)
            return result
    except Exception as e:
        print(f"❌ Marine API Error: {e}")
        return False, 0.0


def check_aviation_conditions(latitude: float, longitude: float) -> Tuple[bool, bool]:
    cache_key = f"svt_aviation_{latitude}_{longitude}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cast(Tuple[bool, bool], cached)

    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "SiliconValleyTrail/1.0"}
        )
        with urllib.request.urlopen(req, timeout=EXTERNAL_HTTP_TIMEOUT) as response:
            data = json.loads(response.read().decode())
            weather_code: int = int(
                data.get("current_weather", {}).get("weathercode", 0)
            )
            wind_speed: float = float(
                data.get("current_weather", {}).get("windspeed", 0.0)
            )

            is_thunderstorm: bool = (
                weather_code >= AVIATION_THUNDERSTORM_CODE
                or random.random() < AVIATION_THUNDERSTORM_RANDOM_CHANCE
            )
            is_turbulent: bool = (
                wind_speed >= AVIATION_TURBULENT_WIND_SPEED
                or random.random() < AVIATION_TURBULENT_RANDOM_CHANCE
            )

            result = (is_thunderstorm, is_turbulent)
            cache.set(cache_key, result, timeout=WEATHER_CACHE_TTL)
            return result
    except Exception as e:
        print(f"❌ Aviation API Error: {e}")
        return False, False
