# Google Drive Tentacle

The Google Drive tentacle provides a simple interface to interact with Google Drive using the official Google Drive API client. It leverages Polvo's core OAuth2 authentication system and supports both single-user and multi-tenant scenarios.

## Features

- Authentication via Polvo's OAuth2 implementation
- Multi-tenant support for managing access for multiple users
- File operations:
  - List files with customizable queries
  - Get file metadata
  - Download file content
  - Create new files
  - Update file content and metadata
  - Delete files

## Architecture

This tentacle follows the standard Polvo architecture:

1. **OAuth2 Authentication**: Uses Polvo's core `OAuth2Auth` implementation for authentication
2. **Google Drive API**: Connects to Google Drive using Google's official Python client
3. **Resource-Specific Classes**: Separates operations into logical classes (e.g., Files)
4. **Multi-Tenant Support**: Manages credentials for multiple users

## Setup

### Prerequisites

1. Install required dependencies:

   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

2. Set up your Google Cloud project and OAuth credentials:

   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project or select an existing one
   - Enable the Google Drive API
   - Configure the OAuth consent screen
   - Create OAuth client ID credentials (Web application type)
   - Note your client ID, client secret, and configure your redirect URI

3. Configure environment variables:
   ```bash
   export POLVO_GOOGLE_CLIENT_ID=your_client_id
   export POLVO_GOOGLE_CLIENT_SECRET=your_client_secret
   export POLVO_GOOGLE_REDIRECT_URI=your_redirect_uri
   ```

## Basic Usage

### Single-User Example

```python
from usepolvo.tentacles.google_drive import GoogleDriveClient

# Initialize the client
client = GoogleDriveClient()

# Get auth URL for a user
auth_url = client.get_auth_url_for_user("user_id")
# Direct the user to auth_url

# Process the callback URL after user authorization
user_id = client.process_callback("callback_url_with_code")

# Set the active user
client.for_user(user_id)

# List files
files = client.files.list(max_results=10)

# Get file metadata
file_info = client.files.get("file_id")

# Download a file
content = client.files.download("file_id")

# Create a new file
new_file = client.files.create(
    name="example.txt",
    content=b"Hello, world!",
    mime_type="text/plain"
)

# Update a file
updated_file = client.files.update(
    file_id="file_id",
    content=b"Updated content",
    metadata={"name": "renamed.txt"}
)

# Delete a file
client.files.delete("file_id")
```

### Multi-Tenant Example

```python
from usepolvo.tentacles.google_drive import GoogleDriveClient

# Initialize the client
client = GoogleDriveClient()

# Authenticate multiple users (in a web app context)
auth_url_1 = client.get_auth_url_for_user("user1")
auth_url_2 = client.get_auth_url_for_user("user2")

# Process callbacks for each user
user1_id = client.process_callback("callback_url_for_user1")
user2_id = client.process_callback("callback_url_for_user2")

# List all authenticated users
users = client.list_authenticated_users()

# Switch between users
client.for_user(user1_id)
user1_files = client.files.list()

client.for_user(user2_id)
user2_files = client.files.list()

# Use context manager for temporary user switching
with client.user_context(user1_id):
    client.files.create(
        name="user1_file.txt",
        content=b"This belongs to user1",
        mime_type="text/plain"
    )
```

## Advanced Usage

### Query Examples

Google Drive supports a query language for filtering files:

```python
# Find PDF files containing "report" in the name
files = client.files.list(
    query="mimeType = 'application/pdf' and name contains 'report'"
)

# Find files in a specific folder
files = client.files.list(
    query="'folder_id' in parents"
)

# Find files modified after a certain date
files = client.files.list(
    query="modifiedTime > '2023-01-01T00:00:00'"
)
```

### Error Handling

```python
try:
    file = client.files.get("nonexistent_file_id")
except Exception as e:
    print(f"Error: {e}")
```

## For More Information

See the examples directory for detailed usage examples:

- `examples/google_drive_usage.py` - Interactive example with real API calls
- `examples/google_drive_api_usage.py` - Code patterns showing API usage
