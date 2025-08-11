#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.api_resource import ApiResource
from worldline.connect.sdk.communication.response_exception import ResponseException
from worldline.connect.sdk.v1.domain.error_response import ErrorResponse
from worldline.connect.sdk.v1.exception_factory import create_exception


class FilesClient(ApiResource):
    """
    Files client. Thread-safe.
    """

    def __init__(self, parent, path_context):
        """
        :param parent:       :class:`worldline.connect.sdk.api_resource.ApiResource`
        :param path_context: dict[str, str]
        """
        super(FilesClient, self).__init__(parent=parent, path_context=path_context)

    def get_file(self, file_id, context=None):
        """
        Resource /{merchantId}/files/{fileId} - Retrieve File

        See also https://apireference.connect.worldline-solutions.com/fileserviceapi/v1/en_US/python/files/getFile.html

        :param file_id:  str
        :param context:  :class:`worldline.connect.sdk.call_context.CallContext`
        :return: a tuple with the headers and a generator of body chunks
        :raise IdempotenceException: if an idempotent request caused a conflict (HTTP status code 409)
        :raise ValidationException: if the request was not correct and couldn't be processed (HTTP status code 400)
        :raise AuthorizationException: if the request was not allowed (HTTP status code 403)
        :raise ReferenceException: if an object was attempted to be referenced that doesn't exist or has been removed,
                   or there was a conflict (HTTP status code 404, 409 or 410)
        :raise PlatformException: if something went wrong at the Worldline Global Collect platform,
                   the Worldline Global Collect platform was unable to process a message from a downstream partner/acquirer,
                   or the service that you're trying to reach is temporary unavailable (HTTP status code 500, 502 or 503)
        :raise ApiException: if the Worldline Global Collect platform returned any other error
        """
        path_context = {
            "fileId": file_id,
        }
        uri = self._instantiate_uri("/files/v1/{merchantId}/files/{fileId}", path_context)
        try:
            return self._communicator.get_with_binary_response(
                    uri,
                    self._client_headers,
                    None,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)
