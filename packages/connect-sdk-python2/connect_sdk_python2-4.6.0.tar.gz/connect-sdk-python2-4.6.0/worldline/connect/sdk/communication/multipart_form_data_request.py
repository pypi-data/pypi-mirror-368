from abc import ABCMeta, abstractmethod


class MultipartFormDataRequest(object):
    """
    A representation of a multipart/form-data request.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def to_multipart_form_data_object(self):
        """
        :return: :class:`worldline.connect.sdk.communication.MultipartFormDataObject`
        """
        raise NotImplementedError
