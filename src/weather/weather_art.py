"""ASCII art representations for weather conditions."""

from typing import Dict, List


class WeatherArt:
    """Provides ASCII art representations for weather conditions."""

    # Compressed ASCII art patterns
    _ART_PATTERNS = {
        "clear_day": ["    \\   |   /    ", "     .-.-.-.     ", "  .- (  ☀️  ) -. ", "     '-'-'-'     ", "    /   |   \\    "],
        "clear_night": ["     *   *       ", "   *             ", "       🌙        ", "   *        *    ", "     *   *       "],
        "few_clouds_day": ["    \\  |  /      ", " .-.  ☀️  .-.    ", "(   ☁️☁️☁️   )   ", " '-'     '-'     ", "                 "],
        "few_clouds_night": ["  *   🌙    *   ", " .-.      .-.   ", "(   ☁️☁️☁️   )  ", " '-'     '-'    ", "   *        *   "],
        "scattered_clouds": ["     .-.-.       ", "   ☁️(     )☁️  ", "  ( ☁️☁️☁️☁️ )  ", "   '-☁️☁️☁️-'   ", "     '-'-'       "],
        "broken_clouds": ["   ☁️☁️☁️☁️☁️    ", " ☁️☁️☁️☁️☁️☁️☁️  ", "☁️☁️☁️☁️☁️☁️☁️☁️ ", " ☁️☁️☁️☁️☁️☁️☁️  ", "   ☁️☁️☁️☁️☁️    "],
        "shower_rain": ["     .-.-.       ", "   ☁️(     )☁️  ", "  ( ☁️☁️☁️☁️ )  ", "   '☔☔☔☔☔'  ", "    💧💧💧💧     "],
        "rain_day": ["    \\  |  /      ", " .-.  ☀️  .-.    ", "(   ☁️☁️☁️   )   ", "  '🌧️🌧️🌧️🌧️'  ", "   💧💧💧💧      "],
        "rain_night": ["     .-.-.       ", "   ☁️(     )☁️  ", "  ( ☁️☁️☁️☁️ )  ", "  '🌧️🌧️🌧️🌧️'  ", "   💧💧💧💧      "],
        "thunderstorm": ["   ☁️☁️☁️☁️☁️    ", " ☁️☁️⛈️⛈️☁️☁️   ", "☁️⚡☁️☁️⚡☁️☁️   ", " '🌧️⚡🌧️⚡🌧️'  ", "   💧⚡💧⚡💧    "],
        "snow": ["     .-.-.       ", "   ☁️(     )☁️  ", "  ( ☁️☁️☁️☁️ )  ", "   '❄️❄️❄️❄️'   ", "    ❄️❄️❄️❄️     "],
        "mist": ["  ≋≋≋≋≋≋≋≋≋≋≋≋   ", " ≋≋≋≋≋≋≋≋≋≋≋≋≋≋  ", "≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋ ", " ≋≋≋≋≋≋≋≋≋≋≋≋≋≋  ", "  ≋≋≋≋≋≋≋≋≋≋≋≋   "],
        "default": ["     ????        ", "   ????????      ", " ????????????    ", "   ????????      ", "     ????        "]
    }
    
    # Icon to pattern mapping
    _ASCII_ART: Dict[str, List[str]] = {
        "01d": _ART_PATTERNS["clear_day"],
        "01n": _ART_PATTERNS["clear_night"],
        "02d": _ART_PATTERNS["few_clouds_day"],
        "02n": _ART_PATTERNS["few_clouds_night"],
        "03d": _ART_PATTERNS["scattered_clouds"],
        "03n": _ART_PATTERNS["scattered_clouds"],
        "04d": _ART_PATTERNS["broken_clouds"],
        "04n": _ART_PATTERNS["broken_clouds"],
        "09d": _ART_PATTERNS["shower_rain"],
        "09n": _ART_PATTERNS["shower_rain"],
        "10d": _ART_PATTERNS["rain_day"],
        "10n": _ART_PATTERNS["rain_night"],
        "11d": _ART_PATTERNS["thunderstorm"],
        "11n": _ART_PATTERNS["thunderstorm"],
        "13d": _ART_PATTERNS["snow"],
        "13n": _ART_PATTERNS["snow"],
        "50d": _ART_PATTERNS["mist"],
        "50n": _ART_PATTERNS["mist"],
    }

    @classmethod
    def get_weather_art(cls, weather_icon: str) -> List[str]:
        """Get ASCII art for a weather condition."""
        return cls._ASCII_ART.get(weather_icon, cls._ART_PATTERNS["default"])

    @classmethod
    def format_weather_with_art(cls, weather_icon: str, weather_text: str) -> str:
        """Combine weather text with ASCII art, text on left, art on right."""
        art_lines = cls.get_weather_art(weather_icon)
        text_lines = weather_text.strip().split("\n")

        max_lines = max(len(art_lines), len(text_lines))
        
        # Pad shorter lists
        art_lines.extend([""] * (max_lines - len(art_lines)))
        text_lines.extend([""] * (max_lines - len(text_lines)))

        # Find max text width for alignment
        max_text_width = max((len(line) for line in text_lines if line), default=0)

        # Combine with separator
        combined_lines = []
        for text_line, art_line in zip(text_lines, art_lines):
            padded_text = text_line.ljust(max_text_width) if text_line else " " * max_text_width
            combined_lines.append(f"{padded_text} │ {art_line}")

        return "\n".join(combined_lines)