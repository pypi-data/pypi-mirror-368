from abc import ABCMeta, abstractmethod

from worldline.connect.sdk.log.logging_capable import LoggingCapable
from worldline.connect.sdk.log.obfuscation_capable import ObfuscationCapable


class Connection(LoggingCapable, ObfuscationCapable):
    """
    Represents a connection to the Worldline Global Collect platform server.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self, url, request_headers):
        """
        Send a GET request to the Worldline Global Collect platform and return the response.

        :param url: The URI to call, including any necessary query parameters.
        :param request_headers: An optional sequence of request headers.
        :return: The response from the Worldline Global Collect platform as a tuple with
         the status code, headers and a generator of body chunks
        :raise CommunicationException: when an exception occurred communicating
         with the Worldline Global Collect platform
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, url, request_headers):
        """
        Send a DELETE request to the Worldline Global Collect platform and return the response.

        :param url: The URI to call, including any necessary query parameters.
        :param request_headers: An optional sequence of request headers.
        :return: The response from the Worldline Global Collect platform as a tuple with
         the status code, headers and a generator of body chunks
        :raise CommunicationException: when an exception occurred communicating
         with the Worldline Global Collect platform
        """
        raise NotImplementedError

    @abstractmethod
    def post(self, url, request_headers, body):
        """
        Send a POST request to the Worldline Global Collect platform and return the response.

        :param url: The URI to call, including any necessary query parameters.
        :param request_headers: An optional sequence of request headers.
        :param body: The optional body to send.
        :return: The response from the Worldline Global Collect platform as a tuple with
         the status code, headers and a generator of body chunks
        :raise CommunicationException: when an exception occurred communicating
         with the Worldline Global Collect platform
        """
        raise NotImplementedError

    @abstractmethod
    def put(self, url, request_headers, body):
        """
        Send a PUT request to the Worldline Global Collect platform and return the response.

        :param url: The URI to call, including any necessary query parameters.
        :param request_headers: An optional sequence of request headers.
        :param body: The optional body to send.
        :return: The response from the Worldline Global Collect platform as a tuple with
         the status code, headers and a generator of body chunks
        :raise CommunicationException: when an exception occurred communicating
         with the Worldline Global Collect platform
        """
        raise NotImplementedError

    def close(self):
        """
        Releases any system resources associated with this object.
        """
        pass
