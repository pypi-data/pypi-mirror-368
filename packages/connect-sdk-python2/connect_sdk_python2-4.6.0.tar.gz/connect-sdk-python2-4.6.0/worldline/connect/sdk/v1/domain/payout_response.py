# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.payout_result import PayoutResult


class PayoutResponse(PayoutResult):

    def to_dictionary(self):
        dictionary = super(PayoutResponse, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary):
        super(PayoutResponse, self).from_dictionary(dictionary)
        return self
