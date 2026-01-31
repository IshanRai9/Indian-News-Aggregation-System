import os.path
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    """Shows basic usage of the Drive v3 API.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                logging.error("credentials.json not found! Cannot authenticate with Google Drive.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        logging.error(f"Unable to connect to Drive Service: {e}")
        return None

def get_or_create_folder(service, folder_name):
    """
    Returns the ID of the folder with the given name. Creates it if it doesn't exist.
    """
    try:
        # Check if folder exists
        query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
        results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])

        if not items:
            # Create folder
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            file = service.files().create(body=file_metadata, fields='id').execute()
            logging.info(f"Created Drive folder: {folder_name} ({file.get('id')})")
            return file.get('id')
        else:
            return items[0]['id']
    except Exception as e:
        logging.error(f"Error checking/creating folder: {e}")
        return None

def upload_file(file_path, folder_name="RedditNewsMedia"):
    """
    Uploads a file to the specified Google Drive folder.
    Returns (file_name, file_id, web_view_link) or None on failure.
    """
    if not os.path.exists(file_path):
        logging.error(f"File not found for upload: {file_path}")
        return None

    service = get_drive_service()
    if not service:
        return None

    folder_id = get_or_create_folder(service, folder_name)
    if not folder_id:
        return None

    file_name = os.path.basename(file_path)
    
    try:
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        
        logging.info(f"Uploading {file_name} to Drive...")
        file = service.files().create(body=file_metadata, media_body=media, fields='id, name, webViewLink').execute()
        
        logging.info(f"Upload complete. File ID: {file.get('id')}")
        return file.get('name'), file.get('id'), file.get('webViewLink')
        
    except Exception as e:
        logging.error(f"Error uploading file {file_name}: {e}")
        return None
