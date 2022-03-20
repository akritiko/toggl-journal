import subprocess

from flask import Flask, redirect, url_for, request, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return render_template("index.html")


@app.route('/success/<command>')
def success(command):
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        togglapi = request.form['togglapi']
        since = request.form['since']
        until = request.form['until']
        project = request.form['project']
        journal = request.form['journal']
        command = "python toggljournal.py " + togglapi + " " + since + " " + until + " " + " " + project + " " + journal
        return redirect(url_for('success', command=command))
    else:
        togglapi = request.args.get('togglapi')
        since = request.args.get('since')
        until = request.args.get('until')
        project = request.args.get('project')
        journal = request.args.get('journal')
        return redirect(url_for('success', command=command))


if __name__ == '__main__':
    app.run(debug=True)
