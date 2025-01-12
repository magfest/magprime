from pockets import classproperty
from pockets.autolog import log
from residue import CoerceUTF8 as UnicodeText, UUID
from markupsafe import Markup

from uber.config import c
from uber.custom_tags import readable_join
from uber.decorators import presave_adjustment, render
from uber.models import Boolean, MagModel, Choice, DefaultColumn as Column, Session
from uber.tasks.email import send_email
from uber.utils import add_opt, check, localized_now, remove_opt


@Session.model_mixin
class AutomatedEmail:
    @presave_adjustment
    def set_auto_approval(self):
        if self.ident in [
            'qrcode_for_checkin', 'badge_confirmation_reminder_last_chance', 'under_18_parental_consent_reminder'
        ]:
            self.needs_approval = False

@Session.model_mixin
class PanelApplication:
    magscouts_opt_in = Column(Choice(c.PANEL_MAGSCOUTS_OPTS), default=c.NO_CHOICE)

@Session.model_mixin
class Group:
    prior_name = Column(UnicodeText)
    has_permit = Column(Boolean, default=False)
    license = Column(UnicodeText)

@Session.model_mixin
class Attendee:
    special_merch = Column(Choice(c.SPECIAL_MERCH_OPTS), default=c.NO_MERCH)
    group_name = Column(UnicodeText)
    donate_badge_cost = Column(Boolean, default=False)

    @presave_adjustment
    def indie_ribbon(self):
        if (self.group and self.group.guest and self.group.guest.group_type == c.MIVS
            ) or (self.group and "Indie Arcade -" in self.group.name) and c.MIVS not in self.ribbon_ints:
            self.ribbon = add_opt(self.ribbon_ints, c.MIVS)

    @property
    def accoutrements(self):
        # Converts ribbons to the new access system for check-in
        stuff = []

        if (c.DEALER_RIBBON in self.ribbon_ints or c.MIVS in self.ribbon_ints
                ) and (self.badge_type not in [c.STAFF_BADGE, c.CONTRACTOR_BADGE]):
            stuff.append("Expo Hall access")
        elif self.unweighted_hours > 0 and self.badge_type not in [c.STAFF_BADGE, c.CONTRACTOR_BADGE]:
            stuff.append("Expo Hall access")

        if c.BAND in self.ribbon_ints and self.badge_type != c.GUEST_BADGE:
            stuff.append("Backstage access")

        if c.UNDER_13 in self.ribbon_ints:
            stuff.append("a 12 and under wristband")

        if c.SUPERSTAR_RIBBON in self.ribbon_ints:
            stuff.append("a Superstar ribbon")

        if c.WRISTBANDS_ENABLED:
            stuff.append('a {} wristband'.format(c.WRISTBAND_COLORS[self.age_group]))

        stuff = (' with ' if stuff else '') + readable_join(stuff)

        return stuff
    
    @property
    def check_in_notes(self):
        notes = []
        if self.age_group_conf['consent_form']:
            notes.append("Before checking this attendee in, please collect a signed parental consent form. If the guardian is there, and they have not already completed one, have them sign one in front of you.")

        if self.accoutrements:
            notes.append(f"Please check this attendee in {self.accoutrements}.")

        if c.VOLUNTEER_RIBBON in self.ribbon_ints:
            notes.append("Instruct this attendee to go to STOPS for their volunteer ribbon.")

        return Markup("<br/><br/>".join(notes))

    @presave_adjustment
    def set_superstar_ribbon(self):
        if self.extra_donation >= c.SUPERSTAR_MINIMUM and c.SUPERSTAR_RIBBON not in self.ribbon_ints:
            self.ribbon = add_opt(self.ribbon_ints, c.SUPERSTAR_RIBBON)
        elif self.extra_donation < c.SUPERSTAR_MINIMUM and \
                self.orig_value_of('extra_donation') >= c.SUPERSTAR_MINIMUM and c.SUPERSTAR_RIBBON in self.ribbon_ints:
            self.ribbon = remove_opt(self.ribbon_ints, c.SUPERSTAR_RIBBON)

    @presave_adjustment
    def convert_imported_badges(self):
        # MAGFest uses attendee badge importing for deferred attendees, who should have valid badges and be comped
        if self.badge_status == c.IMPORTED_STATUS:
            self.badge_status = c.NEW_STATUS
            self.paid = c.NEED_NOT_PAY

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

    @classproperty
    def searchable_fields(cls):
        # List of fields for the attendee search to check search terms against
        return ['first_name', 'last_name', 'legal_name', 'badge_printed_name', 'group_name',
                'email', 'comments', 'admin_notes', 'for_review', 'transfer_code']

    @classproperty
    def searchable_bools(cls):
        return ['placeholder', 'requested_accessibility_services', 'can_spam',
                'got_merch', 'got_staff_merch', 'confirmed', 'checked_in', 'staffing', 
                'agreed_to_volunteer_agreement', 'reviewed_emergency_procedures', 'walk_on_volunteer', 
                'can_work_setup', 'can_work_teardown', 'hotel_eligible', 'attractions_opt_out', 'donate_badge_cost']
    
    def calculate_shipping_fee_cost(self):
        if self.amount_extra >= c.SEASON_LEVEL:
                return 15
        elif self.amount_extra >= c.SUPPORTER_LEVEL:
            return 10
        elif self.amount_extra >= c.SHIRT_LEVEL:
            return 5

    @property
    def volunteer_event_shirt_eligible(self):
        return bool(c.VOLUNTEER_RIBBON in self.ribbon_ints and c.HOURS_FOR_SHIRT and not self.walk_on_volunteer)

    @property
    def staff_merch_items(self):
        """Used by the merch and staff_merch properties for staff swag."""
        merch = ["Volunteer lanyard"] if self.staffing else []
        if self.walk_on_volunteer and self.worked_hours >= 6:
            merch.append("Walk-on volunteer coffee mug")
        if not self.walk_on_volunteer and self.worked_hours >= c.HOURS_FOR_REFUND:
            merch.append("Staff Swadge")
        num_staff_shirts_owed = self.num_staff_shirts_owed
        if num_staff_shirts_owed > 0:
            staff_shirts = '{} Staff Shirt{}'.format(num_staff_shirts_owed, 's' if num_staff_shirts_owed > 1 else '')
            if self.shirt_size_marked:
                try:
                    if c.STAFF_SHIRT_OPTS != c.SHIRT_OPTS:
                        staff_shirts += ' [{}]'.format(c.STAFF_SHIRTS[self.staff_shirt])
                    else:
                        staff_shirts += ' [{}]'.format(c.SHIRTS[self.shirt])
                except KeyError:
                    staff_shirts += ' [{}]'.format("Size unknown")
            merch.append(staff_shirts)

        if self.staffing:
            merch.append('Staffer Info Packet')

        if self.badge_type == c.STAFF_BADGE:
            merch.append('Staff Merch Item')

        return merch
    @property
    def is_not_ready_to_checkin(self):
        """
        Returns None if we are ready for checkin, otherwise a short error
        message why we can't check them in.
        """
        
        if self.badge_status == c.WATCHED_STATUS:
            if self.banned or not self.regdesk_info:
                regdesk_info_append = " [{}]".format(self.regdesk_info) if self.regdesk_info else ""
                return "MUST TALK TO SECURITY before picking up badge{}".format(regdesk_info_append)
            return self.regdesk_info or "Badge status is {}".format(self.badge_status_label)

        if self.badge_status not in [c.COMPLETED_STATUS, c.NEW_STATUS, c.AT_DOOR_PENDING_STATUS]:
            return "Badge status is {}".format(self.badge_status_label)

        if self.group and self.paid == c.PAID_BY_GROUP and self.group.is_dealer and self.group.status != c.APPROVED:
            return "Unapproved dealer"
        
        if self.group and self.paid == c.PAID_BY_GROUP and self.group.amount_unpaid:
            return "Unpaid group"
        
        if self.placeholder:
            return "Placeholder badge"

        if self.is_unassigned:
            return "Badge not assigned"

        if self.is_presold_oneday:
            if self.badge_type_label != localized_now().strftime('%A'):
                return "Wrong day"
            
        if self.donate_badge_cost:
            return "Asked badge + merch to be shipped to them"

        message = check(self)
        return message


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
