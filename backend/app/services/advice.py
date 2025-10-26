from typing import Dict, Tuple
from datetime import datetime
from . import persistence

DEFAULT_LANG = 'en'

# Simple localized templates. Real projects should use gettext or similar.
TEMPLATES = {
    'en': {
        'too_hot': "☀️ DANGER: {crop} store is TOO WARM ({temp}°C). {advice}",
        'too_cold': "❄️ NOTICE: {crop} store is TOO COLD ({temp}°C). {advice}",
        'too_humid': "💧 DANGER: Humidity is {hum}%. High risk of mold on your {crop}. {advice}",
        'ok': "✅ OK: {crop} store conditions are within safe range.",
    },
    'sw': {
        'too_hot': "☀️ HATARI: Hifadhi ya {crop} ina JOTO JAA ({temp}°C). {advice}",
        'too_cold': "❄️ TAARIFA: Hifadhi ya {crop} iko BARIDI ({temp}°C). {advice}",
        'too_humid': "💧 HATARI: Unyevu ni {hum}%. Hatari ya ukungu kwa {crop}. {advice}",
        'ok': "✅ SAWA: Mazingira ya hifadhi ni salama kwa {crop}.",
    }
}

DEFAULT_ADVICE = {
    'too_hot': 'Open vents tonight and increase airflow.',
    'too_cold': 'Insulate and avoid freezing temperatures.',
    'too_humid': 'Increase airflow NOW and reduce humidity; consider drying.',
}

def load_profiles():
    return persistence.load_crop_profiles()

def get_profile(crop: str):
    profiles = load_profiles()
    return profiles.get(crop.lower())

def evaluate_reading(crop: str, temperature: float, humidity: float) -> Tuple[str, dict]:
    """Return (level, details) where level is one of 'ok','too_hot','too_cold','too_humid'"""
    profile = get_profile(crop)
    if not profile:
        return 'ok', {'reason': 'no_profile'}
    tmin = profile['temperature']['min']
    tmax = profile['temperature']['max']
    hmin = profile['humidity']['min']
    hmax = profile['humidity']['max']
    if temperature is not None and temperature > tmax:
        return 'too_hot', {'temp': temperature, 'threshold': tmax}
    if temperature is not None and temperature < tmin:
        return 'too_cold', {'temp': temperature, 'threshold': tmin}
    if humidity is not None and humidity > hmax:
        return 'too_humid', {'hum': humidity, 'threshold': hmax}
    return 'ok', {'temp': temperature, 'hum': humidity}

def format_message(level: str, crop: str, lang: str = DEFAULT_LANG, **kwargs) -> str:
    lang_templates = TEMPLATES.get(lang, TEMPLATES[DEFAULT_LANG])
    tpl = lang_templates.get(level, lang_templates['ok'])
    advice = DEFAULT_ADVICE.get(level, '')
    data = {**kwargs}
    data.setdefault('advice', advice)
    data.setdefault('crop', crop)
    return tpl.format(**data)
