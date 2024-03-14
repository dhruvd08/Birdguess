import http
import time

import requests

from data import birds
from flask import Flask, request

app = Flask(__name__)


def send(msg_type: str, msg: str, to: int):
    endpoint = 'https://foresthut.pythonanywhere.com/messages/message'

    input_params = {
        'msg_id': str(int(time.time())),
        'msg_body': msg,
        'msg_type': msg_type,
        'player_id': to
    }

    header = {
        'api-key': 'fa64f9edd0351f4238d7cbfa5b8e1c12e148aa1629bdceefe639bee8b93a2d5d'
    }

    response = requests.post(url=endpoint, json=input_params, headers=header).json()
    print(response)


@app.route('/notify-wh', methods=['POST'])
def notify():
    content = request.json
    print(content)
    # TODO: do process the message
    send('TEXT', 'Hello', 1)
    return str(http.HTTPStatus.OK.value)


if __name__ == '__main__':
    app.run()
