#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Mapping, Optional

from worldline.connect.sdk.api_resource import ApiResource
from worldline.connect.sdk.call_context import CallContext
from worldline.connect.sdk.communication.response_exception import ResponseException
from worldline.connect.sdk.v1.domain.error_response import ErrorResponse
from worldline.connect.sdk.v1.domain.risk_assessment_bank_account import RiskAssessmentBankAccount
from worldline.connect.sdk.v1.domain.risk_assessment_card import RiskAssessmentCard
from worldline.connect.sdk.v1.domain.risk_assessment_response import RiskAssessmentResponse
from worldline.connect.sdk.v1.exception_factory import create_exception


class RiskassessmentsClient(ApiResource):
    """
    Riskassessments client. Thread-safe.
    """

    def __init__(self, parent: ApiResource, path_context: Optional[Mapping[str, str]]):
        """
        :param parent:       :class:`worldline.connect.sdk.api_resource.ApiResource`
        :param path_context: Mapping[str, str]
        """
        super(RiskassessmentsClient, self).__init__(parent=parent, path_context=path_context)

    def bankaccounts(self, body: RiskAssessmentBankAccount, context: Optional[CallContext] = None) -> RiskAssessmentResponse:
        """
        Resource /{merchantId}/riskassessments/bankaccounts - Risk-assess bankaccount

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/riskassessments/bankaccounts.html

        :param body:     :class:`worldline.connect.sdk.v1.domain.risk_assessment_bank_account.RiskAssessmentBankAccount`
        :param context:  :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.risk_assessment_response.RiskAssessmentResponse`
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
        uri = self._instantiate_uri("/v1/{merchantId}/riskassessments/bankaccounts", None)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    RiskAssessmentResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)

    def cards(self, body: RiskAssessmentCard, context: Optional[CallContext] = None) -> RiskAssessmentResponse:
        """
        Resource /{merchantId}/riskassessments/cards - Risk-assess card

        See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/riskassessments/cards.html

        :param body:     :class:`worldline.connect.sdk.v1.domain.risk_assessment_card.RiskAssessmentCard`
        :param context:  :class:`worldline.connect.sdk.call_context.CallContext`
        :return: :class:`worldline.connect.sdk.v1.domain.risk_assessment_response.RiskAssessmentResponse`
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
        uri = self._instantiate_uri("/v1/{merchantId}/riskassessments/cards", None)
        try:
            return self._communicator.post(
                    uri,
                    self._client_headers,
                    None,
                    body,
                    RiskAssessmentResponse,
                    context)

        except ResponseException as e:
            error_type = ErrorResponse
            error_object = self._communicator.marshaller.unmarshal(e.body, error_type)
            raise create_exception(e.status_code, e.body, error_object, context)
