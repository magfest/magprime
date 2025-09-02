from pockets import classproperty
from pockets.autolog import log
from residue import CoerceUTF8 as UnicodeText, UUID
from markupsafe import Markup

from uber.config import c
from uber.custom_tags import readable_join, format_image_size, email_only, email_to_link
from uber.decorators import presave_adjustment, render
from uber.models import Boolean, MagModel, Choice, DefaultColumn as Column, Session, GuestImage
from uber.tasks.email import send_email
from uber.utils import add_opt, check, localized_now, remove_opt, GuidebookUtils


@Session.model_mixin
class LotteryApplication:
    @property
    def staff_award_status_str(self):
        if not self.is_staff_entry:
            return ''
        app_or_parent = self.parent_application or self
        if not c.HOTEL_ROOM_INVENTORY or not app_or_parent.finalized:
            return ''
        if self.parent_application:
            you_str = f"Your {c.HOTEL_LOTTERY_GROUP_TERM.lower()}'s hotel room"
        else:
            you_str = "Your hotel room"
        
        if app_or_parent.assigned_hotel:
            return f"{you_str} has been successfully assigned."
        else:
            return f"Something went wrong with {you_str.lower()}. Please contact STOPS at {email_to_link(email_only(c.STAFF_EMAIL))}."


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
    broadcast_title = Column(UnicodeText)
    broadcast_subtitle = Column(UnicodeText)

    @presave_adjustment
    def email_when_dept_changes(self):
        from .models import Session

        if not self.is_new and self.department != self.orig_value_of('department'):
            try:
                with Session() as session:
                    send_email.delay(
                        "panels-heads@magfest.org",
                        "panels-heads@magfest.org",
                        'Panel Department Changed',
                        render('emails/panel_changed_dept.txt', {'app': self}, encoding=None),
                        model=self.to_dict('id'))
            except Exception:
                log.error('unable to send panel dept changed email', exc_info=True)


@Session.model_mixin
class GuestGroup:
    def handle_images_from_params(self, session, **params):
        header_image = params.get('header_image')
        thumbnail_image = params.get('thumbnail_image')
        bio_image = params.get('bio_image')
        header_pic, thumbnail_pic, bio_pic = None, None, None
        message = ''

        if bio_image and bio_image.filename:
            bio_pic = GuestImage.upload_image(bio_image, guest_id=self.id)
            if bio_pic.extension not in c.ALLOWED_BIO_PIC_EXTENSIONS:
                message = 'Bio pic must be one of ' + ', '.join(c.ALLOWED_BIO_PIC_EXTENSIONS)

        if not message:
            if header_image and header_image.filename:
                message = GuidebookUtils.check_guidebook_image_filetype(header_image)
                if not message:
                    header_pic = GuestImage.upload_image(header_image, guest_id=self.id,
                                                            is_header=True)
                    if not header_pic.check_image_size():
                        message = f"Your header image must be {format_image_size(c.GUIDEBOOK_HEADER_SIZE)}."
            elif not self.guidebook_header:
                message = f"You must upload a {format_image_size(c.GUIDEBOOK_HEADER_SIZE)} header image."
        
        if not message:
            if thumbnail_image and thumbnail_image.filename:
                message = GuidebookUtils.check_guidebook_image_filetype(thumbnail_image)
                if not message:
                    thumbnail_pic = GuestImage.upload_image(thumbnail_image, guest_id=self.id,
                                                            is_thumbnail=True)
                    if not thumbnail_pic.check_image_size():
                        message = f"Your thumbnail image must be {format_image_size(c.GUIDEBOOK_THUMBNAIL_SIZE)}."
            elif not self.guidebook_thumbnail:
                message = f"You must upload a {format_image_size(c.GUIDEBOOK_THUMBNAIL_SIZE)} thumbnail image."
        
        if not message:
            if bio_pic:
                if self.bio_pic:
                    session.delete(self.bio_pic)
                session.add(bio_pic)
            if header_pic:
                if self.guidebook_header:
                    session.delete(self.guidebook_header)
                session.add(header_pic)
            if thumbnail_pic:
                if self.guidebook_thumbnail:
                    session.delete(self.guidebook_thumbnail)
                session.add(thumbnail_pic)

        return message


@Session.model_mixin
class Group:
    prior_name = Column(UnicodeText)
    has_permit = Column(Boolean, default=False)
    license = Column(UnicodeText)

@Session.model_mixin
class Attendee:
    special_merch = Column(Choice(c.SPECIAL_MERCH_OPTS), default=c.NO_MERCH)
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
    def staff_merch_items(self):
        """Used by the merch and staff_merch properties for staff swag."""
        merch = ["Volunteer lanyard"] if self.staffing and self.badge_type != c.CONTRACTOR_BADGE else []
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
