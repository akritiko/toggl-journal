# toggl-journal

toggl-journal is a python script that can easily create human readable journals by automatically synthesizing Toggl Track time entries using a very simple notation. 

The user can filter the report by project and by a time window (since date - until date). The report is being exported in .html and .pdf formats in order to be easily shareable (copy-paste) via an e-mail or slack or be attached / send as a file. 

This is a proof of concept project tarted in order for me to get familiar with the Toggl API and, at the same time, automate my every-day professional (and personal) journalling process with the use of Toggl Track.

## Features

- Automatically creates reports from Toggl Time Entries based on project and time windows (since - until dates).
- If the user puts 'ALL' instead of a project name, the script generates a report for all projects within the since - until timeframe.
- If the user define the name of the project as PERSONAL_JOURNAL in input, then a special JOURNAL section is created to the report using the time entries of this project.
- Generates report in .html format.
- Generates report in .pdf format.
- Handles pagination for time entries > 50, respecting the API limitations. 
- Handles UTF-8 special characters (i.e. Greek / Cyrillic alphabet).

__NOTES:__

- For the time being it works only for a single workspace / the default workspace of the user. 

## Dependencies

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

Ubuntu setup:

```bash
sudo apt-get install wkhtmltopdf
```

[Windows setup (and other information)](https://www.geeksforgeeks.org/python-convert-html-pdf/)


## Run the script

```python
python toggljournal.py <TOGGL_API_KEY> <START_DATE> <END_DATE> <PROJECT_NAME> <PERSONAL_JOURNAL*>
```

- <TOGGL_API_KEY> (string): The unique user's API Key. You can find it by following [this official guide](https://support.toggl.com/en/articles/3116844-where-is-my-api-key-located).

- <START_DATE> (string): The start date in YYYY-MM-DD format (i.e. 2022-02-22).

- <END_DATE> (string): The end date in YYYY-MM-DD format (i.e. 2022-02-22).

- <PROJECT_NAME> (string): The project name for which we want to create a report or "ALL" if we want a report for all available projects between the time period defined by START_
DATE and END_DATE.

- <PERSONAL_JOURNAL*> (string): The name of the project you want to be used as a Personal Journal. IMPORTANT: You can ommit this parameter as it is not mandatory. In this case none of the projects will be treated as a Personal Journal.

# Annotation in the Toggl Environment

It is really simple! Everytime we make a new Toggl Entry we are following the following annotation in our description:

<ACTION_TITLE> [N] - <NOTE #1> - <NOTE #2> - <NOTE #3> ...

for example:

Meeting w/ John [N] - Refactor library X - We need another awesome Senior Dev

![screenshot](/images/screenshot_1.png)

## Output & Sample files

There are two output templates:

- Report for a specific project name.
- Report for all projects within a selected timeframe.

You can find examples of these reports in .html and .pdf format in [sample_exports](/sample_exports) folder.

## Logging

The script comes with a log (app.log) in which you will find notes during the runtime of the project. 

- [ INFO ] entries: Are notes recorded by the app (mainly for correct runtime verification).
- [ WARNING ] entries: Are notes recorded by the app in case something goes wrong / or to clarify specific functionality of the script.
## Future work

- For projects with TEs that contain tags, provide a time / tag summary (table + chart)
- Send the report directly by e-mail
- Support .odt format
- Support .doc format
- Support .rtf format

## Disclaimer

This open source software project is not related in any way with the official [Toggl Track tool](https://toggl.com/track/) or the [Toggl company](https://toggl.com/).

## License

MIT License

Copyright (c) 2022 Apostolos Kritikos <akritiko [at] gmail [dot] com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
