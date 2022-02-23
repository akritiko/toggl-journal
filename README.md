# toggl-journal

toggl-journal is a python script that can easily create human readable reports by automatically synthesizing time entry descriptions with a very simple notation. 

The user can filter the report by project and time window (since date - until date). The report is being exported in .html and .pdf format in order to be easily shareable (copy-paste) via an e-mail or slack and / or attached as a file. 

This is a proof of concept project that I started in order to get familiar with the Toggl API and, at the same time, automate my every-day work journal through Toggl.

## Features

- Automatically creates reports from Toggl Time Entries based on project and time windows (since - until dates).
- Generates report in .html format.
- Generates report in .pdf format.
- Handles pagination for high time entry volume, respecting the API limitations. 

__NOTES:__

- For the time being it works only for a single workspace / the default workspace of the user. 

## Install Dependencies

In order for the script to run you need to install the following dependencies:

__TogglPy__

```bash
pip install -U TogglPy
```
[more information here](https://pypi.org/project/TogglPy/)

__PDFKit__

```bash
pip install pdfkit
```

__WkHtmlToPdf__

```bash
sudo apt-get install wkhtmltopdf
```
[more information + widnows setup here](https://www.geeksforgeeks.org/python-convert-html-pdf/)


## Run the script

```python
python toggljournal.py python toggljournal.py <TOGGL_API_KEY> <START_DATE> <END_DATE> <PROJECT_NAME>
```

- <TOGGL_API_KEY> (string): The unique user's API Key. You can find it by following [this official guide](https://support.toggl.com/en/articles/3116844-where-is-my-api-key-located).

- <START_DATE> (string): The start date in YYYY-MM-DD format (i.e. 2022-02-22).

- <END_DATE> (string): The end date in YYYY-MM-DD format (i.e. 2022-02-22).

- <PROJECT_NAME> (string): The project name for which we want to create a report.

# Annotation in the Toggl Environment

It is really simple! Everytime we make a new Toggl Entry we are following the following annotation in our description:

<ACTION_TITLE> [N] - <NOTE #1> - <NOTE #2> - <NOTE #3> ...

for example:

Meeting w/ John [N] - Refactor library X - We need another awesome Senior Dev

![screenshot](/images/screenshot_1.png)