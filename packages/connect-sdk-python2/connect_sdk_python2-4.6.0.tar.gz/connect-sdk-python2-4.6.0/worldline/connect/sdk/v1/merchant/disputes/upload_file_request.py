# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.communication.multipart_form_data_object import MultipartFormDataObject
from worldline.connect.sdk.communication.multipart_form_data_request import MultipartFormDataRequest


class UploadFileRequest(MultipartFormDataRequest):
    """
    Multipart/form-data parameters for Upload File

    See also https://apireference.connect.worldline-solutions.com/fileserviceapi/v1/en_US/python/disputes/uploadFile.html
    """

    __file = None

    @property
    def file(self):
        """
        | The file that you will upload as evidence to support a dispute.

        Type: :class:`worldline.connect.sdk.domain.uploadable_file.UploadableFile`
        """
        return self.__file

    @file.setter
    def file(self, value):
        self.__file = value

    def to_multipart_form_data_object(self):
        """
        :return: :class:`worldline.connect.sdk.communication.multipart_form_data_object.MultipartFormDataObject`
        """
        result = MultipartFormDataObject()
        if self.file is not None:
            result.add_file("file", self.file)
        return result
