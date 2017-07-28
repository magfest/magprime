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

    @presave_adjustment
    def child_badge(self):
        if self.age_group not in [c.UNDER_21, c.OVER_21, c.AGE_UNKNOWN] and self.badge_type == c.ATTENDEE_BADGE:
            self.badge_type = c.CHILD_BADGE
            if self.age_group in [c.UNDER_6, c.UNDER_13]:
                self.ribbon = add_opt(self.ribbon_ints, c.UNDER_13)

    @presave_adjustment
    def child_ribbon_or_not(self):
        if self.age_group in [c.UNDER_6, c.UNDER_13]:
            self.ribbon = add_opt(self.ribbon_ints, c.UNDER_13)
        elif c.UNDER_13 in self.ribbon_ints and self.age_group not in [c.UNDER_6, c.UNDER_13]:
            self.ribbon = remove_opt(self.ribbon_ints, c.UNDER_13)

    @presave_adjustment
    def child_to_attendee(self):
        if self.badge_type == c.CHILD_BADGE and self.age_group in [c.UNDER_21, c.OVER_21]:
            self.badge_type = c.ATTENDEE_BADGE
            self.ribbon = remove_opt(self.ribbon_ints, c.UNDER_13)


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
