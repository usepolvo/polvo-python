# src/usepolvo/tentacles/google_drive/files.py

import io
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# Conditional import only used during type checking
if TYPE_CHECKING:
    from usepolvo.tentacles.google_drive.client import GoogleDriveClient


class Files:
    """
    Handles interactions with Google Drive's Files API using Google's official Python client.
    """

    def __init__(self, client: "GoogleDriveClient"):
        """
        Initialize the Files resource.

        Args:
            client: The GoogleDriveClient instance
        """
        self.client = client

    def list(self, query: Optional[str] = None, max_results: int = 100) -> Dict[str, Any]:
        """
        List files in Google Drive for the current user.

        Args:
            query: Optional query string (Google Drive query format)
            max_results: Maximum number of results to return

        Returns:
            Google Drive API response with list of files
        """
        service = self.client.get_current_user_service()

        # Build parameters for files.list() call
        params = {
            "pageSize": max_results,
            "fields": "nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, size)",
        }

        if query:
            params["q"] = query

        try:
            results = service.files().list(**params).execute()
            return results
        except HttpError as error:
            raise Exception(f"An error occurred while listing files: {error}")

    def get(self, file_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """
        Get file metadata by ID.

        Args:
            file_id: Google Drive file ID
            fields: Optional comma-separated list of fields to include

        Returns:
            File metadata
        """
        service = self.client.get_current_user_service()

        params = {}
        if fields:
            params["fields"] = fields

        try:
            return service.files().get(fileId=file_id, **params).execute()
        except HttpError as error:
            raise Exception(f"An error occurred while getting file: {error}")

    def download(self, file_id: str) -> bytes:
        """
        Download file content by ID.

        Args:
            file_id: Google Drive file ID

        Returns:
            File content as bytes
        """
        service = self.client.get_current_user_service()

        try:
            # Create a BytesIO stream to download the file into
            request = service.files().get_media(fileId=file_id)
            file_stream = io.BytesIO()
            downloader = MediaIoBaseDownload(file_stream, request)

            # Download the file in chunks
            done = False
            while not done:
                status, done = downloader.next_chunk()

            # Return the downloaded content as bytes
            return file_stream.getvalue()
        except HttpError as error:
            raise Exception(f"An error occurred while downloading file: {error}")

    def create(
        self, name: str, content: bytes, mime_type: str, parent_folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new file with content.

        Args:
            name: Name of the new file
            content: File content as bytes
            mime_type: MIME type of the file
            parent_folder_id: Optional parent folder ID

        Returns:
            New file metadata
        """
        service = self.client.get_current_user_service()

        # Set up file metadata
        file_metadata = {"name": name, "mimeType": mime_type}

        # Set parent folder if provided
        if parent_folder_id:
            file_metadata["parents"] = [parent_folder_id]

        try:
            # Create a MediaIoBaseUpload object for the content
            from googleapiclient.http import MediaInMemoryUpload

            media = MediaInMemoryUpload(content, mimetype=mime_type)

            # Create the file
            file = (
                service.files()
                .create(
                    body=file_metadata,
                    media_body=media,
                    fields="id,name,mimeType,createdTime,modifiedTime",
                )
                .execute()
            )

            return file
        except HttpError as error:
            raise Exception(f"An error occurred while creating file: {error}")

    def update(
        self,
        file_id: str,
        content: Optional[bytes] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing file's content and/or metadata.

        Args:
            file_id: Google Drive file ID
            content: Optional new file content as bytes
            metadata: Optional new file metadata

        Returns:
            Updated file metadata
        """
        service = self.client.get_current_user_service()

        try:
            # If we're updating content
            if content:
                # Get the current file to determine its MIME type
                current_file = service.files().get(fileId=file_id, fields="mimeType").execute()
                mime_type = current_file["mimeType"]

                # Create a MediaIoBaseUpload object for the new content
                from googleapiclient.http import MediaInMemoryUpload

                media = MediaInMemoryUpload(content, mimetype=mime_type)

                # If we also have metadata, update both
                if metadata:
                    return (
                        service.files()
                        .update(
                            fileId=file_id,
                            body=metadata,
                            media_body=media,
                            fields="id,name,mimeType,modifiedTime",
                        )
                        .execute()
                    )
                # Otherwise just update the content
                else:
                    return (
                        service.files()
                        .update(
                            fileId=file_id, media_body=media, fields="id,name,mimeType,modifiedTime"
                        )
                        .execute()
                    )
            # If we're only updating metadata
            elif metadata:
                return (
                    service.files()
                    .update(fileId=file_id, body=metadata, fields="id,name,mimeType,modifiedTime")
                    .execute()
                )
            else:
                raise ValueError("At least one of content or metadata must be provided")
        except HttpError as error:
            raise Exception(f"An error occurred while updating file: {error}")

    def delete(self, file_id: str) -> None:
        """
        Delete a file permanently.

        Args:
            file_id: Google Drive file ID
        """
        service = self.client.get_current_user_service()

        try:
            service.files().delete(fileId=file_id).execute()
        except HttpError as error:
            raise Exception(f"An error occurred while deleting file: {error}")
