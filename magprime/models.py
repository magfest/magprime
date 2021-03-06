from pockets.autolog import log
from residue import CoerceUTF8 as UnicodeText, UUID

from uber.config import c
from uber.decorators import presave_adjustment, render
from uber.models import Boolean, MagModel, Choice, DefaultColumn as Column, Session
from uber.tasks.email import send_email
from uber.utils import add_opt, remove_opt


@Session.model_mixin
class Attendee:
    sweatpants = Column(Choice(c.SWEATPANTS_OPTS), default=c.NO_SWEATPANTS)

    @presave_adjustment
    def invalid_notification(self):
        if self.staffing and self.badge_status == c.INVALID_STATUS \
                and self.badge_status != self.orig_value_of('badge_status'):
            try:
                send_email.delay(
                    c.STAFF_EMAIL,
                    c.STAFF_EMAIL,
                    'Volunteer invalidated',
                    render('emails/invalidated_volunteer.txt', {'attendee': self}, encoding=None),
                    model=self.to_dict('id'))
            except Exception:
                log.error('unable to send invalid email', exc_info=True)

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
            
    @property
    def volunteer_event_shirt_eligible(self):
        return bool(c.VOLUNTEER_RIBBON in self.ribbon_ints and c.HOURS_FOR_SHIRT and not self.walk_on_volunteer)
            
    @property
    def staff_merch_items(self):
        """Used by the merch and staff_merch properties for staff swag."""
        merch = ["Volunteer lanyard", "Volunteer button"] if self.staffing else []
        if self.walk_on_volunteer and self.worked_hours >= 6:
            merch.append("Walk-on volunteer coffee mug")
        if not self.walk_on_volunteer and self.worked_hours >= c.HOURS_FOR_REFUND:
            merch.append("Staff Swadge")
        num_staff_shirts_owed = self.num_staff_shirts_owed
        if num_staff_shirts_owed > 0:
            staff_shirts = '{} Staff Shirt{}'.format(num_staff_shirts_owed, 's' if num_staff_shirts_owed > 1 else '')
            if self.shirt_size_marked:
                staff_shirts += ' [{}]'.format(c.SHIRTS[self.shirt])
            merch.append(staff_shirts)

        if self.staffing:
            merch.append('Staffer Info Packet')

        return merch


class SeasonPassTicket(MagModel):
    fk_id = Column(UUID)
    slug = Column(UnicodeText)

    @property
    def fk(self):
        return self.session.season_pass(self.fk_id)


class PrevSeasonSupporter(MagModel):
    first_name = Column(UnicodeText)
    last_name = Column(UnicodeText)
    email = Column(UnicodeText)

    email_model_name = 'attendee'  # used by AutomatedEmailFixture code

    _repr_attr_names = ['first_name', 'last_name', 'email']
