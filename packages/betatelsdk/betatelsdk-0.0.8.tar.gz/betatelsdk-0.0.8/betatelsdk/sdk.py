from .base import SDKBase
from .voice import VoiceSDK
from .call import CallSDK
from .carrier import CarrierSDK
from .network import NetworkSDK
from .billing import BillingSDK
from .sms import SMSDK

class BetatelSDK(SDKBase):
    """
    BetatelSDK integrates voice and call services using the Betatel API.
    """
    def __init__(self, api_key: str, user_id: str, version: str = "v1"):
        """
        Initializes the BetatelSDK.

        :param api_key: The API key for authenticating with the Betatel API.
        :param user_id: The user ID for request attribution.
        :param version: The API version to use (default: 'v1').
        """
        super().__init__(api_key=api_key, user_id=user_id, version=version)
        self.voice = VoiceSDK(api_key=api_key, user_id=user_id, version=version)
        self.call = CallSDK(api_key=api_key, user_id=user_id, version=version)
        self.carrier = CarrierSDK(api_key=api_key, user_id=user_id, version=version)
        self.network = NetworkSDK(api_key=api_key, user_id=user_id, version=version)
        self.billing = BillingSDK(api_key=api_key, user_id=user_id, version=version)
        self.sms = SMSDK(api_key=api_key, user_id=user_id, version=version)
        