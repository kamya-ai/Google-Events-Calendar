# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
from __future__ import print_function

from rasa_sdk.events import AllSlotsReset
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import iso8601
import rfc3339
from datetime import datetime, timedelta
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle
import parsedatetime
from pytz import timezone

# Specify the shift start time here.
shift_start = "09:00:00+05:30"

# Specify the shift end time here.
shift_end = "22:00:00+05:30"

# If only dat is specified but the meeting time is not specified, then the following time will be taken by default.
default_meeting_time = '11:30:00+05:30'

# class ActionHelloWorld(Action):

#     def name(self) -> Text:
#         return "action_hello_world"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         dispatcher.utter_message(text="Hello World!")

#         return []


class AddEventToCalendar(Action):
    '''
    Class to add event to the calendar.
    '''

    def name(self) -> Text:
        return "action_add_event"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Fetching name of the scheduled event
        event_name = tracker.get_slot('event')

        # Fetching time at which the event is to be scheduled
        time = tracker.get_slot('time')

        # If time of the event is not specified, then time after one hour will be taken by the chatbot to schedule the event.
        if time is None:
            time = str(datetime.now(timezone('Asia/Kolkata'))+timedelta(hours=1))

        # Converting datetime from datetime object to 
        time = iso8601.parse_date(time)
        just_time = str(time)[11:-6]

        # If only date is specified, then the duckling extractor takes 00:00:00 time by default, that is not feasible. 
        # Hence, that time is to be replaced by some default value.
        if just_time == '00:00:00':
            time = str(time)[:11]+default_meeting_time
            time = iso8601.parse_date(time)

        # If the event name is not specified, then it will take by default as 'Meeting'
        if event_name is None:
            event_name = 'Meeting'

        # Calling function for adding event.
        msg = add_event(event_name, time)

        # The final message is dispatched as a response to the user
        dispatcher.utter_message(text=msg)
        return [AllSlotsReset()]


class GetFreeSlots(Action):
    '''
    Class to get free slots on a specified date.
    '''
    def name(self) -> Text:
        return "action_get_free_slots"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Fetching date on which the free slots are to be found out.
        date = tracker.get_slot('date')
        if date is None:
            date = rfc3339.rfc3339(datetime.now(timezone('Asia/Kolkata')))

        # Calling the function to get free slots.
        msg = get_free_slots(date)

        # The final message is dispatched as a response to the user
        dispatcher.utter_message(text=msg)
        return [AllSlotsReset()]

class getEvent(Action):
    '''
    Class to get event on a specified date.
    '''

    def name(self) -> Text:
        return "action_get_event"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Fetching the date on which the event list is to be found out.
        date = tracker.get_slot('event_date')

        # Setting today's date if it is not specified explicitly.
        if date is None:
            date = rfc3339.rfc3339(datetime.now(timezone('Asia/Kolkata')))

        # Calling the get event function.
        event_name = get_event(date)

        # The final message is dispatched as a response to the user
        dispatcher.utter_message(text="{name}".format(name= event_name))
        return []

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_FILE = 'credentials.json'

def get_calendar_service():
   creds = None
   # The file token.pickle stores the user's access and refresh tokens, and is
   # created automatically when the authorization flow completes for the first
   # time.
   if os.path.exists('token.pickle'):
       with open('token.pickle', 'rb') as token:
           creds = pickle.load(token)
   # If there are no (valid) credentials available, let the user log in.
   if not creds or not creds.valid:
       if creds and creds.expired and creds.refresh_token:
           creds.refresh(Request())
       else:
           flow = InstalledAppFlow.from_client_secrets_file(
               CREDENTIALS_FILE, SCOPES)
           creds = flow.run_local_server(port=0)

       # Save the credentials for the next run
       with open('token.pickle', 'wb') as token:
           pickle.dump(creds, token)

   service = build('calendar', 'v3', credentials=creds)
   return service

