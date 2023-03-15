# File:             toggljournal.py
# Description:      Script to create a daily Work Journal out of Toggl Track Time Entries.
# Author:           Apostolos Kritikos <akritiko@gmail.com>
# License:          MIT (human readable version: https://www.tldrlegal.com/l/mit)
# Code Repository:  https://github.com/akritiko/toggl-journal
# Console Command:  python toggljournal.py <TOGGL_API_KEY> <START_DATE> <END_DATE> <PROJECT_NAME> <PERSONAL_JOURNAL*>
#                   * <PERSONAL_JOURNAL> is not a mandatory parameter and can be ommitted.

import logging
import sys
from datetime import date
from datetime import datetime

import pandas as pd
import pdfkit
from toggl.TogglPy import Toggl

import constants


def convert_millies_to_time(millis):
    """ convert_millies_to_time: Function that converts milliseconds to time in Xh Ym format (i.e. 2h 15m). 
    Used to include duration of tasks to the report. """
    millis = int(millis)
    seconds = (millis / 1000) % 60
    int(seconds)
    minutes = (millis / (1000 * 60)) % 60
    minutes = int(minutes)
    hours = (millis / (1000 * 60 * 60)) % 24
    return "%dh %dm" % (hours, minutes)


def filter_te_with_project(entries, project_name):
    """ Filters TEs by project name. """
    return entries[entries['project'] == project_name]


def contains_notes_delimiter(entries):
    """ Checks if the TEs in a collection follow the notation of toggl-journal. If none of the collection's TEs 
    follow the right notation, then the function will return FALSE. If even one TE follows the notation, the collection 
    qualifies and the script returns TRUE. NOTE: The TEs that do not follow the notation will be excluded in the
    output formatting process (def format_output). """
    hasn = False
    for ind in entries.index:
        if entries['description'][ind].find(constants.NOTES_DEL) != -1:
            hasn = True
    return hasn


def export_tags(entries):
    entries_text = ""
    for entry in entries:
        entries_text = entries_text + str(entry) + " &#8226; "
    return entries_text


def format_output(entries, nofpages):
    """ Formats the output of the qualified TEs. """
    cur_date = ""
    journal_text = ""
    # Iterate through TEs pagination.
    for i in range(nofpages):
        # For every TE.
        for ind in entries.index:
            # check if the TE follows the notation and if not, ignore this specific TE.
            if entries['description'][ind].find(constants.NOTES_DEL) != -1:
                # ...get the date of the TE and check if it is a new date.
                temp_date = datetime.strptime(entries['start'][ind], '%Y-%m-%dT%H:%M:%S%z')
                # If this is a new date, then start a new date section in the report. NOTE: This check needs to be
                # performed between strings always, otherwise it returns TRUE (since str <> datetime).
                if str(temp_date.strftime('%d %b %Y')) != cur_date:
                    journal_text = journal_text + "<h4><span style='background-color: " + constants.H4BGCOLOR + "'>Date: " + temp_date.strftime(
                        '%d %b %Y') + "</span></h4>"
                    cur_date = str(temp_date.strftime('%d %b %Y'))
                # Else just append the note of the TE to the current date section.
                temp_description = entries['description'][ind].split(constants.NOTES_DEL)
                temp_title = temp_description[0]
                # Append the title of the note. It is stored before constants.NOTES_DEL in the Toggl TE.
                if entries['project'][ind] == "Personal Journal":
                    journal_text = journal_text + "<p><u>Entry</u>: <b>" + temp_title + "</b> <br> Tags: " + export_tags(
                        entries['tags'][ind]) + "</p>"
                else:
                    journal_text = journal_text + "<p>Action: <b>" + temp_title + "</b> Duration: <b>" + convert_millies_to_time(
                        str(entries['dur'][ind])) + "</b> <br>Tags: " + export_tags(entries['tags'][ind]) + "</p>"
                # Append the notes of the TE. They are stored after constants.NOTES_DEL and separated by '-' (each dash indicates a
                # note).
                temp_notes = temp_description[1].split('-')
                journal_text = journal_text + "<ul style='list-style-type: circle;'>"
                for i in range(len(temp_notes)):
                    if i != 0:
                        journal_text = journal_text + "<li>" + temp_notes[i] + "</li>"
                journal_text = journal_text + "</ul>"
    return journal_text


