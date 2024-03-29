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
