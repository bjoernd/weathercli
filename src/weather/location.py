"""Enhanced location service with native GPS and IP geolocation fallback."""

import logging
import sys
from typing import Dict, Optional, Tuple

import requests

from weather.base_service import BaseAPIService
from weather.constants import (IPAPI_BASE_URL, USER_AGENT, 
                               PERMISSION_WAIT_TIMEOUT, LOCATION_UPDATE_TIMEOUT)

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
        platform_handlers = {
            "darwin": self._get_macos_location,
            "win32": self._get_windows_location,
            "linux": self._get_linux_location
        }
        
        platform = sys.platform
        if platform.startswith("linux"):
            platform = "linux"
            
        handler = platform_handlers.get(platform)
        if not handler:
            logger.debug(f"Native location not supported on {sys.platform}")
            return None
            
        return self._try_platform_location(handler, platform)
    
    def _try_platform_location(self, handler, platform_name: str) -> Optional[Tuple[float, float]]:
        """Try platform-specific location handler with error handling."""
        try:
            return handler()
        except ImportError:
            logger.debug(f"{platform_name} location libraries not available")
            return None
        except Exception as e:
            logger.debug(f"{platform_name} location error: {e}")
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
        """Get location using macOS Core Location framework."""
        import time
        from CoreLocation import (  # type: ignore[import-not-found]
            CLLocationManager, kCLAuthorizationStatusAuthorizedAlways,
            kCLAuthorizationStatusAuthorizedWhenInUse,
            kCLLocationAccuracyBest)

        location_manager = CLLocationManager.alloc().init()
        
        if not CLLocationManager.locationServicesEnabled():
            logger.debug("Location services are disabled")
            return None

        # Check and request permission
        authorized = [kCLAuthorizationStatusAuthorizedAlways, 
                     kCLAuthorizationStatusAuthorizedWhenInUse]
        auth_status = location_manager.authorizationStatus()
        
        if auth_status not in authorized:
            location_manager.requestWhenInUseAuthorization()
            time.sleep(PERMISSION_WAIT_TIMEOUT)
            if location_manager.authorizationStatus() not in authorized:
                return None

        # Get location with retry
        location_manager.setDesiredAccuracy_(kCLLocationAccuracyBest)
        location = location_manager.location()
        
        if location is None:
            location_manager.requestLocation()
            time.sleep(LOCATION_UPDATE_TIMEOUT)
            location = location_manager.location()

        if location is None:
            return None

        coordinate = location.coordinate()
        return (float(coordinate.latitude), float(coordinate.longitude))

    def _get_windows_location(self) -> Optional[Tuple[float, float]]:
        """Get location using Windows Location API."""
        import pythoncom  # type: ignore[import-untyped]
        import win32com.client  # type: ignore[import-untyped]

        pythoncom.CoInitialize()
        try:
            locator = win32com.client.Dispatch(
                "LocationDisp.LatLongReportFactory"
            )
            
            if locator.RequestPermissions(0) is None:
                return None
                
            location_report = locator.GetReport()
            if location_report is None:
                return None

            lat, lon = location_report.Latitude, location_report.Longitude
            return (float(lat), float(lon)) if lat and lon else None
            
        finally:
            pythoncom.CoUninitialize()

    def _get_linux_location(self) -> Optional[Tuple[float, float]]:
        """Get location using Linux GPSD daemon."""
        import gpsd  # type: ignore[import-not-found]
        
        gpsd.connect()
        packet = gpsd.get_current()
        
        if packet.mode < 2:
            return None
            
        lat, lon = packet.lat, packet.lon
        if not lat or not lon or lat == 0.0 or lon == 0.0:
            return None
            
        return (float(lat), float(lon))

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
