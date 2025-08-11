#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Mapping, Optional

from worldline.connect.sdk.api_resource import ApiResource
from worldline.connect.sdk.call_context import CallContext
from worldline.connect.sdk.communication.response_exception import ResponseException
from worldline.connect.sdk.v1.domain.approve_refund_request import ApproveRefundRequest
from worldline.connect.sdk.v1.domain.error_response import ErrorResponse
from worldline.connect.sdk.v1.domain.find_refunds_response import FindRefundsResponse
from worldline.connect.sdk.v1.domain.refund_response import RefundResponse
from worldline.connect.sdk.v1.merchant.refunds.find_refunds_params import FindRefundsParams
from worldline.connect.sdk.v1.exception_factory import create_exception


class RefundsClient(ApiResource):
    """
    Refunds client. Thread-safe.
    """

    def __init__(self, parent: ApiResource, path_context: Optional[Mapping[str, str]]):
        """
        :param parent:       :class:`worldline.connect.sdk.api_resource.ApiResource`
        :param path_context: Mapping[str, str]
        """
        super(RefundsClient, self).__init__(parent=parent, path_context=path_context)

    def find(self, query: FindRefundsParams, context: Optional[CallContext] = None) -> FindRefundsResponse:
        """
        Resource /{merchantId}/refunds - Find refunds

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/refunds/find.html

        :param query:    :class:`worldline.connect.sdk.v1.merchant.refunds.find_refunds_params.FindRefundsParams`
        :param context:  :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.find_refunds_response.FindRefundsResponse`
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
        uri = self._instantiate_uri("/v1/{merchantId}/refunds", None)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    query,
                    FindRefundsResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def get(self, refund_id: str, context: Optional[CallContext] = None) -> RefundResponse:
        """
        Resource /{merchantId}/refunds/{refundId} - Get refund

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/refunds/get.html

        :param refund_id:  str
        :param context:    :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.refund_response.RefundResponse`
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
            "refundId": refund_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/refunds/{refundId}", path_context)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    None,
                    RefundResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def approve(self, refund_id: str, body: ApproveRefundRequest, context: Optional[CallContext] = None) -> None:
        """
        Resource /{merchantId}/refunds/{refundId}/approve - Approve refund

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/refunds/approve.html

        :param refund_id:  str
        :param body:       :class:`worldline.connect.sdk.v1.domain.approve_refund_request.ApproveRefundRequest`
        :param context:    :class:`worldline.connect.sdk.call_context.CallContext`
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
            "refundId": refund_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/refunds/{refundId}/approve", path_context)
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

    def cancel(self, refund_id: str, context: Optional[CallContext] = None) -> None:
        """
        Resource /{merchantId}/refunds/{refundId}/cancel - Cancel refund

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/refunds/cancel.html

        :param refund_id:  str
        :param context:    :class:`worldline.connect.sdk.call_context.CallContext`
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
            "refundId": refund_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/refunds/{refundId}/cancel", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    None,
                    None,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def cancelapproval(self, refund_id: str, context: Optional[CallContext] = None) -> None:
        """
        Resource /{merchantId}/refunds/{refundId}/cancelapproval - Undo approve refund

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/refunds/cancelapproval.html

        :param refund_id:  str
        :param context:    :class:`worldline.connect.sdk.call_context.CallContext`
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
            "refundId": refund_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/refunds/{refundId}/cancelapproval", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    None,
                    None,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)