def add_event(event_name, time):
    '''
    Function to schedule event on a specific time along with checking the availability for the specified time
    and giving free slots for the day, if busy.
    '''

    service = get_calendar_service()

    # Specified start time of the event
    start = time.isoformat()

    # Here, by default the event time is set to one hour, which can be changed according to the requirement.
    end = (time + timedelta(hours=1)).isoformat()

    # Getting event date from the isoformat datetime
    event_date = start[:10]

    # Converting into rfc3339 format
    day_start = f'{event_date}T{shift_start}'
    day_end = f'{event_date}T{shift_end}'

    # Converting to datetime object for using operators.
    iso_day_start = iso8601.parse_date(f'{event_date}T{shift_start}')
    iso_day_end = iso8601.parse_date(f'{event_date}T{shift_end}')

    # Getting list of events scheduled at the given time.
    events = service.events().list(calendarId='primary', timeMin=start, timeMax=end, maxResults=10, singleEvents = True, orderBy='startTime').execute().get("items",[])

    # Checking if there are any events or not.
    if events:
        events_list = list()
        for event in events:
            event_details = f'{event["summary"]}:- {event["start"]["dateTime"][11:-6]} to {event["end"]["dateTime"][11:-6]}'
            events_list.append(event_details)
        free_busy_query ={
            "timeMin": day_start,           # Starting time in rfc3339 format
            "timeMax": day_end,             # End time in rfc3339 format
            "timeZone": "Asia/Kolkata",     # Time Zone
            "items":
            [
                {
                    "id": "primary"
                }
            ]
        }

        # Using freebusy api for getting the list of busy time slots
        result = service.freebusy().query(body = free_busy_query).execute()
        busy_slots = result['calendars']['primary']['busy']
        busy_starts = list()
        busy_ends = list()

        # Getting free slots from the busy slots.
        for x in busy_slots:
            x_start = x['start']
            x_end = x['end']
            busy_starts.append(iso8601.parse_date(x_start))
            busy_ends.append(iso8601.parse_date(x_end))
        free_starts = list()
        free_ends = list()
        for i in range(len(busy_slots)):
            if iso_day_start>busy_starts[i]:
                free_starts.append(busy_ends[i])
            else:
                if free_starts:
                    free_ends.append(busy_starts[i])
                    free_starts.append(busy_ends[i])
                else:
                    free_starts.append(iso_day_start)
                    free_ends.append(busy_starts[i])
                    free_starts.append(busy_ends[i])
        if busy_ends[-1]<iso_day_end:
            free_ends.append(iso_day_end)
        else:
            free_ends.append(busy_starts[-1])
        
        free_intervals = list()
        for i in range(len(free_starts)):
            free_intervals.append(
                {
                    "start":rfc3339.rfc3339(free_starts[i])[11:-6],
                    "end":rfc3339.rfc3339(free_ends[i])[11:-6]
                }
            )
        msg = f'Existing meetings are scheduled:- {events_list}. The free slots available for the day are:- {free_intervals}'
        return msg
    
    # if there is not any existing event.
    else:
        # Requesting the google calendar api for adding event to the calendar.
        event_result = service.events().insert(calendarId='primary',
            body={
                "summary": event_name,
                "description": 'This is a tutorial example of automating google calendar with python',
                "start": {"dateTime": start, "timeZone": 'Asia/Kolkata'},
                "end": {"dateTime": end, "timeZone": 'Asia/Kolkata'},
            }
        ).execute()
        msg = f'Event \'{event_name}\' added!'
        print("created event")
        print("id: ", event_result['id'])
        print("summary: ", event_result['summary'])
        print("starts at: ", event_result['start']['dateTime'])
        print("ends at: ", event_result['end']['dateTime'])
        return msg

