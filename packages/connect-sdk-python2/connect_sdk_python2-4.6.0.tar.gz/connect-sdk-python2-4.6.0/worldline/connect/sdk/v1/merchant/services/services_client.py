#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.api_resource import ApiResource
from worldline.connect.sdk.communication.response_exception import ResponseException
from worldline.connect.sdk.v1.domain.bank_details_response import BankDetailsResponse
from worldline.connect.sdk.v1.domain.convert_amount import ConvertAmount
from worldline.connect.sdk.v1.domain.error_response import ErrorResponse
from worldline.connect.sdk.v1.domain.get_iin_details_response import GetIINDetailsResponse
from worldline.connect.sdk.v1.domain.get_privacy_policy_response import GetPrivacyPolicyResponse
from worldline.connect.sdk.v1.domain.test_connection import TestConnection
from worldline.connect.sdk.v1.exception_factory import create_exception


class ServicesClient(ApiResource):
    """
    Services client. Thread-safe.
    """

    def __init__(self, parent, path_context):
        """
        :param parent:       :class:`worldline.connect.sdk.api_resource.ApiResource`
        :param path_context: dict[str, str]
        """
        super(ServicesClient, self).__init__(parent=parent, path_context=path_context)

    def convert_amount(self, query, context=None):
        """
        Resource /{merchantId}/services/convert/amount - Convert amount

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/services/convertAmount.html

        :param query:    :class:`worldline.connect.sdk.v1.merchant.services.convert_amount_params.ConvertAmountParams`
        :param context:  :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.convert_amount.ConvertAmount`
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
        uri = self._instantiate_uri("/v1/{merchantId}/services/convert/amount", None)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    query,
                    ConvertAmount,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def bankaccount(self, body, context=None):
        """
        Resource /{merchantId}/services/convert/bankaccount - Convert bankaccount

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/services/bankaccount.html

        :param body:     :class:`worldline.connect.sdk.v1.domain.bank_details_request.BankDetailsRequest`
        :param context:  :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.bank_details_response.BankDetailsResponse`
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
        uri = self._instantiate_uri("/v1/{merchantId}/services/convert/bankaccount", None)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    BankDetailsResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def get_iin_details(self, body, context=None):
        """
        Resource /{merchantId}/services/getIINdetails - Get IIN details

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/services/getIINdetails.html

        :param body:     :class:`worldline.connect.sdk.v1.domain.get_iin_details_request.GetIINDetailsRequest`
        :param context:  :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.get_iin_details_response.GetIINDetailsResponse`
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
        uri = self._instantiate_uri("/v1/{merchantId}/services/getIINdetails", None)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    GetIINDetailsResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def privacypolicy(self, query, context=None):
        """
        Resource /{merchantId}/services/privacypolicy - Get privacy policy

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/services/privacypolicy.html

        :param query:    :class:`worldline.connect.sdk.v1.merchant.services.privacypolicy_params.PrivacypolicyParams`
        :param context:  :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.get_privacy_policy_response.GetPrivacyPolicyResponse`
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
        uri = self._instantiate_uri("/v1/{merchantId}/services/privacypolicy", None)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    query,
                    GetPrivacyPolicyResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def testconnection(self, context=None):
        """
        Resource /{merchantId}/services/testconnection - Test connection

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/services/testconnection.html

        :param context:  :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.test_connection.TestConnection`
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
        uri = self._instantiate_uri("/v1/{merchantId}/services/testconnection", None)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    None,
                    TestConnection,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)
