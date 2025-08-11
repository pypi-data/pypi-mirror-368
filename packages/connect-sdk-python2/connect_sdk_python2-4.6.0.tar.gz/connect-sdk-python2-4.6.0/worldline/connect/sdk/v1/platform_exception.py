#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from api_exception import ApiException


class PlatformException(ApiException):
    """
    Represents an error response from the Worldline Global Collect platform when something went wrong at the Worldline Global Collect platform or further downstream.
    """

    def __init__(self, status_code, response_body, error_id, errors,
                 message="the Worldline Global Collect platform returned an error response"):
        super(PlatformException, self).__init__(status_code, response_body, error_id, errors, message)
