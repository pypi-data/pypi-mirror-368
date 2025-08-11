# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.approve_payment_direct_debit_payment_method_specific_input import ApprovePaymentDirectDebitPaymentMethodSpecificInput


class ApprovePaymentSepaDirectDebitPaymentMethodSpecificInput(ApprovePaymentDirectDebitPaymentMethodSpecificInput):

    def to_dictionary(self):
        dictionary = super(ApprovePaymentSepaDirectDebitPaymentMethodSpecificInput, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary):
        super(ApprovePaymentSepaDirectDebitPaymentMethodSpecificInput, self).from_dictionary(dictionary)
        return self
