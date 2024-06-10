from flask import (
    Blueprint,
    jsonify,
)
from flask import current_app as app


exceptions_bp = Blueprint('exceptions', __name__)


class CustomException(Exception):
    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        app.logger.error("{error} - {message}".format(
            error=self.status_code,
            message=self.message
        ))

    def to_dict(self):
        return {
            "status": self.status_code,
            "detail": self.message
        }


@exceptions_bp.app_errorhandler(CustomException)
def handle_custom_exception(e):
    return jsonify(e.to_dict()), e.status_code
