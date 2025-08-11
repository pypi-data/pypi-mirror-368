#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from declined_transaction_exception import DeclinedTransactionException


class DeclinedPaymentException(DeclinedTransactionException):
    """
    Represents an error response from a create payment call.
    """

    def __init__(self, status_code, response_body, response):
        if response is not None:
            super(DeclinedPaymentException, self).__init__(status_code, response_body, response.error_id, response.errors,
                                                           DeclinedPaymentException.__create_message(response))
        else:
            super(DeclinedPaymentException, self).__init__(status_code, response_body, None, None,
                                                           DeclinedPaymentException.__create_message(response))
        self.__response = response

    @staticmethod
    def __create_message(response):
        if response is not None and response.payment_result is not None:
            payment = response.payment_result.payment
        else:
            payment = None
        if payment is not None:
            return "declined payment '%s' with status '%s'" % (payment.id, payment.status)
        else:
            return "the Worldline Global Collect platform returned a declined payment response"

    @property
    def create_payment_result(self):
        """
        :return: The result of creating a payment if available, otherwise None.
        """
        if self.__response is None:
            return None
        else:
            return self.__response.payment_result
