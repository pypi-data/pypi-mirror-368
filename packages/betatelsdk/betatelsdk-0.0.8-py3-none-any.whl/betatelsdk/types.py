from typing import TypedDict, List, Dict, Optional, Any, Union, TypeVar, Generic
from datetime import datetime

class NetworkStatus(TypedDict):
    status: str
    version: str
    uptime: str

class NetworkMCCMNC(TypedDict):
    mccmnc: int
    mcc: str
    mnc: str
    operator: str
    country: str

class BillingStatus(TypedDict):
    status: str
    version: str
    uptime: str

class UserBalance(TypedDict):
    userId: str
    balance: float
    currency: str
    lastUpdated: str

class ServicePreAuthRequest(TypedDict):
    userId: str
    serviceId: str
    phoneNumber: str
    quantity: int

class ServicePreAuthResponse(TypedDict):
    correlationId: str
    userId: str
    serviceId: str
    status: str
    estimatedCost: float
    currency: str
    timestamp: str

class CoreService(TypedDict):
    serviceId: str
    quantity: int

class ServiceUsageRequest(TypedDict):
    correlationId: str
    actualQuantity: int
    coreServices: List[CoreService]
    metadata: Dict[str, Any]

class ServiceUsageResponse(TypedDict):
    transactionId: str
    correlationId: str
    userId: str
    serviceId: str
    type: str
    description: str
    datetime: str
    unitPrice: float
    quantity: int
    value: float
    currency: str
    balanceAfter: float

class DateTimeRange(TypedDict):
    from_: str  # Using from_ to avoid Python keyword
    to: str

class TransactionHistoryFilter(TypedDict, total=False):
    serviceId: Optional[str]
    datetime: Optional[DateTimeRange]
    type: Optional[str]
    currency: Optional[str]

class TransactionHistoryRequest(TypedDict):
    filter: TransactionHistoryFilter
    rowsPerPage: Optional[int]
    page: Optional[int]

class TransactionEvent(TypedDict):
    eventId: str
    type: str
    timestamp: str

class Transaction(TypedDict):
    transactionId: str
    correlationId: str
    userId: str
    serviceId: str
    type: str
    description: str
    datetime: str
    unitPrice: float
    quantity: int
    value: float
    currency: str
    balanceAfter: float
    metadata: Optional[Dict[str, Any]]
    events: Optional[List[TransactionEvent]]

class BillingPricing(TypedDict):
    id: str
    serviceId: str
    mcc: str
    mnc: str
    countryCode: str
    country: str
    description: str
    network: str
    unitPrice: float
    currency: str
    validFrom: str

class BillingEvent(TypedDict):
    eventId: str
    eventType: str
    timestamp: str
    payload: Dict[str, Any]

class BillingEventResponse(TypedDict):
    correlationId: str
    events: List[BillingEvent]

T = TypeVar('T')

class PaginatedResponse(TypedDict, Generic[T]):
    filter: Dict[str, Any]
    page: int
    rowsPerPage: int
    list: List[T]
    total: int
    totalPages: int
    hasPreviousPage: bool
    hasNextPage: bool

class SMSSendRequest(TypedDict):
    """Request payload for sending an SMS message"""
    from_: str  # The sender's phone number
    to: str     # The recipient's phone number
    text: str   # The SMS message content

class SMSSendResponse(TypedDict):
    """Response from SMS send operation"""
    messageId: str  # Unique identifier for the sent message
    from_: str      # The sender's phone number
    to: str         # The recipient's phone number

class SMSStatusResponse(TypedDict):
    """Response from SMS status check"""
    messageId: str  # Unique identifier for the message
    status: str     # Current status of the message (e.g., "Delivered")
    userId: str     # ID of the user who sent the message

class SMSDetailsResponse(TypedDict):
    """Response with complete SMS message details"""
    messageId: str  # Unique identifier for the message
    status: str     # Current status of the message
    from_: str      # The sender's phone number
    to: str         # The recipient's phone number
    text: str       # The SMS message content
    timestamp: str  # ISO timestamp when the message was sent
    userId: str     # ID of the user who sent the message
    segments: int   # Number of SMS segments used 