def create_report_header(fullname, project, since, until, personal_journal):
    """ Initialize journal string with Project, Author, Start & End report dates. We chose html format since it can
    easily be exported in .html and .pdf formats. //XXX: The CSS styling is fused to the data due to time brevity :)
    In future extensions the styling of the report should be extracted from the code and transformed to templates! """
    journal_text = "<html><head><meta charset=\"UTF-8\"></head><body>"
    if project != personal_journal:
        if project != "ALL":
            journal_text = journal_text + "<h1>Toggl Journal for project <span style='background-color: " + constants.H1BGCOLOR + "'>" + project + "</span> <br>by <span style='background-color: " + constants.H1BGCOLOR + "'>" + fullname + "</span> from: <span style='background-color: " + constants.H1BGCOLOR + "'>" + since + "</span> to <span style='background-color: " + constants.H1BGCOLOR + "'>" + until + "</span></h1>"
        else:
            journal_text = journal_text + "<h1>Toggl Journal for <span style='background-color: " + constants.H1BGCOLOR + "'>" + project + "</span> projects <br>by <span style='background-color: " + constants.H1BGCOLOR + "'>" + fullname + "</span> from: <span style='background-color: " + constants.H1BGCOLOR + "'>" + since + "</span> to <span style='background-color: " + constants.H1BGCOLOR + "'>" + until + "</span></h1>"
        journal_text = journal_text + "<hr>"
        journal_text = journal_text + "<h2 style='text-align: center; background-color: " + constants.H2BGCOLOR + "'> PROJECTS </h2>"
    else:
        journal_text = journal_text + "<h1>Toggl <span style='background-color: " + constants.H1BGCOLOR + "'> Personal Journal</span> by <span style='background-color: " + constants.H1BGCOLOR + "'>" + fullname + "</span> <br>from: <span style='background-color: " + constants.H1BGCOLOR + "'>" + since + "</span> to <span style='background-color: " + constants.H1BGCOLOR + "'>" + until + "</span></h1>"
    return journal_text


def create_report_footer(journal_text):
    """ Create report's footer. """
    today = datetime.now()
    journal_text = journal_text + "<hr>"
    journal_text = journal_text + "Report generated on: " + today.strftime(
        '%d %b %Y, %H:%M:%S %z') + " by <a href='https://github.com/akritiko/toggl-journal' target='top'>toggl-journal</a>"
    journal_text = journal_text + "</body></html>"
    return journal_text


def exports(journal_text, fullname, project, since, until):
    """ Generate report in .html and .pdf formats. """
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
    }
    filename = fullname + " - " + project + " - " + since + " - " + until + ".html"
    filename_no_ext = fullname + " - " + project + " - " + since + " - " + until
    Html_file = open(filename, "w", encoding='utf8')
    Html_file.write(journal_text)
    Html_file.close()
    pdfkit.from_file(filename, filename_no_ext + ".pdf", options=options)


def create_project_entry(journal_text, newdf, nof_pages, project):
    journal_text = journal_text + "<h3 style='text-align: center; background-color: " + constants.H3BGCOLOR + ";'><b>Project: " + str(
        project) + "</b></h3>"
    journal_text = journal_text + format_output(newdf, nof_pages)
    return journal_text


def create_journal_entry(journal_text, newdf, nof_pages):
    journal_text = journal_text + "<h2 style='text-align: center; background-color: " + constants.H2BGCOLOR + ";'><b>PERSONAL JOURNAL</b></h2>"
    journal_text = journal_text + format_output(newdf, nof_pages)
    return journal_text


