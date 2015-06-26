from uber.common import *
from magclassic._version import __version__

config = parse_config(__file__)
mount_site_sections(config['module_root'])
static_overrides(join(config['module_root'], 'static'))
template_overrides(join(config['module_root'], 'templates'))