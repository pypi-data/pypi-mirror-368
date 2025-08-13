"""
Main NAV Online Számla API client.

This module provides the main client class for interacting with the NAV Online Számla API.
"""

import logging
from datetime import datetime
from typing import List, Optional

from xsdata.formats.dataclass.context import XmlContext
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.formats.dataclass.parsers import XmlParser

from .config import (
    ONLINE_SZAMLA_URL,
    MAX_DATE_RANGE_DAYS,
    SOFTWARE_ID,
    SOFTWARE_NAME,
    SOFTWARE_VERSION,
    SOFTWARE_DEV_NAME,
    SOFTWARE_DEV_CONTACT,
    SOFTWARE_DEV_COUNTRY,
)
from .models import (
    # Official API types from generated models
    InvoiceDirectionType,
    BasicHeaderType,
    # Additional types from generated models
    InvoiceDetailType,
    DateIntervalParamType,
    MandatoryQueryParamsType,
    InvoiceQueryParamsType,
    CryptoType,
    ManageInvoiceOperationType,
    # Query parameter types
    InvoiceNumberQueryType,
    # Request wrappers (root elements)
    QueryInvoiceDigestRequest,
    QueryInvoiceCheckRequest,
    QueryInvoiceDataRequest,
    QueryInvoiceChainDigestRequest,
    # Token exchange
    TokenExchangeRequest,
    TokenExchangeResponse,
    # Response wrappers 
    QueryInvoiceDataResponse,
    QueryInvoiceDigestResponse,
    QueryInvoiceCheckResponse,
    QueryInvoiceChainDigestResponse,
    # Invoice data types
    InvoiceData,
    # Common types
    UserHeaderType,
    SoftwareType,
    SoftwareOperationType,
)

# Import only essential custom classes
from .models_legacy import (
    NavCredentials,
)
from .exceptions import (
    NavApiException,
    NavValidationException,
    NavXmlParsingException,
    NavInvoiceNotFoundException,
)
from .utils import (
    generate_password_hash,
    generate_custom_id,
    calculate_request_signature,
    validate_tax_number,
    format_timestamp_for_nav,
)
from .http_client import NavHttpClient

logger = logging.getLogger(__name__)


