#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.api_resource import ApiResource
from worldline.connect.sdk.communication.response_exception import ResponseException
from worldline.connect.sdk.v1.domain.cancel_approval_payment_response import CancelApprovalPaymentResponse
from worldline.connect.sdk.v1.domain.cancel_payment_response import CancelPaymentResponse
from worldline.connect.sdk.v1.domain.capture_response import CaptureResponse
from worldline.connect.sdk.v1.domain.captures_response import CapturesResponse
from worldline.connect.sdk.v1.domain.complete_payment_response import CompletePaymentResponse
from worldline.connect.sdk.v1.domain.create_payment_response import CreatePaymentResponse
from worldline.connect.sdk.v1.domain.create_token_response import CreateTokenResponse
from worldline.connect.sdk.v1.domain.device_fingerprint_details import DeviceFingerprintDetails
from worldline.connect.sdk.v1.domain.dispute_response import DisputeResponse
from worldline.connect.sdk.v1.domain.disputes_response import DisputesResponse
from worldline.connect.sdk.v1.domain.error_response import ErrorResponse
from worldline.connect.sdk.v1.domain.find_payments_response import FindPaymentsResponse
from worldline.connect.sdk.v1.domain.payment_approval_response import PaymentApprovalResponse
from worldline.connect.sdk.v1.domain.payment_error_response import PaymentErrorResponse
from worldline.connect.sdk.v1.domain.payment_response import PaymentResponse
from worldline.connect.sdk.v1.domain.refund_error_response import RefundErrorResponse
from worldline.connect.sdk.v1.domain.refund_response import RefundResponse
from worldline.connect.sdk.v1.domain.refunds_response import RefundsResponse
from worldline.connect.sdk.v1.domain.third_party_status_response import ThirdPartyStatusResponse
from worldline.connect.sdk.v1.exception_factory import create_exception


