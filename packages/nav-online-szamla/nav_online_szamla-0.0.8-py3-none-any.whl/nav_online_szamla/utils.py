"""
Utility functions for NAV Online Számla API.

This module contains utility functions for hashing, date manipulation, 
XML processing, and other common tasks.
"""

import hashlib
import random
from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Optional
import xml.dom.minidom

from .config import (
    CUSTOM_ID_CHARACTERS,
    CUSTOM_ID_LENGTH,
    MAX_DATE_RANGE_DAYS,
    NETWORK_ERROR_KEYWORDS,
)
from .exceptions import NavValidationException, NavXmlParsingException


def generate_password_hash(password: str) -> str:
    """
    Generate SHA-512 hash of password in uppercase hexadecimal format.

    Args:
        password: The password to hash

    Returns:
        str: SHA-512 hash in uppercase hexadecimal format
    """
    hash_object = hashlib.sha512(password.encode("utf-8"))
    return hash_object.hexdigest().upper()


def generate_custom_id(length: int = CUSTOM_ID_LENGTH) -> str:
    """
    Generate a random custom ID string.

    Args:
        length: Length of the generated ID

    Returns:
        str: Random ID string
    """
    return "".join(random.choice(CUSTOM_ID_CHARACTERS) for _ in range(length))


def calculate_request_signature(
    request_id: str, timestamp: str, signer_key: str
) -> str:
    """
    Calculate request signature for NAV API calls.

    Args:
        request_id: Unique request ID
        timestamp: Timestamp in ISO format
        signer_key: Signer key for authentication

    Returns:
        str: SHA3-512 hash signature in uppercase
    """
    # Convert timestamp to YYYYMMDDHHMMSS format
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    timestamp_str = dt.strftime("%Y%m%d%H%M%S")

    # Create partial authentication string
    partial_auth = f"{request_id}{timestamp_str}{signer_key}"

    # Generate SHA3-512 hash
    hash_object = hashlib.sha3_512(partial_auth.encode("utf-8"))
    return hash_object.hexdigest().upper()


def validate_tax_number(tax_number: str) -> bool:
    """
    Validate Hungarian tax number format (8 digits).

    Args:
        tax_number: Tax number to validate

    Returns:
        bool: True if valid, False otherwise
    """
    return tax_number.isdigit() and len(tax_number) == 8


def split_date_range(
    start_date: str, end_date: str, max_days: int = MAX_DATE_RANGE_DAYS
) -> List[Tuple[str, str]]:
    """
    Split a date range into chunks of maximum days.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        max_days: Maximum days per chunk

    Returns:
        List[Tuple[str, str]]: List of date range tuples
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    date_ranges = []
    current_start = start

    while current_start <= end:
        current_end = min(current_start + timedelta(days=max_days - 1), end)
        date_ranges.append(
            (current_start.strftime("%Y-%m-%d"), current_end.strftime("%Y-%m-%d"))
        )
        current_start = current_end + timedelta(days=1)

    return date_ranges


def get_xml_element_value(
    xml_doc: xml.dom.minidom.Document, tag_name: str, default_value: str = ""
) -> str:
    """
    Get text content of an XML element.
    Handles namespace inconsistencies by trying multiple namespace prefixes.

    Args:
        xml_doc: XML document or element
        tag_name: Tag name to search for
        default_value: Default value if element not found

    Returns:
        str: Element text content or default value
    """
    try:
        # First try the exact tag name (no namespace)
        elements = xml_doc.getElementsByTagName(tag_name)
        if elements and elements[0].firstChild:
            return elements[0].firstChild.data.strip()

        # If not found, try with common namespace prefixes in order of likelihood
        # Based on the NAV API response patterns
        for prefix in ["ns2:", "ns3:", "ns4:", "common:", "base:"]:
            namespaced_tag = f"{prefix}{tag_name}"
            elements = xml_doc.getElementsByTagName(namespaced_tag)
            if elements and elements[0].firstChild:
                return elements[0].firstChild.data.strip()

        return default_value
    except Exception:
        return default_value


def find_xml_elements_with_namespace_aware(
    xml_doc: xml.dom.minidom.Document, tag_name: str
) -> list:
    """
    Find XML elements by tag name, trying multiple namespace prefixes.

    Args:
        xml_doc: XML document or element
        tag_name: Tag name to search for

    Returns:
        list: List of found elements
    """
    # First try the exact tag name (no namespace)
    elements = xml_doc.getElementsByTagName(tag_name)
    if elements:
        return elements

    # If not found, try with common namespace prefixes
    for prefix in ["ns2:", "ns3:", "ns4:", "common:", "base:"]:
        namespaced_tag = f"{prefix}{tag_name}"
        elements = xml_doc.getElementsByTagName(namespaced_tag)
        if elements:
            return elements

    return []


def format_timestamp_for_nav(dt: Optional[datetime] = None) -> str:
    """
    Format datetime for NAV API requests.

    Args:
        dt: Datetime to format, uses current UTC time if None

    Returns:
        str: Formatted timestamp string with max 3 decimal places
    """
    if dt is None:
        dt = datetime.now(timezone.utc)

    # Format with microseconds and then truncate to 3 decimal places
    timestamp_str = dt.strftime("%Y-%m-%dT%H:%M:%S.%f")
    # Keep only first 3 decimal places (microseconds -> milliseconds)
    timestamp_str = timestamp_str[:-3] + "Z"
    return timestamp_str
