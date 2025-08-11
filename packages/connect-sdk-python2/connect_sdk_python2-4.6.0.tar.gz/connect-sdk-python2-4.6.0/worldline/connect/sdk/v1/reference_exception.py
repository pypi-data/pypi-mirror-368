#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from api_exception import ApiException


class ReferenceException(ApiException):
    """
    Represents an error response from the Worldline Global Collect platform when a non-existing or removed object is trying to be accessed.
    """

    def __init__(self, status_code, response_body, error_id, errors,
                 message="the Worldline Global Collect platform returned a reference error response"):
        super(ReferenceException, self).__init__(status_code, response_body, error_id, errors, message)
