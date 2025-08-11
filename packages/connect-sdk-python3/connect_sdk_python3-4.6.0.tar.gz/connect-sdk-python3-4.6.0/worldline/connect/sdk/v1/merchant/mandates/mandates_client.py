#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Mapping, Optional

from worldline.connect.sdk.api_resource import ApiResource
from worldline.connect.sdk.call_context import CallContext
from worldline.connect.sdk.communication.response_exception import ResponseException
from worldline.connect.sdk.v1.domain.create_mandate_request import CreateMandateRequest
from worldline.connect.sdk.v1.domain.create_mandate_response import CreateMandateResponse
from worldline.connect.sdk.v1.domain.error_response import ErrorResponse
from worldline.connect.sdk.v1.domain.get_mandate_response import GetMandateResponse
from worldline.connect.sdk.v1.exception_factory import create_exception


class MandatesClient(ApiResource):
    """
    Mandates client. Thread-safe.
    """

    def __init__(self, parent: ApiResource, path_context: Optional[Mapping[str, str]]):
        """
        :param parent:       :class:`worldline.connect.sdk.api_resource.ApiResource`
        :param path_context: Mapping[str, str]
        """
        super(MandatesClient, self).__init__(parent=parent, path_context=path_context)

    def create(self, body: CreateMandateRequest, context: Optional[CallContext] = None) -> CreateMandateResponse:
        """
        Resource /{merchantId}/mandates - Create mandate

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/mandates/create.html

        :param body:     :class:`worldline.connect.sdk.v1.domain.create_mandate_request.CreateMandateRequest`
        :param context:  :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.create_mandate_response.CreateMandateResponse`
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
        uri = self._instantiate_uri("/v1/{merchantId}/mandates", None)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    CreateMandateResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def create_with_mandate_reference(self, unique_mandate_reference: str, body: CreateMandateRequest, context: Optional[CallContext] = None) -> CreateMandateResponse:
        """
        Resource /{merchantId}/mandates/{uniqueMandateReference} - Create mandate with mandatereference

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/mandates/createWithMandateReference.html

        :param unique_mandate_reference:  str
        :param body:                      :class:`worldline.connect.sdk.v1.domain.create_mandate_request.CreateMandateRequest`
        :param context:                   :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.create_mandate_response.CreateMandateResponse`
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
            "uniqueMandateReference": unique_mandate_reference,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/mandates/{uniqueMandateReference}", path_context)
        try:
            return self._communicator.put(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    CreateMandateResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def get(self, unique_mandate_reference: str, context: Optional[CallContext] = None) -> GetMandateResponse:
        """
        Resource /{merchantId}/mandates/{uniqueMandateReference} - Get mandate

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/mandates/get.html

        :param unique_mandate_reference:  str
        :param context:                   :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.get_mandate_response.GetMandateResponse`
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
            "uniqueMandateReference": unique_mandate_reference,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/mandates/{uniqueMandateReference}", path_context)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    None,
                    GetMandateResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def block(self, unique_mandate_reference: str, context: Optional[CallContext] = None) -> GetMandateResponse:
        """
        Resource /{merchantId}/mandates/{uniqueMandateReference}/block - Block mandate

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/mandates/block.html

        :param unique_mandate_reference:  str
        :param context:                   :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.get_mandate_response.GetMandateResponse`
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
            "uniqueMandateReference": unique_mandate_reference,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/mandates/{uniqueMandateReference}/block", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    None,
                    GetMandateResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def unblock(self, unique_mandate_reference: str, context: Optional[CallContext] = None) -> GetMandateResponse:
        """
        Resource /{merchantId}/mandates/{uniqueMandateReference}/unblock - Unblock mandate

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/mandates/unblock.html

        :param unique_mandate_reference:  str
        :param context:                   :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.get_mandate_response.GetMandateResponse`
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
            "uniqueMandateReference": unique_mandate_reference,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/mandates/{uniqueMandateReference}/unblock", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    None,
                    GetMandateResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def revoke(self, unique_mandate_reference: str, context: Optional[CallContext] = None) -> GetMandateResponse:
        """
        Resource /{merchantId}/mandates/{uniqueMandateReference}/revoke - Revoke mandate

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/mandates/revoke.html

        :param unique_mandate_reference:  str
        :param context:                   :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.get_mandate_response.GetMandateResponse`
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
            "uniqueMandateReference": unique_mandate_reference,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/mandates/{uniqueMandateReference}/revoke", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    None,
                    GetMandateResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)
