#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Mapping, Optional

from worldline.connect.sdk.api_resource import ApiResource
from worldline.connect.sdk.call_context import CallContext
from worldline.connect.sdk.communication.response_exception import ResponseException
from worldline.connect.sdk.v1.domain.dispute_response import DisputeResponse
from worldline.connect.sdk.v1.domain.error_response import ErrorResponse
from worldline.connect.sdk.v1.domain.upload_dispute_file_response import UploadDisputeFileResponse
from worldline.connect.sdk.v1.merchant.disputes.upload_file_request import UploadFileRequest
from worldline.connect.sdk.v1.exception_factory import create_exception


class DisputesClient(ApiResource):
    """
    Disputes client. Thread-safe.
    """

    def __init__(self, parent: ApiResource, path_context: Optional[Mapping[str, str]]):
        """
        :param parent:       :class:`worldline.connect.sdk.api_resource.ApiResource`
        :param path_context: Mapping[str, str]
        """
        super(DisputesClient, self).__init__(parent=parent, path_context=path_context)

    def get(self, dispute_id: str, context: Optional[CallContext] = None) -> DisputeResponse:
        """
        Resource /{merchantId}/disputes/{disputeId} - Get dispute

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/disputes/get.html

        :param dispute_id:  str
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
            "disputeId": dispute_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/disputes/{disputeId}", path_context)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    None,
                    DisputeResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def submit(self, dispute_id: str, context: Optional[CallContext] = None) -> DisputeResponse:
        """
        Resource /{merchantId}/disputes/{disputeId}/submit - Submit dispute

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/disputes/submit.html

        :param dispute_id:  str
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
            "disputeId": dispute_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/disputes/{disputeId}/submit", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    None,
                    DisputeResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def cancel(self, dispute_id: str, context: Optional[CallContext] = None) -> DisputeResponse:
        """
        Resource /{merchantId}/disputes/{disputeId}/cancel - Cancel dispute

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/disputes/cancel.html

        :param dispute_id:  str
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
            "disputeId": dispute_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/disputes/{disputeId}/cancel", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    None,
                    DisputeResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def upload_file(self, dispute_id: str, body: UploadFileRequest, context: Optional[CallContext] = None) -> UploadDisputeFileResponse:
        """
        Resource /{merchantId}/disputes/{disputeId} - Upload File

        See also https://apireference.connect.worldline-solutions.com/fileserviceapi/v1/en_US/python/disputes/uploadFile.html

        :param dispute_id:  str
        :param body:        :class:`worldline.connect.sdk.v1.merchant.disputes.upload_file_request.UploadFileRequest`
        :param context:     :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.upload_dispute_file_response.UploadDisputeFileResponse`
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
            "disputeId": dispute_id,
        }
        uri = self._instantiate_uri("/files/v1/{merchantId}/disputes/{disputeId}", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    UploadDisputeFileResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)
