#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from base64 import b64encode

from api_resource import ApiResource

from worldline.connect.sdk.log.logging_capable import LoggingCapable
from worldline.connect.sdk.log.obfuscation_capable import ObfuscationCapable
from worldline.connect.sdk.v1.v1_client import V1Client


class Client(ApiResource, LoggingCapable, ObfuscationCapable):
    """
    Worldline Global Collect platform client.

    This client and all its child clients are bound to one specific value for the X-GCS-ClientMetaInfo header.
    To get a new client with a different header value, use with_client_meta_info.

    Thread-safe.
    """

    def __init__(self, communicator, client_meta_info=None):
        """
        :param communicator:      :class:`worldline.connect.sdk.communicator.Communicator`
        :param client_meta_info:  str
        """
        super(Client, self).__init__(communicator=communicator,
                                     client_meta_info=client_meta_info)

    def with_client_meta_info(self, client_meta_info):
        """
        :param client_meta_info: JSON string containing the metadata for the client
        :return: a new Client which uses the passed metadata for the X-GCS-ClientMetaInfo header.
        :raise MarshallerSyntaxException: if the given clientMetaInfo is not a valid JSON string
        """
        if self._client_meta_info is None and client_meta_info is None:
            return self
        if client_meta_info is None:
            return Client(self._communicator, None)
        # Checking to see if this is valid JSON (no JSON parse exceptions)
        self._communicator.marshaller.unmarshal(client_meta_info, object)
        client_meta_info = b64encode(client_meta_info.encode('utf-8'))
        if client_meta_info == self._client_meta_info:
            return self
        return Client(self._communicator, client_meta_info)

    def close_idle_connections(self, idle_time):
        """
        Utility method that delegates the call to this client's communicator.

        :param idle_time: a datetime.timedelta object indicating the idle time
        """
        self._communicator.close_idle_connections(idle_time)

    def close_expired_connections(self):
        """
        Utility method that delegates the call to this client's communicator.
        """
        self._communicator.close_expired_connections()

    def set_body_obfuscator(self, body_obfuscator):
        # delegate to the communicator
        self._communicator.set_body_obfuscator(body_obfuscator)

    def set_header_obfuscator(self, header_obfuscator):
        # delegate to the communicator
        self._communicator.set_header_obfuscator(header_obfuscator)

    def enable_logging(self, communicator_logger):
        # delegate to the communicator
        self._communicator.enable_logging(communicator_logger)

    def disable_logging(self):
        # delegate to the communicator
        self._communicator.disable_logging()

    def close(self):
        """
        Releases any system resources associated with this object.
        """
        self._communicator.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def v1(self):
        return V1Client(self, None)
