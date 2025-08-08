import requests
from typing import Dict

from .base import SDKBase
from .validators import (
    ValidationError,
    validate_required_str,
    validate_preauth_request,
    validate_service_usage_request,
    validate_transaction_history_request,
    handle_api_error
)
from .types import (
    BillingStatus,
    UserBalance,
    ServicePreAuthRequest,
    ServicePreAuthResponse,
    ServiceUsageRequest,
    ServiceUsageResponse,
    TransactionHistoryRequest,
    Transaction,
    PaginatedResponse,
    BillingPricing,
    BillingEventResponse,
)

class BillingSDK(SDKBase):
    """BillingSDK provides methods for interacting with the Betatel Index API."""

    def get_status(self) -> BillingStatus:
        """Get the operational status of the billing service.

        Returns:
            BillingStatus: The billing service status.

        Raises:
            ValidationError: If the API response is invalid
            requests.exceptions.RequestException: If the API call fails
        """
        response = requests.get(
            f"{self._base_ver_api}/billing/status",
            headers=self._get_auth_headers()
        )
        
        data = response.json()
        if response.status_code >= 400:
            handle_api_error(data)
        return data

    def get_user_balance(self, user_id: str) -> UserBalance:
        """Get the current balance for a specific user.

        Args:
            user_id (str): The unique identifier for the user.

        Returns:
            UserBalance: The user's balance information.

        Raises:
            ValidationError: If the user ID is invalid or the API response is invalid
            requests.exceptions.RequestException: If the API call fails
        """
        validate_required_str(user_id, 'User ID')

        response = requests.get(
            f"{self._base_ver_api}/billing/users/{user_id}/balance",
            headers=self._get_auth_headers()
        )
        
        data = response.json()
        if response.status_code >= 400:
            handle_api_error(data)
        return data

    def preauthorize_service(self, request: ServicePreAuthRequest) -> ServicePreAuthResponse:
        """Verify if a user has sufficient funds for a service and create a billing event.

        Args:
            request (ServicePreAuthRequest): The pre-authorization request.

        Returns:
            ServicePreAuthResponse: The pre-authorization response.

        Raises:
            ValidationError: If the request is invalid or the API response is invalid
            requests.exceptions.RequestException: If the API call fails
        """
        validate_preauth_request(request)

        response = requests.post(
            f"{self._base_ver_api}/billing/services/preauth",
            headers=self._get_auth_headers(),
            json=request
        )
        
        data = response.json()
        if response.status_code >= 400:
            handle_api_error(data)
        return data

    def record_service_usage(self, request: ServiceUsageRequest) -> ServiceUsageResponse:
        """Record actual service usage and finalize billing.

        Args:
            request (ServiceUsageRequest): The service usage request.

        Returns:
            ServiceUsageResponse: The service usage response.

        Raises:
            ValidationError: If the request is invalid or the API response is invalid
            requests.exceptions.RequestException: If the API call fails
        """
        validate_service_usage_request(request)

        response = requests.post(
            f"{self._base_ver_api}/billing/usage",
            headers=self._get_auth_headers(),
            json=request
        )
        
        data = response.json()
        if response.status_code >= 400:
            handle_api_error(data)
        return data

    def get_user_transaction_history(
        self, user_id: str, request: TransactionHistoryRequest
    ) -> PaginatedResponse[Transaction]:
        """Get transaction history for a specific user.

        Args:
            user_id (str): The unique identifier for the user.
            request (TransactionHistoryRequest): The transaction history request parameters.

        Returns:
            PaginatedResponse[Transaction]: The paginated transaction history.

        Raises:
            ValidationError: If the user ID or request is invalid or the API response is invalid
            requests.exceptions.RequestException: If the API call fails
        """
        validate_required_str(user_id, 'User ID')
        validate_transaction_history_request(request)

        response = requests.post(
            f"{self._base_ver_api}/billing/users/{user_id}/history",
            headers=self._get_auth_headers(),
            json=request
        )
        
        data = response.json()
        if response.status_code >= 400:
            handle_api_error(data)
        return data

    def search_transactions(self, request: TransactionHistoryRequest) -> PaginatedResponse[Transaction]:
        """Search for transactions across all users.

        Args:
            request (TransactionHistoryRequest): The transaction search request parameters.

        Returns:
            PaginatedResponse[Transaction]: The paginated transaction search results.

        Raises:
            ValidationError: If the request is invalid or the API response is invalid
            requests.exceptions.RequestException: If the API call fails
        """
        validate_transaction_history_request(request)

        response = requests.post(
            f"{self._base_ver_api}/billing/transactions/search",
            headers=self._get_auth_headers(),
            json=request
        )
        
        data = response.json()
        if response.status_code >= 400:
            handle_api_error(data)
        return data

    def get_transaction_details(self, transaction_id: str) -> Transaction:
        """Get detailed information about a specific transaction.

        Args:
            transaction_id (str): The unique identifier for the transaction.

        Returns:
            Transaction: The transaction details.

        Raises:
            ValidationError: If the transaction ID is invalid or the API response is invalid
            requests.exceptions.RequestException: If the API call fails
        """
        validate_required_str(transaction_id, 'Transaction ID')

        response = requests.get(
            f"{self._base_ver_api}/billing/transactions/{transaction_id}",
            headers=self._get_auth_headers()
        )
        
        data = response.json()
        if response.status_code >= 400:
            handle_api_error(data)
        return data

    def search_pricing(self, request: TransactionHistoryRequest) -> PaginatedResponse[BillingPricing]:
        """Search for pricing information.

        Args:
            request (TransactionHistoryRequest): The pricing search request parameters.

        Returns:
            PaginatedResponse[BillingPricing]: The paginated pricing search results.

        Raises:
            ValidationError: If the request is invalid or the API response is invalid
            requests.exceptions.RequestException: If the API call fails
        """
        validate_transaction_history_request(request)

        response = requests.post(
            f"{self._base_ver_api}/billing/pricing/search",
            headers=self._get_auth_headers(),
            json=request
        )
        
        data = response.json()
        if response.status_code >= 400:
            handle_api_error(data)
        return data

    def get_service_pricing(
        self, service_id: str, request: TransactionHistoryRequest
    ) -> PaginatedResponse[BillingPricing]:
        """Get pricing information for a specific service.

        Args:
            service_id (str): The unique identifier for the service.
            request (TransactionHistoryRequest): The service pricing request parameters.

        Returns:
            PaginatedResponse[BillingPricing]: The paginated service pricing results.

        Raises:
            ValidationError: If the service ID or request is invalid or the API response is invalid
            requests.exceptions.RequestException: If the API call fails
        """
        validate_required_str(service_id, 'Service ID')
        validate_transaction_history_request(request)

        response = requests.post(
            f"{self._base_ver_api}/billing/service/{service_id}/pricing",
            headers=self._get_auth_headers(),
            json=request
        )
        
        data = response.json()
        if response.status_code >= 400:
            handle_api_error(data)
        return data

    def get_service_price(self, service_id: str, callee: str) -> BillingPricing:
        """Get the current unit price for a specific service.

        Args:
            service_id (str): The unique identifier for the service.
            callee (str): Destination phone number to get region-specific pricing.

        Returns:
            BillingPricing: The service pricing information.

        Raises:
            requests.exceptions.RequestException: If the API call fails.
        """
        response = requests.get(
            f"{self._base_ver_api}/billing/services/{service_id}/price",
            params={"callee": callee},
            headers=self._get_auth_headers()
        )
        response.raise_for_status()
        return response.json()

    def get_billing_events(self, correlation_id: str) -> BillingEventResponse:
        """Get all events associated with a specific correlation ID.

        Args:
            correlation_id (str): The correlation ID for the service request.

        Returns:
            BillingEventResponse: The billing events.

        Raises:
            requests.exceptions.RequestException: If the API call fails.
        """
        response = requests.get(
            f"{self._base_ver_api}/billing/events/{correlation_id}",
            headers=self._get_auth_headers()
        )
        response.raise_for_status()
        return response.json() 