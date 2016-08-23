from uber.common import *
from magprime._version import __version__

magprime_config = parse_config(__file__)
static_overrides(join(magprime_config['module_root'], 'static'))
template_overrides(join(magprime_config['module_root'], 'templates'))


@Config.mixin
class ExtraConfig:
    @property
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


@Session.model_mixin
class Attendee:
    extra_donation = Column(Integer, default=0)

    @cost_property
    def donation_cost(self):
        return self.extra_donation or 0

    @presave_adjustment
    def set_empty_donation(self):
        if not self.extra_donation:
            self.extra_donation = 0

    @validation.Attendee
    def only_positive_donation(self):
        if self.extra_donation and self.extra_donation < 0:
            return "You cannot donate negative money."

    @property
    def addons(self):
        return ['Extra donation of ${}'.format(self.extra_donation)] if self.extra_donation else []


# these need to come last so they can make use of everything defined above
from magprime.utils import *
from magprime.models import *
from magprime.automated_emails import *
from magprime.model_checks import *
mount_site_sections(magprime_config['module_root'])

if c.AT_THE_CON:
    from uber.site_sections.preregistration import Root

    @cherrypy.expose
    def form(self, *args, **kwargs):
        raise HTTPRedirect('../registration/register')
    Root.form = form
