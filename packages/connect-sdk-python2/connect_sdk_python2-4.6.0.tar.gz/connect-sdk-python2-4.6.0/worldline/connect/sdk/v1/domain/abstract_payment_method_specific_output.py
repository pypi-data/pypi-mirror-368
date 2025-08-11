# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.domain.data_object import DataObject


class AbstractPaymentMethodSpecificOutput(DataObject):

    __payment_product_id = None

    @property
    def payment_product_id(self):
        """
        | Payment product identifier
        | Please see payment products <https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/paymentproducts.html> for a full overview of possible values.

        Type: int
        """
        return self.__payment_product_id

    @payment_product_id.setter
    def payment_product_id(self, value):
        self.__payment_product_id = value

    def to_dictionary(self):
        dictionary = super(AbstractPaymentMethodSpecificOutput, self).to_dictionary()
        if self.payment_product_id is not None:
            dictionary['paymentProductId'] = self.payment_product_id
        return dictionary

    def from_dictionary(self, dictionary):
        super(AbstractPaymentMethodSpecificOutput, self).from_dictionary(dictionary)
        if 'paymentProductId' in dictionary:
            self.payment_product_id = dictionary['paymentProductId']
        return self
