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

# Console & Other parameters
toggl_api_key = sys.argv[1]                         # A valid Toggl API Key
since = sys.argv[2]                                 # Report Start Date (in YYYY-MM-DD format)
since_date = datetime.strptime(since, '%Y-%m-%d')   
until = sys.argv[3]                                 # Report End Date (in YYYY-MM-DD format)
until_date = datetime.strptime(until, '%Y-%m-%d')
workspace_id = sys.argv[4]                          # Workspace ID //TODO: Make it work with Workspace Name
project = sys.argv[5]                               # Project Name
fullname = sys.argv[6]                              # Author's Full Name

# Wrapper init & set API Key 
toggl = Toggl()
toggl.setAPIKey(toggl_api_key)

# HTTP Request for Time Entries (TEs)
response = toggl.request("https://api.track.toggl.com/reports/api/v2/details?workspace_id=" + workspace_id + "&since=" + since + "&until=" + until + "&user_agent=" + toggl_api_key)
# Isolate Time Entry data
time_entries = response['data']
# Store total TEs number
total_te = len(time_entries)
# Calculate pages (50 TEs per page - API limit -)
total_pages = round(total_te / 50)

# Journal initialization w/ Project, Author, Start & End report dates.
journal_text = "<h1>Toggl Journal Report for <span style='background-color: #eee'>" + project + "</span> by <span style='background-color: #eee'>" + fullname + "</span></h1>"
journal_text = journal_text + "<h2> From: <span style='background-color: #eee'>" + since_date.strftime('%d %b %Y') + "</span> to <span style='background-color: #eee'>" + until_date.strftime('%d %b %Y') + "</span></h2>"
journal_text = journal_text + "<hr>"

# Iterate through TEs
for te in time_entries:
    # Initialize cur_date
    cur_date = ""
    # Check if TE belongs to the target project
    if te["project"] == project:
        # Get the date of the TE and check if it is a new date
        temp_date = datetime.strptime(te['start'], '%Y-%m-%dT%H:%M:%S%z')
        # If this is a new date, then start a new date section in the report
        if temp_date != cur_date:
            journal_text = journal_text + "<h3> <span style='background-color: #eee'>Day: " + temp_date.strftime('%d %b %Y') + "</span></h3>"
            cur_date = temp_date
        # else just append the note of the TE to the current date section
        temp_description = te['description'].split('[N]')
        temp_title = temp_description[0]
        # this is the title of the note identified by [N] in the Toggl TE
        journal_text = journal_text + "<p><b> Action: " + temp_title + "</b></p>"
        journal_text = journal_text + "<p>Notes: </p>"
        # these are the notes of the TE identified by '-' (each dash indicates a note)
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
