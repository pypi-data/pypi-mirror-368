#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.api_resource import ApiResource
from worldline.connect.sdk.communication.response_exception import ResponseException
from worldline.connect.sdk.v1.domain.create_token_response import CreateTokenResponse
from worldline.connect.sdk.v1.domain.error_response import ErrorResponse
from worldline.connect.sdk.v1.domain.token_response import TokenResponse
from worldline.connect.sdk.v1.exception_factory import create_exception


class TokensClient(ApiResource):
    """
    Tokens client. Thread-safe.
    """

    def __init__(self, parent, path_context):
        """
        :param parent:       :class:`worldline.connect.sdk.api_resource.ApiResource`
        :param path_context: dict[str, str]
        """
        super(TokensClient, self).__init__(parent=parent, path_context=path_context)

    def create(self, body, context=None):
        """
        Resource /{merchantId}/tokens - Create token

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/tokens/create.html

        :param body:     :class:`worldline.connect.sdk.v1.domain.create_token_request.CreateTokenRequest`
        :param context:  :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.create_token_response.CreateTokenResponse`
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
        uri = self._instantiate_uri("/v1/{merchantId}/tokens", None)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    CreateTokenResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def get(self, token_id, context=None):
        """
        Resource /{merchantId}/tokens/{tokenId} - Get token

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/tokens/get.html

        :param token_id:  str
        :param context:   :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.token_response.TokenResponse`
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
            "tokenId": token_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/tokens/{tokenId}", path_context)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    None,
                    TokenResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def update(self, token_id, body, context=None):
        """
        Resource /{merchantId}/tokens/{tokenId} - Update token

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/tokens/update.html

        :param token_id:  str
        :param body:      :class:`worldline.connect.sdk.v1.domain.update_token_request.UpdateTokenRequest`
        :param context:   :class:`worldline.connect.sdk.call_context.CallContext`
        :return: None
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
            "tokenId": token_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/tokens/{tokenId}", path_context)
        try:
            return self._communicator.put(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    None,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def delete(self, token_id, query, context=None):
        """
        Resource /{merchantId}/tokens/{tokenId} - Delete token

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/tokens/delete.html

        :param token_id:  str
        :param query:     :class:`worldline.connect.sdk.v1.merchant.tokens.delete_token_params.DeleteTokenParams`
        :param context:   :class:`worldline.connect.sdk.call_context.CallContext`
        :return: None
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
            "tokenId": token_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/tokens/{tokenId}", path_context)
        try:
            return self._communicator.delete(
                    uri,
                    self._client_headers,
                    query,
                    None,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def approvesepadirectdebit(self, token_id, body, context=None):
        """
        Resource /{merchantId}/tokens/{tokenId}/approvesepadirectdebit - Approve SEPA DD mandate

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/tokens/approvesepadirectdebit.html

        :param token_id:  str
        :param body:      :class:`worldline.connect.sdk.v1.domain.approve_token_request.ApproveTokenRequest`
        :param context:   :class:`worldline.connect.sdk.call_context.CallContext`
        :return: None
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
            "tokenId": token_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/tokens/{tokenId}/approvesepadirectdebit", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    None,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)
