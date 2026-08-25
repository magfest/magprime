import logging

from sqlalchemy import String, Uuid
from markupsafe import Markup
from typing import ClassVar

from uber.email import EmailService
from uber.config import c
from uber.custom_tags import readable_join, format_image_size, email_only, email_to_link
from uber.decorators import presave_adjustment, render
from uber.models import Boolean, MagModel, Choice, DefaultColumn as Column, Session
from uber.models.types import DefaultField as Field
from uber.utils import add_opt, check, localized_now, remove_opt, GuidebookUtils


log = logging.getLogger(__name__)


@Session.model_mixin
class LotteryApplication:
    @property
    def staff_award_status_str(self):
        if not self.is_staff_entry:
            return ''
        app_or_parent = self.parent_application if self.entry_type == c.GROUP_ENTRY else self
        if not app_or_parent.finalized:
            return ''
        if self.parent_application:
            you_str = f"Your {c.HOTEL_LOTTERY_GROUP_TERM.lower()}'s hotel room"
        else:
            you_str = "Your hotel room"

        attendee = app_or_parent.attendee
        if any(ra.is_live for ra in (attendee.room_assignments if attendee else [])):
            return f"{you_str} has been successfully assigned."
        else:
            return f"Something went wrong with {you_str.lower()}. Please contact STOPS at {email_to_link(email_only(c.STAFF_EMAIL))}."


@Session.model_mixin
class PanelApplication:
    magscouts_opt_in: int = Field(sa_column=Column(Choice(c.PANEL_MAGSCOUTS_OPTS), default=c.NO_CHOICE))
    broadcast_title: str = Field(sa_type=String, default='')
    broadcast_subtitle: str = Field(sa_type=String, default='')
    recording_details: str = Field(sa_type=String, default='')
    accessibility_info: str = Field(sa_type=String, default='')
    after_9pm: bool = Field(sa_type=Boolean, default=False)
    extreme_times: bool = Field(sa_type=Boolean, default=False)
    no_transfer: bool = Field(sa_type=Boolean, default=False)

    @presave_adjustment
    def no_magscouts_mature_panel(self):
        if self.magscouts_opt_in != c.NO_CHOICE and self.granular_rating_ints != [c.NONE]:
            self.magscouts_opt_in = c.NO_CHOICE

    @presave_adjustment
    def email_when_dept_changes(self):
        from .models import Session

        if not self.is_new and self.department != self.orig_value_of('department'):
            with Session() as session:
                EmailService.queue_email(session, 'panel_dept_changed_admin', to="panels-heads@magfest.org",
                                         data={'app': self, 'old_dept_name': self.orig_value_of('department_name')})


@Session.model_mixin
class Group:
    prior_name: str = Field(sa_type=String, default='')
    has_permit: bool = Field(sa_type=Boolean, default=False)
    license: str = Field(sa_type=String, default='')

