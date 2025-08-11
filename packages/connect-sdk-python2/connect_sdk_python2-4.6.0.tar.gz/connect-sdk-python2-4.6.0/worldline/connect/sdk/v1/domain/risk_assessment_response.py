# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.result_do_risk_assessment import ResultDoRiskAssessment


class RiskAssessmentResponse(DataObject):

    __results = None

    @property
    def results(self):
        """
        | Object that contains the results of the performed fraudchecks

        Type: list[:class:`worldline.connect.sdk.v1.domain.result_do_risk_assessment.ResultDoRiskAssessment`]
        """
        return self.__results

    @results.setter
    def results(self, value):
        self.__results = value

    def to_dictionary(self):
        dictionary = super(RiskAssessmentResponse, self).to_dictionary()
        if self.results is not None:
            dictionary['results'] = []
            for element in self.results:
                if element is not None:
                    dictionary['results'].append(element.to_dictionary())
        return dictionary

    def from_dictionary(self, dictionary):
        super(RiskAssessmentResponse, self).from_dictionary(dictionary)
        if 'results' in dictionary:
            if not isinstance(dictionary['results'], list):
                raise TypeError('value \'{}\' is not a list'.format(dictionary['results']))
            self.results = []
            for element in dictionary['results']:
                value = ResultDoRiskAssessment()
                self.results.append(value.from_dictionary(element))
        return self
