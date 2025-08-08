from django.utils.translation import gettext_lazy

from . import __version__

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    default = True
    name = "pretix_wallet"
    verbose_name = "Wallet"

    class PretixPluginMeta:
        name = gettext_lazy("Wallet")
        author = "Q Misell"
        description = gettext_lazy("Short description")
        visible = True
        version = __version__
        category = "PAYMENT"
        compatibility = "pretix>=2.7.0"
        settings_links = []
        navigation_links = []

    def ready(self):
        from django.conf import settings
        settings.MIDDLEWARE.append("pretix_wallet.middleware.CorsMiddleware")

        from . import signals  # NOQA
