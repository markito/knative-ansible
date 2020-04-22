#!/usr/bin/python3

import flask
from flask import request, jsonify
import logging
import ansible_runner
import urllib
import requests 
import json 
import os 

# logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
logger = logging.getLogger(__name__)
app = flask.Flask(__name__)
app.config["DEBUG"] = True

PLAYBOOK_PATH="/tmp/playbook.yaml"
BROKER_URL=os.environ["BROKER_URL"]

@app.route('/', methods=['GET'])
def run():
    query_parameters = request.args
    playbook = query_parameters.get('playbook')

    logger.debug(f"Reading... {playbook}")
    save_from_url(playbook)
    logger.debug("Saved...")  

    r = ansible_runner.run(playbook=PLAYBOOK_PATH, private_data_dir='/tmp', event_handler=publishCloudEvent)

    os.remove(PLAYBOOK_PATH)
    logger.info(r)
    return f"Playbook status: {r.status}"

@app.route('/', methods=['POST'])
def post():
    print(request.data)
    print(request.headers)

    return request.args


def save_from_url(url):
    try: 
        urllib.request.urlretrieve(url, PLAYBOOK_PATH)
    except Exception as e:
        logger.error(f"Could not access file or URL: {url} \n due to: {e}")
        # TODO: delete file from previous requiret

def publishCloudEvent(message): 
    event_type= message['event'] if len(message['event']) > 1 else "unknown_event_type"
    # ignore verbose events
    # if "verbose" in event_type:
    #     return

    data = json.dumps(message)
    headers = { "Ce-Id": "ansible-runner",
                "Ce-Specversion": "0.3",
                "Ce-Type": f"{event_type}",
                "Ce-Source": "RedHat",
                "Content-Type": "application/json"}
    requests.post(BROKER_URL, data=data, headers=headers)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=8080)     