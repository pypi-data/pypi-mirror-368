#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Mapping, Optional

from worldline.connect.sdk.api_resource import ApiResource
from worldline.connect.sdk.call_context import CallContext
from worldline.connect.sdk.communication.response_exception import ResponseException
from worldline.connect.sdk.v1.domain.approve_payout_request import ApprovePayoutRequest
from worldline.connect.sdk.v1.domain.create_payout_request import CreatePayoutRequest
from worldline.connect.sdk.v1.domain.error_response import ErrorResponse
from worldline.connect.sdk.v1.domain.find_payouts_response import FindPayoutsResponse
from worldline.connect.sdk.v1.domain.payout_error_response import PayoutErrorResponse
from worldline.connect.sdk.v1.domain.payout_response import PayoutResponse
from worldline.connect.sdk.v1.merchant.payouts.find_payouts_params import FindPayoutsParams
from worldline.connect.sdk.v1.exception_factory import create_exception


class PayoutsClient(ApiResource):
    """
    Payouts client. Thread-safe.
    """

    def __init__(self, parent: ApiResource, path_context: Optional[Mapping[str, str]]):
        """
        :param parent:       :class:`worldline.connect.sdk.api_resource.ApiResource`
        :param path_context: Mapping[str, str]
        """
        super(PayoutsClient, self).__init__(parent=parent, path_context=path_context)

    def create(self, body: CreatePayoutRequest, context: Optional[CallContext] = None) -> PayoutResponse:
        """
        Resource /{merchantId}/payouts - Create payout

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payouts/create.html

        :param body:     :class:`worldline.connect.sdk.v1.domain.create_payout_request.CreatePayoutRequest`
        :param context:  :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.payout_response.PayoutResponse`
        :raise DeclinedPayoutException: if the Worldline Global Collect platform declined / rejected the payout. The payout result will be available from the exception.
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
        uri = self._instantiate_uri("/v1/{merchantId}/payouts", None)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    PayoutResponse,
                    context)

        except ResponseException as e:
            error_type = PayoutErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def find(self, query: FindPayoutsParams, context: Optional[CallContext] = None) -> FindPayoutsResponse:
        """
        Resource /{merchantId}/payouts - Find payouts

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payouts/find.html

        :param query:    :class:`worldline.connect.sdk.v1.merchant.payouts.find_payouts_params.FindPayoutsParams`
        :param context:  :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.find_payouts_response.FindPayoutsResponse`
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
        uri = self._instantiate_uri("/v1/{merchantId}/payouts", None)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    query,
                    FindPayoutsResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def get(self, payout_id: str, context: Optional[CallContext] = None) -> PayoutResponse:
        """
        Resource /{merchantId}/payouts/{payoutId} - Get payout

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payouts/get.html

        :param payout_id:  str
        :param context:    :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.payout_response.PayoutResponse`
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
            "payoutId": payout_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/payouts/{payoutId}", path_context)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    None,
                    PayoutResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def approve(self, payout_id: str, body: ApprovePayoutRequest, context: Optional[CallContext] = None) -> PayoutResponse:
        """
        Resource /{merchantId}/payouts/{payoutId}/approve - Approve payout

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payouts/approve.html

        :param payout_id:  str
        :param body:       :class:`worldline.connect.sdk.v1.domain.approve_payout_request.ApprovePayoutRequest`
        :param context:    :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.payout_response.PayoutResponse`
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
            "payoutId": payout_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/payouts/{payoutId}/approve", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    PayoutResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def cancel(self, payout_id: str, context: Optional[CallContext] = None) -> None:
        """
        Resource /{merchantId}/payouts/{payoutId}/cancel - Cancel payout

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payouts/cancel.html

        :param payout_id:  str
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
            "payoutId": payout_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/payouts/{payoutId}/cancel", path_context)
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

    def cancelapproval(self, payout_id: str, context: Optional[CallContext] = None) -> None:
        """
        Resource /{merchantId}/payouts/{payoutId}/cancelapproval - Undo approve payout

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payouts/cancelapproval.html

        :param payout_id:  str
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
            "payoutId": payout_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/payouts/{payoutId}/cancelapproval", path_context)
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
