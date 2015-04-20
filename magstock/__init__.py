from uber.common import *
from magstock._version import __version__

config = parse_config(__file__)
django.conf.settings.TEMPLATE_DIRS.insert(0, join(config['module_root'], 'templates'))


@Session.model_mixin
class Attendee:
    coming_with  = Column(UnicodeText, default='')
    site_type    = Column(Choice(c.SITE_TYPE_OPTS), nullable=True)
    noise_level  = Column(Choice(c.NOISE_LEVEL_OPTS), nullable=True)
    camping_type = Column(Choice(c.CAMPING_TYPE_OPTS), nullable=True)



Session.initialize_db()
