from magprime import *


@Session.model_mixin
class Attendee:
    @presave_adjustment
    def invalid_notification(self):
        if self.staffing and self.badge_status == c.INVALID_STATUS and self.badge_status != self.orig_value_of('badge_status'):
            try:
                send_email(c.STAFF_EMAIL, c.STAFF_EMAIL, 'Volunteer invalidated',
                           render('emails/invalidated_volunteer.txt', {'attendee': self}), model=self)
            except:
                log.error('unable to send invalid email')


class SeasonPassTicket(MagModel):
    fk_id    = Column(UUID)
    slug     = Column(UnicodeText)

    @property
    def fk(self):
        return self.session.season_pass(self.fk_id)


class PrevSeasonSupporter(MagModel):
    first_name = Column(UnicodeText)
    last_name  = Column(UnicodeText)
    email      = Column(UnicodeText)

    email_model_name = 'attendee'  # used by AutomatedEmail code

    _repr_attr_names = ['first_name', 'last_name', 'email']


class FakeBadgeLock:
    """
    When c.SHIFT_CUSTOM_BADGES is turned on, we protect badge shifting with the
    c.BADGE_LOCK property.  Unfortunately, we've seen some bugs with this in the
    past where the lock might not get released after a database exception.  Since
    badge shifting is turned off for us now, I'm going to disable this lock via
    this dump monkeypatch, with the intention of straightening the whole thing
    out after MAGFest.
    """
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback): pass

    def acquire(self): pass

    def release(self): pass

c.BADGE_LOCK = FakeBadgeLock()
