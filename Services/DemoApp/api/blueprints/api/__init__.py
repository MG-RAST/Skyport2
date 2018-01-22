from flask import Blueprint
from flask import Response
from flask import request
#from flask import jsonify
#from flask import stream_with_context
import logging
import re
import sys
import time
sys.path.append("../..")
#import export
sys.path.pop()
sys.path.append("..")



api = Blueprint('api', __name__, template_folder='templates')

logger = logging.getLogger(__name__)

port = 80
api_url_internal = 'http://localhost'
api_url = 'http://submission-api'

# modify /etc/hosts/: 127.0.0.1    localhost submission-api
STATUS_Bad_Request = 400  # A client error
STATUS_Unauthorized = 401
STATUS_Not_Found = 404
STATUS_Server_Error = 500


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code and status_code==STATUS_Server_Error:
            logger.warning(message)
        else:
            logger.debug(message)
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@api.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response




@api.route('/testing')
def api_testing():
    return 'this is a test'


@api.route('/')
def api_root():
    return 'This is the Skyport submission server.\n'

