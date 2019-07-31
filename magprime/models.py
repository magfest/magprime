from pockets.autolog import log
from residue import CoerceUTF8 as UnicodeText, UUID

from uber.config import c
from uber.decorators import presave_adjustment, render
from uber.models import MagModel, Choice, DefaultColumn as Column, Session
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
    def merch_items(self):
        """
        Here is the business logic surrounding shirts:
        - People who kick in enough to get a shirt get an event shirt.
        - People with staff badges get a configurable number of staff shirts.
        - Volunteers who meet the requirements get a complementary event shirt
            (NOT a staff shirt).

        If the c.SEPARATE_STAFF_SWAG setting is true, then this excludes staff
        merch; see the staff_merch property.

        This property returns a list containing strings and sub-lists of each
        donation tier with multiple sub-items, e.g.
            [
                'tshirt',
                'Supporter Pack',
                [
                    'Swag Bag',
                    'Badge Hpolder'
                ],
                'Season Pass Certificate'
            ]
        """
        merch = []
        for amount, desc in sorted(c.DONATION_TIERS.items()):
            if amount and self.amount_extra >= amount:
                merch.append(desc)
                items = c.DONATION_TIER_ITEMS.get(amount, [])
                if len(items) == 1:
                    merch[-1] = items[0]
                elif len(items) > 1:
                    merch.append(items)

        if self.num_event_shirts_owed == 1 and not self.paid_for_a_shirt:
            merch.append('a tshirt')
        elif self.num_event_shirts_owed > 1:
            merch.append('a 2nd tshirt')

        if self.amount_extra >= c.SUPPORTER_LEVEL:
            merch.append('a {} size pair of sweatpants'.format(self.sweatpants_label))

        if self.volunteer_event_shirt_eligible and not self.volunteer_event_shirt_earned:
            merch[-1] += (
                ' (this volunteer must work at least 6 hours or they will be reported for picking up their shirt)')

        if not c.SEPARATE_STAFF_MERCH:
            merch.extend(self.staff_merch_items)

        if self.extra_merch:
            merch.append(self.extra_merch)

        return merch


@Session.model_mixin
class Group:
    @presave_adjustment
    def delete_declined(self):
        from uber.models import Tracking
        if self.status == c.DECLINED and not self.is_new:
            Tracking.track(c.DELETED, self)
            self.session.query(Group).filter_by(id=self.id).delete()
            self.session.expunge(self)


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
