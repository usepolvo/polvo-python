#!/usr/bin/env python3
"""
Example demonstrating how to use the Google Drive client in both single-user
and multi-tenant scenarios.

Before running this example:
1. Set up environment variables:
   - POLVO_GOOGLE_CLIENT_ID=your_client_id
   - POLVO_GOOGLE_CLIENT_SECRET=your_client_secret
   - POLVO_GOOGLE_REDIRECT_URI=http://localhost:8080/callback

2. Install required packages:
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""

import os
import time
import webbrowser
from typing import Dict

from usepolvo.tentacles.google_drive import GoogleDriveClient

# ======== Single-User Example ========


def single_user_example():
    """Example of using Google Drive client in a single-user scenario."""
    print("\n===== SINGLE-USER EXAMPLE =====")

    # 1. Initialize the client
    client = GoogleDriveClient()

    # 2. Get authentication URL for a user (using a fixed user ID for simplicity)
    user_id = "single_user"
    auth_url = client.get_auth_url_for_user(user_id)

    # 3. Open the authorization URL in a browser
    print(f"Opening authorization URL for user '{user_id}'...")
    webbrowser.open(auth_url)

    # 4. Wait for the user to authorize and get the callback URL
    callback_url = input("After authorizing, paste the full callback URL here: ")

    # 5. Process the callback to complete authentication
    user_id = client.process_callback(callback_url)
    print(f"Successfully authenticated user: {user_id}")

    # 6. Set the active user context
    client.for_user(user_id)

    # 7. Use the client to perform operations
    perform_file_operations(client)


# ======== Multi-Tenant Example ========


def multi_tenant_example():
    """Example of using Google Drive client in a multi-tenant scenario."""
    print("\n===== MULTI-TENANT EXAMPLE =====")

    # 1. Initialize the client
    client = GoogleDriveClient()

    # 2. List authenticated users
    users = client.list_authenticated_users()
    print(f"Authenticated users: {users}")

    # 3. If no users are authenticated, authenticate a couple of test users
    if not users:
        users = authenticate_example_users(client)

    # 4. Demonstrate switching between users
    for user_id in users:
        print(f"\nSwitching to user '{user_id}'...")

        # Set the active user context
        client.for_user(user_id)

        # Perform operations for this user
        print_user_files(client)

        # Demonstrate context manager approach
        print("\nUsing context manager approach:")
        with client.user_context(user_id):
            print_user_files(client)

    # 5. Demonstrate creating, updating, and deleting a file for a specific user
    if users:
        print(f"\nPerforming file operations for user '{users[0]}'...")
        client.for_user(users[0])
        perform_file_operations(client)


def authenticate_example_users(client):
    """Helper to authenticate example users for multi-tenant example."""
    users = []

    # Authenticate two example users
    for i in range(1, 3):
        user_id = f"example_user_{i}"

        # Get authentication URL
        auth_url = client.get_auth_url_for_user(user_id)

        # Open the authorization URL in a browser
        print(f"\nOpening authorization URL for user '{user_id}'...")
        webbrowser.open(auth_url)

        # Wait for the user to authorize and get the callback URL
        callback_url = input("After authorizing, paste the full callback URL here: ")

        # Process the callback to complete authentication
        user_id = client.process_callback(callback_url)
        print(f"Successfully authenticated user: {user_id}")
        users.append(user_id)

    return users


# ======== Common Operations ========


def print_user_files(client):
    """Print the first 5 files for the current user."""
    try:
        files = client.files.list(max_results=5)
        file_items = files.get("files", [])

        if not file_items:
            print("No files found.")
        else:
            print("Files:")
            for item in file_items:
                print(f"  - {item['name']} ({item['id']})")
    except Exception as e:
        print(f"Error listing files: {e}")


def perform_file_operations(client):
    """Demonstrate various file operations."""
    try:
        # 1. Create a test file
        print("\nCreating a test file...")
        test_content = b"Hello, this is a test file created by the Polvo Google Drive client!"
        file = client.files.create(
            name="polvo_test_file.txt", content=test_content, mime_type="text/plain"
        )
        file_id = file["id"]
        print(f"Created file with ID: {file_id}")

        # 2. Get the file metadata
        print("\nGetting file metadata...")
        metadata = client.files.get(file_id)
        print(f"File name: {metadata['name']}")
        print(f"File type: {metadata['mimeType']}")
        print(f"Created: {metadata.get('createdTime')}")

        # 3. Update the file
        print("\nUpdating file content and name...")
        updated_content = b"This is the updated content of the test file."
        updated_file = client.files.update(
            file_id=file_id,
            content=updated_content,
            metadata={"name": "polvo_updated_test_file.txt"},
        )
        print(f"Updated file name: {updated_file['name']}")

        # 4. Download the file
        print("\nDownloading file content...")
        content = client.files.download(file_id)
        print(f"File content: {content.decode('utf-8')}")

        # 5. List files to see our test file
        print("\nListing files (should include our test file)...")
        files = client.files.list(query=f"name contains 'polvo'", max_results=10)
        for item in files.get("files", []):
            print(f"  - {item['name']} ({item['id']})")

        # 6. Delete the test file
        print("\nDeleting test file...")
        client.files.delete(file_id)
        print("File deleted successfully.")

        # 7. Verify the file is gone
        print("\nListing files again (test file should be gone)...")
        files = client.files.list(query=f"name contains 'polvo'", max_results=10)
        if not files.get("files"):
            print("No files found matching 'polvo' - deletion confirmed.")
        else:
            for item in files.get("files", []):
                print(f"  - {item['name']} ({item['id']})")

    except Exception as e:
        print(f"Error during file operations: {e}")


# ======== Main Entry Point ========

if __name__ == "__main__":
    # Choose which example to run
    print("Google Drive Client Examples")
    print("1. Single-user example")
    print("2. Multi-tenant example")
    choice = input("Choose an example to run (1 or 2): ")

    if choice == "1":
        single_user_example()
    elif choice == "2":
        multi_tenant_example()
    else:
        print("Invalid choice. Please run again and select 1 or 2.")
