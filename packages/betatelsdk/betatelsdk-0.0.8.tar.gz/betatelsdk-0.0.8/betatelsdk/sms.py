import requests
from .base import SDKBase
from .types import SMSSendRequest, SMSSendResponse, SMSStatusResponse, SMSDetailsResponse

class SMSDK(SDKBase):
    """
    SMSDK provides functionality for sending SMS messages using the Betatel API.
    """
    
    def send(self, from_number: str, to: str, text: str) -> SMSSendResponse:
        """
        Send an SMS message.

        :param from_number: The sender's phone number.
        :param to: The recipient's phone number.
        :param text: The SMS message content.
        :return: SMS send response with message ID.
        :raises: Exception if the API call fails.
        """
        url = f"{self._base_api}/connect-hub/sms"
        payload = {
            "from": from_number,
            "to": to,
            "text": text
        }
        headers = self._get_auth_headers()

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            raise requests.exceptions.HTTPError(f"SMSDK.send failed: {response.status_code} - {response.text}")

        return response.json()
    
    def get_status(self, message_id: str) -> SMSStatusResponse:
        """
        Get the status of an SMS message.

        :param message_id: The unique identifier of the SMS message.
        :return: SMS status response.
        :raises: Exception if the API call fails.
        """
        url = f"{self._base_api}/connect-hub/sms/{message_id}/status"
        headers = self._get_auth_headers()

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise requests.exceptions.HTTPError(f"SMSDK.get_status failed: {response.status_code} - {response.text}")

        return response.json()
    
    def get_details(self, message_id: str) -> SMSDetailsResponse:
        """
        Get complete details of an SMS message.

        :param message_id: The unique identifier of the SMS message.
        :return: Complete SMS details response.
        :raises: Exception if the API call fails.
        """
        url = f"{self._base_api}/connect-hub/sms/{message_id}"
        headers = self._get_auth_headers()

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise requests.exceptions.HTTPError(f"SMSDK.get_details failed: {response.status_code} - {response.text}")

        return response.json()