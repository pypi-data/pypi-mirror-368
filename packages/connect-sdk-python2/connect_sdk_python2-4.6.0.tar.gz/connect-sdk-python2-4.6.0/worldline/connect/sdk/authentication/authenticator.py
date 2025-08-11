from abc import ABCMeta, abstractmethod


class Authenticator(object):
    """
    Used to authenticate requests to the Worldline Global Collect platform.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_authorization(self, http_method, resource_uri, request_headers):
        """
        Returns a value that can be used for the "Authorization" header.

        :param http_method: The HTTP method.
        :param resource_uri: The URI of the resource.
        :param request_headers: A sequence of RequestHeaders.
         This sequence may not be modified and may not contain headers with the same name.
        """
        raise NotImplementedError
