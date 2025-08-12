#!/usr/bin/env python3

from cmd_ai import config
from cmd_ai.version import __version__
import json
import os
import datetime as dt
import sys

"""
texts.py contains the description: tool_***={}
In syscom.py ADD the tool_Name to  config.TOOLLIST
In g_askme.py IMPORT module:   from cmd_ai import  function_***
In g_askme.py - add to ... config.available_functions



*************************************
 pip3 install --upgrade google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib
*************************************

"""

import datetime

"""
 pip install --upgrade google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib

"""

# calendar needs
from google.auth.transport.requests import Request
#from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
#from googleapiclient.discovery import build
#from googleapiclient.errors import HttpError

# gmail needs
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
import base64

# gmail attachment version
from email.mime.multipart import MIMEMultipart
#from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


# If modifying these scopes, delete the file token.json.
#SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
#SCOPES = ["https://www.googleapis.com/auth/calendar"]
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# -------- this may be refreshed at some point????
GMAIL_TOKEN = config.CONFIG["gmail_token"]
GMAIL_CREDENTIALS = config.CONFIG["gmail_credentials"]



# ============================================================
#
# ------------------------------------------------------------
def die_if_no_credentials(GMAIL_CREDENTIALS):
    """
    put proper dates and name to the  event
    """
    if os.path.exists(os.path.expanduser(GMAIL_CREDENTIALS)):
        pass
    else:
        print(f"X... you need to get credentials(g).json from google API")
        print(f"X... the file will/must be stored as  {config.CONFIG['gmail_credentials']} ")
        print(f"""
   *) FROM SCRATCH: *****************************************
     goto https://console.developers.google.com/
     -
     enable API&services
     create a new project
     Go to Credentials and  +Create credentials
     The options are 1. API keys 2. OAuth client ID 3. Service account... select OAuth client
     Create 'consent screen', a new menu-system appears
     go to Clients, create DEsktop client, get ClientID, Client secret ...
     now, download json (to credentials.json)
     ... token will be obtained using these credentials and authorization screen...

   *) IF API ALEADY EXISTS *********************************
    http://console.cloud.google.com/apis/credentials
    if API is enabled...
    if Branding is done ... relates to the definition of the consent screen:
   *) btw Audience should/may need 1 test user, you?
   *) authorize credentials
      <go to clients>  .... see your oauth20_client line, press download buttonf, press download json
      save (as credentialsg.json),  move to {GMAIL_CREDENTIALS}
   *) since there no tokeng.json yet, new web-page opens, select the account, <advanced>,
     goto <yourappname (unsafe)>, press <continue>

""")
        print(f"X... I am dying now ...")
        sys.exit(1)


# ============================================================
#
# ------------------------------------------------------------
def update_event(event, date_, time_, hint, description):
    """
    put proper dates and name to the  event
    """
    formatted_date_time = f"{date_[:4]}-{date_[4:6]}-{date_[6:]}T{time_[:2]}:{time_[2:]}:00"
    start_time_obj = dt.datetime.strptime(formatted_date_time, "%Y-%m-%dT%H:%M:%S")
    end_time_obj = start_time_obj + dt.timedelta(hours=1)
    formatted_end_time = end_time_obj.strftime("%Y-%m-%dT%H:%M:%S")

    print("DEBUG: starttime=", start_time_obj, formatted_date_time)
    #print("DEBUG:   endtime=", end_time_obj, formatted_end_time)

    event['start']['dateTime'] = formatted_date_time
    event['end']['dateTime'] = formatted_end_time
    event['summary'] = hint
    event['description'] = description
    return event


