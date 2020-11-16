import os
import logging
from http import HTTPStatus
from libtrustbridge.websub.constants import (
    TOPIC_ATTR_KEY,
    MODE_ATTR_KEY,
    LEASE_SECONDS_ATTR_KEY
)
from flask import Flask, request, jsonify


HUB_CHALLENGE_ATTR_KEY = 'hub.challenge'


PORT = os.environ['PORT']
HOST = '0.0.0.0'


app = Flask(__name__)

app.config['TESTING'] = True
app.config['DEBUG'] = True

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('CALLBACK_SERVER')


CALLBACKS_RECORD = []


@app.route('/callback/<result>/<id>', methods=['GET', 'POST'])
@app.route('/callback/<result>', methods=['GET', 'POST'])
def callback_websub_valid(id=None, result=None):
    global CALLBACKS_RECORD
    if result not in ['valid', 'invalid']:
        return ('', HTTPStatus.NOT_FOUND)
    callback_record = dict(
        id=id,
        url=request.url,
        method=request.method,
        headers=dict(request.headers)
    )
    response = None
    if request.method == 'GET':
        try:
            callback_record['args'] = dict(request.args)

            request.args[TOPIC_ATTR_KEY]
            request.args[MODE_ATTR_KEY]
            request.args[LEASE_SECONDS_ATTR_KEY]
            request.args[HUB_CHALLENGE_ATTR_KEY]

            challenge_response_text = request.args[HUB_CHALLENGE_ATTR_KEY]
            if result == 'invalid':
                challenge_response_text *= 2

            callback_record['status_code'] = HTTPStatus.OK
            response = (challenge_response_text, callback_record['status_code'])
        except KeyError:
            callback_record['status_code'] = HTTPStatus.BAD_REQUEST
            response = ('', callback_record['status_code'])
    else:
        callback_record['json'] = request.json
        if result == 'valid':
            callback_record['status_code'] = HTTPStatus.OK
            response = ('', callback_record['status_code'])
        else:
            callback_record['status_code'] = HTTPStatus.BAD_REQUEST
            response = ('', callback_record['status_code'])
    if id:
        CALLBACKS_RECORD.append(callback_record)
    return response


@app.route('/callbacks', methods=['DELETE', 'GET'])
@app.route('/callbacks/<index>', methods=['GET'])
def callbacks_record(index=None):
    global CALLBACKS_RECORD
    if request.method == 'GET':
        if index is not None:
            try:
                index = int(index)
                return jsonify(CALLBACKS_RECORD[index])
            except IndexError:
                return ('', HTTPStatus.NOT_FOUND)
            except ValueError:
                return ('', HTTPStatus.BAD_REQUEST)
        else:
            return jsonify(CALLBACKS_RECORD)
    elif request:
        CALLBACKS_RECORD.clear()
        return ('', HTTPStatus.OK)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
