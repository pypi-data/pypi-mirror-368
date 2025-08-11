# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.abstract_order_status import AbstractOrderStatus
from worldline.connect.sdk.v1.domain.capture_output import CaptureOutput
from worldline.connect.sdk.v1.domain.capture_status_output import CaptureStatusOutput


class Capture(AbstractOrderStatus):

    __capture_output = None
    __status = None
    __status_output = None

    @property
    def capture_output(self):
        """
        | Object containing capture details

        Type: :class:`worldline.connect.sdk.v1.domain.capture_output.CaptureOutput`
        """
        return self.__capture_output

    @capture_output.setter
    def capture_output(self, value):
        self.__capture_output = value

    @property
    def status(self):
        """
        | Current high-level status of the captures in a human-readable form. Possible values are:
        
        * CREATED - The capture has been created on our side
        * CAPTURE_REQUESTED - The transaction is in the queue to be captured
        * CAPTURED - The transaction has been captured and we have received online confirmation
        * PAID - We have matched the incoming funds to the transaction
        * CANCELLED - You have cancelled the capture
        * REJECTED_CAPTURE - The capture has been rejected
        * REVERSED - The capture has been reversed
        * CHARGEBACK_NOTIFICATION - We have received a notification of chargeback and this status informs you that your account will be debited for a particular transaction
        * CHARGEBACKED - The transaction has been chargebacked
        
        
        | Please see Statuses <https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/statuses.html> for a full overview of possible values.

        Type: str
        """
        return self.__status

    @status.setter
    def status(self, value):
        self.__status = value

    @property
    def status_output(self):
        """
        | This object has the numeric representation of the current capture status, timestamp of last status change and performable action on the current capture resource. In case of failed captures and negative scenarios, detailed error information is listed.

        Type: :class:`worldline.connect.sdk.v1.domain.capture_status_output.CaptureStatusOutput`
        """
        return self.__status_output

    @status_output.setter
    def status_output(self, value):
        self.__status_output = value

    def to_dictionary(self):
        dictionary = super(Capture, self).to_dictionary()
        if self.capture_output is not None:
            dictionary['captureOutput'] = self.capture_output.to_dictionary()
        if self.status is not None:
            dictionary['status'] = self.status
        if self.status_output is not None:
            dictionary['statusOutput'] = self.status_output.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary):
        super(Capture, self).from_dictionary(dictionary)
        if 'captureOutput' in dictionary:
            if not isinstance(dictionary['captureOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['captureOutput']))
            value = CaptureOutput()
            self.capture_output = value.from_dictionary(dictionary['captureOutput'])
        if 'status' in dictionary:
            self.status = dictionary['status']
        if 'statusOutput' in dictionary:
            if not isinstance(dictionary['statusOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['statusOutput']))
            value = CaptureStatusOutput()
            self.status_output = value.from_dictionary(dictionary['statusOutput'])
        return self