# ============================================================
#
# ------------------------------------------------------------
def get_credentials():
    """
    contacts google to download json credentials/ or take an existing token
    """
    # -------- this may be refreshed at some point????
    GMAIL_TOKEN = os.path.expanduser(config.CONFIG["gmail_token"])
    GMAIL_CREDENTIALS = os.path.expanduser(config.CONFIG["gmail_credentials"])
    die_if_no_credentials(GMAIL_CREDENTIALS)

    creds = None
    if os.path.exists(GMAIL_TOKEN):
        os.remove(GMAIL_TOKEN)  # Delete old token to regenerate

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            GMAIL_CREDENTIALS, SCOPES)
        creds = flow.run_local_server(port=0)

        with open(GMAIL_TOKEN, 'w') as token_file:
            token_file.write(creds.to_json())

    return creds


"""

##

#### return json



"""


from fire import Fire
import datetime as dt
from console import fg


# ============================================================
#
# ------------------------------------------------------------

def sendGmail(email_recipient, email_subject, email_body, attachment_path=None):
    """
    Send an email with an optional attachment.
    """
    # -------- this may be refreshed at some point????
    GMAIL_TOKEN = os.path.expanduser(config.CONFIG["gmail_token"])
    GMAIL_CREDENTIALS = os.path.expanduser(config.CONFIG["gmail_credentials"])
    die_if_no_credentials(GMAIL_CREDENTIALS)

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(GMAIL_TOKEN):
        creds = Credentials.from_authorized_user_file(GMAIL_TOKEN, SCOPES)
        # If there are no (valid) credentials available, let the user log in.

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GMAIL_CREDENTIALS, SCOPES
            )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
        with open(GMAIL_TOKEN, "w") as token:
            token.write(creds.to_json())


    try:
        service = build("gmail", "v1", credentials=creds)

        # Create the email container
        message = MIMEMultipart()
        message['to'] = email_recipient
        message['subject'] = email_subject
        message.attach(MIMEText(email_body, 'plain'))

        # Add attachment if provided
        if attachment_path:
            attachment_path1 = os.path.expanduser(attachment_path)
            print("i... adding the attachment: ", attachment_path1)
            with open(attachment_path1, "rb") as file:
                mime_base = MIMEBase('application', 'octet-stream')
                mime_base.set_payload(file.read())
            encoders.encode_base64(mime_base)
            mime_base.add_header(
                'Content-Disposition',
                f'attachment; filename={os.path.basename(attachment_path1)}',
            )
            message.attach(mime_base)

        # Encode the message to Base64
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        email_message = {'raw': raw}
        print("i... total message size:", sys.getsizeof(email_message) )

        # Send the email
        sent_message = service.users().messages().send(userId="me", body=email_message).execute()
        print(f"Message Id: {sent_message['id']}")

    except HttpError as error:
        print(f'An error occurred: {error}')

    return json.dumps({"result": "ok"}, ensure_ascii=False)



def XsendGmail( email_recipient, email_subject, email_body ):
    """
    just send the email
    """
    # -------- this may be refreshed at some point????
    GMAIL_TOKEN = os.path.expanduser(config.CONFIG["gmail_token"])
    GMAIL_CREDENTIALS = os.path.expanduser(config.CONFIG["gmail_credentials"])
    die_if_no_credentials(GMAIL_CREDENTIALS)

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(GMAIL_TOKEN):
        creds = Credentials.from_authorized_user_file(GMAIL_TOKEN, SCOPES)
        # If there are no (valid) credentials available, let the user log in.

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GMAIL_CREDENTIALS, SCOPES
            )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
        with open(GMAIL_TOKEN, "w") as token:
            token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)

        message = MIMEText( email_body )
        message['to'] = email_recipient
        message['subject'] = email_subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        email_message = {'raw': raw}

        sent_message = service.users().messages().send(userId="me", body=email_message).execute()
        print(f"Message Id: {sent_message['id']}")

    except HttpError as error:
        print(f'An error occurred: {error}')


    return json.dumps(  {"result":"ok" } , ensure_ascii=False)  # MUST OUTPUT FORMAT


# *******************************************************************************






# ============================================================
#
# ------------------------------------------------------------
if __name__=="__main__":
    Fire({'s':sendGmail })
