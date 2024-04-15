import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]


class user_input:
  def __init__(self, client, sector, project, flights):
    self.client = client
    self.sector = sector
    self.project = project
    self.flights = flights
  def __repr__(self):  
        return "User Input cleint:% s sector:% s project:% s flights:% s  " % (self.client, self.sector, self.project, self.flights) 

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
        # if creds and creds.expired and creds.refresh_token:
        #     print("hey")
        #     creds.refresh(Request())
        # else:
        flow = InstalledAppFlow.from_client_secrets_file(
              "./auth/credentials.json", SCOPES
          )
        creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
        with open("./auth/token.json", "w", encoding="utf-8") as token:
            token.write(creds.to_json())
    return creds

def accept_user_input():
    """Process user parameters
    """
    client = input("Enter Client Name:")
    print("Client: " + client)
    sector = input("Sector Name (Construction):")
    if not sector:
        sector = "Construction"
    print("Sector: " + sector)
    project = input("Enter Project Name:")
    print("Project: " + project)
    flights = input("Enter Number of Flights:")
    print("Flights: " + flights)
    return user_input(client, sector, project, flights)

def get_parent_id(creds, name):
  try:
   # create drive api client
   service = build("drive", "v3", credentials=creds)
   parents = []
   page_token = None
   while True:
     # pylint: disable=maybe-no-member
     response = (
         service.files()
         .list(
             q="mimeType = 'application/vnd.google-apps.folder' and name='{0}'".format(name),
             spaces="drive",
             fields="nextPageToken, files(id)",
             pageToken=page_token,
         )
         .execute()
     )
     parent = response.get("files")
     parent_id = parent[0].get("id")
     page_token = response.get("nextPageToken", None)
     parents.extend(response.get("files", []))
     if page_token is None:
       break
  except HttpError as error:
    print(f"An error occurred, cannot locate folder Firstlook Services: {error}")
    parent = None

  return parent_id
   
def sub_folder_search(creds, parent_name, sub_folder_name):
  parent_id = get_parent_id(creds, parent_name)
  try:
    # create drive api client
    service = build("drive", "v3", credentials=creds)
    sub_folders = []
    page_token = None
    while True:
      # pylint: disable=maybe-no-member
      response = (
          service.files()
          .list(
              q="mimeType = 'application/vnd.google-apps.folder' and parents in '{0}' and name contains '{1}'".format(parent_id, sub_folder_name),
              spaces="drive",
              fields="nextPageToken, files(id, name)",
              pageToken=page_token,
          )
          .execute()
      )
      sub_folder = response.get("files")
    #   for folder in response.get("files"):
    #     # Process change
    #     print(f'Found folder: {folder.get("name")}, {folder.get("id")}')
      page_token = response.get("nextPageToken", None)
      sub_folders.extend(response.get("files", []))
      if page_token is None:
        break
  except HttpError as error:
    print(f"An error occurred: {error}")
    sub_folders = None

  return sub_folder

def create_project(creds, user_input):
  client = sub_folder_search(creds, 'Firstlook Services', user_input.client)
  client_name = client[0].get("name")
  sector = sub_folder_search(creds, client_name, user_input.sector)
  sector_id = sector[0].get("id")
#   for x in sector:
#        print(f'Found folder: {x.get("name")}, {x.get("id")}')
  print(sector_id)

# def create_drive_folders():
#     """Create Drive Folders and sub-directories
#     """
#     user_input = accept_user_input()
#     #print([user_input])
#     creds = drive_auth()
#     try:
#         service = build("drive", "v3", credentials=creds)
#         parent_metadata = {
#             "name": "ParentFolder",
#             "mimeType": "application/vnd.google-apps.folder",
#         }
#         # pylint: disable=maybe-no-member
#         parent = service.files().create(body=parent_metadata, fields="id").execute()
#         parent_id = parent.get("id")
#         folder_names = ["ChildFolder1", "ChildFolder2", "ChildFolder3"]
#         for folder in folder_names:
#             child_metadata = {
#                 "name": folder,
#                 "mimeType": "application/vnd.google-apps.folder",
#                 "parents": [parent_id],
#             }
#             service.files().create(body=child_metadata, fields="id").execute()
#     except HttpError as error:
#         print(f"An error occurred creating Folder: {error}")
#         return None

if __name__ == "__main__":
    creds = drive_auth()
    input_vars = accept_user_input()
    create_project(creds,input_vars)
    #create_drive_folders()
