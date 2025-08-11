# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.payment import Payment


class PaymentResponse(Payment):

    def to_dictionary(self):
        dictionary = super(PaymentResponse, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary):
        super(PaymentResponse, self).from_dictionary(dictionary)
        return self
