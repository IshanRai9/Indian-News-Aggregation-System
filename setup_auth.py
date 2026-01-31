from uploader import get_drive_service
import logging

# Configure logging to see output
logging.basicConfig(level=logging.INFO)

print("Starting Drive Authentication...")
print("This will open a browser window. Please log in.")
service = get_drive_service()

if service:
    print("Authentication Successful! 'token.json' has been created.")
else:
    print("Authentication Failed.")
