#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Mapping, Optional

from worldline.connect.sdk.api_resource import ApiResource
from worldline.connect.sdk.call_context import CallContext
from worldline.connect.sdk.communication.response_exception import ResponseException
from worldline.connect.sdk.v1.domain.create_payment_product_session_request import CreatePaymentProductSessionRequest
from worldline.connect.sdk.v1.domain.create_payment_product_session_response import CreatePaymentProductSessionResponse
from worldline.connect.sdk.v1.domain.device_fingerprint_request import DeviceFingerprintRequest
from worldline.connect.sdk.v1.domain.device_fingerprint_response import DeviceFingerprintResponse
from worldline.connect.sdk.v1.domain.directory import Directory
from worldline.connect.sdk.v1.domain.error_response import ErrorResponse
from worldline.connect.sdk.v1.domain.get_customer_details_request import GetCustomerDetailsRequest
from worldline.connect.sdk.v1.domain.get_customer_details_response import GetCustomerDetailsResponse
from worldline.connect.sdk.v1.domain.payment_product_networks_response import PaymentProductNetworksResponse
from worldline.connect.sdk.v1.domain.payment_product_response import PaymentProductResponse
from worldline.connect.sdk.v1.domain.payment_products import PaymentProducts
from worldline.connect.sdk.v1.merchant.products.directory_params import DirectoryParams
from worldline.connect.sdk.v1.merchant.products.find_products_params import FindProductsParams
from worldline.connect.sdk.v1.merchant.products.get_product_params import GetProductParams
from worldline.connect.sdk.v1.merchant.products.networks_params import NetworksParams
from worldline.connect.sdk.v1.exception_factory import create_exception


class ProductsClient(ApiResource):
    """
    Products client. Thread-safe.
    """

    def __init__(self, parent: ApiResource, path_context: Optional[Mapping[str, str]]):
        """
        :param parent:       :class:`worldline.connect.sdk.api_resource.ApiResource`
        :param path_context: Mapping[str, str]
        """
        super(ProductsClient, self).__init__(parent=parent, path_context=path_context)

    def find(self, query: FindProductsParams, context: Optional[CallContext] = None) -> PaymentProducts:
        """
        Resource /{merchantId}/products - Get payment products

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/products/find.html

        :param query:    :class:`worldline.connect.sdk.v1.merchant.products.find_products_params.FindProductsParams`
        :param context:  :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.payment_products.PaymentProducts`
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
        uri = self._instantiate_uri("/v1/{merchantId}/products", None)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    query,
                    PaymentProducts,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def get(self, payment_product_id: int, query: GetProductParams, context: Optional[CallContext] = None) -> PaymentProductResponse:
        """
        Resource /{merchantId}/products/{paymentProductId} - Get payment product

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/products/get.html

        :param payment_product_id:  int
        :param query:               :class:`worldline.connect.sdk.v1.merchant.products.get_product_params.GetProductParams`
        :param context:             :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.payment_product_response.PaymentProductResponse`
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
            "paymentProductId": str(payment_product_id),
        }
        uri = self._instantiate_uri("/v1/{merchantId}/products/{paymentProductId}", path_context)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    query,
                    PaymentProductResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def directory(self, payment_product_id: int, query: DirectoryParams, context: Optional[CallContext] = None) -> Directory:
        """
        Resource /{merchantId}/products/{paymentProductId}/directory - Get payment product directory

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/products/directory.html

        :param payment_product_id:  int
        :param query:               :class:`worldline.connect.sdk.v1.merchant.products.directory_params.DirectoryParams`
        :param context:             :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.directory.Directory`
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
            "paymentProductId": str(payment_product_id),
        }
        uri = self._instantiate_uri("/v1/{merchantId}/products/{paymentProductId}/directory", path_context)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    query,
                    Directory,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def customer_details(self, payment_product_id: int, body: GetCustomerDetailsRequest, context: Optional[CallContext] = None) -> GetCustomerDetailsResponse:
        """
        Resource /{merchantId}/products/{paymentProductId}/customerDetails - Get customer details

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/products/customerDetails.html

        :param payment_product_id:  int
        :param body:                :class:`worldline.connect.sdk.v1.domain.get_customer_details_request.GetCustomerDetailsRequest`
        :param context:             :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.get_customer_details_response.GetCustomerDetailsResponse`
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
            "paymentProductId": str(payment_product_id),
        }
        uri = self._instantiate_uri("/v1/{merchantId}/products/{paymentProductId}/customerDetails", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    GetCustomerDetailsResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def device_fingerprint(self, payment_product_id: int, body: DeviceFingerprintRequest, context: Optional[CallContext] = None) -> DeviceFingerprintResponse:
        """
        Resource /{merchantId}/products/{paymentProductId}/deviceFingerprint - Get device fingerprint

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/products/deviceFingerprint.html

        :param payment_product_id:  int
        :param body:                :class:`worldline.connect.sdk.v1.domain.device_fingerprint_request.DeviceFingerprintRequest`
        :param context:             :class:`worldline.connect.sdk.call_context.CallContext`
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
            "paymentProductId": str(payment_product_id),
        }
        uri = self._instantiate_uri("/v1/{merchantId}/products/{paymentProductId}/deviceFingerprint", path_context)
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

    def networks(self, payment_product_id: int, query: NetworksParams, context: Optional[CallContext] = None) -> PaymentProductNetworksResponse:
        """
        Resource /{merchantId}/products/{paymentProductId}/networks - Get payment product networks

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/products/networks.html

        :param payment_product_id:  int
        :param query:               :class:`worldline.connect.sdk.v1.merchant.products.networks_params.NetworksParams`
        :param context:             :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.payment_product_networks_response.PaymentProductNetworksResponse`
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
            "paymentProductId": str(payment_product_id),
        }
        uri = self._instantiate_uri("/v1/{merchantId}/products/{paymentProductId}/networks", path_context)
        try:
            return self._communicator.get(
                    uri,
                    self._client_headers,
                    query,
                    PaymentProductNetworksResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def sessions(self, payment_product_id: int, body: CreatePaymentProductSessionRequest, context: Optional[CallContext] = None) -> CreatePaymentProductSessionResponse:
        """
        Resource /{merchantId}/products/{paymentProductId}/sessions - Create session for payment product

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/products/sessions.html

        :param payment_product_id:  int
        :param body:                :class:`worldline.connect.sdk.v1.domain.create_payment_product_session_request.CreatePaymentProductSessionRequest`
        :param context:             :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.create_payment_product_session_response.CreatePaymentProductSessionResponse`
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
            "paymentProductId": str(payment_product_id),
        }
        uri = self._instantiate_uri("/v1/{merchantId}/products/{paymentProductId}/sessions", path_context)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    CreatePaymentProductSessionResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)
