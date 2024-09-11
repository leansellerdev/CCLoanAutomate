import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from settings import PDFS_DIR


class GoogleDrive:
    # If modifying these SCOPES, delete the file token.json.

    def __init__(self) -> None:
        self._SCOPES = ['https://www.googleapis.com/auth/drive']

        self.cases_folder_id = "1_khSJGGZolLz2VeoWBnv62jrswWqbf2s"

    def _authenticate(self) -> any:
        """ Authenticates user and returns Google Drive service """
        creds = None
        # Token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self._SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self._SCOPES)
                creds = flow.run_local_server(port=8080)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service = build('drive', 'v3', credentials=creds)
        return service

    def create_folder(self, folder_name, parent_folder_id: str = None) -> str:
        """Creates a folder in Google Drive."""
        service = self._authenticate()

        folder_metadata = dict(
            name=folder_name,
            mimeType='application/vnd.google-apps.folder'
        )

        if parent_folder_id:
            folder_metadata['parents'] = [parent_folder_id]

        folder = service.files().create(body=folder_metadata, fields='id').execute()
        return folder['id']

    def upload_file(self, file_name, file_path, folder_id: str = None) -> None:
        """ Uploads a file to Google Drive """
        service = self._authenticate()

        file_metadata = {'name': file_name}
        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaFileUpload(file_path, mimetype='application/octet-stream')

        # Upload the file
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id').execute()

        print(f'File uploaded successfully. File ID: {file.get("id")}')
