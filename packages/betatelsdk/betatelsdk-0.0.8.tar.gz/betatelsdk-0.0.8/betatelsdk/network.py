import requests
from typing import Dict

from .base import SDKBase
from .types import NetworkStatus, NetworkMCCMNC
from .validators import validate_phone_number, ValidationError, handle_api_error

class NetworkSDK(SDKBase):
    """NetworkSDK provides methods for interacting with the Betatel Network API."""

    def get_status(self) -> NetworkStatus:
        """Get the operational status of the network service.

        Returns:
            NetworkStatus: The network service status.

        Raises:
            ValidationError: If the API response is invalid
            requests.exceptions.RequestException: If the API call fails
        """
        response = requests.get(
            f"{self._base_ver_api}/network/status",
            headers=self._get_auth_headers()
        )
        
        data = response.json()
        if response.status_code >= 400:
            handle_api_error(data)
        return data

    def lookup_mccmnc(self, phone_number: str) -> NetworkMCCMNC:
        """Lookup the MCC/MNC of a phone number.

        Args:
            phone_number (str): The phone number to lookup (e.g., 38761123456).

        Returns:
            NetworkMCCMNC: The MCC/MNC information.

        Raises:
            ValidationError: If the phone number is invalid or the API response is invalid
            requests.exceptions.RequestException: If the API call fails
        """
        if not phone_number:
            raise ValidationError("Phone number is required")
        if not validate_phone_number(phone_number):
            raise ValidationError("Invalid phone number format")

        response = requests.get(
            f"{self._base_ver_api}/network/mccmnc/{phone_number}",
            headers=self._get_auth_headers()
        )
        
        data = response.json()
        if response.status_code >= 400:
            handle_api_error(data)
        return data 