from os.path import join

import cherrypy
import uber
from sideboard.lib import parse_config
from uber.config import c, Config, dynamic
from uber.errors import HTTPRedirect
from uber.jinja import template_overrides
from uber.models import Attendee, Session
from uber.utils import mount_site_sections, static_overrides

from magprime._version import __version__  # noqa: F401


magprime_config = parse_config(__file__)
static_overrides(join(magprime_config['module_root'], 'static'))
template_overrides(join(magprime_config['module_root'], 'templates'))


@Config.mixin
class ExtraConfig:
    @property
    @dynamic
    def SEASON_BADGE_PRICE(self):
        return self.BADGE_PRICE + self.SEASON_LEVEL

    @property
    def SEASON_EVENTS(self):
        return magprime_config['season_events']

    @property
    def PREREG_BADGE_TYPES(self):
        types = [self.ATTENDEE_BADGE, self.PSEUDO_DEALER_BADGE, self.CHILD_BADGE]
        for reg_open, badge_type in [(self.BEFORE_GROUP_PREREG_TAKEDOWN, self.PSEUDO_GROUP_BADGE)]:
            if reg_open:
                types.append(badge_type)
        return types

    @property
    def DEALER_REG_OPEN(self):
        return self.AFTER_DEALER_REG_START and self.BEFORE_DEALER_REG_SHUTDOWN and not self.DEALER_REG_SOFT_CLOSED


# These need to come last so they can make use of config properties
from magprime.utils import *  # noqa: F401,E402,F403
from magprime.models import *  # noqa: F401,E402,F403
from magprime.automated_emails import *  # noqa: F401,E402,F403
from magprime.model_checks import *  # noqa: F401,E402,F403

# Silence pyflakes
from magprime.models import PrevSeasonSupporter  # noqa: E402


@Session.model_mixin
class SessionMixin:
    def season_pass(self, id):
        pss = self.query(PrevSeasonSupporter).filter_by(id=id).all()
        if pss:
            return pss[0]
        else:
            attendee = self.attendee(id)
            assert attendee.amount_extra >= c.SEASON_LEVEL
            return attendee

    def season_passes(self):
        attendees = {a.email: a for a in self.query(Attendee).filter(Attendee.amount_extra >= c.SEASON_LEVEL).all()}
        prev = [pss for pss in self.query(PrevSeasonSupporter).all() if pss.email not in attendees]
        return prev + list(attendees.values())


mount_site_sections(magprime_config['module_root'])

if c.AT_THE_CON:
    from uber.site_sections.preregistration import Root

    @cherrypy.expose
    def form(self, *args, **kwargs):
        raise HTTPRedirect('../registration/register')
    Root.form = form

# override badge CSV exports for magfest prime specific settings.
# magfest prime no longer uses one-day badges, so remove it.
_badge_exports = uber.site_sections.badge_exports.Root
_badge_exports.badge_zipfile_contents = \
    [fn for fn in _badge_exports.badge_zipfile_contents if fn.__name__ is not 'printed_badges_one_day']
