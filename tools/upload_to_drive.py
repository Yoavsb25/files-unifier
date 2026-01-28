import argparse
import os
from typing import Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def _build_drive_service():
    """
    Build an authenticated Google Drive service using OAuth 2.0 user credentials.

    Expects the following environment variables to be set:
      - GDRIVE_CLIENT_ID
      - GDRIVE_CLIENT_SECRET
      - GDRIVE_REFRESH_TOKEN
    """
    client_id = os.environ.get("GDRIVE_CLIENT_ID")
    client_secret = os.environ.get("GDRIVE_CLIENT_SECRET")
    refresh_token = os.environ.get("GDRIVE_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        raise RuntimeError(
            "Missing one or more required environment variables: "
            "GDRIVE_CLIENT_ID, GDRIVE_CLIENT_SECRET, GDRIVE_REFRESH_TOKEN"
        )

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token",
    )

    if not creds.valid:
        creds.refresh(Request())

    return build("drive", "v3", credentials=creds)


def _detect_mime_type(file_path: str, explicit: Optional[str]) -> str:
    if explicit:
        return explicit
    # Basic heuristic – can be extended if needed
    _, ext = os.path.splitext(file_path.lower())
    if ext == ".zip":
        return "application/zip"
    return "application/octet-stream"


def upload_file(
    folder_id: str,
    file_path: str,
    mime_type: Optional[str] = None,
    overwrite: str = "skip",
) -> None:
    """
    Upload a file to Google Drive using OAuth 2.0 user credentials.

    :param folder_id: Target Drive folder ID.
    :param file_path: Local file path to upload.
    :param mime_type: Optional MIME type; if None, inferred from extension.
    :param overwrite: Strategy when a file with the same name exists in the folder.
                      One of: "skip" (default), "replace".
    """
    if overwrite not in {"skip", "replace"}:
        raise ValueError(f"Unsupported overwrite mode: {overwrite}")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File to upload not found: {file_path}")

    service = _build_drive_service()

    file_name = os.path.basename(file_path)
    resolved_mime_type = _detect_mime_type(file_path, mime_type)

    # Check for existing files with the same name in the target folder
    escaped_name = file_name.replace("'", "\\'")
    query = (
        f"name = '{escaped_name}' and "
        f"'{folder_id}' in parents and trashed = false"
    )
    existing_files = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute().get("files", [])

    if existing_files and overwrite == "skip":
        print(
            f"File '{file_name}' already exists in folder '{folder_id}'. "
            "Skipping upload because overwrite=skip."
        )
        return

    if existing_files and overwrite == "replace":
        for f in existing_files:
            service.files().delete(fileId=f["id"]).execute()
        print(
            f"Deleted {len(existing_files)} existing file(s) named '{file_name}' "
            f"in folder '{folder_id}' before upload."
        )

    file_metadata = {"name": file_name, "parents": [folder_id]}
    media = MediaFileUpload(file_path, mimetype=resolved_mime_type, resumable=False)

    created = (
        service.files()
        .create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink",
            supportsAllDrives=True,
        )
        .execute()
    )

    file_id = created.get("id")
    web_view_link = created.get("webViewLink")
    print(f"Uploaded file '{file_name}' to Google Drive.")
    print(f"File ID: {file_id}")
    if web_view_link:
        print(f"Web view link: {web_view_link}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload a file to Google Drive using a service account key."
    )
    parser.add_argument(
        "--folder-id",
        required=True,
        help="Target Google Drive folder ID.",
    )
    parser.add_argument(
        "--file-path",
        required=True,
        help="Local path of the file to upload.",
    )
    parser.add_argument(
        "--mime-type",
        required=False,
        help="Optional MIME type for the uploaded file. "
        "If omitted, inferred from file extension.",
    )
    parser.add_argument(
        "--overwrite",
        choices=["skip", "replace"],
        default="skip",
        help="Behavior when a file with the same name already exists in the "
        "target folder. 'skip' (default) leaves existing file, "
        "'replace' deletes existing file(s) and uploads a new one.",
    )

    args = parser.parse_args()

    upload_file(
        folder_id=args.folder_id,
        file_path=args.file_path,
        mime_type=args.mime_type,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()

