import requests
from .base import SDKBase

class CarrierSDK(SDKBase):
    """
    CarrierSDK provides functionalities for managing CarrierIQ services.
    """

    def info(self, number: str) -> bool:
        """
        Gets carrier info about a specific number.

        :param number: Phone number in E164 format.
        :return: True if the call is successful, otherwise False.
        :raises: Exception if the API response status is invalid or an HTTP error occurs.
        """
        url = f"{self._base_api}/carrieriq/cid/{number}"

        response = requests.post(url, headers=self._get_auth_headers())

        if response.status_code != 200:
            raise requests.exceptions.HTTPError(f"CarrierSDK.info failed: {response.status_code} - {response.text}")

        return response.content

    def check_number(self, number: str) -> bool:
        """
        Gets information about a specific number.

        :param number: Phone number in E164 format.
        :return: True if the call is successful, otherwise False.
        :raises: Exception if the API response status is invalid or an HTTP error occurs.
        """
        url = f"{self._base_api}/carrieriq/ncheck/{number}"

        response = requests.post(url, headers=self._get_auth_headers())

        if response.status_code != 200:
            raise requests.exceptions.HTTPError(f"CarrierSDK.check_number failed: {response.status_code} - {response.text}")

        return response.content
