from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def empty():
    return 'Hello'

@app.route('/git_webhook')
def reloader():
    return 'Nothing'