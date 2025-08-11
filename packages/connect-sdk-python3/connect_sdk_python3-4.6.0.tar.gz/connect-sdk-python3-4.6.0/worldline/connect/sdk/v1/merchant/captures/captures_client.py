#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Mapping, Optional

from worldline.connect.sdk.api_resource import ApiResource
from worldline.connect.sdk.call_context import CallContext
from worldline.connect.sdk.communication.response_exception import ResponseException
from worldline.connect.sdk.v1.domain.capture_response import CaptureResponse
from worldline.connect.sdk.v1.domain.error_response import ErrorResponse
from worldline.connect.sdk.v1.domain.refund_error_response import RefundErrorResponse
from worldline.connect.sdk.v1.domain.refund_request import RefundRequest
from worldline.connect.sdk.v1.domain.refund_response import RefundResponse
from worldline.connect.sdk.v1.exception_factory import create_exception


class CapturesClient(ApiResource):
    """
    Captures client. Thread-safe.
    """

    def __init__(self, parent: ApiResource, path_context: Optional[Mapping[str, str]]):
        """
        :param parent:       :class:`worldline.connect.sdk.api_resource.ApiResource`
        :param path_context: Mapping[str, str]
        """
        super(CapturesClient, self).__init__(parent=parent, path_context=path_context)

    def get(self, capture_id: str, context: Optional[CallContext] = None) -> CaptureResponse:
        """
        Resource /{merchantId}/captures/{captureId} - Get capture

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/captures/get.html

        :param capture_id:  str
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
            "captureId": capture_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/captures/{captureId}", path_context)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    None,
                    CaptureResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def refund(self, capture_id: str, body: RefundRequest, context: Optional[CallContext] = None) -> RefundResponse:
        """
        Resource /{merchantId}/captures/{captureId}/refund - Create Refund

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/captures/refund.html

        :param capture_id:  str
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
            "captureId": capture_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/captures/{captureId}/refund", path_context)
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
