"""
SOAP client implementation.

This is a minimal SOAP client adapter providing basic SOAP protocol support.
"""

import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Union

from usepolvo_core.auth.base import Auth
from usepolvo_core.core.client import AsyncClient, Client
from usepolvo_core.core.response import Response
from usepolvo_core.middleware.base import Middleware


class SoapClient(Client):
    """SOAP client for making SOAP API requests."""

    def __init__(
        self,
        endpoint: str,
        wsdl_url: Optional[str] = None,
        namespace: str = "http://schemas.xmlsoap.org/soap/envelope/",
        auth: Optional[Auth] = None,
        middlewares: Optional[List[Middleware]] = None,
        timeout: Union[float, tuple] = 30.0,  # SOAP requests often need longer timeouts
        verify: bool = True,
        **kwargs,
    ):
        """
        Initialize a SOAP client.

        Args:
            endpoint: SOAP service endpoint URL
            wsdl_url: URL to the WSDL definition (optional)
            namespace: SOAP namespace URI
            auth: Authentication method
            middlewares: List of middleware to apply to requests
            timeout: Request timeout in seconds
            verify: Verify SSL certificates
            **kwargs: Additional keyword arguments to pass to the underlying transport
        """
        super().__init__(
            base_url=endpoint,
            auth=auth,
            middlewares=middlewares,
            timeout=timeout,
            verify=verify,
            **kwargs,
        )
        self.namespace = namespace
        self.wsdl_url = wsdl_url
        self._wsdl_cache = None

        # Register XML namespaces
        ET.register_namespace("soap", namespace)
        ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")
        ET.register_namespace("xsd", "http://www.w3.org/2001/XMLSchema")

    def _create_envelope(self, body_content: str) -> str:
        """
        Create a SOAP envelope around the provided body content.

        Args:
            body_content: XML content for the SOAP body

        Returns:
            Complete SOAP envelope as a string
        """
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="{self.namespace}">
    <soap:Header></soap:Header>
    <soap:Body>
        {body_content}
    </soap:Body>