class PaymentsClient(ApiResource):
    """
    Payments client. Thread-safe.
    """

    def __init__(self, parent, path_context):
        """
        :param parent:       :class:`worldline.connect.sdk.api_resource.ApiResource`
        :param path_context: dict[str, str]
        """
        super(PaymentsClient, self).__init__(parent=parent, path_context=path_context)

    def create(self, body, context=None):
        """
        Resource /{merchantId}/payments - Create payment

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payments/create.html

        :param body:     :class:`worldline.connect.sdk.v1.domain.create_payment_request.CreatePaymentRequest`
        :param context:  :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.create_payment_response.CreatePaymentResponse`
        :raise DeclinedPaymentException: if the Worldline Global Collect platform declined / rejected the payment. The payment result will be available from the exception.
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
        uri = self._instantiate_uri("/v1/{merchantId}/payments", None)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    CreatePaymentResponse,
                    context)

        except ResponseException as e:
            error_type = PaymentErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def find(self, query, context=None):
        """
        Resource /{merchantId}/payments - Find payments

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payments/find.html

        :param query:    :class:`worldline.connect.sdk.v1.merchant.payments.find_payments_params.FindPaymentsParams`
        :param context:  :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.find_payments_response.FindPaymentsResponse`
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
        uri = self._instantiate_uri("/v1/{merchantId}/payments", None)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    query,
                    FindPaymentsResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def get(self, payment_id, context=None):
        """
        Resource /{merchantId}/payments/{paymentId} - Get payment

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payments/get.html

        :param payment_id:  str
        :param context:     :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.payment_response.PaymentResponse`
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
            "paymentId": payment_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/payments/{paymentId}", path_context)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    None,
                    PaymentResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def complete(self, payment_id, body, context=None):
        """
        Resource /{merchantId}/payments/{paymentId}/complete - Complete payment

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payments/complete.html

        :param payment_id:  str
        :param body:        :class:`worldline.connect.sdk.v1.domain.complete_payment_request.CompletePaymentRequest`
        :param context:     :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.complete_payment_response.CompletePaymentResponse`
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
            "paymentId": payment_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/payments/{paymentId}/complete", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    CompletePaymentResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def third_party_status(self, payment_id, context=None):
        """
        Resource /{merchantId}/payments/{paymentId}/thirdpartystatus - Third party status poll

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payments/thirdPartyStatus.html

        :param payment_id:  str
        :param context:     :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.third_party_status_response.ThirdPartyStatusResponse`
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
            "paymentId": payment_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/payments/{paymentId}/thirdpartystatus", path_context)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    None,
                    ThirdPartyStatusResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def tokenize(self, payment_id, body, context=None):
        """
        Resource /{merchantId}/payments/{paymentId}/tokenize - Create a token from payment

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payments/tokenize.html

        :param payment_id:  str
        :param body:        :class:`worldline.connect.sdk.v1.domain.tokenize_payment_request.TokenizePaymentRequest`
        :param context:     :class:`worldline.connect.sdk.call_context.CallContext`
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
        path_context = {
            "paymentId": payment_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/payments/{paymentId}/tokenize", path_context)
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

    def processchallenged(self, payment_id, context=None):
        """
        Resource /{merchantId}/payments/{paymentId}/processchallenged - Approves challenged payment

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payments/processchallenged.html

        :param payment_id:  str
        :param context:     :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.payment_response.PaymentResponse`
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
            "paymentId": payment_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/payments/{paymentId}/processchallenged", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    None,
                    PaymentResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def approve(self, payment_id, body, context=None):
        """
        Resource /{merchantId}/payments/{paymentId}/approve - Approve payment

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payments/approve.html

        :param payment_id:  str
        :param body:        :class:`worldline.connect.sdk.v1.domain.approve_payment_request.ApprovePaymentRequest`
        :param context:     :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.payment_approval_response.PaymentApprovalResponse`
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
            "paymentId": payment_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/payments/{paymentId}/approve", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    PaymentApprovalResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def capture(self, payment_id, body, context=None):
        """
        Resource /{merchantId}/payments/{paymentId}/capture - Capture payment

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payments/capture.html

        :param payment_id:  str
        :param body:        :class:`worldline.connect.sdk.v1.domain.capture_payment_request.CapturePaymentRequest`
        :param context:     :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.capture_response.CaptureResponse`
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
            "paymentId": payment_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/payments/{paymentId}/capture", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    CaptureResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def cancelapproval(self, payment_id, context=None):
        """
        Resource /{merchantId}/payments/{paymentId}/cancelapproval - Undo capture payment

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payments/cancelapproval.html

        :param payment_id:  str
        :param context:     :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.cancel_approval_payment_response.CancelApprovalPaymentResponse`
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
            "paymentId": payment_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/payments/{paymentId}/cancelapproval", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    None,
                    CancelApprovalPaymentResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def captures(self, payment_id, context=None):
        """
        Resource /{merchantId}/payments/{paymentId}/captures - Get captures of payment

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payments/captures.html

        :param payment_id:  str
        :param context:     :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.captures_response.CapturesResponse`
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
            "paymentId": payment_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/payments/{paymentId}/captures", path_context)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    None,
                    CapturesResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def refund(self, payment_id, body, context=None):
        """
        Resource /{merchantId}/payments/{paymentId}/refund - Create refund

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payments/refund.html

        :param payment_id:  str
        :param body:        :class:`worldline.connect.sdk.v1.domain.refund_request.RefundRequest`
        :param context:     :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.refund_response.RefundResponse`
        :raise DeclinedRefundException: if the Worldline Global Collect platform declined / rejected the refund. The refund result will be available from the exception.
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
            "paymentId": payment_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/payments/{paymentId}/refund", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    RefundResponse,
                    context)

        except ResponseException as e:
            error_type = RefundErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def refunds(self, payment_id, context=None):
        """
        Resource /{merchantId}/payments/{paymentId}/refunds - Get refunds of payment

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payments/refunds.html

        :param payment_id:  str
        :param context:     :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.refunds_response.RefundsResponse`
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
            "paymentId": payment_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/payments/{paymentId}/refunds", path_context)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    None,
                    RefundsResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def cancel(self, payment_id, context=None):
        """
        Resource /{merchantId}/payments/{paymentId}/cancel - Cancel payment

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payments/cancel.html

        :param payment_id:  str
        :param context:     :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.cancel_payment_response.CancelPaymentResponse`
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
            "paymentId": payment_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/payments/{paymentId}/cancel", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    None,
                    CancelPaymentResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def dispute(self, payment_id, body, context=None):
        """
        Resource /{merchantId}/payments/{paymentId}/dispute - Create dispute

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payments/dispute.html

        :param payment_id:  str
        :param body:        :class:`worldline.connect.sdk.v1.domain.create_dispute_request.CreateDisputeRequest`
        :param context:     :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.dispute_response.DisputeResponse`
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
            "paymentId": payment_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/payments/{paymentId}/dispute", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    DisputeResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def disputes(self, payment_id, context=None):
        """
        Resource /{merchantId}/payments/{paymentId}/disputes - Get disputes

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payments/disputes.html

        :param payment_id:  str
        :param context:     :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.disputes_response.DisputesResponse`
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
            "paymentId": payment_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/payments/{paymentId}/disputes", path_context)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    None,
                    DisputesResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def devicefingerprint(self, payment_id, context=None):
        """
        Resource /{merchantId}/payments/{paymentId}/devicefingerprint - Get Device Fingerprint details

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payments/devicefingerprint.html

        :param payment_id:  str
        :param context:     :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.device_fingerprint_details.DeviceFingerprintDetails`
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
            "paymentId": payment_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/payments/{paymentId}/devicefingerprint", path_context)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    None,
                    DeviceFingerprintDetails,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)
