#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from declined_transaction_exception import DeclinedTransactionException


class DeclinedRefundException(DeclinedTransactionException):
    """
    Represents an error response from a refund call.
    """

    def __init__(self, status_code, response_body, response):
        if response is not None:
            super(DeclinedRefundException, self).__init__(status_code, response_body, response.error_id, response.errors,
                                                          DeclinedRefundException.__create_message(response))
        else:
            super(DeclinedRefundException, self).__init__(status_code, response_body, None, None,
                                                          DeclinedRefundException.__create_message(response))
        self.__response = response

    @staticmethod
    def __create_message(response):
        if response is not None:
            refund_result = response.refund_result
        else:
            refund_result = None
        if refund_result is not None:
            return "declined refund '%s' with status '%s'" % (refund_result.id, refund_result.status)
        else:
            return "the Worldline Global Collect platform returned a declined refund response"

    @property
    def refund_result(self):
        """
        :return: The result of creating a refund if available, otherwise None.
        """
        if self.__response is None:
            return None
        else:
            return self.__response.refund_result
