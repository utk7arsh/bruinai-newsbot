from __future__ import print_function
import base64
import re
import os.path
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def scrape_email():
    creds = None
    # The file token.json stores the user's access and refresh tokens and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=4000)  # Changed port here to match the OAuth credentials.
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)

        # Request the latest email from 'dan@tldrnewsletter.com'
        results = service.users().messages().list(userId='me', q='from:(TLDR AI dan@tldrnewsletter.com)', maxResults=1).execute()
        messages = results.get('messages', [])
        
        if messages:
            latest_msg = messages[0]
            msg = service.users().messages().get(userId='me', id=latest_msg['id']).execute()

            try:
                payload = msg['payload']
                headers = payload['headers']

                for d in headers:
                    if d['name'] == 'Subject':
                        subject = d['value']
                    if d['name'] == 'From':
                        sender = d['value']

                parts = payload.get('parts')[0]
                data = parts['body']['data']
                data = data.replace("-", "+").replace("_", "/")
                decoded_data = base64.b64decode(data)

                # print("Subject: ", subject)
                # print("From: ", sender)

                data = decoded_data.decode("utf-8")
                # print(decoded_data.decode("utf-8"))
                x = data.find("HEADLINES & LAUNCHES")
                y = data.find("RESEARCH & INNOVATION")
                printable_data = data[x:y-9].split('\n')
                return printable_data

            except Exception as error:
                print(f'An error occurred: {error}')
        else:
            print("No emails found from 'dan@tldrnewsletter.com'.")

    except HttpError as error:
        # TODO(developer) - Handle errors from Gmail API.
        print(f'An error occurred: {error}')
