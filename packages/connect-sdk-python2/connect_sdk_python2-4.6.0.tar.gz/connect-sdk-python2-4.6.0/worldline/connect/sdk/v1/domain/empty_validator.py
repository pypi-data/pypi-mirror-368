# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.domain.data_object import DataObject


class EmptyValidator(DataObject):
    """
    | A validator object that contains no additional properties.
    """

    def to_dictionary(self):
        dictionary = super(EmptyValidator, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary):
        super(EmptyValidator, self).from_dictionary(dictionary)
        return self
