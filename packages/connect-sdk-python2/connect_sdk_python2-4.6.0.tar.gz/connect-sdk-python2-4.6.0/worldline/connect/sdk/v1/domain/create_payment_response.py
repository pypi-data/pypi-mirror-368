# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.create_payment_result import CreatePaymentResult


class CreatePaymentResponse(CreatePaymentResult):

    def to_dictionary(self):
        dictionary = super(CreatePaymentResponse, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary):
        super(CreatePaymentResponse, self).from_dictionary(dictionary)
        return self