class NavOnlineInvoiceClient:
    """
    Main client for interacting with the NAV Online Számla API.

    This client provides methods for querying invoice data, getting invoice details,
    and managing invoice operations through the NAV API.
    """

    def __init__(self, credentials: NavCredentials, base_url: str = ONLINE_SZAMLA_URL, timeout: int = 30):
        """
        Initialize the NAV API client.

        Args:
            credentials: NAV API credentials
            base_url: Base URL for the NAV API  
            timeout: Request timeout in seconds
        """
        self.validate_credentials(credentials)
        self.credentials = credentials
        self.base_url = base_url
        self.http_client = NavHttpClient(base_url, timeout)
        
        # Initialize xsdata XML context, serializer, and parser
        self.xml_context = XmlContext()
        self.xml_serializer = XmlSerializer(context=self.xml_context)
        self.xml_parser = XmlParser(context=self.xml_context)

    def validate_credentials(self, credentials: NavCredentials) -> None:
        """
        Validate NAV API credentials.

        Args:
            credentials: NAV API credentials

        Raises:
            NavValidationException: If credentials are invalid
        """
        if not all([credentials.login, credentials.password, credentials.signer_key]):
            raise NavValidationException(
                "Missing required credentials: login, password, or signer_key"
            )

        if not validate_tax_number(credentials.tax_number):
            raise NavValidationException(
                f"Invalid tax number format: {credentials.tax_number}"
            )

    def _create_basic_header(self) -> BasicHeaderType:
        """Create basic header for requests."""
        return BasicHeaderType(
            request_id=generate_custom_id(),
            timestamp=format_timestamp_for_nav(datetime.now()),
            request_version="3.0",
            header_version="1.0"
        )

    def _create_user_header(self, credentials: NavCredentials, header: BasicHeaderType) -> UserHeaderType:
        """Create user header with authentication data using the provided header."""
        password_hash = generate_password_hash(credentials.password)
        request_signature = calculate_request_signature(
            header.request_id, 
            header.timestamp, 
            credentials.signer_key
        )
        
        return UserHeaderType(
            login=credentials.login,
            password_hash=CryptoType(
                value=password_hash,
                crypto_type="SHA-512"
            ),
            tax_number=credentials.tax_number,
            request_signature=CryptoType(
                value=request_signature,
                crypto_type="SHA3-512"
            )
        )

    def _create_software_info(self, credentials: NavCredentials) -> SoftwareType:
        """Create software information."""
        return SoftwareType(
            software_id=SOFTWARE_ID,
            software_name=SOFTWARE_NAME,
            software_operation=SoftwareOperationType.LOCAL_SOFTWARE,
            software_main_version=SOFTWARE_VERSION,
            software_dev_name=SOFTWARE_DEV_NAME,
            software_dev_contact=SOFTWARE_DEV_CONTACT,
            software_dev_country_code=SOFTWARE_DEV_COUNTRY,
            software_dev_tax_number=credentials.tax_number
        )

    def _serialize_request_to_xml(self, request_obj) -> str:
        """Serialize a request object to XML using xsdata with proper namespace formatting."""
        config = SerializerConfig(
            indent="  ",  # Use indent instead of pretty_print
            xml_declaration=True,
            encoding="UTF-8"
        )
        
        serializer = XmlSerializer(context=self.xml_context, config=config)
        xml_output = serializer.render(request_obj)
        
        # Format with custom namespace prefixes to match NAV expected format
        return self._format_xml_with_custom_namespaces(xml_output)
    
    def _parse_response_from_xml(self, xml_response: str, response_class):
        """
        Generic function for parsing XML responses using xsdata.
        
        This function provides automatic parsing of NAV API responses to typed dataclasses:
        1. Takes raw XML response string
        2. Uses xsdata parser with the provided response class
        3. Returns fully typed response object
        4. Handles parsing errors appropriately
        
        Args:
            xml_response: Raw XML response string from NAV API
            response_class: The dataclass type to parse into (e.g., QueryInvoiceDataResponse)
            
        Returns:
            Parsed response object of the specified type
            
        Raises:
            NavXmlParsingException: If XML parsing fails
            NavApiException: If response contains API errors
        """
        try:
            # Parse XML to response object using xsdata
            response_obj = self.xml_parser.from_string(xml_response, response_class)
            
            # Check for API errors in the response
            if hasattr(response_obj, 'result') and response_obj.result:
                func_code = response_obj.result.func_code
                # Handle both enum and string values
                func_code_value = func_code.value if hasattr(func_code, 'value') else str(func_code)
                
                if func_code_value != 'OK':
                    error_code = getattr(response_obj.result, 'error_code', 'UNKNOWN_ERROR')
                    message = getattr(response_obj.result, 'message', 'No error message provided')
                    raise NavApiException(f"API Error: {error_code} - {message}")
            
            return response_obj
            
        except Exception as e:
            if isinstance(e, NavApiException):
                raise
            logger.error(f"Failed to parse XML response: {e}")
            raise NavXmlParsingException(f"Failed to parse response XML: {e}")
    
    def _format_xml_with_custom_namespaces(self, xml_string: str) -> str:
        """
        Convert xsdata generated XML to match NAV expected format:
        - ns0 -> default namespace
        - ns1 -> common prefix
        """
        # Replace namespace declarations and prefixes
        xml_string = xml_string.replace(
            'xmlns:ns0="http://schemas.nav.gov.hu/OSA/3.0/api"',
            'xmlns="http://schemas.nav.gov.hu/OSA/3.0/api" xmlns:common="http://schemas.nav.gov.hu/NTCA/1.0/common"'
        )
        
        # Remove redundant namespace declarations
        xml_string = xml_string.replace(
            ' xmlns:ns1="http://schemas.nav.gov.hu/NTCA/1.0/common"',
            ''
        )
        
        # Replace element prefixes
        xml_string = xml_string.replace('ns0:', '')  # Remove ns0 prefix (default namespace)
        xml_string = xml_string.replace('ns1:', 'common:')  # Replace ns1 with common
        
        return xml_string

    def create_query_invoice_digest_request(
        self, 
        credentials: NavCredentials, 
        page: int,
        invoice_direction: InvoiceDirectionType,
        invoice_query_params: InvoiceQueryParamsType
    ) -> QueryInvoiceDigestRequest:
        """Create a QueryInvoiceDigestRequest using generated models."""
        
        header = self._create_basic_header()
        user = self._create_user_header(credentials, header)
        software = self._create_software_info(credentials)
        
        return QueryInvoiceDigestRequest(
            header=header,
            user=user,
            software=software,
            page=page,
            invoice_direction=invoice_direction,
            invoice_query_params=invoice_query_params
        )

    def create_token_exchange_request(self) -> TokenExchangeRequest:
        """Create a TokenExchangeRequest using generated models."""
        
        header = self._create_basic_header()
        user = self._create_user_header(self.credentials, header)
        software = self._create_software_info(self.credentials)
        
        return TokenExchangeRequest(
            header=header,
            user=user,
            software=software
        )

    def create_query_invoice_data_request(
        self,
        credentials: NavCredentials,
        invoice_number: str,
        invoice_direction: InvoiceDirectionType,
        batch_index: Optional[int] = None,
        supplier_tax_number: Optional[str] = None
    ) -> QueryInvoiceDataRequest:
        """Create a QueryInvoiceDataRequest using generated models."""
        
        header = self._create_basic_header()
        user = self._create_user_header(credentials, header)
        software = self._create_software_info(credentials)
        
        invoice_number_query = InvoiceNumberQueryType(
            invoice_number=invoice_number,
            invoice_direction=invoice_direction,
            batch_index=batch_index,
            supplier_tax_number=supplier_tax_number
        )
        
        return QueryInvoiceDataRequest(
            header=header,
            user=user,
            software=software,
            invoice_number_query=invoice_number_query
        )

    def create_query_invoice_check_request(
        self,
        invoice_number: str,
        invoice_direction: InvoiceDirectionType,
        batch_index: Optional[int] = None,
        supplier_tax_number: Optional[str] = None
    ) -> QueryInvoiceCheckRequest:
        """Create a QueryInvoiceCheckRequest using generated models."""
        
        header = self._create_basic_header()
        user = self._create_user_header(self.credentials, header)
        software = self._create_software_info(self.credentials)
        
        invoice_number_query = InvoiceNumberQueryType(
            invoice_number=invoice_number,
            invoice_direction=invoice_direction,
            batch_index=batch_index,
            supplier_tax_number=supplier_tax_number
        )
        
        return QueryInvoiceCheckRequest(
            header=header,
            user=user,
            software=software,
            invoice_number_query=invoice_number_query
        )

    def create_query_invoice_chain_digest_request(
        self,
        page: int,
        invoice_number: str,
        invoice_direction: InvoiceDirectionType,
        tax_number: Optional[str] = None
    ) -> QueryInvoiceChainDigestRequest:
        """Create a QueryInvoiceChainDigestRequest using generated models."""
        
        header = self._create_basic_header()
        user = self._create_user_header(self.credentials, header)
        software = self._create_software_info(self.credentials)
        
        return QueryInvoiceChainDigestRequest(
            header=header,
            user=user,
            software=software,
            page=page,
            invoice_number=invoice_number,
            invoice_direction=invoice_direction,
            tax_number=tax_number
        )

    def query_invoice_digest(
        self,
        page: int,
        invoice_direction: InvoiceDirectionType,
        invoice_query_params: InvoiceQueryParamsType
    ) -> QueryInvoiceDigestResponse:
        """
        Query invoice digest using xsdata-generated dataclasses.
        This uses automatic XML serialization and parsing for type-safe API interactions.
        
        Args:
            page: Page number for pagination (1-based)
            invoice_direction: Invoice direction (OUTBOUND/INBOUND)
            invoice_query_params: Query parameters (date range, supplier info, etc.)
            
        Returns:
            QueryInvoiceDigestResponse: Fully parsed response with typed invoice digests
            
        Raises:
            NavValidationException: If parameters are invalid
            NavApiException: If API request fails
            NavXmlParsingException: If XML parsing fails
        """
        if page < 1:
            raise NavValidationException("Page number must be >= 1")

        if not invoice_query_params:
            raise NavValidationException("Invoice query parameters are required")

        try:
            # Create request using xsdata dataclasses
            request = self.create_query_invoice_digest_request(
                credentials=self.credentials,
                page=page,
                invoice_direction=invoice_direction,
                invoice_query_params=invoice_query_params
            )
            
            # Serialize request to XML
            xml_request = self._serialize_request_to_xml(request)
            
            # Make API call
            with self.http_client as client:
                response = client.post("queryInvoiceDigest", xml_request)
                xml_response = response.text
            
            # Parse response using generic parsing function
            parsed_response = self._parse_response_from_xml(xml_response, QueryInvoiceDigestResponse)
            
            logger.info(f"Successfully queried invoice digest for page {page}")
            return parsed_response

        except Exception as e:
            if isinstance(e, (NavValidationException, NavApiException, NavXmlParsingException)):
                raise
            logger.error(f"Unexpected error querying invoice digest: {e}")
            raise NavApiException(f"Failed to query invoice digest: {e}")
      
    def query_invoice_data(
        self,
        invoice_number: str,
        invoice_direction: InvoiceDirectionType,
        batch_index: Optional[int] = None,
        supplier_tax_number: Optional[str] = None
    ) -> QueryInvoiceDataResponse:
        """
        Query invoice data using xsdata-generated dataclasses.
        This uses automatic XML serialization and parsing for type-safe API interactions.
        
        Args:
            invoice_number: Invoice number to query
            invoice_direction: Invoice direction (OUTBOUND/INBOUND)
            batch_index: Optional batch index for batched invoices
            supplier_tax_number: Optional supplier tax number
            
        Returns:
            QueryInvoiceDataResponse: Fully parsed response with typed invoice data
            
        Raises:
            NavValidationException: If parameters are invalid
            NavInvoiceNotFoundException: If invoice not found
            NavApiException: If API request fails
            NavXmlParsingException: If XML parsing fails
        """
        if not invoice_number:
            raise NavValidationException("Invoice number is required")

        try:
            # Create request using xsdata dataclasses
            request = self.create_query_invoice_data_request(
                credentials=self.credentials,
                invoice_number=invoice_number,
                invoice_direction=invoice_direction,
                batch_index=batch_index,
                supplier_tax_number=supplier_tax_number
            )
            
            # Serialize request to XML
            xml_request = self._serialize_request_to_xml(request)
            
            # Make API call
            with self.http_client as client:
                response = client.post("queryInvoiceData", xml_request)
                xml_response = response.text
            
            # Parse response using generic parsing function
            parsed_response = self._parse_response_from_xml(xml_response, QueryInvoiceDataResponse)
            
            # Check if invoice was found
            if not parsed_response.invoice_data_result or not parsed_response.invoice_data_result.invoice_data:
                raise NavInvoiceNotFoundException(f"Invoice {invoice_number} not found")

            logger.info(f"Successfully queried invoice data for {invoice_number}")
            # Parse the Base64 encoded invoice data
            if parsed_response.invoice_data_result.invoice_data:
                try:
                    # The invoice_data field is already decoded from Base64 by xsdata, 
                    # but it's in bytes format containing XML
                    xml_bytes = parsed_response.invoice_data_result.invoice_data
                    
                    # Try UTF-8 first, then fall back to other encodings
                    try:
                        xml_content = xml_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            # Try latin-1 which can handle any byte sequence
                            xml_content = xml_bytes.decode('latin-1')
                        except UnicodeDecodeError:
                            # Last resort - decode with error replacement
                            xml_content = xml_bytes.decode('utf-8', errors='replace')
                    
                    # Parse the decoded XML into InvoiceData object
                    parsed_invoice_data = self._parse_response_from_xml(xml_content, InvoiceData)
                    # Replace the bytes with the parsed object
                    parsed_response.invoice_data_result.invoice_data = parsed_invoice_data
                    logger.info(f"Successfully parsed invoice data XML for {invoice_number}")
                    
                except Exception as e:
                    logger.warning(f"Failed to parse invoice data XML: {e}")
                    # Keep the original bytes data if parsing fails
            
            logger.info(f"Successfully queried invoice data for {invoice_number}")
            return parsed_response

        except Exception as e:
            if isinstance(e, (NavValidationException, NavInvoiceNotFoundException, NavApiException, NavXmlParsingException)):
                raise
            logger.error(f"Unexpected error querying invoice data: {e}")
            raise NavApiException(f"Failed to query invoice data: {e}")

    def query_invoice_check(
        self, request: QueryInvoiceCheckRequest
    ) -> QueryInvoiceCheckResponse:
        """
        Check if an invoice exists using xsdata-generated dataclasses.
        This uses automatic XML serialization and parsing for type-safe API interactions.

        Args:
            request: QueryInvoiceCheckRequest with proper API structure

        Returns:
            QueryInvoiceCheckResponse: Fully parsed response with typed check results

        Raises:
            NavValidationException: If request validation fails
            NavApiException: If API call fails
            NavXmlParsingException: If XML parsing fails
        """
        try:
            # Serialize request to XML
            xml_request = self._serialize_request_to_xml(request)
            
            # Make API call
            with self.http_client as client:
                response = client.post("queryInvoiceCheck", xml_request)
                xml_response = response.text

            # Parse response using generic parsing function
            parsed_response = self._parse_response_from_xml(xml_response, QueryInvoiceCheckResponse)
            
            logger.info(f"Successfully checked invoice: {request.invoice_number_query.invoice_number}")
            return parsed_response

        except Exception as e:
            if isinstance(e, (NavApiException, NavValidationException, NavXmlParsingException)):
                raise
            logger.error(f"Unexpected error in query_invoice_check: {e}")
            raise NavApiException(f"Failed to check invoice: {str(e)}")

    def query_invoice_chain_digest(
        self, request: QueryInvoiceChainDigestRequest
    ) -> QueryInvoiceChainDigestResponse:
        """
        Query invoice chain digests using xsdata-generated dataclasses.
        This uses automatic XML serialization and parsing for type-safe API interactions.

        Args:
            request: QueryInvoiceChainDigestRequest with proper API structure

        Returns:
            QueryInvoiceChainDigestResponse: Fully parsed response with typed chain digest data

        Raises:
            NavValidationException: If request validation fails
            NavApiException: If API call fails
            NavXmlParsingException: If XML parsing fails
        """
        try:
            # Serialize request to XML
            xml_request = self._serialize_request_to_xml(request)
            
            # Make API call
            with self.http_client as client:
                response = client.post("queryInvoiceChainDigest", xml_request)
                xml_response = response.text

            # Parse response using generic parsing function
            parsed_response = self._parse_response_from_xml(xml_response, QueryInvoiceChainDigestResponse)
            
            logger.info(f"Successfully queried invoice chain digest for: {request.invoice_number}")
            return parsed_response

        except Exception as e:
            if isinstance(e, (NavApiException, NavValidationException, NavXmlParsingException)):
                raise
            logger.error(f"Unexpected error in query_invoice_chain_digest: {e}")
            raise NavApiException(f"Failed to query invoice chain digest: {str(e)}")

    def get_token(self) -> TokenExchangeResponse:
        """
        Get exchange token from NAV API using xsdata-generated dataclasses.
        This uses automatic XML serialization and parsing for type-safe API interactions.

        Returns:
            TokenExchangeResponse: Complete response with token and validity information

        Raises:
            NavValidationException: If credentials are invalid
            NavApiException: If API call fails
            NavXmlParsingException: If XML parsing fails
        """
        try:
            # Create request using helper method
            request = self.create_token_exchange_request()
            
            # Serialize request to XML
            xml_request = self._serialize_request_to_xml(request)
            
            # Make API call
            with self.http_client as client:
                response = client.post("tokenExchange", xml_request)
                xml_response = response.text

            # Parse response using generic parsing function
            parsed_response = self._parse_response_from_xml(xml_response, TokenExchangeResponse)
            
            logger.info("Successfully obtained exchange token")
            return parsed_response

        except Exception as e:
            if isinstance(e, (NavApiException, NavValidationException, NavXmlParsingException)):
                raise
            logger.error(f"Unexpected error in get_token: {e}")
            raise NavApiException(f"Failed to get token: {str(e)}")

    def get_invoice_chain_digest(
        self,
        page: int,
        invoice_number: str,
        invoice_direction: InvoiceDirectionType = InvoiceDirectionType.OUTBOUND,
        tax_number: Optional[str] = None
    ) -> QueryInvoiceChainDigestResponse:
        """
        Convenience method to get invoice chain digest with automatic request creation.
        
        Args:
            page: Page number for pagination
            invoice_number: Invoice number to query
            invoice_direction: Direction of the invoice (default: OUTBOUND)
            tax_number: Optional tax number filter
        
        Returns:
            QueryInvoiceChainDigestResponse: Complete response with chain digest data
        """
        request = self.create_query_invoice_chain_digest_request(
            page=page,
            invoice_number=invoice_number,
            invoice_direction=invoice_direction,
            tax_number=tax_number
        )
        return self.query_invoice_chain_digest(request)

    def get_invoice_data(
        self,
        invoice_number: str,
        invoice_direction: InvoiceDirectionType = InvoiceDirectionType.OUTBOUND,
        batch_index: Optional[int] = None,
        supplier_tax_number: Optional[str] = None
    ) -> InvoiceData:
        """
        Get invoice data and return a fully parsed InvoiceData dataclass.
        
        This function provides a high-level interface that:
        1. Uses query_invoice_data to get the API response
        2. Extracts and decodes the base64 invoice data
        3. Returns a typed InvoiceData dataclass
        
        Args:
            invoice_number: Invoice number to query
            invoice_direction: Invoice direction (default: OUTBOUND)
            batch_index: Optional batch index for batched invoices
            supplier_tax_number: Optional supplier tax number
            
        Returns:
            InvoiceData: Fully parsed invoice data as a dataclass
            
        Raises:
            NavValidationException: If parameters are invalid
            NavInvoiceNotFoundException: If invoice not found
            NavApiException: If API request fails
            NavXmlParsingException: If XML parsing fails
        """
        try:
            # Use query_invoice_data to get the full API response
            response = self.query_invoice_data(
                invoice_number=invoice_number,
                invoice_direction=invoice_direction,
                batch_index=batch_index,
                supplier_tax_number=supplier_tax_number
            )
            
            # Extract the already-parsed invoice data from the response
            if not response.invoice_data_result or not response.invoice_data_result.invoice_data:
                raise NavInvoiceNotFoundException(f"No invoice data found for invoice {invoice_number}")
            
            # query_invoice_data already parsed the XML into an InvoiceData object
            invoice_data = response.invoice_data_result.invoice_data
            
            # Ensure it's an InvoiceData object (should be after query_invoice_data processing)
            if not isinstance(invoice_data, InvoiceData):
                raise NavXmlParsingException(f"Expected InvoiceData object, got {type(invoice_data)}")
            
            logger.info(f"Successfully extracted invoice data for {invoice_number}")
            return invoice_data

        except Exception as e:
            if isinstance(e, (NavApiException, NavValidationException, NavInvoiceNotFoundException, NavXmlParsingException)):
                raise
            logger.error(f"Unexpected error in get_invoice_data: {e}")
            raise NavApiException(f"Failed to get invoice data: {str(e)}")

    def get_exchange_token(self) -> str:
        """
        Convenience method to get just the encoded exchange token string.
        
        Returns:
            str: The encoded exchange token
        """
        response = self.get_token()
        return response.encoded_exchange_token.decode('utf-8')

    def check_invoice_exists(
        self,
        invoice_number: str,
        invoice_direction: InvoiceDirectionType = InvoiceDirectionType.OUTBOUND,
        batch_index: Optional[int] = None,
        supplier_tax_number: Optional[str] = None
    ) -> bool:
        """
        Check if an invoice exists with a simplified interface.
        
        This function provides a high-level interface that:
        1. Creates the request using the provided parameters
        2. Calls query_invoice_check to get the API response
        3. Returns a simple boolean result
        
        Args:
            invoice_number: Invoice number to check
            invoice_direction: Invoice direction (default: OUTBOUND)
            batch_index: Optional batch index for batched invoices
            supplier_tax_number: Optional supplier tax number
            
        Returns:
            bool: True if invoice exists, False otherwise
            
        Raises:
            NavValidationException: If parameters are invalid
            NavApiException: If API request fails
            NavXmlParsingException: If XML parsing fails
        """
        try:
            # Create request using xsdata dataclasses
            request = self.create_query_invoice_check_request(
                invoice_number=invoice_number,
                invoice_direction=invoice_direction,
                batch_index=batch_index,
                supplier_tax_number=supplier_tax_number
            )
            
            # Get full response
            response = self.query_invoice_check(request)
            
            # Extract boolean result
            return response.invoice_check_result or False

        except Exception as e:
            if isinstance(e, (NavApiException, NavValidationException, NavXmlParsingException)):
                raise
            logger.error(f"Unexpected error in check_invoice_exists: {e}")
            raise NavApiException(f"Failed to check if invoice exists: {str(e)}")

    def get_all_invoice_data_for_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        invoice_direction: InvoiceDirectionType = InvoiceDirectionType.OUTBOUND,
    ) -> List[tuple[InvoiceData, ManageInvoiceOperationType]]:
        """
        Get all invoice data for a given date range by first querying invoice digests
        and then fetching detailed data for each invoice.

        Args:
            start_date: Start date for the query range
            end_date: End date for the query range
            invoice_direction: Invoice direction to query (default: OUTBOUND)

        Returns:
            List[tuple[InvoiceData, ManageInvoiceOperationType]]: List of tuples containing 
            complete invoice data objects and their operation types

        Raises:
            NavValidationException: If parameters are invalid
            NavApiException: If API requests fail
        """
        if start_date >= end_date:
            raise NavValidationException("Start date must be before end date")

        # Validate date range is not too large
        date_diff = (end_date - start_date).days
        if date_diff > MAX_DATE_RANGE_DAYS:
            raise NavValidationException(
                f"Date range too large. Maximum allowed: {MAX_DATE_RANGE_DAYS} days"
            )

        all_invoice_data = []
        processed_count = 0

        try:
            logger.info(
                f"Starting comprehensive invoice data retrieval for date range: {start_date.date()} to {end_date.date()}"
            )

            # Step 1: Query invoice digests to get all invoices in the date range
            page = 1
            total_found = 0

            while True:
                logger.info(f"Querying invoice digests - page {page}")
                # Create invoice query params
                invoice_query_params = InvoiceQueryParamsType(
                    mandatory_query_params=MandatoryQueryParamsType(
                        invoice_issue_date=DateIntervalParamType(
                            date_from=start_date.strftime("%Y-%m-%d"),
                            date_to=end_date.strftime("%Y-%m-%d"),
                        )
                    )
                )

                # Query invoice digests
                digest_response = self.query_invoice_digest(
                    page=page,
                    invoice_direction=invoice_direction,
                    invoice_query_params=invoice_query_params
                )

                if not digest_response.invoice_digest_result or not digest_response.invoice_digest_result.invoice_digest:
                    logger.info(f"No more invoices found on page {page}")
                    break

                invoice_digests = digest_response.invoice_digest_result.invoice_digest
                total_found += len(invoice_digests)
                logger.info(
                    f"Found {len(invoice_digests)} invoices on page {page} (total so far: {total_found})"
                )

                # Step 2: Get detailed data for each invoice digest
                for digest in invoice_digests:
                    try:
                        logger.info(
                            f"Fetching details for invoice: {digest.invoice_number}"
                        )

                        # Create detailed data request
                        # For OUTBOUND invoices, don't include supplier_tax_number as it causes API error
                        # For INBOUND invoices, include supplier_tax_number if available
                        supplier_tax_for_request = None
                        if invoice_direction == InvoiceDirectionType.INBOUND:
                            supplier_tax_for_request = digest.supplier_tax_number

                        # Get detailed invoice data using the get_invoice_data method
                        # which returns the parsed InvoiceData object directly
                        invoice_data = self.get_invoice_data(
                            invoice_number=digest.invoice_number,
                            invoice_direction=invoice_direction,
                            batch_index=digest.batch_index,
                            supplier_tax_number=supplier_tax_for_request
                        )

                        if invoice_data:
                            # Combine invoice data with operation type from digest
                            all_invoice_data.append((invoice_data, digest.invoice_operation))
                            processed_count += 1

                            if processed_count % 10 == 0:
                                logger.info(
                                    f"Processed {processed_count} invoices so far..."
                                )
                        else:
                            logger.warning(
                                f"No detail data found for invoice: {digest.invoice_number}"
                            )

                    except NavInvoiceNotFoundException:
                        logger.warning(
                            f"Invoice details not found for: {digest.invoice_number}"
                        )
                        continue
                    except Exception as e:
                        logger.error(
                            f"Error processing invoice {digest.invoice_number}: {str(e)}"
                        )
                        # Continue with next invoice rather than failing completely
                        continue

                # Check if there are more pages
                if (
                    digest_response.invoice_digest_result.available_page is None
                    or page >= digest_response.invoice_digest_result.available_page
                ):
                    logger.info("All pages processed")
                    break

                page += 1

            logger.info(
                f"Completed invoice data retrieval. Total processed: {processed_count} invoices"
            )
            return all_invoice_data

        except (NavValidationException, NavApiException):
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error in get_all_invoice_data_for_date_range: {str(e)}"
            )
            raise NavApiException(
                f"Unexpected error during comprehensive data retrieval: {str(e)}"
            )

    def close(self):
        """Close the HTTP client."""
        self.http_client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
