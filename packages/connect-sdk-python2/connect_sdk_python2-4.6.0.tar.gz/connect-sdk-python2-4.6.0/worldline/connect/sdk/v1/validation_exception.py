#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from api_exception import ApiException


class ValidationException(ApiException):
    """
    Represents an error response from the Worldline Global Collect platform when validation of requests failed.
    """

    def __init__(self, status_code, response_body, error_id, errors,
                 message="the Worldline Global Collect platform returned an incorrect request error response"):
        super(ValidationException, self).__init__(status_code, response_body, error_id, errors, message)
