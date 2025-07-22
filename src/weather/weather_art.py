"""ASCII art representations for weather conditions."""

from typing import Dict, List


class WeatherArt:
    """Provides ASCII art representations for weather conditions."""

    # Multi-line ASCII art for weather conditions
    _ASCII_ART: Dict[str, List[str]] = {
        # Clear sky - day
        "01d": [
            "    \\   |   /    ",
            "     .-.-.-.     ",
            "  .- (  ☀️  ) -. ",
            "     '-'-'-'     ",
            "    /   |   \\    ",
        ],
        # Clear sky - night
        "01n": [
            "     *   *       ",
            "   *             ",
            "       🌙        ",
            "   *        *    ",
            "     *   *       ",
        ],
        # Few clouds - day
        "02d": [
            "    \\  |  /      ",
            " .-.  ☀️  .-.    ",
            "(   ☁️☁️☁️   )   ",
            " '-'     '-'     ",
            "                 ",
        ],
        # Few clouds - night
        "02n": [
            "  *   🌙    *   ",
            " .-.      .-.   ",
            "(   ☁️☁️☁️   )  ",
            " '-'     '-'    ",
            "   *        *   ",
        ],
        # Scattered clouds
        "03d": [
            "     .-.-.       ",
            "   ☁️(     )☁️  ",
            "  ( ☁️☁️☁️☁️ )  ",
            "   '-☁️☁️☁️-'   ",
            "     '-'-'       ",
        ],
        "03n": [
            "     .-.-.       ",
            "   ☁️(     )☁️  ",
            "  ( ☁️☁️☁️☁️ )  ",
            "   '-☁️☁️☁️-'   ",
            "     '-'-'       ",
        ],
        # Broken/overcast clouds
        "04d": [
            "   ☁️☁️☁️☁️☁️    ",
            " ☁️☁️☁️☁️☁️☁️☁️  ",
            "☁️☁️☁️☁️☁️☁️☁️☁️ ",
            " ☁️☁️☁️☁️☁️☁️☁️  ",
            "   ☁️☁️☁️☁️☁️    ",
        ],
        "04n": [
            "   ☁️☁️☁️☁️☁️    ",
            " ☁️☁️☁️☁️☁️☁️☁️  ",
            "☁️☁️☁️☁️☁️☁️☁️☁️ ",
            " ☁️☁️☁️☁️☁️☁️☁️  ",
            "   ☁️☁️☁️☁️☁️    ",
        ],
        # Shower rain
        "09d": [
            "     .-.-.       ",
            "   ☁️(     )☁️  ",
            "  ( ☁️☁️☁️☁️ )  ",
            "   '☔☔☔☔☔'  ",
            "    💧💧💧💧     ",
        ],
        "09n": [
            "     .-.-.       ",
            "   ☁️(     )☁️  ",
            "  ( ☁️☁️☁️☁️ )  ",
            "   '☔☔☔☔☔'  ",
            "    💧💧💧💧     ",
        ],
        # Rain
        "10d": [
            "    \\  |  /      ",
            " .-.  ☀️  .-.    ",
            "(   ☁️☁️☁️   )   ",
            "  '🌧️🌧️🌧️🌧️'  ",
            "   💧💧💧💧      ",
        ],
        "10n": [
            "     .-.-.       ",
            "   ☁️(     )☁️  ",
            "  ( ☁️☁️☁️☁️ )  ",
            "  '🌧️🌧️🌧️🌧️'  ",
            "    💧💧💧💧     ",
        ],
        # Thunderstorm
        "11d": [
            "   ☁️☁️☁️☁️☁️    ",
            " ☁️☁️⛈️⛈️☁️☁️   ",
            "☁️⚡☁️☁️⚡☁️☁️   ",
            " '🌧️⚡🌧️⚡🌧️'  ",
            "   💧⚡💧⚡💧    ",
        ],
        "11n": [
            "   ☁️☁️☁️☁️☁️    ",
            " ☁️☁️⛈️⛈️☁️☁️   ",
            "☁️⚡☁️☁️⚡☁️☁️   ",
            " '🌧️⚡🌧️⚡🌧️'  ",
            "   💧⚡💧⚡💧    ",
        ],
        # Snow
        "13d": [
            "     .-.-.       ",
            "   ☁️(     )☁️  ",
            "  ( ☁️☁️☁️☁️ )  ",
            "   '❄️❄️❄️❄️'   ",
            "    ❄️❄️❄️❄️     ",
        ],
        "13n": [
            "     .-.-.       ",
            "   ☁️(     )☁️  ",
            "  ( ☁️☁️☁️☁️ )  ",
            "   '❄️❄️❄️❄️'   ",
            "    ❄️❄️❄️❄️     ",
        ],
        # Mist/Fog
        "50d": [
            "  ≋≋≋≋≋≋≋≋≋≋≋≋   ",
            " ≋≋≋≋≋≋≋≋≋≋≋≋≋≋  ",
            "≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋ ",
            " ≋≋≋≋≋≋≋≋≋≋≋≋≋≋  ",
            "  ≋≋≋≋≋≋≋≋≋≋≋≋   ",
        ],
        "50n": [
            "  ≋≋≋≋≋≋≋≋≋≋≋≋   ",
            " ≋≋≋≋≋≋≋≋≋≋≋≋≋≋  ",
            "≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋ ",
            " ≋≋≋≋≋≋≋≋≋≋≋≋≋≋  ",
            "  ≋≋≋≋≋≋≋≋≋≋≋≋   ",
        ],
    }

    # Default fallback art for unknown conditions
    _DEFAULT_ART: List[str] = [
        "     ????        ",
        "   ????????      ",
        " ????????????    ",
        "   ????????      ",
        "     ????        ",
    ]

    @classmethod
    def get_weather_art(cls, weather_icon: str) -> List[str]:
        """
        Get ASCII art for a weather condition.

        Args:
            weather_icon: OpenWeatherMap icon code (e.g., '01d', '10n')

        Returns:
            List of strings representing ASCII art lines
        """
        return cls._ASCII_ART.get(weather_icon, cls._DEFAULT_ART)

    @classmethod
    def format_weather_with_art(
        cls, weather_icon: str, weather_text: str
    ) -> str:
        """
        Combine weather text with ASCII art, text on left, art on right.

        Args:
            weather_icon: OpenWeatherMap icon code
            weather_text: Formatted weather information text

        Returns:
            Combined text and ASCII art output
        """
        art_lines = cls.get_weather_art(weather_icon)
        text_lines = weather_text.strip().split("\n")

        # Find the maximum number of lines needed
        max_lines = max(len(art_lines), len(text_lines))

        # Pad shorter lists with empty strings
        while len(art_lines) < max_lines:
            art_lines.append("")
        while len(text_lines) < max_lines:
            text_lines.append("")

        # Find the maximum width of text lines for consistent alignment
        non_empty_lines = [line for line in text_lines if line]
        max_text_width = (
            max(len(line) for line in non_empty_lines)
            if non_empty_lines
            else 0
        )

        # Combine lines with text on left, art aligned to the right
        combined_lines = []
        for text_line, art_line in zip(text_lines, art_lines):
            if text_line:
                # Pad text to consistent width and add art to the right
                padded_text = text_line.ljust(max_text_width)
                combined_lines.append(f"{padded_text}\t{art_line}")
            else:
                # Art-only lines (aligned to the right position)
                padding = " " * max_text_width
                combined_lines.append(f"{padding}\t{art_line}")

        return "\n".join(combined_lines)