</soap:Envelope>"""

    def call(
        self,
        operation: str,
        params: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
        soap_action: Optional[str] = None,
        **kwargs,
    ) -> Response:
        """
        Make a SOAP operation call.

        Args:
            operation: Name of the SOAP operation to call
            params: Parameters for the operation
            namespace: Namespace URI for the operation (if different from client namespace)
            soap_action: SOAPAction header value
            **kwargs: Additional keyword arguments to pass to the underlying transport

        Returns:
            Response object
        """
        # Create operation XML
        op_namespace = namespace or self.namespace
        params_xml = ""

        if params:
            for key, value in params.items():
                # Simple conversion of parameters to XML
                # For complex types, this would need enhancement
                params_xml += f"<{key}>{value}</{key}>"

        operation_xml = f"""<{operation} xmlns="{op_namespace}">
            {params_xml}
        </{operation}>"""

        # Create full SOAP envelope
        soap_envelope = self._create_envelope(operation_xml)

        # Set up headers
        headers = kwargs.pop("headers", {})
        headers["Content-Type"] = "text/xml; charset=utf-8"

        if soap_action:
            headers["SOAPAction"] = soap_action

        # Send the request
        response = self.post(
            "", data=soap_envelope, headers=headers, **kwargs  # We use base_url as the endpoint
        )

        return response

    def extract_result(self, response: Response, xpath: str = ".//") -> Dict[str, Any]:
        """
        Extract data from a SOAP response using XPath.

        Args:
            response: Response object from a SOAP call
            xpath: XPath expression to locate the result element

        Returns:
            Extracted data as a dictionary
        """
        # Parse the XML response
        root = ET.fromstring(response.content)
        result = {}

        # Find elements using XPath
        elements = root.findall(
            xpath,
            {
                "soap": self.namespace,
                "ns": self.namespace,  # Default namespace for service operations
            },
        )

        # Convert elements to dictionary
        for element in elements:
            # Remove namespace prefixes for cleaner keys
            tag = re.sub(r"\{.*?\}", "", element.tag)

            if len(element) > 0:
                # Element has children, recursively process them
                result[tag] = {re.sub(r"\{.*?\}", "", child.tag): child.text for child in element}
            else:
                # Leaf element
                result[tag] = element.text

        return result


class AsyncSoapClient(AsyncClient):
    """Asynchronous SOAP client for making SOAP API requests."""

    def __init__(
        self,
        endpoint: str,
        wsdl_url: Optional[str] = None,
        namespace: str = "http://schemas.xmlsoap.org/soap/envelope/",
        auth: Optional[Auth] = None,
        middlewares: Optional[List[Middleware]] = None,
        timeout: Union[float, tuple] = 30.0,
        verify: bool = True,
        **kwargs,
    ):
        """
        Initialize an asynchronous SOAP client.

        Args:
            endpoint: SOAP service endpoint URL
            wsdl_url: URL to the WSDL definition (optional)
            namespace: SOAP namespace URI
            auth: Authentication method
            middlewares: List of middleware to apply to requests
            timeout: Request timeout in seconds
            verify: Verify SSL certificates
            **kwargs: Additional keyword arguments to pass to the underlying transport
        """
        super().__init__(
            base_url=endpoint,
            auth=auth,
            middlewares=middlewares,
            timeout=timeout,
            verify=verify,
            **kwargs,
        )
        self.namespace = namespace
        self.wsdl_url = wsdl_url
        self._wsdl_cache = None

        # Register XML namespaces
        ET.register_namespace("soap", namespace)
        ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")
        ET.register_namespace("xsd", "http://www.w3.org/2001/XMLSchema")

    def _create_envelope(self, body_content: str) -> str:
        """
        Create a SOAP envelope around the provided body content.

        Args:
            body_content: XML content for the SOAP body

        Returns:
            Complete SOAP envelope as a string
        """
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="{self.namespace}">
    <soap:Header></soap:Header>
    <soap:Body>
        {body_content}
    </soap:Body>
</soap:Envelope>"""

    async def call(
        self,
        operation: str,
        params: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
        soap_action: Optional[str] = None,
        **kwargs,
    ) -> Response:
        """
        Make an asynchronous SOAP operation call.

        Args:
            operation: Name of the SOAP operation to call
            params: Parameters for the operation
            namespace: Namespace URI for the operation (if different from client namespace)
            soap_action: SOAPAction header value
            **kwargs: Additional keyword arguments to pass to the underlying transport

        Returns:
            Response object
        """
        # Create operation XML
        op_namespace = namespace or self.namespace
        params_xml = ""

        if params:
            for key, value in params.items():
                # Simple conversion of parameters to XML
                params_xml += f"<{key}>{value}</{key}>"

        operation_xml = f"""<{operation} xmlns="{op_namespace}">
            {params_xml}
        </{operation}>"""

        # Create full SOAP envelope
        soap_envelope = self._create_envelope(operation_xml)

        # Set up headers
        headers = kwargs.pop("headers", {})
        headers["Content-Type"] = "text/xml; charset=utf-8"

        if soap_action:
            headers["SOAPAction"] = soap_action

        # Send the request
        response = await self.post(
            "", data=soap_envelope, headers=headers, **kwargs  # We use base_url as the endpoint
        )

        return response

    def extract_result(self, response: Response, xpath: str = ".//") -> Dict[str, Any]:
        """
        Extract data from a SOAP response using XPath.

        Args:
            response: Response object from a SOAP call
            xpath: XPath expression to locate the result element

        Returns:
            Extracted data as a dictionary
        """
        # Parse the XML response
        root = ET.fromstring(response.content)
        result = {}

        # Find elements using XPath
        elements = root.findall(
            xpath,
            {
                "soap": self.namespace,
                "ns": self.namespace,  # Default namespace for service operations
            },
        )

        # Convert elements to dictionary
        for element in elements:
            # Remove namespace prefixes for cleaner keys
            tag = re.sub(r"\{.*?\}", "", element.tag)

            if len(element) > 0:
                # Element has children, recursively process them
                result[tag] = {re.sub(r"\{.*?\}", "", child.tag): child.text for child in element}
            else:
                # Leaf element
                result[tag] = element.text

        return result
