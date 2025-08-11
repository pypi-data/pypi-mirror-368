#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.api_resource import ApiResource
from worldline.connect.sdk.communication.response_exception import ResponseException
from worldline.connect.sdk.v1.domain.create_hosted_checkout_response import CreateHostedCheckoutResponse
from worldline.connect.sdk.v1.domain.error_response import ErrorResponse
from worldline.connect.sdk.v1.domain.get_hosted_checkout_response import GetHostedCheckoutResponse
from worldline.connect.sdk.v1.exception_factory import create_exception


class HostedcheckoutsClient(ApiResource):
    """
    Hostedcheckouts client. Thread-safe.
    """

    def __init__(self, parent, path_context):
        """
        :param parent:       :class:`worldline.connect.sdk.api_resource.ApiResource`
        :param path_context: dict[str, str]
        """
        super(HostedcheckoutsClient, self).__init__(parent=parent, path_context=path_context)

    def create(self, body, context=None):
        """
        Resource /{merchantId}/hostedcheckouts - Create hosted checkout

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/hostedcheckouts/create.html

        :param body:     :class:`worldline.connect.sdk.v1.domain.create_hosted_checkout_request.CreateHostedCheckoutRequest`
        :param context:  :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.create_hosted_checkout_response.CreateHostedCheckoutResponse`
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
        uri = self._instantiate_uri("/v1/{merchantId}/hostedcheckouts", None)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    CreateHostedCheckoutResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def get(self, hosted_checkout_id, context=None):
        """
        Resource /{merchantId}/hostedcheckouts/{hostedCheckoutId} - Get hosted checkout status

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/hostedcheckouts/get.html

        :param hosted_checkout_id:  str
        :param context:             :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.get_hosted_checkout_response.GetHostedCheckoutResponse`
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
            "hostedCheckoutId": hosted_checkout_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/hostedcheckouts/{hostedCheckoutId}", path_context)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    None,
                    GetHostedCheckoutResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def delete(self, hosted_checkout_id, context=None):
        """
        Resource /{merchantId}/hostedcheckouts/{hostedCheckoutId} - Delete hosted checkout

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/hostedcheckouts/delete.html

        :param hosted_checkout_id:  str
        :param context:             :class:`worldline.connect.sdk.call_context.CallContext`
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
            "hostedCheckoutId": hosted_checkout_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/hostedcheckouts/{hostedCheckoutId}", path_context)
        try:
            return self._communicator.delete(
                    uri,
                    self._client_headers,
                    None,
                    None,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)
