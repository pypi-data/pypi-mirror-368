# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.domain.data_object import DataObject


class NetworkTokenData(DataObject):
    """
    | Object holding data that describes a network token
    """

    __network_token = None
    __token_expiry_date = None
    __token_reference_id = None

    @property
    def network_token(self):
        """
        | The network token alternative for the full Permanent Account Number. To receive a non-obfuscated network token please contact your account manager.

        Type: str
        """
        return self.__network_token

    @network_token.setter
    def network_token(self, value):
        self.__network_token = value

    @property
    def token_expiry_date(self):
        """
        | The expiry date of the network token.

        Type: str
        """
        return self.__token_expiry_date

    @token_expiry_date.setter
    def token_expiry_date(self, value):
        self.__token_expiry_date = value

    @property
    def token_reference_id(self):
        """
        | A unique identifier that can be used with Visa Token Service (VTS) or Mastercard Digital Enablement Service (MDES) to retrieve token details. It remains valid as long as the token is valid. Note: A prefix "V:" is added to show that this is a network token for a Visa product and "M:" to show that this is a network token for a Mastercard product. 

        Type: str
        """
        return self.__token_reference_id

    @token_reference_id.setter
    def token_reference_id(self, value):
        self.__token_reference_id = value

    def to_dictionary(self):
        dictionary = super(NetworkTokenData, self).to_dictionary()
        if self.network_token is not None:
            dictionary['networkToken'] = self.network_token
        if self.token_expiry_date is not None:
            dictionary['tokenExpiryDate'] = self.token_expiry_date
        if self.token_reference_id is not None:
            dictionary['tokenReferenceId'] = self.token_reference_id
        return dictionary

    def from_dictionary(self, dictionary):
        super(NetworkTokenData, self).from_dictionary(dictionary)
        if 'networkToken' in dictionary:
            self.network_token = dictionary['networkToken']
        if 'tokenExpiryDate' in dictionary:
            self.token_expiry_date = dictionary['tokenExpiryDate']
        if 'tokenReferenceId' in dictionary:
            self.token_reference_id = dictionary['tokenReferenceId']
        return self
