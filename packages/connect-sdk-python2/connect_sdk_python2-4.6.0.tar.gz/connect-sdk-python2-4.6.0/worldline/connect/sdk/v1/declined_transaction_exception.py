#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from api_exception import ApiException


class DeclinedTransactionException(ApiException):
    """
    Represents an error response from a create payment, payout or refund call.
    """

    def __init__(self, status_code, response_body, error_id, errors, message=None):
        if message:
            super(DeclinedTransactionException, self).__init__(status_code, response_body, error_id, errors, message)
        else:
            super(DeclinedTransactionException, self).__init__(status_code, response_body, error_id, errors)
