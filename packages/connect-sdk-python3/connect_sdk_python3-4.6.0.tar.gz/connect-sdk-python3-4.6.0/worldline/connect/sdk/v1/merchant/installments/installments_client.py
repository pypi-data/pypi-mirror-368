#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Mapping, Optional

from worldline.connect.sdk.api_resource import ApiResource
from worldline.connect.sdk.call_context import CallContext
from worldline.connect.sdk.communication.response_exception import ResponseException
from worldline.connect.sdk.v1.domain.error_response import ErrorResponse
from worldline.connect.sdk.v1.domain.get_installment_request import GetInstallmentRequest
from worldline.connect.sdk.v1.domain.installment_options_response import InstallmentOptionsResponse
from worldline.connect.sdk.v1.exception_factory import create_exception


class InstallmentsClient(ApiResource):
    """
    Installments client. Thread-safe.
    """

    def __init__(self, parent: ApiResource, path_context: Optional[Mapping[str, str]]):
        """
        :param parent:       :class:`worldline.connect.sdk.api_resource.ApiResource`
        :param path_context: Mapping[str, str]
        """
        super(InstallmentsClient, self).__init__(parent=parent, path_context=path_context)

    def get_installments_info(self, body: GetInstallmentRequest, context: Optional[CallContext] = None) -> InstallmentOptionsResponse:
        """
        Resource /{merchantId}/installments/getInstallmentsInfo - Get installment information

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/installments/getInstallmentsInfo.html

        :param body:     :class:`worldline.connect.sdk.v1.domain.get_installment_request.GetInstallmentRequest`
        :param context:  :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.installment_options_response.InstallmentOptionsResponse`
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
        uri = self._instantiate_uri("/v1/{merchantId}/installments/getInstallmentsInfo", None)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    InstallmentOptionsResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)
