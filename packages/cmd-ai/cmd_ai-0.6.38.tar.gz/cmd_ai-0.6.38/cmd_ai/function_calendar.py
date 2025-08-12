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
pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
*************************************

"""


import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
#SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# -------- this may be refreshed at some point????
CALENDAR_TOKEN = config.CONFIG["calendar_token"]
CALENDAR_CREDENTIALS = config.CONFIG["calendar_credentials"]



# ============================================================
#
# ------------------------------------------------------------
def die_if_no_credentials(CALENDAR_CREDENTIALS):
    """
    put proper dates and name to the calendar event
    """
    if os.path.exists(os.path.expanduser(CALENDAR_CREDENTIALS)):
        pass
    else:
        print(f"X... you need to get credentials.json from google API")
        print(f"X... the file will/must be stored as  {config.CONFIG['calendar_credentials']} ")
        print(f"""
   *) https://developers.google.com/calendar/api/quickstart/go
    if API is enabled...
    if Branding is done:
   *) authorize credentials
      <go to clients>  .... see your oauth20_client line, press downnload buttonf, press download json
      save (as credentials.json),  move to {CALENDAR_CREDENTIALS}
   *) since there no token.json yet, new web-page opens, select the account, <advanced>,
     goto <yourappname (unsafe)>, press <continue>

