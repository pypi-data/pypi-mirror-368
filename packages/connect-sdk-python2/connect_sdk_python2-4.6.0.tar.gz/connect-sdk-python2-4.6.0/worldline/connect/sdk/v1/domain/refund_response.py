# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.refund_result import RefundResult


class RefundResponse(RefundResult):

    def to_dictionary(self):
        dictionary = super(RefundResponse, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary):
        super(RefundResponse, self).from_dictionary(dictionary)
        return self
