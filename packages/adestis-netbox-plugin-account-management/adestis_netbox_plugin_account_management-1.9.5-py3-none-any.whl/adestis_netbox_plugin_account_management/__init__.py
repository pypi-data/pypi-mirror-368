from netbox.plugins import PluginConfig
from .version import __version__


class AdestisAccountManagementConfig(PluginConfig):
    name = 'adestis_netbox_plugin_account_management'
    verbose_name = 'Account Management'
    description = 'A NetBox plugin for managing the ownership of accounts.'
    version = __version__
    author = 'ADESTIS GmbH'
    author_email = 'pypi@adestis.de'
    base_url = 'account-management'
    required_settings = []
    min_version = '4.1.0'
    max_version = '4.2.99'
    default_settings = {
        'top_level_menu': True,
    }


config = AdestisAccountManagementConfig
