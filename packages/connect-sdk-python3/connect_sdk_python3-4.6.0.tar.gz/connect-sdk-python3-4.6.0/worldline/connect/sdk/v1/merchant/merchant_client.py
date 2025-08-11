#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Mapping, Optional

from worldline.connect.sdk.api_resource import ApiResource
from worldline.connect.sdk.v1.merchant.captures.captures_client import CapturesClient
from worldline.connect.sdk.v1.merchant.disputes.disputes_client import DisputesClient
from worldline.connect.sdk.v1.merchant.files.files_client import FilesClient
from worldline.connect.sdk.v1.merchant.hostedcheckouts.hostedcheckouts_client import HostedcheckoutsClient
from worldline.connect.sdk.v1.merchant.hostedmandatemanagements.hostedmandatemanagements_client import HostedmandatemanagementsClient
from worldline.connect.sdk.v1.merchant.installments.installments_client import InstallmentsClient
from worldline.connect.sdk.v1.merchant.mandates.mandates_client import MandatesClient
from worldline.connect.sdk.v1.merchant.payments.payments_client import PaymentsClient
from worldline.connect.sdk.v1.merchant.payouts.payouts_client import PayoutsClient
from worldline.connect.sdk.v1.merchant.productgroups.productgroups_client import ProductgroupsClient
from worldline.connect.sdk.v1.merchant.products.products_client import ProductsClient
from worldline.connect.sdk.v1.merchant.refunds.refunds_client import RefundsClient
from worldline.connect.sdk.v1.merchant.riskassessments.riskassessments_client import RiskassessmentsClient
from worldline.connect.sdk.v1.merchant.services.services_client import ServicesClient
from worldline.connect.sdk.v1.merchant.sessions.sessions_client import SessionsClient
from worldline.connect.sdk.v1.merchant.tokens.tokens_client import TokensClient


class MerchantClient(ApiResource):
    """
    Merchant client. Thread-safe.
    """

    def __init__(self, parent: ApiResource, path_context: Optional[Mapping[str, str]]):
        """
        :param parent:       :class:`worldline.connect.sdk.api_resource.ApiResource`
        :param path_context: Mapping[str, str]
        """
        super(MerchantClient, self).__init__(parent=parent, path_context=path_context)

    def hostedcheckouts(self) -> HostedcheckoutsClient:
        """
        Resource /{merchantId}/hostedcheckouts

        :return: :class:`worldline.connect.sdk.v1.merchant.hostedcheckouts.hostedcheckouts_client.HostedcheckoutsClient`
        """
        return HostedcheckoutsClient(self, None)

    def hostedmandatemanagements(self) -> HostedmandatemanagementsClient:
        """
        Resource /{merchantId}/hostedmandatemanagements

        :return: :class:`worldline.connect.sdk.v1.merchant.hostedmandatemanagements.hostedmandatemanagements_client.HostedmandatemanagementsClient`
        """
        return HostedmandatemanagementsClient(self, None)

    def payments(self) -> PaymentsClient:
        """
        Resource /{merchantId}/payments

        :return: :class:`worldline.connect.sdk.v1.merchant.payments.payments_client.PaymentsClient`
        """
        return PaymentsClient(self, None)

    def captures(self) -> CapturesClient:
        """
        Resource /{merchantId}/captures

        :return: :class:`worldline.connect.sdk.v1.merchant.captures.captures_client.CapturesClient`
        """
        return CapturesClient(self, None)

    def refunds(self) -> RefundsClient:
        """
        Resource /{merchantId}/refunds

        :return: :class:`worldline.connect.sdk.v1.merchant.refunds.refunds_client.RefundsClient`
        """
        return RefundsClient(self, None)

    def disputes(self) -> DisputesClient:
        """
        Resource /{merchantId}/disputes

        :return: :class:`worldline.connect.sdk.v1.merchant.disputes.disputes_client.DisputesClient`
        """
        return DisputesClient(self, None)

    def payouts(self) -> PayoutsClient:
        """
        Resource /{merchantId}/payouts

        :return: :class:`worldline.connect.sdk.v1.merchant.payouts.payouts_client.PayoutsClient`
        """
        return PayoutsClient(self, None)

    def productgroups(self) -> ProductgroupsClient:
        """
        Resource /{merchantId}/productgroups

        :return: :class:`worldline.connect.sdk.v1.merchant.productgroups.productgroups_client.ProductgroupsClient`
        """
        return ProductgroupsClient(self, None)

    def products(self) -> ProductsClient:
        """
        Resource /{merchantId}/products

        :return: :class:`worldline.connect.sdk.v1.merchant.products.products_client.ProductsClient`
        """
        return ProductsClient(self, None)

    def riskassessments(self) -> RiskassessmentsClient:
        """
        Resource /{merchantId}/riskassessments

        :return: :class:`worldline.connect.sdk.v1.merchant.riskassessments.riskassessments_client.RiskassessmentsClient`
        """
        return RiskassessmentsClient(self, None)

    def services(self) -> ServicesClient:
        """
        Resource /{merchantId}/services

        :return: :class:`worldline.connect.sdk.v1.merchant.services.services_client.ServicesClient`
        """
        return ServicesClient(self, None)

    def tokens(self) -> TokensClient:
        """
        Resource /{merchantId}/tokens

        :return: :class:`worldline.connect.sdk.v1.merchant.tokens.tokens_client.TokensClient`
        """
        return TokensClient(self, None)

    def mandates(self) -> MandatesClient:
        """
        Resource /{merchantId}/mandates

        :return: :class:`worldline.connect.sdk.v1.merchant.mandates.mandates_client.MandatesClient`
        """
        return MandatesClient(self, None)

    def sessions(self) -> SessionsClient:
        """
        Resource /{merchantId}/sessions

        :return: :class:`worldline.connect.sdk.v1.merchant.sessions.sessions_client.SessionsClient`
        """
        return SessionsClient(self, None)

    def installments(self) -> InstallmentsClient:
        """
        Resource /{merchantId}/installments

        :return: :class:`worldline.connect.sdk.v1.merchant.installments.installments_client.InstallmentsClient`
        """
        return InstallmentsClient(self, None)

    def files(self) -> FilesClient:
        """
        Resource /{merchantId}/files

        :return: :class:`worldline.connect.sdk.v1.merchant.files.files_client.FilesClient`
        """
        return FilesClient(self, None)
