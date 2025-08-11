# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.abstract_token import AbstractToken
from worldline.connect.sdk.v1.domain.customer_token import CustomerToken
from worldline.connect.sdk.v1.domain.token_card_data import TokenCardData


class TokenCard(AbstractToken):

    __customer = None
    __data = None

    @property
    def customer(self):
        """
        | Object containing the details of the customer

        Type: :class:`worldline.connect.sdk.v1.domain.customer_token.CustomerToken`
        """
        return self.__customer

    @customer.setter
    def customer(self, value):
        self.__customer = value

    @property
    def data(self):
        """
        | Object containing the card tokenizable details

        Type: :class:`worldline.connect.sdk.v1.domain.token_card_data.TokenCardData`
        """
        return self.__data

    @data.setter
    def data(self, value):
        self.__data = value

    def to_dictionary(self):
        dictionary = super(TokenCard, self).to_dictionary()
        if self.customer is not None:
            dictionary['customer'] = self.customer.to_dictionary()
        if self.data is not None:
            dictionary['data'] = self.data.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary):
        super(TokenCard, self).from_dictionary(dictionary)
        if 'customer' in dictionary:
            if not isinstance(dictionary['customer'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['customer']))
            value = CustomerToken()
            self.customer = value.from_dictionary(dictionary['customer'])
        if 'data' in dictionary:
            if not isinstance(dictionary['data'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['data']))
            value = TokenCardData()
            self.data = value.from_dictionary(dictionary['data'])
        return self
