from netbox.plugins import PluginConfig
from importlib.metadata import metadata
from pathlib import Path

plugin = metadata('netbox-cvexplorer')

class CVExplorerConfig(PluginConfig):
    name = plugin.get('Name').replace('-', '_')
    verbose_name = plugin.get('Name').replace('-', ' ').title()
    version = plugin.get('Version')
    description = plugin.get('Summary')
    author = plugin.get('Author')
    author_email = plugin.get('Author-email')
    base_url = "netbox_cvexplorer" # Base path to use for plugin URLs (optional). If not specified, the project's name will be used.
    min_version = '4.0'
    required_settings = []
    default_settings = {
        'top_level_menu': True,
        'static_image_directory': "netbox_cvexplorer/img"
    }
    caching_config = {
        '*': None
    }
    # menu_items = "navigation.menu_items" # The dotted path to the list of menu items provided by the plugin (default: navigation.menu_items)
    # menu = menu

config = CVExplorerConfig