""")
        print(f"X... I am dying now ...")
        sys.exit(1)


# ============================================================
#
# ------------------------------------------------------------
def update_event(event, date_, time_, hint, description):
    """
    put proper dates and name to the calendar event
    """
    formatted_date_time = f"{date_[:4]}-{date_[4:6]}-{date_[6:]}T{time_[:2]}:{time_[2:]}:00"
    start_time_obj = dt.datetime.strptime(formatted_date_time, "%Y-%m-%dT%H:%M:%S")
    end_time_obj = start_time_obj + dt.timedelta(hours=1)
    formatted_end_time = end_time_obj.strftime("%Y-%m-%dT%H:%M:%S")

    #print("DEBUG: starttime=", start_time_obj, formatted_date_time)
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
    CALENDAR_TOKEN = os.path.expanduser(config.CONFIG["calendar_token"])
    CALENDAR_CREDENTIALS = os.path.expanduser(config.CONFIG["calendar_credentials"])
    die_if_no_credentials(CALENDAR_CREDENTIALS)

    creds = None
    if os.path.exists(CALENDAR_TOKEN):
        os.remove(CALENDAR_TOKEN)  # Delete old token to regenerate

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            CALENDAR_CREDENTIALS, SCOPES)
        creds = flow.run_local_server(port=0)

        with open(CALENDAR_TOKEN, 'w') as token_file:
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
def set_calendar( date_, time_, hint, description):
    """
    set event
    """
    # -------- this may be refreshed at some point????
    CALENDAR_TOKEN = os.path.expanduser(config.CONFIG["calendar_token"])
    CALENDAR_CREDENTIALS = os.path.expanduser(config.CONFIG["calendar_credentials"])
    die_if_no_credentials(CALENDAR_CREDENTIALS)

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(CALENDAR_TOKEN):
        creds = Credentials.from_authorized_user_file(CALENDAR_TOKEN, SCOPES)
        # If there are no (valid) credentials available, let the user log in.

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CALENDAR_CREDENTIALS, SCOPES
            )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
        with open(CALENDAR_TOKEN, "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        # Refer to the Python quickstart on how to setup the environment:
        # https://developers.google.com/calendar/quickstart/python
        # Change the scope to 'https://www.googleapis.com/auth/calendar' and delete any
        # stored credentials.
        event = {
            'summary': 'Google I/O 2015',
            'location': 'Workplace',
            'description': 'GPT added the meeting',
            'start': {
                'dateTime': '2015-05-28T09:00:00',
                'timeZone': 'Europe/Prague',
            },
            'end': {
                'dateTime': '2015-05-28T17:00:00',
                'timeZone': 'Europe/Prague',
            },
            #      'recurrence': [
            #        'RRULE:FREQ=DAILY;COUNT=2'
            #      ],
            #     'attendees': [
            #        {'email': 'lpage@example.com'},
            #        {'email': 'sbrin@example.com'},
            #      ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    #          {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 15},
                ],
            },
        }

        # REAUTH
        #get_credentials()
        #print('Authorized Scopes:', creds.scopes)
        #calendars = service.calendarList().list().execute()


        update_event(event, date_, time_, hint, description)
        event = service.events().insert(calendarId='primary', body=event).execute()
        print( f' {fg.dimgray}Event created: {fg.default} %s' % (event.get('htmlLink')))

    except HttpError as error:
        print(f"An error occurred: {error}")



# *******************************************************************************






# ============================================================
#
# ------------------------------------------------------------
def make_dir_with_date( NEWDIR):
    """
    just create NEW DIRECTORY
    """
    LDIR = os.path.expanduser("/tmp/")
    LILE = "yyymmdd_.org"
    LFILE = "gpt_calendar.log"
    with open( LDIR+LFILE, "a") as f:
        f.write("*************************************************************\n")
        f.write(f"... making folder ........ {NEWDIR}\n")
        os.makedirs(NEWDIR, exist_ok=True)
        #
        #
        #

def check_date_time(date_, time_):
    input_datetime = dt.datetime.strptime(f"{date_} {time_}", "%Y%m%d %H%M")
    if input_datetime < dt.datetime.now():
        return False
    return True


# ============================================================
#
# ------------------------------------------------------------
def setMeetingRecord(  date_, time_, hint, content ):
    """
    All this should be given by AI
    """
    if not check_date_time(date_, time_):
        print("X... DATE TIME is from the PAST!!!! ")
        return json.dumps(  {"result":"failed: datetime is from the past" } , ensure_ascii=False)

    DIR = os.path.expanduser("~/01_Dokumenty/01_Urad/08_pozvani/")
    DIR = DIR.rstrip("/")
    LDIR = os.path.expanduser("/tmp/")
    LFILE = "gpt_calendar.log"
    NEWDIR = (date_)#dt.datetime.strftime("%Y%m%d_%H%M%S")
    NEWDIR = f"{DIR}/{NEWDIR}"

    newhint = hint.replace(" ", "_")

    NEWDIR = f"{date_}_{time_}_{newhint}"
    NEWDIR = NEWDIR.rstrip("/")
    #NEWDIR = dt.datetime.strftime("%Y%m%d_%H%M%S")
    now = dt.datetime.now().strftime("%Y%m%d_%H%M%S")


    FILE = f"{DIR}/{NEWDIR}/{now}_{newhint}.org"

    TOTPATH = f"{DIR}/{NEWDIR}"
    print(f"{fg.dimgray}{TOTPATH}/{LDIR+LFILE}{fg.default}")
    make_dir_with_date( TOTPATH ) # REALLY MAKE IT

    with open( LDIR+LFILE, "a") as f:
        f.write(f"... ... writing content to {FILE} \n")
        f.write(f"... ... CONTENT:\n")
        f.write(f"... ...    {content} \n\n")
        f.write("\n")

    with open( FILE, "a") as f:
        f.write(content)
        f.write("\n")
        f.write("\n")

    set_calendar( date_, time_, hint, content)

    return json.dumps(  {"result":"ok" } , ensure_ascii=False)  # MUST OUTPUT FORMAT

def getTodaysDateTime():
    res = dt.datetime.now().strftime("%a %d.%m. %Y %H:%M")
    print(f"{fg.dimgray}D... {res}{fg.default}")
    return res


# ============================================================
#
# ------------------------------------------------------------
# def calendar_update(  date_, hint):
#     DIR = os.path.expanduser("~/01_Dokumenty/01_Urad/08_pozvani/")
#     DIR = os.path.expanduser("/tmp/")
#     NEWDIR = dt.datetime.strftime("%Y%m%d_%H%M%S")
#     FILE = "yyymmdd_.org"
#     LFILE = "gpt_calendar.log"

#     with open( LDIR+LFILE, "a") as f:
#         f.write(f"... updating calendar {date_} {hint} \n")
#         f.write("\n")

#     return json.dumps(  {"result":"ok" } , ensure_ascii=False)  # MUST OUTPUT FORMAT



# ============================================================
#
# ------------------------------------------------------------
if __name__=="__main__":
    Fire({'m':make_dir_with_date,
          'f':setMeetingRecord,
          'g':getTodaysDateTime})
