import os.path

# from pprint import pprint
# from alive_progress import alive_bar;
from datetime import datetime
import calendar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]


class UserInput:
    """Object to capture User enterd values
    """
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
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
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
    return UserInput(client, sector, project, int(flights))

def get_parent_id(creds, name):
    """Return the file id for a folder (normally a parent folder)
    """
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
    """Get the folder ID for a child folder
    """
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
    """Create Project Folder Function
    """
    client = sub_folder_search(creds, 'Firstlook Services', user_input.client)
    client_name = client[0].get("name")
    sector = sub_folder_search(creds, client_name, user_input.sector)
    sector_id = sector[0].get("id")
#   for x in sector:
#        print(f'Found folder: {x.get("name")}, {x.get("id")}')
    try:
        service = build("drive", "v3", credentials=creds)
        project_metadata = {
            "parents": [sector_id],
            "name": user_input.project,
            "mimeType": "application/vnd.google-apps.folder",
        }
        project = service.files().create(body=project_metadata, fields="id").execute()
        project_id = project.get("id")
    except HttpError as error:
        print(f"An error occurred creating Folder: {error}")
        return None
    create_flights(creds, project_id, user_input.flights, user_input.project)
    create_insurance(creds, project_id)
    create_contract(creds, project_id)

def create_insurance(creds, id):
    """Create Insurance folder and children folders
    """
    try:
        service = build("drive", "v3", credentials=creds)
        insurance_metadata = {
            "parents": [id],
            "name": "Insurance",
            "mimeType": "application/vnd.google-apps.folder",
        }
        # pylint: disable=maybe-no-member
        insurance = service.files().create(body=insurance_metadata, fields="id").execute()
        insurance_id = insurance.get("id")
        child_names = ["Requirements", "COIs"]
        for folder in child_names:
            child_metadata = {
                "name": folder,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [insurance_id],
            }
            service.files().create(body=child_metadata, fields="id").execute()
    except HttpError as error:
        print(f"An error occurred creating Folder: {error}")
        return None

def create_contract(creds, id):
    """Create contract prep and children folders
    """
    try:
        service = build("drive", "v3", credentials=creds)
        contract_metadata = {
            "parents": [id],
            "name": "Contract Prep",
            "mimeType": "application/vnd.google-apps.folder",
        }
        # pylint: disable=maybe-no-member
        contract = service.files().create(body=contract_metadata, fields="id").execute()
        contract_id = contract.get("id")
        child_names = ["Plans", "Schedule", "Proposal", "Contract"]
        for folder in child_names:
            child_metadata = {
                "name": folder,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [contract_id],
            }
            service.files().create(body=child_metadata, fields="id").execute()
    except HttpError as error:
        print(f"An error occurred creating Folder: {error}")
        return None

def create_flights(creds, id, flights, project):
    """Create Flights folder and children folders
    """
    current_year = datetime.now().year
    try:
        service = build("drive", "v3", credentials=creds)
        flights_metadata = {
            "parents": [id],
            "name": str(current_year) + " Flights",
            "mimeType": "application/vnd.google-apps.folder",
        }
        # pylint: disable=maybe-no-member
        parent_flight = service.files().create(body=flights_metadata, fields="id").execute()
        parent_flight_id = parent_flight.get("id")
        current_month = datetime.now().month
        if flights > 1:
            month_metadata = {
                "name": calendar.month_name[current_month] + " Flights",
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_flight_id],
            }
            month_child = service.files().create(body=month_metadata, fields="id").execute()
            month_child_id = month_child.get("id")
            date_folders = []
            for folder_num in range(1, flights + 1):
                date_folders.append("Date"+str(folder_num))
            for index, date in enumerate(date_folders):
                date_metadata = {
                    "name": date,
                    "mimeType": "application/vnd.google-apps.folder",
                    "parents": [month_child_id],
                }
                date_child = service.files().create(body=date_metadata, fields="id").execute()
                date_child_id = date_child.get("id")
                date_child_names = ["Raw Footage", "Photos", "Video", "Photo Report " + project + " " + calendar.month_name[current_month] + " " + str(index + 1)]
                for date_child in date_child_names:
                    date_child_metadata = {
                        "name": date_child,
                        "mimeType": "application/vnd.google-apps.folder",
                        "parents": [date_child_id],
                    }
                    service.files().create(body=date_child_metadata, fields="id").execute()
        else:
            date_metadata = {
                "name": "Date1",
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_flight_id],
            }
            date_child = service.files().create(body=date_metadata, fields="id").execute()
            date_child_id = date_child.get("id")
            date_child_names = ["Raw Footage", "Photos", "Video", "Photo Report " + project + " " + calendar.month_name[current_month] + " " + str(1)]
            for date_child in date_child_names:
                date_child_metadata = {
                    "name": date_child,
                    "mimeType": "application/vnd.google-apps.folder",
                    "parents": [date_child_id],
                }
                service.files().create(body=date_child_metadata, fields="id").execute()

    except HttpError as error:
        print(f"An error occurred creating Folder: {error}")
        return None
    
if __name__ == "__main__":
    creds = drive_auth()
    input_vars = accept_user_input()
    create_project(creds,input_vars)
