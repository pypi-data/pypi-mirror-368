# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.abstract_indicator import AbstractIndicator


class AuthenticationIndicator(AbstractIndicator):
    """
    | Indicates if the payment product supports 3D Security (mandatory, optional or not needed).
    """

    def to_dictionary(self):
        dictionary = super(AuthenticationIndicator, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary):
        super(AuthenticationIndicator, self).from_dictionary(dictionary)
        return self
