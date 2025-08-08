class SDKBase:
    """
    Base class for interacting with the Betatel API.
    """
    def __init__(self, api_key: str, user_id: str, version: str = 'v1'):
        if not api_key:
            raise ValueError("SDKBase: API key is required.")
        if not user_id:
            raise ValueError("SDKBase: User ID is required.")
        
        self._api_key = api_key
        self._user_id = user_id        
        # Root base URL and version
        self._base_url = 'https://api.betatel.com'
        self._version = version

        # Two canonical API base patterns to mirror the Node SDK
        # Pattern A (used by SMS/Carrier/Voice/Call): /api/{version}/...
        self._base_api = f"{self._base_url}/api/{self._version}"
        # Pattern B (used by Billing/Network): /{version}/api/...
        self._base_ver_api = f"{self._base_url}/{self._version}/api"

    def _get_auth_headers(self) -> dict:
        """
        Gets the standard authentication headers for API requests.
        
        Returns:
            dict: Headers dictionary with x-api-key and x-user-id.
        """
        return {
            "x-api-key": self._api_key,
            "x-user-id": self._user_id
        }      