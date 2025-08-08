import requests
from .base import SDKBase

class CallSDK(SDKBase): 
    """
    CallSDK provides functionality for managing calls using the Betatel API.
    """
    def flash(self, callee, caller, max_ring_time=5):
        """
        Initiates a flash call between a caller and a callee.

        :param callee: The callee's phone number.
        :param caller: The caller's phone number.
        :param max_ring_time: The maximum ring time before timeout (default: 5 seconds).
        :return: True if the call was successful, False otherwise.
        :raises: Exception if the API call fails.
        """
        url = f"{self._base_api}/callgen/call/flash"
        payload = {
            "callType": "flash",
            "callee": callee,
            "caller": caller,
            "maxRingTime": max_ring_time
        }
        headers = self._get_auth_headers()

        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise requests.exceptions.HTTPError(f"CallSDK.flash failed: {response.status_code} - {response.text}")
        
        return response.status_code == 200