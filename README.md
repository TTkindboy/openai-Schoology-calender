# Schoology Workload Manager
## Overview
Schoology Workload Manager is a tool designed to help students efficiently manage their academic workload by integrating with their Schoology calendar. It retrieves calendar data, organizes tasks, and provides personalized workload management.
## Code
```py
from flask import Flask, request, Response
import requests
from icalendar import Calendar, Event
from datetime import datetime
import pytz

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download_file():
    # Get the URL from the query string
    url = request.args.get('url')
    if not url:
        return Response("No URL provided", status=400)
    if "webcal://" in url:
        url = url.replace("webcal://", "https://")
    # Send a request
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return Response(str(e), status=500)
    # Parse the calender file
    calendar = Calendar.from_ical(response.content)
    # Filter events
    current_time = datetime.now(pytz.utc)
    filtered_calendar = Calendar()
    for component in calendar.walk():
        if component.name == "VEVENT":
            dtstart = component.get('dtstart').dt
            if dtstart.tzinfo is None or dtstart.tzinfo.utcoffset(dtstart) is None:
                dtstart = pytz.utc.localize(dtstart)
            if dtstart > current_time:
                filtered_calendar.add_component(component)

    if len(filtered_calendar.walk()) == 1: 
        return Response("No future events found", status=404)
    headers = {
        'Content-Disposition': 'inline; filename="filtered_calendar.ics"',
        'Content-Type': 'text/calendar'
    }
    return Response(filtered_calendar.to_ical(), headers=headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```
## Request
```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "Get Calendar",
    "description": "Retrieves Calendar data.",
    "version": "v1.0.0"
  },
  "servers": [
    {
      "url": "https://api-ttkindboi.replit.app/"
    }
  ],
  "paths": {
    "/download": {
      "get": {
        "description": "Get calendar data from a file url",
        "operationId": "GetCalendar",
        "parameters": [
          {
            "name": "url",
            "in": "query",
            "description": "The user's calendar url.",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "deprecated": false
      }
    }
  },
  "components": {
    "schemas": {}
  }
}
```
## Prompt
```
You are Schoology Organizer an AI whose purpose is to explain what homework needs to be done. 
The user will provide you with a link to their calendar You will download it using the function GetCalendar. After downloading the calendar file you will look at it using a python program.
After looking at it you will provide the user with an overview of the work they need to do tonight, make sure to also tell the user what they have to work ahead on for the rest of the week.
All of the timestamps in the calendar are the due date of the assignment rather than the time to do it.
If the user is unsure of how to get their Schoology calendar url give them this link for the instructions: https://scribehow.com/shared/Find_Schoology_calendar_url__-3h0QcI8Q9GuWafSIi-0aQ
```
