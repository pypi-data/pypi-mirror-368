# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.abstract_payment_method_specific_input import AbstractPaymentMethodSpecificInput


class AbstractBankTransferPaymentMethodSpecificInput(AbstractPaymentMethodSpecificInput):

    __additional_reference = None

    @property
    def additional_reference(self):
        """
        Type: str
        """
        return self.__additional_reference

    @additional_reference.setter
    def additional_reference(self, value):
        self.__additional_reference = value

    def to_dictionary(self):
        dictionary = super(AbstractBankTransferPaymentMethodSpecificInput, self).to_dictionary()
        if self.additional_reference is not None:
            dictionary['additionalReference'] = self.additional_reference
        return dictionary

    def from_dictionary(self, dictionary):
        super(AbstractBankTransferPaymentMethodSpecificInput, self).from_dictionary(dictionary)
        if 'additionalReference' in dictionary:
            self.additional_reference = dictionary['additionalReference']
        return self
