import re
from datetime import datetime
from typing import Optional, Dict, Any

from .types import ServicePreAuthRequest, TransactionHistoryRequest, ServiceUsageRequest

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def validate_phone_number(phone_number: str) -> bool:
    """Validate phone number format.
    
    Args:
        phone_number (str): Phone number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return bool(re.match(r'^\+?[1-9]\d{1,14}$', phone_number))

def validate_required_str(value: Optional[str], field_name: str) -> None:
    """Validate required string field.
    
    Args:
        value (Optional[str]): Value to validate
        field_name (str): Name of the field for error message
        
    Raises:
        ValidationError: If validation fails
    """
    if not value or not isinstance(value, str):
        raise ValidationError(f"{field_name} is required and must be a string")

def validate_pagination(page: Optional[int], rows_per_page: Optional[int]) -> None:
    """Validate pagination parameters.
    
    Args:
        page (Optional[int]): Page number
        rows_per_page (Optional[int]): Number of rows per page
        
    Raises:
        ValidationError: If validation fails
    """
    if page is not None:
        if not isinstance(page, int) or page < 1:
            raise ValidationError("Page must be a positive integer")
    
    if rows_per_page is not None:
        if not isinstance(rows_per_page, int) or rows_per_page < 1 or rows_per_page > 100:
            raise ValidationError("Rows per page must be between 1 and 100")

def validate_date_range(from_date: Optional[str], to_date: Optional[str]) -> None:
    """Validate date range.
    
    Args:
        from_date (Optional[str]): Start date
        to_date (Optional[str]): End date
        
    Raises:
        ValidationError: If validation fails
    """
    if from_date and to_date:
        try:
            from_dt = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
            to_dt = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
            
            if from_dt > to_dt:
                raise ValidationError("Start date must be before end date")
        except ValueError:
            raise ValidationError("Invalid date format. Use ISO format (e.g., 2024-03-25T09:00:00Z)")

def validate_preauth_request(request: ServicePreAuthRequest) -> None:
    """Validate service pre-authorization request.
    
    Args:
        request (ServicePreAuthRequest): Request to validate
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(request, dict):
        raise ValidationError("Request must be a dictionary")
        
    validate_required_str(request.get('userId'), 'User ID')
    validate_required_str(request.get('serviceId'), 'Service ID')
    validate_required_str(request.get('phoneNumber'), 'Phone number')
    
    if not validate_phone_number(request['phoneNumber']):
        raise ValidationError("Invalid phone number format")
        
    quantity = request.get('quantity')
    if not isinstance(quantity, (int, float)) or quantity <= 0:
        raise ValidationError("Quantity must be a positive number")

def validate_service_usage_request(request: ServiceUsageRequest) -> None:
    """Validate service usage request.
    
    Args:
        request (ServiceUsageRequest): Request to validate
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(request, dict):
        raise ValidationError("Request must be a dictionary")
        
    validate_required_str(request.get('correlationId'), 'Correlation ID')
    
    actual_quantity = request.get('actualQuantity')
    if not isinstance(actual_quantity, (int, float)) or actual_quantity <= 0:
        raise ValidationError("Actual quantity must be a positive number")
        
    core_services = request.get('coreServices')
    if not isinstance(core_services, list) or not core_services:
        raise ValidationError("At least one core service is required")
        
    for service in core_services:
        if not isinstance(service, dict):
            raise ValidationError("Invalid core service format")
        validate_required_str(service.get('serviceId'), 'Core service ID')
        quantity = service.get('quantity')
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            raise ValidationError("Core service quantity must be a positive number")

def validate_transaction_history_request(request: TransactionHistoryRequest) -> None:
    """Validate transaction history request.
    
    Args:
        request (TransactionHistoryRequest): Request to validate
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(request, dict):
        raise ValidationError("Request must be a dictionary")
        
    validate_pagination(request.get('page'), request.get('rowsPerPage'))
    
    filter_data = request.get('filter', {})
    if not isinstance(filter_data, dict):
        raise ValidationError("Filter must be a dictionary")
        
    if 'datetime' in filter_data:
        datetime_filter = filter_data['datetime']
        if not isinstance(datetime_filter, dict):
            raise ValidationError("Datetime filter must be a dictionary")
        validate_date_range(datetime_filter.get('from'), datetime_filter.get('to'))
        
    if 'serviceId' in filter_data:
        validate_required_str(filter_data['serviceId'], 'Service ID in filter')
        
    if 'currency' in filter_data:
        validate_required_str(filter_data['currency'], 'Currency in filter')
        
    if 'type' in filter_data:
        validate_required_str(filter_data['type'], 'Type in filter')

def handle_api_error(response: Dict[str, Any]) -> None:
    """Handle API error response.
    
    Args:
        response (Dict[str, Any]): API response to handle
        
    Raises:
        ValidationError: If response contains error
    """
    if isinstance(response, dict):
        error_message = 'API Error'
        
        if 'message' in response:
            error_message = str(response['message'])
        elif 'error' in response:
            error = response['error']
            error_message = str(error) if isinstance(error, str) else str(error)
            
        if 'code' in response:
            error_message = f"[{response['code']}] {error_message}"
            
        raise ValidationError(error_message) 