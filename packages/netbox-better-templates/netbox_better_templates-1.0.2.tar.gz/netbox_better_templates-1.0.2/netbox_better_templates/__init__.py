from netbox.plugins import PluginConfig
from .monkey_patches import patch_config_template_render

class NetboxBetterTemplatesConfig(PluginConfig):
    name = 'netbox_better_templates'
    verbose_name = 'Better Templates'
    description = 'Adds new functionality to NetBox config templates.'
    author = 'radin-system'
    author_email = 'technical@rsto.ir'
    version = '1.0.1'
    base_url = 'better-templates'


    def ready(self):
        patch_config_template_render()


config = NetboxBetterTemplatesConfig