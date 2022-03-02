# File:             toggljournal.py
# Description:      Script to create a daily Work Journal out of Toggl Track Time Entries.
# Author:           Apostolos Kritikos <akritiko@gmail.com>
# License:          MIT (human readable version: https://www.tldrlegal.com/l/mit)
# Code Repository:  https://github.com/akritiko/toggl-journal
# Console Command:  python toggljournal.py <TOGGL_API_KEY> <START_DATE> <END_DATE> <PROJECT_NAME>

import sys
import pdfkit
import pandas as pd
import logging
from datetime import date
from datetime import datetime
from toggl.TogglPy import Toggl

def convert_millies_to_time(millis):
    """ convert_millies_to_time: Function that converts milliseconds to time in Xh Ym format (i.e. 2h 15m). 
    Used to include duration of tasks to the report. """
    millis = int(millis)
    seconds=(millis/1000)%60
    seconds = int(seconds)
    minutes=(millis/(1000*60))%60
    minutes = int(minutes)
    hours=(millis/(1000*60*60))%24
    return ("%dh %dm" % (hours, minutes))

def filter_te_with_project(entries, project_name):
    """ Filters TEs by project name. """
    return entries[entries['project'] == project_name]

def hasN(entries):
    """ Checks if the TEs in a collection follow the notation of toggl-journal. If none of the collection's TEs 
    follow the right notation, then the collection is ignored entirely by the script. If even one TE follows
    the notation, the collection qualifies and the TEs that do not follow the notation will be excluded in the
    output formatting process (def format_output). """
    hasN = False
    for ind in entries.index:
        if entries['description'][ind].find('[N]') != -1:
            hasN = True
    return hasN

def format_output(entries, nofpages):
    """ Formats the output of the qualified TEs. """
    cur_date = ""
    journal_text = ""
    #Iterate through TEs pagination.
    for i in range(nofpages):
        # For every TE.
        for ind in entries.index:
            # check if the TE follows the notation and if not, ignore this specific TE.
            if entries['description'][ind].find('[N]') != -1:
                # ...get the date of the TE and check if it is a new date.
                temp_date = datetime.strptime(entries['start'][ind], '%Y-%m-%dT%H:%M:%S%z')
                # If this is a new date, then start a new date section in the report. 
                # NOTE: This check needs to be performed between strings always, otherwise it returns TRUE (since str <> datetime).
                if str(temp_date.strftime('%d %b %Y')) != cur_date:
                    journal_text = journal_text + "<h4><span style='background-color: #eee'>Date: " + temp_date.strftime('%d %b %Y') + "</span></h4>"
                    cur_date = str(temp_date.strftime('%d %b %Y'))
                # Else just append the note of the TE to the current date section.
                temp_description = entries['description'][ind].split('[N]')
                temp_title = temp_description[0]
                # Append the title of the note. It is stored before [N] in the Toggl TE.
                if entries['project'][ind] == "Personal Journal":
                    journal_text = journal_text + "<p><u>Entry</u>: <b>"+ temp_title + "</b></p>"
                else:
                    journal_text = journal_text + "<p><u>Action</u>: <b>"+ temp_title + "(" + convert_millies_to_time(str(entries['dur'][ind])) + ")" + "</b></p>"
                # Append the notes of the TE. They are stored after [N] and separated by '-' (each dash indicates a note).
                temp_notes = temp_description[1].split('-')
                journal_text = journal_text + "<ul style='list-style-type: circle;'>"
                for i in range(len(temp_notes)):
                    if i != 0:
                        journal_text = journal_text + "<li>" + temp_notes[i] + "</li>"
                journal_text = journal_text + "</ul>"
    return journal_text

def create_report_footer(journal_text):
    """ Create report's footer. """
    today = datetime.now()
    journal_text = journal_text + "<hr>" 
    journal_text = journal_text + "Report generated on: " + today.strftime('%d %b %Y, %H:%M:%S %z') + " by <a href='https://github.com/akritiko/toggl-journal' target='top'>toggl-journal</a>"
    journal_text = journal_text + "</body></html>"
    return journal_text

