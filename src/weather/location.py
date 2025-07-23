"""Enhanced location service with native GPS and IP geolocation fallback."""

import logging
import sys
from typing import Dict, Optional, Tuple

import requests

from weather.base_service import BaseAPIService
from weather.constants import IPAPI_BASE_URL, USER_AGENT

logger = logging.getLogger(__name__)


class LocationService(BaseAPIService):
    """Enhanced location service with native GPS and IP geolocation."""

    def __init__(self):
        """Initialize location service."""
        super().__init__(IPAPI_BASE_URL)

    def get_current_location(self) -> Optional[Tuple[float, float]]:
        """
        Get current location using 3-layer fallback approach:
        1. Native system location (GPS/WiFi positioning)
        2. IP geolocation (existing implementation)
        3. Returns None if all methods fail

        Returns:
            Tuple of (latitude, longitude) or None if failed

        Raises:
            requests.RequestException: If API request fails
        """
        # Layer 1: Try native system location first
        logger.debug("Attempting native system location...")
        native_coords = self._get_native_location()
        if native_coords:
            logger.info(f"Using native location: {native_coords}")
            return native_coords

        # Layer 2: Fallback to IP geolocation
        logger.debug("Falling back to IP geolocation...")
        ip_coords = self._get_ip_location()
        if ip_coords:
            logger.info(f"Using IP geolocation: {ip_coords}")
            return ip_coords

        # Layer 3: All methods failed
        logger.warning("All location methods failed")
        return None

    def _get_native_location(self) -> Optional[Tuple[float, float]]:
        """
        Get location from native system location services.

        Returns:
            Tuple of (latitude, longitude) or None if unavailable
        """
        try:
            if sys.platform == "darwin":
                return self._get_macos_location()
            elif sys.platform == "win32":
                return self._get_windows_location()
            elif sys.platform.startswith("linux"):
                return self._get_linux_location()
            else:
                logger.debug(
                    f"Native location not supported on {sys.platform}"
                )
                return None
        except Exception as e:
            logger.debug(f"Native location failed: {e}")
            return None

    def _get_ip_location(self) -> Optional[Tuple[float, float]]:
        """
        Get current location coordinates via IP geolocation.

        Returns:
            Tuple of (latitude, longitude) or None if failed
        """
        try:
            location_data = self._make_request(
                headers={"User-Agent": USER_AGENT}
            )

            if location_data.get("error"):
                error_msg = location_data.get("reason", "Unknown error")
                logger.warning(f"IP location service error: {error_msg}")
                return None

            latitude = location_data.get("latitude")
            longitude = location_data.get("longitude")

            if latitude is None or longitude is None:
                return None

            return (float(latitude), float(longitude))
        except Exception as e:
            logger.debug(f"IP geolocation failed: {e}")
            return None

    def _get_macos_location(self) -> Optional[Tuple[float, float]]:
        """
        Get location using macOS Core Location framework.

        Returns:
            Tuple of (latitude, longitude) or None if unavailable
        """
        try:
            import time

            from CoreLocation import (  # type: ignore[import-not-found]
                CLLocationManager, kCLAuthorizationStatusAuthorizedAlways,
                kCLAuthorizationStatusAuthorizedWhenInUse,
                kCLLocationAccuracyBest)

            # Create location manager
            location_manager = CLLocationManager.alloc().init()

            # Check if location services are enabled
            if not CLLocationManager.locationServicesEnabled():
                logger.debug("Location services are disabled")
                return None

            # Request permission if needed
            auth_status = location_manager.authorizationStatus()
            if auth_status not in [
                kCLAuthorizationStatusAuthorizedAlways,
                kCLAuthorizationStatusAuthorizedWhenInUse,
            ]:
                logger.debug("Location permission not granted")
                # Try requesting permission
                location_manager.requestWhenInUseAuthorization()
                time.sleep(1)  # Brief wait for permission dialog

                # Check again
                auth_status = location_manager.authorizationStatus()
                if auth_status not in [
                    kCLAuthorizationStatusAuthorizedAlways,
                    kCLAuthorizationStatusAuthorizedWhenInUse,
                ]:
                    return None

            # Configure location manager
            location_manager.setDesiredAccuracy_(kCLLocationAccuracyBest)

            # Get current location
            location = location_manager.location()
            if location is None:
                # Try requesting location update
                location_manager.requestLocation()
                time.sleep(2)  # Wait for location update
                location = location_manager.location()

            if location is None:
                logger.debug("Could not get macOS location")
                return None

            coordinate = location.coordinate()
            return (float(coordinate.latitude), float(coordinate.longitude))

        except ImportError:
            logger.debug("CoreLocation framework not available")
            return None
        except Exception as e:
            logger.debug(f"macOS location error: {e}")
            return None

    def _get_windows_location(self) -> Optional[Tuple[float, float]]:
        """
        Get location using Windows Location API.

        Returns:
            Tuple of (latitude, longitude) or None if unavailable
        """
        try:
            import pythoncom  # type: ignore[import-untyped]
            import win32com.client  # type: ignore[import-untyped]

            # Initialize COM
            pythoncom.CoInitialize()

            try:
                # Create Location API object
                locator = win32com.client.Dispatch(
                    "LocationDisp.LatLongReportFactory"
                )

                # Request location with timeout
                report = locator.RequestPermissions(0)
                if report is None:
                    logger.debug("Windows location permission denied")
                    return None

                # Get latest report
                location_report = locator.GetReport()
                if location_report is None:
                    logger.debug("No Windows location report available")
                    return None

                lat = location_report.Latitude
                lon = location_report.Longitude

                if lat is None or lon is None:
                    return None

                return (float(lat), float(lon))

            finally:
                pythoncom.CoUninitialize()

        except ImportError:
            logger.debug("Windows COM location API not available")
            return None
        except Exception as e:
            logger.debug(f"Windows location error: {e}")
            return None

    def _get_linux_location(self) -> Optional[Tuple[float, float]]:
        """
        Get location using Linux GPSD daemon.

        Returns:
            Tuple of (latitude, longitude) or None if unavailable
        """
        try:
            import gpsd  # type: ignore[import-not-found]

            # Connect to GPSD daemon
            gpsd.connect()

            # Get GPS fix
            packet = gpsd.get_current()

            if packet.mode < 2:  # No fix available
                logger.debug("No GPS fix available")
                return None

            lat = packet.lat
            lon = packet.lon

            if lat is None or lon is None or lat == 0.0 or lon == 0.0:
                return None

            return (float(lat), float(lon))

        except ImportError:
            logger.debug("GPSD library not available")
            return None
        except Exception as e:
            logger.debug(f"Linux GPS error: {e}")
            return None

    def get_location_info(self) -> Optional[Dict[str, str]]:
        """
        Get detailed location information via IP geolocation.

        Returns:
            Dictionary containing location details or None if failed
        """
        try:
            location_data = self._make_request(
                headers={"User-Agent": USER_AGENT}
            )

            if location_data.get("error"):
                return None

            return {
                "city": location_data.get("city", "Unknown"),
                "region": location_data.get("region", "Unknown"),
                "country": location_data.get("country_name", "Unknown"),
                "country_code": location_data.get("country", "Unknown"),
                "timezone": location_data.get("timezone", "Unknown"),
            }
        except (requests.RequestException, ValueError, KeyError):
            return None
