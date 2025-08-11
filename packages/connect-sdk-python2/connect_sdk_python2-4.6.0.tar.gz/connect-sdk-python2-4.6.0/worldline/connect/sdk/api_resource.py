from worldline.connect.sdk.communication.request_header import RequestHeader


class ApiResource(object):
    """
    Base class of all Worldline Global Collect platform API resources.
    """

    def __init__(self, parent=None, communicator=None, path_context=None, client_meta_info=None):
        """
        The parent and/or communicator must be given.
        """
        if not parent and not communicator:
            raise ValueError("parent and/or communicator is required")
        self.__parent = parent
        self.__communicator = communicator if communicator else parent._communicator
        self.__path_context = path_context
        self.__client_meta_info = client_meta_info if client_meta_info or not parent else parent._client_meta_info

    @property
    def _communicator(self):
        return self.__communicator

    @property
    def _client_meta_info(self):
        return self.__client_meta_info

    @property
    def _client_headers(self):
        if self._client_meta_info is not None:
            client_headers = [RequestHeader("X-GCS-ClientMetaInfo", self._client_meta_info)]
            return client_headers
        else:
            return None

    def _instantiate_uri(self, uri, path_context):
        uri = self.__replace_all(uri, path_context)
        uri = self.__instantiate_uri(uri)
        return uri

    def __instantiate_uri(self, uri):
        uri = self.__replace_all(uri, self.__path_context)
        if self.__parent is not None:
            uri = self.__parent.__instantiate_uri(uri)
        return uri

    @staticmethod
    def __replace_all(uri, path_context):
        if path_context:
            for key, value in path_context.iteritems():
                uri = uri.replace("{" + key + "}", value)
        return uri
