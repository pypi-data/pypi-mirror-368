# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.dispute_response import DisputeResponse
from worldline.connect.sdk.v1.domain.payment_response import PaymentResponse
from worldline.connect.sdk.v1.domain.payout_response import PayoutResponse
from worldline.connect.sdk.v1.domain.refund_response import RefundResponse
from worldline.connect.sdk.v1.domain.token_response import TokenResponse


class WebhooksEvent(DataObject):

    __api_version = None
    __created = None
    __dispute = None
    __id = None
    __merchant_id = None
    __payment = None
    __payout = None
    __refund = None
    __token = None
    __type = None

    @property
    def api_version(self):
        """
        Type: str
        """
        return self.__api_version

    @api_version.setter
    def api_version(self, value):
        self.__api_version = value

    @property
    def created(self):
        """
        Type: str
        """
        return self.__created

    @created.setter
    def created(self, value):
        self.__created = value

    @property
    def dispute(self):
        """
        Type: :class:`worldline.connect.sdk.v1.domain.dispute_response.DisputeResponse`
        """
        return self.__dispute

    @dispute.setter
    def dispute(self, value):
        self.__dispute = value

    @property
    def id(self):
        """
        Type: str
        """
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = value

    @property
    def merchant_id(self):
        """
        Type: str
        """
        return self.__merchant_id

    @merchant_id.setter
    def merchant_id(self, value):
        self.__merchant_id = value

    @property
    def payment(self):
        """
        Type: :class:`worldline.connect.sdk.v1.domain.payment_response.PaymentResponse`
        """
        return self.__payment

    @payment.setter
    def payment(self, value):
        self.__payment = value

    @property
    def payout(self):
        """
        Type: :class:`worldline.connect.sdk.v1.domain.payout_response.PayoutResponse`
        """
        return self.__payout

    @payout.setter
    def payout(self, value):
        self.__payout = value

    @property
    def refund(self):
        """
        Type: :class:`worldline.connect.sdk.v1.domain.refund_response.RefundResponse`
        """
        return self.__refund

    @refund.setter
    def refund(self, value):
        self.__refund = value

    @property
    def token(self):
        """
        Type: :class:`worldline.connect.sdk.v1.domain.token_response.TokenResponse`
        """
        return self.__token

    @token.setter
    def token(self, value):
        self.__token = value

    @property
    def type(self):
        """
        Type: str
        """
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = value

    def to_dictionary(self):
        dictionary = super(WebhooksEvent, self).to_dictionary()
        if self.api_version is not None:
            dictionary['apiVersion'] = self.api_version
        if self.created is not None:
            dictionary['created'] = self.created
        if self.dispute is not None:
            dictionary['dispute'] = self.dispute.to_dictionary()
        if self.id is not None:
            dictionary['id'] = self.id
        if self.merchant_id is not None:
            dictionary['merchantId'] = self.merchant_id
        if self.payment is not None:
            dictionary['payment'] = self.payment.to_dictionary()
        if self.payout is not None:
            dictionary['payout'] = self.payout.to_dictionary()
        if self.refund is not None:
            dictionary['refund'] = self.refund.to_dictionary()
        if self.token is not None:
            dictionary['token'] = self.token.to_dictionary()
        if self.type is not None:
            dictionary['type'] = self.type
        return dictionary

    def from_dictionary(self, dictionary):
        super(WebhooksEvent, self).from_dictionary(dictionary)
        if 'apiVersion' in dictionary:
            self.api_version = dictionary['apiVersion']
        if 'created' in dictionary:
            self.created = dictionary['created']
        if 'dispute' in dictionary:
            if not isinstance(dictionary['dispute'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['dispute']))
            value = DisputeResponse()
            self.dispute = value.from_dictionary(dictionary['dispute'])
        if 'id' in dictionary:
            self.id = dictionary['id']
        if 'merchantId' in dictionary:
            self.merchant_id = dictionary['merchantId']
        if 'payment' in dictionary:
            if not isinstance(dictionary['payment'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['payment']))
            value = PaymentResponse()
            self.payment = value.from_dictionary(dictionary['payment'])
        if 'payout' in dictionary:
            if not isinstance(dictionary['payout'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['payout']))
            value = PayoutResponse()
            self.payout = value.from_dictionary(dictionary['payout'])
        if 'refund' in dictionary:
            if not isinstance(dictionary['refund'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['refund']))
            value = RefundResponse()
            self.refund = value.from_dictionary(dictionary['refund'])
        if 'token' in dictionary:
            if not isinstance(dictionary['token'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['token']))
            value = TokenResponse()
            self.token = value.from_dictionary(dictionary['token'])
        if 'type' in dictionary:
            self.type = dictionary['type']
        return self
