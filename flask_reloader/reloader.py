from flask import Flask, request, jsonify
from os import environ, system
from json import loads
from hashlib import sha1
import hmac
import requests

username = 'gitreloader'  # Your pythonanywhere username
domain_name = 'gitreloader.pythonanywhere.com'  # Your domain
app = Flask(__name__)
files_to_reload = ["flask_reloader/reloader.py", 'testfile']
git_secret = environ.get('GITSECRET')
ref = 'refs/heads/master'  # Your branch
repo_id = 266953712  # Your repo id


@app.route('/')
def empty():
    return 'Hello'


@app.route('/git_webhook', methods=['POST'])
def reloader():
    if request.headers.get('X-GitHub-Event') == 'push':
        data = loads(request.data)
        if git_secret is not None:
            hashed = hmac.new(git_secret.encode(), request.data, sha1)
            sig = request.headers.get('X-Hub-Signature')
            if (not sig) or sig.strip().split('=')[1] != hashed.hexdigest():
                return jsonify(status=400, reason='Invalid signature'), 400
        with open('latest_delivery', 'w+') as latest_delivery:
            if latest_delivery.read() == request.headers.get('X-GitHub-Delivery'):
                return jsonify(status=400, reason='Replayed Request')
            latest_delivery.write(request.headers.get('X-GitHub-Delivery'))
        if data['ref'] == ref:
            system("git pull")
        data = data['head_commit']
        for i in data['removed'] + data['modified']:
            if i in files_to_reload:
                response = requests.post(
                    'https://www.pythonanywhere.com//api/v0/user/{username}/webapps/{domain_name}/reload/'.format(
                        username=username,
                        domain_name=domain_name
                    ),
                    headers={'Authorization': 'Token {token}'.format(token=environ.get("API_TOKEN"))}
                )
    return jsonify(status=200)


if __name__ == '__main__':
    app.run(port=10000)
