"""
BIS Data Provider Factory.
Provides a singleton instance of BaseBISDataProvider based on application settings.
"""
from app.core.config import settings
from app.services.data_providers.base_provider import BaseBISDataProvider
from app.services.data_providers.seed_provider import SeedBISDataProvider
from app.services.data_providers.live_provider import LiveBISDataProvider

_provider_instance: BaseBISDataProvider = None


def get_bis_data_provider() -> BaseBISDataProvider:
    """Returns configured singleton BaseBISDataProvider instance."""
    global _provider_instance
    if _provider_instance is None:
        provider_type = getattr(settings, "DATA_PROVIDER_TYPE", "seed").lower()
        if provider_type == "live":
            _provider_instance = LiveBISDataProvider()
        else:
            _provider_instance = SeedBISDataProvider()
    return _provider_instance