def exports(journal_text, fullname, project, since, until):
    """ Generate report in .html and .pdf formats. """
    filename = fullname + " - " + project + " - " + since + " - " + until + ".html"
    filename_no_ext = fullname + " - " + project + " - " + since + " - " + until
    Html_file= open(filename, "w", encoding='utf8')
    Html_file.write(journal_text)
    Html_file.close()
    pdfkit.from_file(filename, filename_no_ext + ".pdf")

def main(args):
    """ Main function. """
    logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO, format='%(asctime)s [ %(levelname)s ] %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    toggl_api_key = sys.argv[1] # User's Toggl API Key.
    since = sys.argv[2] # Report's Start Date (in YYYY-MM-DD format).
    since_date = datetime.strptime(since, '%Y-%m-%d')   
    until = sys.argv[3] # Report's End Date (in YYYY-MM-DD format).
    until_date = ""                                 
    if until != 'TODAY': # If 'TODAY' keyword is used: 
        until_date = datetime.strptime(until, '%Y-%m-%d')
    else: # Else if a date is provided:
        until = str(date.today())
        until_date = datetime.strptime(until, '%Y-%m-%d')
    project = sys.argv[4] # Project Name or ALL for all projects.

    toggl = Toggl()
    toggl.setAPIKey(toggl_api_key)

    response = toggl.request("https://api.track.toggl.com/api/v8/me")
    workspace_id = str(response['data']['default_wid']) # //TODO: extend functionality for multiple workspace accounts / paid feature.
    logging.info("Workspace_id infered from API")   
    fullname = str(response['data']['fullname'])
    logging.info("Fullanme infered from API") 

    response = toggl.request("https://api.track.toggl.com/reports/api/v2/details?workspace_id=" + workspace_id 
        + "&since=" + since 
        + "&until=" + until 
        + "&user_agent=" + toggl_api_key)
    df = pd.DataFrame(response['data'])
    total_te = len(df) # Store total TEs number and calculate pages (50 TEs per page - API limit -).
    nof_pages = round(total_te / 50)

    # Initialize journal string with Project, Author, Start & End report dates. We chose html format since it can easily be exported in .html and .pdf formats.
    # //XXX: The CSS styling is fused to the data due to time brevity :) In future extensions the styling of the report should be extracted from the code and transformed to templates!
    journal_text = "<html><head><meta charset=\"UTF-8\"></head><body>"
    journal_text = journal_text + "<h1>Toggl Journal Report for <span style='background-color: #eee'>" + project + "</span> by <span style='background-color: #eee'>" + fullname + "</span></h1>"
    journal_text = journal_text + "<h2> From: <span style='background-color: #eee'>" + since_date.strftime('%d %b %Y') + "</span> to <span style='background-color: #eee'>" + until_date.strftime('%d %b %Y') + "</span></h2>"
    journal_text = journal_text + "<hr>"
    
    if project != "ALL":
        newdf = filter_te_with_project(df, project)
        if hasN(newdf):
            journal_text = journal_text + "<h3 span style='text-align: center; background-color: #ddd;'><b>" + project + "</b></h3>"
            journal_text = journal_text + format_output(newdf, nof_pages)
            journal_text = create_report_footer(journal_text)
            exports(journal_text, fullname, project, since, until)
        else:
            logging.warning("Project *" + str(project) + "* either does not exists or does not have any Time Entries that follow the toggl-journal notation.") 
    else:
        projects = pd.unique(df['project'])
        valid_report = False # Flag to create the report if at least one project qualifies re notation.        
        for p in projects:
            newdf = filter_te_with_project(df, p)
            if hasN(newdf): #  Check if it qualifies re notation.
                valid_report = True
                journal_text = journal_text + "<h3 span style='text-align: center; background-color: #ddd;'><b>Project: "+ str(p) + "</b></h3>"
                journal_text = journal_text + format_output(newdf, nof_pages)
            else:
                logging.warning("Project *" + str(p) + "* either does not exists or does not have any Time Entries that follow the toggl-journal notation.") 
        if valid_report: # Since we got many possible projects that qualify we need only one footer in the end of the documents.
            journal_text = create_report_footer(journal_text)
            exports(journal_text, fullname, project, since, until)

if __name__ == "__main__":
    main(sys.argv[1:])