#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.webhooks.v1_webhooks_factory import V1WebhooksFactory


class Webhooks(object):
    """
    Worldline Global Collect platform factory for several webhooks components.
    """

    __V1 = V1WebhooksFactory()

    @staticmethod
    def v1() -> V1WebhooksFactory:
        return Webhooks.__V1
