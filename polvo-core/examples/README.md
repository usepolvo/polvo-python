# Polvo Core Examples

This directory contains example scripts demonstrating how to use Polvo Core.

## Basic Examples

- **basic_request.py**: Demonstrates how to make basic HTTP requests using Polvo Core
- **authentication.py**: Shows how to use different authentication methods
- **middleware.py**: Examples of using middleware components for logging, retry, and rate limiting
- **rest_resource.py**: Shows how to use the REST resource pattern for API interactions
- **error_handling.py**: Demonstrates error handling and recovery
- **soap_example.py**: Illustrates how to interact with SOAP web services

## Running the Examples

To run any example, simply execute it using Python:

```bash
python basic_request.py
```

## Requirements

All examples require the Polvo Core package to be installed. If you're working with the development version, you can install it in development mode:

```bash
pip install -e ../
```

## Example APIs Used

The examples use the following public APIs for demonstration purposes:

- [httpbin.org](https://httpbin.org/): A service that echoes HTTP requests
- [JSONPlaceholder](https://jsonplaceholder.typicode.com/): A fake REST API for testing
- [DNE Online Calculator](http://www.dneonline.com/calculator.asmx): A simple SOAP calculator service

These services are free to use and provide predictable responses, making them ideal for example code.

## Additional Notes

- The examples demonstrate both synchronous and asynchronous usage patterns
- Error handling examples show how to properly catch and handle different types of errors
- Middleware examples demonstrate how to compose middleware to add functionality to clients
