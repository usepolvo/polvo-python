"""
SOAP client example using Polvo Core.

This example demonstrates how to use the SOAP client to interact with SOAP web services.
"""

import asyncio
import xml.etree.ElementTree as ET
from pprint import pprint

import usepolvo_core as pv


def basic_soap_request():
    """Example of a basic SOAP request to a public SOAP service."""

    # Create a SOAP client targeting a public calculator web service
    client = pv.SoapClient(
        endpoint="http://www.dneonline.com/calculator.asmx",
        namespace="http://tempuri.org/",  # This is the namespace used by this particular service
    )

    # Make a SOAP call to add two numbers
    response = client.call(
        operation="Add",
        params={"intA": 5, "intB": 3},
        soap_action="http://tempuri.org/Add",  # SOAPAction header for this operation
    )

    print(f"SOAP Response Status: {response.status_code}")

    # Parse the response manually
    print("\nRaw Response Content:")
    print(response.text())

    # Extract results using the helper method
    result = client.extract_result(response, ".//AddResult")
    print("\nExtracted Result:")
    pprint(result)

    # Manual extraction
    root = ET.fromstring(response.content)
    # Find the result element (specific to this service)
    result_elem = root.find(".//{http://tempuri.org/}AddResult")
    if result_elem is not None:
        print(f"\nAdd Result: {result_elem.text}")


def soap_with_complex_params():
    """Example of a SOAP request with more complex parameters."""

    # Create a SOAP client
    client = pv.SoapClient(
        endpoint="http://www.dneonline.com/calculator.asmx", namespace="http://tempuri.org/"
    )

    # Make multiple SOAP calls
    operations = [
        {"operation": "Add", "params": {"intA": 10, "intB": 20}},
        {"operation": "Subtract", "params": {"intA": 30, "intB": 15}},
        {"operation": "Multiply", "params": {"intA": 5, "intB": 7}},
        {"operation": "Divide", "params": {"intA": 100, "intB": 4}},
    ]

    for op in operations:
        response = client.call(
            operation=op["operation"],
            params=op["params"],
            soap_action=f"http://tempuri.org/{op['operation']}",
        )

        # Find the result element based on the operation
        root = ET.fromstring(response.content)
        result_elem = root.find(f".//{{{client.namespace}}}{op['operation']}Result")
        if result_elem is not None:
            print(f"{op['operation']} Result: {result_elem.text}")


async def async_soap_example():
    """Example of using the async SOAP client."""

    # Create an async SOAP client
    client = pv.AsyncSoapClient(
        endpoint="http://www.dneonline.com/calculator.asmx", namespace="http://tempuri.org/"
    )

    # Prepare operations to call concurrently
    operations = [
        {
            "operation": "Add",
            "params": {"intA": 10, "intB": 20},
            "soap_action": "http://tempuri.org/Add",
        },
        {
            "operation": "Multiply",
            "params": {"intA": 5, "intB": 7},
            "soap_action": "http://tempuri.org/Multiply",
        },
    ]

    # Create tasks for concurrent execution
    tasks = [
        client.call(operation=op["operation"], params=op["params"], soap_action=op["soap_action"])
        for op in operations
    ]

    # Wait for all responses
    responses = await asyncio.gather(*tasks)

    # Process each response
    for i, response in enumerate(responses):
        op_name = operations[i]["operation"]

        # Parse the response
        root = ET.fromstring(response.content)
        result_elem = root.find(f".//{{{client.namespace}}}{op_name}Result")

        if result_elem is not None:
            print(f"Async {op_name} Result: {result_elem.text}")


if __name__ == "__main__":
    print("Basic SOAP Request Example:")
    basic_soap_request()

    print("\nSOAP with Complex Parameters:")
    soap_with_complex_params()

    print("\nAsync SOAP Example:")
    asyncio.run(async_soap_example())
