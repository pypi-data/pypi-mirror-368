import requests
from .base import SDKBase

class VoiceSDK(SDKBase):
    """
    VoiceSDK provides functionality for managing voice-related actions using the Betatel API.
    """
    def otp(self, text, language='en', pause_digit=50, pause_phrase=200, repeats=1):
        """
        Creates an OTP message.

        :param text: The text content of the OTP message.
        :param language: Language for the OTP message (default: 'en').
        :param pause_digit: Pause duration between digits in milliseconds (default: 50).
        :param pause_phrase: Pause duration between phrases in milliseconds (default: 200).
        :param repeats: Number of times the message should repeat (default: 1).
        :return: The OTP message as binary content.
        :raises: Exception if the API call fails.
        """
        url = f"{self._base_api}/otp"
        params = {
            "text": text,
            "language": language,
            "pauseDigit": pause_digit,
            "pausePhrase": pause_phrase,
            "repeats": repeats
        }
        headers = self._get_auth_headers()

        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code != 200:
            raise requests.exceptions.HTTPError(f"VoiceSDK.otp failed: {response.status_code} - {response.text}")
        
        return response.content 