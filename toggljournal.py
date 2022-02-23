"""
Title:              toggl-journal
Description:        Script to create a Work Journal out of the Toggl Entries for a specific 
                    Toggl Project.
Author:             Apostolos Kritikos <akritiko@gmail.com>
License:            MIT (You can find a human friendly version of the license here: https://www.tldrlegal.com/l/mit)
Available at:       https://github.com/akritiko/toggl-journal
Console Command:    python toggljournal.py <TOGGL_API_KEY> <START_DATE> <END_DATE> <PROJECT_NAME> <AUTHORS_FULL_NAME>
"""

import sys
import pdfkit
from datetime import datetime
from toggl.TogglPy import Toggl

# Initialize parameters
toggl_api_key = sys.argv[1]                         # A valid Toggl API Key
since = sys.argv[2]                                 # Report Start Date (in YYYY-MM-DD format)
since_date = datetime.strptime(since, '%Y-%m-%d')   
until = sys.argv[3]                                 # Report End Date (in YYYY-MM-DD format)
until_date = datetime.strptime(until, '%Y-%m-%d')
project = sys.argv[4]                               # Project Name

# Initialize TogglePy instance & set API Key 
toggl = Toggl()
toggl.setAPIKey(toggl_api_key)

# Infer default workspace from user [//TODO: extend functionality for multiple workspace accounts / paid feature]
response = toggl.request("https://api.track.toggl.com/api/v8/me")
workspace_id = str(response['data']['default_wid'])
fullname = str(response['data']['fullname'])

# HTTP Request Time Entries (TEs)
response = toggl.request("https://api.track.toggl.com/reports/api/v2/details?workspace_id=" + workspace_id + "&since=" + since + "&until=" + until + "&user_agent=" + toggl_api_key)
# Isolate TEs data
time_entries = response['data']
# Store total TEs number (used for possible pagination of results)
total_te = len(time_entries)
# Calculate pages (50 TEs per page - API limit -)
nof_pages = round(total_te / 50)

# Initialize journal string with Project, Author, Start & End report dates. We chose html format since it can easily be exported in .html and .pdf formats.
# //XXX: The CSS styling is fused to the data due to time brevity :) In future extensions the styling of the report should be extracted from the code and transformed to templates!
journal_text = "<h1>Toggl Journal Report for <span style='background-color: #eee'>" + project + "</span> by <span style='background-color: #eee'>" + fullname + "</span></h1>"
journal_text = journal_text + "<h2> From: <span style='background-color: #eee'>" + since_date.strftime('%d %b %Y') + "</span> to <span style='background-color: #eee'>" + until_date.strftime('%d %b %Y') + "</span></h2>"
journal_text = journal_text + "<hr>"

# Initialize cur_date
cur_date = ""

#Iterate through TEs pagination
for i in range(nof_pages):
    # For every TE
    for te in time_entries:
        # Check if TE belongs to the target project...
        if project != "ALL" and te["project"] == project:
            # ...get the date of the TE and check if it is a new date
            temp_date = datetime.strptime(te['start'], '%Y-%m-%dT%H:%M:%S%z')
            # If this is a new date, then start a new date section in the report. 
            # NOTE: This check needs to be performed between strings always, otherwise it returns TRUE (since str <> datetime).
            if str(temp_date.strftime('%d %b %Y')) != cur_date:
                journal_text = journal_text + "<h3><span style='background-color: #eee'>Date: " + temp_date.strftime('%d %b %Y') + "</span></h3>"
                cur_date = str(temp_date.strftime('%d %b %Y'))
            # Else just append the note of the TE to the current date section
            temp_description = te['description'].split('[N]')
            temp_title = temp_description[0]
            # Append the title of the note. It is stored before [N] in the Toggl TE
            journal_text = journal_text + "<p><u>Action</u>: <b>"+ temp_title + "</b></p>"
            # Append the notes of the TE. They are stored after [N] and separated by '-' (each dash indicates a note)
            temp_notes = temp_description[1].split('-')
            journal_text = journal_text + "<ul style='list-style-type: circle;'>"
            for i in range(len(temp_notes)):
                if i != 0:
                    journal_text = journal_text + "<li>" + temp_notes[i] + "</li>"
            journal_text = journal_text + "</ul>"
        else:
            if te['description'].find('[N]') != -1:
                # ...get the date of the TE and check if it is a new date
                temp_date = datetime.strptime(te['start'], '%Y-%m-%dT%H:%M:%S%z')
                # If this is a new date, then start a new date section in the report. 
                # NOTE: This check needs to be performed between strings always, otherwise it returns TRUE (since str <> datetime).
                if str(temp_date.strftime('%d %b %Y')) != cur_date:
                    journal_text = journal_text + "<h3><span style='background-color: #eee'>Date: " + temp_date.strftime('%d %b %Y') + "</span></h3>"
                    cur_date = str(temp_date.strftime('%d %b %Y'))
                # Else just append the note of the TE to the current date section
                temp_description = te['description'].split('[N]')
                temp_title = temp_description[0]
                # Append the title of the note. It is stored before [N] in the Toggl TE
                journal_text = journal_text + "<p><u>Project</u>: <b>" + te["project"] + "</b> <u>Action</u>: <b>"+ temp_title + "</b></p>"
                # Append the notes of the TE. They are stored after [N] and separated by '-' (each dash indicates a note)
                temp_notes = temp_description[1].split('-')
                journal_text = journal_text + "<ul style='list-style-type: circle;'>"
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
filename_no_ext = fullname + " - " + project + " - " + since + " - " + until
Html_file= open(filename,"w")
Html_file.write(journal_text)
Html_file.close()


pdfkit.from_file(filename, filename+".pdf")