def get_event(date):
    '''
    Function that is able to get events for a specific date.
    '''
    service = get_calendar_service()

    # Converting the date into the required format.
    cal = parsedatetime.Calendar()
    timestruct, parsestatus = cal.parse(date)
    event_date = str(datetime(*timestruct[:6]).date())

    # Converting into rfc3339 format.
    day_start = f'{event_date}T{shift_start}'
    day_end = f'{event_date}T{shift_end}'

    # Fetching list of events from the calendar api.
    events = service.events().list(calendarId='primary', timeMin=day_start, timeMax=day_end, maxResults=10, singleEvents = True, orderBy='startTime').execute().get("items",[])
    event_items = list()
    for i, event in enumerate(events):
        event_items.append(
            {
                event['summary']: f'{event["start"]["dateTime"][11:-6]} : {event["end"]["dateTime"][11:-6]}'
            }
        )
    return f"Scheduled events are:- {event_items}"

def get_free_slots(date):
    '''
    Getting free slots for a specific date
    '''
    service = get_calendar_service()

    # Converting the date into the required format.
    cal = parsedatetime.Calendar()
    timestruct, parsestatus = cal.parse(date)
    event_date = str(datetime(*timestruct[:6]).date())

    # Converting into rfc3339 format.
    day_start = f'{event_date}T{shift_start}'
    day_end = f'{event_date}T{shift_end}'

    # Getting the datetime as a datetime object
    iso_day_start = iso8601.parse_date(f'{event_date}T{shift_start}')
    iso_day_end = iso8601.parse_date(f'{event_date}T{shift_end}')

    # Fetching list of events from the calendar api.
    events = service.events().list(calendarId='primary', timeMin=day_start, timeMax=day_end, maxResults=10, singleEvents = True, orderBy='startTime').execute().get("items",[])
    if events:
        events_list = list()
        for event in events:
            event_details = f'{event["summary"]}:- {event["start"]["dateTime"][11:-6]} to {event["end"]["dateTime"][11:-6]}'
            events_list.append(event_details)
        free_busy_query ={
            "timeMin": day_start,
            "timeMax": day_end,
            "timeZone": "Asia/Kolkata",
            "items":
            [
                {
                    "id": "primary"
                }
            ]
        }
        result = service.freebusy().query(body = free_busy_query).execute()
        busy_slots = result['calendars']['primary']['busy']
        busy_starts = list()
        busy_ends = list()
        for x in busy_slots:
            x_start = x['start']
            x_end = x['end']
            busy_starts.append(iso8601.parse_date(x_start))
            busy_ends.append(iso8601.parse_date(x_end))
        free_starts = list()
        free_ends = list()
        for i in range(len(busy_slots)):
            if iso_day_start>busy_starts[i]:
                free_starts.append(busy_ends[i])
            else:
                if free_starts:
                    free_ends.append(busy_starts[i])
                    free_starts.append(busy_ends[i])
                else:
                    free_starts.append(iso_day_start)
                    free_ends.append(busy_starts[i])
                    free_starts.append(busy_ends[i])
        if busy_ends[-1]<iso_day_end:
            free_ends.append(iso_day_end)
        else:
            free_ends.append(busy_starts[-1])
        
        free_intervals = list()
        for i in range(len(free_starts)):
            free_intervals.append(
                {
                    "start":rfc3339.rfc3339(free_starts[i])[11:-6],
                    "end":rfc3339.rfc3339(free_ends[i])[11:-6]
                }
            )
        print(free_intervals)
        msg = f'The free slots available for the day are:- {free_intervals}'
    else:
        msg = 'There is not any event scheduled for the day.'
    return msg

# def do_event():

#     service = get_calendar_service() 
#     now = datetime.utcnow().isoformat() + 'Z'
#     print(now)
#     events = service.events().list( calendarId='primary', timeMin=now,
#        maxResults=10, singleEvents=True,
#        orderBy='startTime').execute().get("items",[])

#     print(events[0]["end"])
#     return events[0]["end"]

# class ActionDoEvent(Action):

#     def name(self) -> Text:
#         return "action_do_event"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         event_name = do_event()

#         print(event_name)
#         #confirmed_event = tracker.get_slot(Any)
#         dispatcher.utter_message(text="got events {name}".format(name= event_name))
#         return [] 