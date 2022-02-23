"""
Title:              toggl-journal
Description:        Script to create a Work Journal out of the Toggl Entries for a specific 
                    project. Sample script created for the Toggl Test Week to test the API
                    and provide an easy way to report after the end of it :)
Author:             Apostolos Kritikos
License:            MIT
Available at:       https://github.com/akritiko/toggl-journal
Console Command:    python toggljournal.py <TOGGL_API_KEY> <START_DATE> <END_DATE> <PROJECT_NAME> <AUTHORS_FULL_NAME>
"""

import sys
from datetime import datetime
from toggl.TogglPy import Toggl

# Your Toggl API Key
toggl_api_key = sys.argv[1] 
# The start date of the period you want a report
since = sys.argv[2] 
since_date = datetime.strptime(since, '%Y-%m-%d')
# The end date of the period you want a report
until = sys.argv[3] 
until_date = datetime.strptime(until, '%Y-%m-%d')
# The workspace_id for the project of which you would like to produce a Toggle work journal
workspace_id = sys.argv[4] 
# The project name for which you would like to produce a Toggl work journal
project = sys.argv[5] 
# User's full name
fullname = sys.argv[6] 

toggl = Toggl()
toggl.setAPIKey(toggl_api_key)

response = toggl.request("https://api.track.toggl.com/reports/api/v2/details?workspace_id=" + workspace_id + "&since=" + since + "&until=" + until + "&user_agent=" + toggl_api_key)
time_entries = response['data']
total_te = len(time_entries)
total_pages = round(total_te / 50)

# Journal initialization / format: HTML
journal_text = "<h1>Toggl Journal Report for <span style='background-color: #eee'>" + project + "</span> by <span style='background-color: #eee'>" + fullname + "</span></h1>"
journal_text = journal_text + "<h2> From: <span style='background-color: #eee'>" + since_date.strftime('%d %b %Y') + "</span> to <span style='background-color: #eee'>" + until_date.strftime('%d %b %Y') + "</span></h2>"
journal_text = journal_text + "<hr>"

for te in time_entries:
    cur_date = ""
    if te["project"] == project:
        # Get the date of the te and check if it is a new date
        temp_date = datetime.strptime(te['start'], '%Y-%m-%dT%H:%M:%S%z')
        if temp_date != cur_date:
            journal_text = journal_text + "<h3> <span style='background-color: #eee'>Day: " + temp_date.strftime('%d %b %Y') + "</span></h3>"
            cur_date = temp_date
        temp_description = te['description'].split('[N]')
        temp_title = temp_description[0]
        journal_text = journal_text + "<p><b> Action: " + temp_title + "</b></p>"
        journal_text = journal_text + "<p>Notes: </p>"
        temp_notes = temp_description[1].split('-')
        journal_text = journal_text + "<ul>"
        for i in range(len(temp_notes)):
            if i != 0:
                journal_text = journal_text + "<li>" + temp_notes[i] + "</li>"
        journal_text = journal_text + "</ul>"

# Get report's timestamp
today = datetime.now()
journal_text = journal_text + "<hr>" 
journal_text = journal_text + "Report generated on: " + today.strftime('%d %b %Y, %H:%M:%S %z') + " by <a href='https://github.com/akritiko/toggl-journal' target='top'>toggl-journal</a>"

# Generate report in .html format
filename = fullname + " - " + project + " - " + since + " - " + until + ".html"
Html_file= open(filename,"w")
Html_file.write(journal_text)
Html_file.close()
