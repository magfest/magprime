from uber.common import *
from magstock._version import __version__

config = parse_config(__file__)
static_overrides(join(config['module_root'], 'static'))
template_overrides(join(config['module_root'], 'templates'))


@Session.model_mixin
class Attendee:
    allergies    = Column(UnicodeText, default='')
    coming_with  = Column(UnicodeText, default='')
    coming_as    = Column(Choice(c.COMING_AS_OPTS), nullable=True)
    site_type    = Column(Choice(c.SITE_TYPE_OPTS), nullable=True)
    noise_level  = Column(Choice(c.NOISE_LEVEL_OPTS), nullable=True)
    camping_type = Column(Choice(c.CAMPING_TYPE_OPTS), nullable=True)

    @presave_adjustment
    def roughing_it(self):
        if self.site_type == c.PRIMITIVE and self.ribbon == c.NO_RIBBON:
            self.ribbon = c.ROUGHING_IT

Attendee._unrestricted.update({'allergies', 'coming_with', 'coming_as', 'site_type', 'noise_level', 'camping_type'})


@validation.Attendee
def camping_checks(attendee):
    if not attendee.placeholder:
        if not attendee.noise_level:
            return 'Noise Level is a required field'
        elif not attendee.site_type:
            return 'Site Type is a required field'
        elif not attendee.camping_type:
            return 'Please tell us how you are camping'
        elif not attendee.coming_as:
            return 'Please tell us whether you are leading a group'
        elif not attendee.coming_with:
            if attendee.coming_as == c.TENT_LEADER:
                return 'Please tell us who is in your camping group'
            else:
                return 'Please tell us who your camp leader is'


Session.initialize_db()
