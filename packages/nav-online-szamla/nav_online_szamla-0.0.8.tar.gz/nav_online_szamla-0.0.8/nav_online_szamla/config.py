"""
Configuration and constants for NAV Online Számla API.

This module contains configuration settings, constants, and default values 
used throughout the NAV Online Számla API client.
"""

# API Base URL
ONLINE_SZAMLA_URL = "https://api.onlineszamla.nav.gov.hu/invoiceService/v3/"

# HTTP Headers
DEFAULT_HEADERS = {"Content-Type": "application/xml", "Accept": "application/xml"}

# Default timeout for HTTP requests (seconds)
DEFAULT_TIMEOUT = 30

# Maximum retry attempts for failed API calls
MAX_RETRY_ATTEMPTS = 3

# Exponential backoff configuration
RETRY_BACKOFF_MULTIPLIER = 1
RETRY_BACKOFF_MIN = 4
RETRY_BACKOFF_MAX = 10

# Date range limits
MAX_DATE_RANGE_DAYS = 35

# API Version
API_VERSION = "3.0"

# Request signature algorithm
SIGNATURE_ALGORITHM = "SHA3-512"
PASSWORD_HASH_ALGORITHM = "SHA-512"

# Character set for custom ID generation
CUSTOM_ID_CHARACTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
CUSTOM_ID_LENGTH = 30

# Error handling
NETWORK_ERROR_KEYWORDS = ["connection", "timeout", "network", "resolve"]
RETRYABLE_HTTP_STATUS_CODES = [500, 502, 503, 504]

# XML Namespaces (if needed for parsing)
XML_NAMESPACES = {
    "ns2": "http://schemas.nav.gov.hu/OSA/3.0/api",
    "base": "http://schemas.nav.gov.hu/OSA/3.0/base",
}

# Customer VAT status mappings
CUSTOMER_VAT_STATUS_MAPPING = {
    "DOMESTIC": "Belföldi ÁFA alany",
    "PRIVATE_PERSON": "Nem ÁFA alany (belföldi vagy külföldi) természetes személy",
    "OTHER": "Egyéb (belföldi nem ÁFA alany, nem természetes személy, külföldi Áfa alany és külföldi nem ÁFA alany, nem természetes személy)",
}

# Source type mappings
INVOICE_SOURCE_MAPPING = {
    "PAPER": "Papír",
    "ELECTRONIC": "Elektronikus",
    "EDI": "EDI",
    "UNKNOWN": "Ismeretlen",
}

# Operation type mappings
INVOICE_OPERATION_MAPPING = {
    "CREATE": "Létrehozás",
    "MODIFY": "Módosítás",
    "STORNO": "Stornó",
}

# Logging configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# Software identification for NAV API
# Must be exactly 18 characters: [0-9A-Z\-]{18}
SOFTWARE_ID = "NAVPYTHONCLIENT123"  # 18 characters, uppercase letters and numbers
SOFTWARE_NAME = "NAV Python Client"
SOFTWARE_VERSION = "1.0"
SOFTWARE_DEV_NAME = "Python NAV Client"
SOFTWARE_DEV_CONTACT = "support@example.com"
SOFTWARE_DEV_COUNTRY = "HU"
