from flask import Flask, request
from os import environ
from json import loads
from hashlib import sha1
import hmac

app = Flask(__name__)
files_to_reload = []
git_secret = environ.get('GITSECRET')
ref = 'refs/heads/master'  # Your branch


@app.route('/')
def empty():
    return 'Hello'


@app.route('/git_webhook')
def reloader():
    if request.headers.get('X-Github-Event') == 'push':
        data = loads(request.data)
        if git_secret is not None:
            hashed = hmac.new(git_secret.encode(), request.data, sha1)
            sig = request.headers.get('X-Hub-Signature')
            if (not sig) or sig.strip().split('=')[1] == hashed.hexdigest():
                return '{}', 400

    return '{}'


if __name__ == '__main__':
    app.run(port=10000)
