#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from webhooks_helper import WebhooksHelper
from worldline.connect.sdk.json.default_marshaller import DefaultMarshaller


class V1WebhooksFactory(object):
    """
    Worldline Global Collect platform factory for several v1 webhooks components.
    """

    @staticmethod
    def create_helper(secret_key_store, marshaller=None):
        """
        Creates a WebhooksHelper that will use the given SecretKeyStore.
        """
        if not marshaller:
            marshaller = DefaultMarshaller.instance()
        return WebhooksHelper(marshaller, secret_key_store)
