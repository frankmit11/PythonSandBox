import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]

def drive_auth():
    """Authenticate with Drive API Project
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("./auth/token.json"):
        creds = Credentials.from_authorized_user_file("./auth/token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
              "./auth/credentials.json", SCOPES
          )
        creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
        with open("./auth/token.json", "w") as token:
            token.write(creds.to_json())
    return creds
def create_drive_folders():
    """Create Drive Folders and sub-directories
    """
    creds = drive_auth()
    try:
        service = build("drive", "v3", credentials=creds)
        parent_metadata = {
            "name": "ParentFolder",
            "mimeType": "application/vnd.google-apps.folder",
        }
        # pylint: disable=maybe-no-member
        parent = service.files().create(body=parent_metadata, fields="id").execute()
        parent_id = parent.get("id")
        folder_names = ["ChildFolder1", "ChildFolder2", "ChildFolder3"]
        for folder in folder_names:
            child_metadata = {
                "name": folder,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_id],
            }
            service.files().create(body=child_metadata, fields="id").execute()
    except HttpError as error:
        print(f"An error occurred creating Folder: {error}")
        return None

if __name__ == "__main__":
    create_drive_folders()
