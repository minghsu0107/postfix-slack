from flask import Flask, jsonify, request, make_response, Response
import os
import json
import dotenv
import hmac
import hashlib
import time
from functools import update_wrapper
from slack import WebClient
from slack.errors import SlackApiError
from mail.send import generateResult

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)
verification_token = os.environ['VERIFICATION_TOKEN']
slack_api_token = os.environ['SLACK_API_TOKEN']

slack_client = WebClient(
    token=os.environ['SLACK_API_TOKEN']
)

app = Flask(__name__)


def isVerificated():
    timestamp = request.headers.get('X-Slack-Request-Timestamp', '0')
    request_body = request.get_data().decode('utf8')
    slack_signature = request.headers.get('X-Slack-Signature', '')

    # The request timestamp is more than five minutes from local time.
    # It could be a replay attack, so let's ignore it
    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False

    sig_basestring = 'v0:' + timestamp + ':' + request_body
    my_signature = 'v0=' + hmac.new(verification_token.encode('utf8'),
                                    sig_basestring.encode('utf8'),
                                    digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(my_signature, slack_signature)


def verfication_failure():
    err_payload = {
        "response_type": "ephemeral",
        "text": "Sorry, that didn't work. Please try again."
    }
    return make_response(jsonify(err_payload), 400)

def verification():
    def _decorator(f):
        def wrapper(*args, **kwargs):
            if not isVerificated():
                return verfication_failure()
            return f(*args, **kwargs)
        return update_wrapper(wrapper, f)
    return _decorator

@app.route('/mailq', methods=['POST'])
@verification()
def showMailQueue():
    payload = {
        "response_type": "in_channel",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": generateResult()
                }
            }
        ]
    }
    return make_response(jsonify(payload), 200)