def main(args):
    """ Main function. """
    global since, until
    logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO,
                        format='%(asctime)s [ %(levelname)s ] %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    toggl_api_key = ""
    since_date = ""
    until_date = ""
    project = ""
    personal_journal = ""
    journal_text = ""

    if args and len(args) >= 4:
        toggl_api_key = sys.argv[1]  # User's Toggl API Key.
        since = sys.argv[2]  # Report's Start Date (in YYYY-MM-DD format).
        since_date = datetime.strptime(since, '%Y-%m-%d')
        until = sys.argv[3]  # Report's End Date (in YYYY-MM-DD format).
        until_date = ""
        if until != 'TODAY':  # If 'TODAY' keyword is used:
            until_date = datetime.strptime(until, '%Y-%m-%d')
        else:  # Else if a date is provided:
            until = str(date.today())
            until_date = datetime.strptime(until, '%Y-%m-%d')
        project = sys.argv[4]  # Project Name or ALL for all projects.
        if len(args) > 4:
            personal_journal = sys.argv[5]
        else:
            personal_journal = "-999"
    else:
        logging.error(
            "Invalid command. Please call the script again using the command: <TOGGL_API_KEY> <START_DATE> <END_DATE> <PROJECT_NAME> <PERSONAL_JOURNAL>")
        print(
            "[error] Invalid command. Please call the script again using the command: <TOGGL_API_KEY> <START_DATE> <END_DATE> <PROJECT_NAME> <PERSONAL_JOURNAL>. Program will exit!")
        exit()

    toggl = Toggl()
    toggl.setAPIKey(toggl_api_key)

    response = toggl.request("https://api.track.toggl.com/api/v8/me")
    workspace_id = str(
        response['data']['default_wid'])  # //TODO: extend functionality for multiple workspace accounts / paid feature.
    logging.info("Workspace_id inferred from API")
    fullname = str(response['data']['fullname'])
    logging.info("Fullanme inferred from API")

    response = toggl.request("https://api.track.toggl.com/reports/api/v2/details?workspace_id=" + workspace_id
                             + "&since=" + since
                             + "&until=" + until
                             + "&user_agent=" + toggl_api_key)
    df = pd.DataFrame(response['data'])
    total_te = len(df)  # Store total TEs number and calculate pages (50 TEs per page - API limit -).
    nof_pages = round(total_te / 50)
    if (nof_pages == 0):
        nof_pages = 1

    journal_text = journal_text + create_report_header(fullname, project, since, until, personal_journal)

    if project != "ALL":
        newdf = filter_te_with_project(df, project)
        if contains_notes_delimiter(newdf):
            if project == personal_journal:
                journal_text = create_journal_entry(journal_text, newdf, nof_pages)
            else:
                journal_text = create_project_entry(journal_text, newdf, nof_pages, project)
            journal_text = create_report_footer(journal_text)
            exports(journal_text, fullname, project, since, until)
        else:
            logging.warning("Project *" + str(
                project) + "* either does not exists or does not have any Time Entries that follow the toggl-journal notation.")
    else:
        projects = pd.unique(df['project'])
        valid_report = False  # Flag to create the report if at least one project qualifies re notation.
        for p in projects:
            newdf = filter_te_with_project(df, p)
            if contains_notes_delimiter(newdf) and p != personal_journal:  # Check if it qualifies re notation.
                valid_report = True
                journal_text = create_project_entry(journal_text, newdf, nof_pages, p)
            else:
                logging.warning("Project *" + str(
                    p) + "* either does not exists or does not have any Time Entries that follow the toggl-journal notation.")
        newdf = filter_te_with_project(df, personal_journal)
        if contains_notes_delimiter(newdf):  # Check if it qualifies re notation.
            valid_report = True
            if personal_journal != "-999":
                journal_text = create_journal_entry(journal_text, newdf, nof_pages)
            else:
                logging.info("No personal journal found!")
        if valid_report:  # Since we got many possible projects that qualify we need only one footer in the end of the documents.
            journal_text = create_report_footer(journal_text)
            exports(journal_text, fullname, project, since, until)


if __name__ == "__main__":
    main(sys.argv[1:])