@Session.model_mixin
class Attendee:
    special_merch: int = Field(sa_column=Column(Choice(c.SPECIAL_MERCH_OPTS)), default=c.NO_MERCH)
    donate_badge_cost: bool = Field(sa_type=Boolean, default=False)
    swadge_addon: bool = Field(sa_type=Boolean, default=False)
    gets_emergency_texts: bool = Field(sa_type=Boolean, default=False)

    @presave_adjustment
    def defaults(self):
        if not self.special_merch:
            self.special_merch = c.NO_MERCH
        if not self.donate_badge_cost:
            self.donate_badge_cost = False

    @presave_adjustment
    def swadge_addon_only_supporter(self):
        if self.amount_extra != c.SUPPORTER_LEVEL:
            self.swadge_addon = False

    @presave_adjustment
    def indie_ribbon(self):
        if (self.group and self.group.guest and self.group.guest.group_type == c.MIVS
            ) or (self.group and "Indie Arcade -" in self.group.name) and c.MIVS not in self.ribbon_ints:
            self.ribbon = add_opt(self.ribbon_ints, c.MIVS)

    @property
    def donation_swag(self):
        donation_items = []
        highest_tier_listed = False

        for amount, desc in sorted(c.DONATION_TIERS.items(), reverse=True):
            if amount and self.amount_extra >= amount:
                if not highest_tier_listed:
                    donation_items.append(f"${amount} {desc}")
                    highest_tier_listed = True
                else:
                    donation_items.append(f"{desc} (Included)")

        if self.extra_donation >= c.SUPERSTAR_MINIMUM:
            donation_items.append(f"MAGFest Superstar donation of ${self.extra_donation}")
        elif self.extra_donation:
            donation_items.append(f'Extra donation of ${self.extra_donation}')

        if self.swadge_addon and self.amount_extra == c.SUPPORTER_LEVEL:
            donation_items.append(f"${c.SWADGE_PRICE} Swadge add-on")
        return donation_items

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

        #if c.UNDER_13 in self.ribbon_ints:
        #    stuff.append("a 12 and under wristband")

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
        if self.staffing and self.badge_status == c.INVALID_STATUS and self.badge_status != self.orig_value_of('badge_status'):
            EmailService.queue_email(self.session, 'invalidated_volunteer_admin', to=c.STAFF_EMAIL,
                                     data={'attendee': self})

    @property
    def watchlist_warning(self):
        regdesk_info_append = " [{}]".format(self.regdesk_info) if self.regdesk_info else ""
        return "MUST TALK TO SECURITY before picking up badge{}".format(regdesk_info_append)

    def calculate_shipping_fee_cost(self):
        if self.amount_extra >= c.SEASON_LEVEL:
                return 15
        elif self.amount_extra >= c.SUPPORTER_LEVEL:
            return 10
        elif self.amount_extra >= c.SHIRT_LEVEL:
            return 5
        
    @property
    def selected_hotel_type(self):
        if not self.hotel_eligible:
            return 'enter the staff prelottery'
        elif self.lottery_application and self.lottery_application.status == c.DISQUALIFIED:
            return 'utilize staff crash space'
        return ''

    @property
    def volunteer_event_shirt_eligible(self):
        return bool(c.VOLUNTEER_RIBBON in self.ribbon_ints and c.HOURS_FOR_SHIRT and not self.walk_on_volunteer)
    
    @property
    def merch_items(self):
        merch = []
        for amount, desc in sorted(c.DONATION_TIERS.items()):
            if amount and (self.amount_extra or 0) >= amount:
                merch.append(desc)
                items = c.DONATION_TIER_ITEMS.get(amount, [])
                if len(items) == 1:
                    merch[-1] = items[0]
                elif len(items) > 1:
                    merch.append(items)

        if self.num_event_shirts_owed == 1 and not self.paid_for_a_shirt:
            merch.append('A T-shirt')
        elif self.num_event_shirts_owed > 1:
            merch.append('A 2nd T-Shirt')

        if merch and self.volunteer_event_shirt_eligible and not self.volunteer_event_shirt_earned:
            merch[-1] += (
                ' (this volunteer must work at least {} hours or they will be reported for picking up their shirt)'
                .format(c.HOURS_FOR_SHIRT))

        if not c.SEPARATE_STAFF_MERCH:
            merch.extend(self.staff_merch_items)
        
        if self.swadge_addon and self.amount_extra == c.SUPPORTER_LEVEL:
            merch.append('A Swadge')

        if self.extra_merch:
            merch.append(self.extra_merch)

        return merch

    @property
    def staff_merch_items(self):
        """Used by the merch and staff_merch properties for staff swag."""
        if self.badge_type == c.CONTRACTOR_BADGE or not self.staffing:
            return []
        
        merch = ["Staffer Info Packet (optional)"]

        if self.weighted_hours >= 1:
            merch.append("Lanyard")
            if self.badge_type != c.STAFF_BADGE:
                merch.append("Volunteer Ribbon")

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
        elif self.could_get_staff_shirt and self.shirt_opt_out in [c.STAFF_OPT_OUT, c.ALL_OPT_OUT]:
            merch.append("NO Staff Shirt")

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

        if self.badge_status not in [c.COMPLETED_STATUS, c.NEW_STATUS]:
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


class SeasonPassTicket(MagModel, table=True):
    fk_id: str = Field(sa_type=Uuid(as_uuid=False))
    slug: str = Field(sa_type=String, default='')

    @property
    def fk(self):
        return self.session.season_pass(self.fk_id)


class PrevSeasonSupporter(MagModel, table=True):
    first_name: str = Field(sa_type=String, default='')
    last_name: str = Field(sa_type=String, default='')
    email: str = Field(sa_type=String, default='')

    email_model_name: ClassVar = 'attendee'  # used by AutomatedEmailFixture code

    _repr_attr_names = ['first_name', 'last_name', 'email']
