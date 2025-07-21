"""Tests for weather art module."""

import unittest

from weather.weather_art import WeatherArt


class TestWeatherArt(unittest.TestCase):
    """Test weather ASCII art functionality."""

    def test_get_weather_art_clear_day(self):
        """Test getting ASCII art for clear day condition."""
        art = WeatherArt.get_weather_art("01d")

        self.assertIsInstance(art, list)
        self.assertTrue(len(art) >= 5)  # Should have at least 5 lines
        self.assertIn("☀️", "".join(art))  # Should contain sun emoji

    def test_get_weather_art_clear_night(self):
        """Test getting ASCII art for clear night condition."""
        art = WeatherArt.get_weather_art("01n")

        self.assertIsInstance(art, list)
        self.assertEqual(len(art), 5)
        self.assertIn("🌙", "".join(art))  # Should contain moon emoji

    def test_get_weather_art_cloudy(self):
        """Test getting ASCII art for cloudy conditions."""
        for icon in ["02d", "02n", "03d", "03n", "04d", "04n"]:
            with self.subTest(icon=icon):
                art = WeatherArt.get_weather_art(icon)
                self.assertIsInstance(art, list)
                self.assertEqual(len(art), 5)
                self.assertIn("☁️", "".join(art))

    def test_get_weather_art_rain(self):
        """Test getting ASCII art for rain conditions."""
        for icon in ["09d", "09n", "10d", "10n"]:
            with self.subTest(icon=icon):
                art = WeatherArt.get_weather_art(icon)
                self.assertIsInstance(art, list)
                self.assertEqual(len(art), 5)
                art_text = "".join(art)
                self.assertTrue(
                    "☔" in art_text or "🌧️" in art_text or "💧" in art_text
                )

    def test_get_weather_art_thunderstorm(self):
        """Test getting ASCII art for thunderstorm conditions."""
        for icon in ["11d", "11n"]:
            with self.subTest(icon=icon):
                art = WeatherArt.get_weather_art(icon)
                self.assertIsInstance(art, list)
                self.assertEqual(len(art), 5)
                art_text = "".join(art)
                self.assertIn("⚡", art_text)  # Should contain lightning

    def test_get_weather_art_snow(self):
        """Test getting ASCII art for snow conditions."""
        for icon in ["13d", "13n"]:
            with self.subTest(icon=icon):
                art = WeatherArt.get_weather_art(icon)
                self.assertIsInstance(art, list)
                self.assertEqual(len(art), 5)
                self.assertIn("❄️", "".join(art))  # Should contain snowflake

    def test_get_weather_art_mist(self):
        """Test getting ASCII art for mist/fog conditions."""
        for icon in ["50d", "50n"]:
            with self.subTest(icon=icon):
                art = WeatherArt.get_weather_art(icon)
                self.assertIsInstance(art, list)
                self.assertEqual(len(art), 5)
                self.assertIn("≋", "".join(art))  # Should contain mist pattern

    def test_get_weather_art_unknown_condition(self):
        """Test getting ASCII art for unknown weather condition."""
        art = WeatherArt.get_weather_art("99x")  # Unknown condition

        self.assertIsInstance(art, list)
        self.assertEqual(len(art), 5)
        self.assertIn("?", "".join(art))  # Should contain question marks

    def test_format_weather_with_art_basic(self):
        """Test basic formatting of weather with ASCII art."""
        weather_text = """Weather in London, UK:
Temperature: 15.5°C (feels like 14.2°C)
Humidity: 78%
Conditions: Clear Sky"""

        result = WeatherArt.format_weather_with_art("01d", weather_text)

        self.assertIsInstance(result, str)
        self.assertIn("Weather in London, UK:", result)
        self.assertIn("☀️", result)  # Should contain sun from art
        self.assertIn("15.5°C", result)  # Should contain temperature
        lines = result.split("\n")
        self.assertTrue(len(lines) >= 4)  # Should have at least 4 lines total

    def test_format_weather_with_art_alignment(self):
        """Test that ASCII art and text are properly aligned."""
        weather_text = "Weather in Paris, France:\nTemperature: 22.1°C"

        result = WeatherArt.format_weather_with_art("01d", weather_text)
        lines = result.split("\n")

        # Check that the result contains both weather text and ASCII art
        self.assertIn("Weather in Paris, France:", result)
        self.assertIn("Temperature: 22.1°C", result)
        self.assertIn("☀️", result)  # Should contain sun emoji from art

        # Check that each non-empty line has some content
        non_empty_lines = [line for line in lines if line.strip()]
        self.assertTrue(len(non_empty_lines) > 0)

    def test_format_weather_with_art_different_line_counts(self):
        """Test formatting when weather text has different line count."""
        short_text = "Weather in Tokyo, Japan:"
        long_text = """Weather in Tokyo, Japan:
Temperature: 18.3°C (feels like 17.9°C)
Humidity: 65%
Conditions: Partly Cloudy
Wind: 5.2 km/h
Pressure: 1013 hPa
Extra line"""

        # Test short text (fewer lines than art)
        result_short = WeatherArt.format_weather_with_art("01d", short_text)
        lines_short = result_short.split("\n")
        self.assertTrue(len(lines_short) >= 5)  # Should match art line count

        # Test long text (more lines than art)
        result_long = WeatherArt.format_weather_with_art("01d", long_text)
        lines_long = result_long.split("\n")
        self.assertEqual(len(lines_long), 7)  # Should match text line count

    def test_format_weather_with_art_empty_text(self):
        """Test formatting with empty weather text."""
        result = WeatherArt.format_weather_with_art("01d", "")

        self.assertIsInstance(result, str)
        lines = result.split("\n")
        self.assertTrue(len(lines) >= 5)  # Should still have art lines
        self.assertIn("☀️", result)  # Should contain art

    def test_format_weather_with_art_preserves_text_content(self):
        """Test that all weather text content is preserved."""
        weather_text = """Weather in Berlin, Germany:
Temperature: -2.5°C (feels like -5.1°C)
Humidity: 85%
Conditions: Heavy Snow"""

        result = WeatherArt.format_weather_with_art("13d", weather_text)

        # Check that all original text content is present
        self.assertIn("Weather in Berlin, Germany:", result)
        self.assertIn("-2.5°C", result)
        self.assertIn("feels like -5.1°C", result)
        self.assertIn("85%", result)
        self.assertIn("Heavy Snow", result)

        # Check that snow art is present
        self.assertIn("❄️", result)


if __name__ == "__main__":
    unittest.main()
