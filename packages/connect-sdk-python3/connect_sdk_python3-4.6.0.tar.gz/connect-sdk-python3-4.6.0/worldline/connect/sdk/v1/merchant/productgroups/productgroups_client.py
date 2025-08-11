#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Mapping, Optional

from worldline.connect.sdk.api_resource import ApiResource
from worldline.connect.sdk.call_context import CallContext
from worldline.connect.sdk.communication.response_exception import ResponseException
from worldline.connect.sdk.v1.domain.device_fingerprint_request import DeviceFingerprintRequest
from worldline.connect.sdk.v1.domain.device_fingerprint_response import DeviceFingerprintResponse
from worldline.connect.sdk.v1.domain.error_response import ErrorResponse
from worldline.connect.sdk.v1.domain.payment_product_group_response import PaymentProductGroupResponse
from worldline.connect.sdk.v1.domain.payment_product_groups import PaymentProductGroups
from worldline.connect.sdk.v1.merchant.productgroups.find_productgroups_params import FindProductgroupsParams
from worldline.connect.sdk.v1.merchant.productgroups.get_productgroup_params import GetProductgroupParams
from worldline.connect.sdk.v1.exception_factory import create_exception


class ProductgroupsClient(ApiResource):
    """
    Productgroups client. Thread-safe.
    """

    def __init__(self, parent: ApiResource, path_context: Optional[Mapping[str, str]]):
        """
        :param parent:       :class:`worldline.connect.sdk.api_resource.ApiResource`
        :param path_context: Mapping[str, str]
        """
        super(ProductgroupsClient, self).__init__(parent=parent, path_context=path_context)

    def find(self, query: FindProductgroupsParams, context: Optional[CallContext] = None) -> PaymentProductGroups:
        """
        Resource /{merchantId}/productgroups - Get payment product groups

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/productgroups/find.html

        :param query:    :class:`worldline.connect.sdk.v1.merchant.productgroups.find_productgroups_params.FindProductgroupsParams`
        :param context:  :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.payment_product_groups.PaymentProductGroups`
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
        uri = self._instantiate_uri("/v1/{merchantId}/productgroups", None)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    query,
                    PaymentProductGroups,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def get(self, payment_product_group_id: str, query: GetProductgroupParams, context: Optional[CallContext] = None) -> PaymentProductGroupResponse:
        """
        Resource /{merchantId}/productgroups/{paymentProductGroupId} - Get payment product group

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/productgroups/get.html

        :param payment_product_group_id:  str
        :param query:                     :class:`worldline.connect.sdk.v1.merchant.productgroups.get_productgroup_params.GetProductgroupParams`
        :param context:                   :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.payment_product_group_response.PaymentProductGroupResponse`
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
            "paymentProductGroupId": payment_product_group_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/productgroups/{paymentProductGroupId}", path_context)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    query,
                    PaymentProductGroupResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def device_fingerprint(self, payment_product_group_id: str, body: DeviceFingerprintRequest, context: Optional[CallContext] = None) -> DeviceFingerprintResponse:
        """
        Resource /{merchantId}/productgroups/{paymentProductGroupId}/deviceFingerprint - Get device fingerprint

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/productgroups/deviceFingerprint.html

        :param payment_product_group_id:  str
        :param body:                      :class:`worldline.connect.sdk.v1.domain.device_fingerprint_request.DeviceFingerprintRequest`
        :param context:                   :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.device_fingerprint_response.DeviceFingerprintResponse`
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
            "paymentProductGroupId": payment_product_group_id,
        }
        uri = self._instantiate_uri("/v1/{merchantId}/productgroups/{paymentProductGroupId}/deviceFingerprint", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    DeviceFingerprintResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)
