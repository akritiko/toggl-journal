"""
Title:              toggl-journal
Description:        Script to create a Work Journal out of the Toggl Entries for a specific 
                    Toggl Project.
Author:             Apostolos Kritikos <akritiko@gmail.com>
License:            MIT (You can find a human friendly version of the license here: https://www.tldrlegal.com/l/mit)
Available at:       https://github.com/akritiko/toggl-journal
Console Command:    python toggljournal.py <TOGGL_API_KEY> <START_DATE> <END_DATE> <PROJECT_NAME>
"""

""" Import Libraries """

import sys
import pdfkit
import pandas as pd
from datetime import datetime
from toggl.TogglPy import Toggl

""" Define functions """

# Filters the TEs by project name
def filter_te_with_project(entries, project_name):
    return entries[entries['project'] == project_name]

# Checks if the TEs in a collection follow the notation of toggl-journal. If none of the collection's TEs 
# follow the right notation, then the collection is ignored entirely by the script. If even one TE follows
# the notation, the collection qualifies and the TEs that do not follow the notation will be excluded in the
# output formatting process (def format_output).
def hasN(entries):
    hasN = False
    for ind in entries.index:
        if entries['description'][ind].find('[N]') != -1:
            hasN = True
    return hasN

# Formats the output of the qualified TEs.
def format_output(entries, nofpages):
    cur_date = ""
    journal_text = ""
    #Iterate through TEs pagination
    for i in range(nofpages):
        # For every TE
        for ind in entries.index:
            # check if the TE follows the notation and if not, ignore this specific TE
            if entries['description'][ind].find('[N]') != -1:
                # ...get the date of the TE and check if it is a new date
                temp_date = datetime.strptime(entries['start'][ind], '%Y-%m-%dT%H:%M:%S%z')
                # If this is a new date, then start a new date section in the report. 
                # NOTE: This check needs to be performed between strings always, otherwise it returns TRUE (since str <> datetime).
                if str(temp_date.strftime('%d %b %Y')) != cur_date:
                    journal_text = journal_text + "<h4><span style='background-color: #eee'>Date: " + temp_date.strftime('%d %b %Y') + "</span></h4>"
                    cur_date = str(temp_date.strftime('%d %b %Y'))
                # Else just append the note of the TE to the current date section
                temp_description = entries['description'][ind].split('[N]')
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
    return journal_text

# Create report's footer
def create_report_footer(journal_text):
    today = datetime.now()
    journal_text = journal_text + "<hr>" 
    journal_text = journal_text + "Report generated on: " + today.strftime('%d %b %Y, %H:%M:%S %z') + " by <a href='https://github.com/akritiko/toggl-journal' target='top'>toggl-journal</a>"
    return journal_text

def exports(journal_text):
    # Generate report in .html format
    filename = fullname + " - " + project + " - " + since + " - " + until + ".html"
    filename_no_ext = fullname + " - " + project + " - " + since + " - " + until
    Html_file= open(filename,"w")
    Html_file.write(journal_text)
    Html_file.close()
    # Generate report in .pdf format
    pdfkit.from_file(filename, filename_no_ext + ".pdf")

""" MAIN SCRIPT """

# Initialize parameters
toggl_api_key = sys.argv[1]                         # A valid Toggl API Key
since = sys.argv[2]                                 # Report Start Date (in YYYY-MM-DD format)
since_date = datetime.strptime(since, '%Y-%m-%d')   
until = sys.argv[3]                                 # Report End Date (in YYYY-MM-DD format)
until_date = datetime.strptime(until, '%Y-%m-%d')
project = sys.argv[4]                               # Project Name or ALL for all projects

# Initialize TogglePy instance & set API Key 
toggl = Toggl()
toggl.setAPIKey(toggl_api_key)

# Infer default workspace from user [//TODO: extend functionality for multiple workspace accounts / paid feature]
response = toggl.request("https://api.track.toggl.com/api/v8/me")
workspace_id = str(response['data']['default_wid'])
fullname = str(response['data']['fullname'])

# HTTP Request Time Entries (TEs)
response = toggl.request("https://api.track.toggl.com/reports/api/v2/details?workspace_id=" + workspace_id + "&since=" + since + "&until=" + until + "&user_agent=" + toggl_api_key)
# Isolate TEs data and create a dataframe
df = pd.DataFrame(response['data'])
# Store total TEs number (used for possible pagination of results)
total_te = len(df)
# Calculate pages (50 TEs per page - API limit -)
nof_pages = round(total_te / 50)

# Initialize journal string with Project, Author, Start & End report dates. We chose html format since it can easily be exported in .html and .pdf formats.
# //XXX: The CSS styling is fused to the data due to time brevity :) In future extensions the styling of the report should be extracted from the code and transformed to templates!
journal_text = "<h1>Toggl Journal Report for <span style='background-color: #eee'>" + project + "</span> by <span style='background-color: #eee'>" + fullname + "</span></h1>"
journal_text = journal_text + "<h2> From: <span style='background-color: #eee'>" + since_date.strftime('%d %b %Y') + "</span> to <span style='background-color: #eee'>" + until_date.strftime('%d %b %Y') + "</span></h2>"
journal_text = journal_text + "<hr>"

# Get the right TEs
if project != "ALL":
    # For the selected project
    newdf = filter_te_with_project(df, project)
    # Check if TEs qualify re notation
    if hasN(newdf):
        # Create reports
        journal_text = journal_text + "<h3 span style='text-align: center; background-color: #ddd;'><b>Project: " + project + "</b></h3>"
        journal_text = journal_text + format_output(newdf, nof_pages)
        journal_text = create_report_footer(journal_text)
        exports(journal_text)
    else:
        # Print error
        print("ERROR: This project either does not exists or does not have any Time Entries that follow the toggl-journal notation.")
else:
    # For all projects between the selected dates (since - until)
    projects = pd.unique(df['project'])
    # Flag to create the report if at least one project qualifies re notation
    valid_report = False
    # For every project
    for p in projects:
        # Filter TEs of this project
        newdf = filter_te_with_project(df, p)
        #  Check if it qualifies re notation
        if hasN(newdf):
            # Set valid project to True
            valid_report = True
            # Create reports
            journal_text = journal_text + "<h3 span style='text-align: center; background-color: #ddd;'><b>Project: "+ str(p) + "</b></h3>"
            journal_text = journal_text + format_output(newdf, nof_pages)
        else:
            # Print error
            print("ERROR: This project either does not exists or does not have any Time Entries that follow the toggl-journal notation.")
    # Since we got many possible projects that qualify
    if valid_report:
        # We need only one footer in the end of the documents
        journal_text = create_report_footer(journal_text)
        exports(journal_text)
