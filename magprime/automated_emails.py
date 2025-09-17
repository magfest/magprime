from uber.models import Attendee, AutomatedEmail, GuestGroup
from uber.automated_emails import StopsEmailFixture, AutomatedEmailFixture, MarketplaceEmailFixture, HotelLotteryEmailFixture
from uber.config import c
from uber.utils import before, days_after, days_before, DeptChecklistConf

from magprime.models import SeasonPassTicket
from magprime.utils import SeasonEvent


if c.HOTEL_LOTTERY_STAFF_START:
    HotelLotteryEmailFixture(
        f'{c.EVENT_NAME_AND_YEAR} Staff Pre-Lottery Award Notification',
        'hotel/award_notification.html',
        lambda a: a.status == c.AWARDED and a.is_staff_entry and (
            a.booking_url or a.parent_application and a.parent_application.booking_url),
        ident='hotel_lottery_awarded_staff'
    )

if c.HOTEL_LOTTERY_FORM_START:
    HotelLotteryEmailFixture(
        f'{c.EVENT_NAME_AND_YEAR} Hotel Lottery Notification',
        'hotel/award_notification.html',
        lambda a: a.status == c.AWARDED and not a.is_staff_entry and (
            a.booking_url or a.parent_application and a.parent_application.booking_url),
        ident='hotel_lottery_awarded'
    )


# leave this off for now, this code is now old and needs updating
_send_season_supporter_emails = False


if _send_season_supporter_emails:
    # This line currently does, but should not, return Attendee objects.
    # It can cause issues. see _assert_same_model_type()
    # !!THIS LINE IS BROKEN!!
    # AutomatedEmailFixture.queries[SeasonPassTicket] = lambda session: session.season_passes()

    class SeasonSupporterEmailFixture(AutomatedEmailFixture):
        def __init__(self, event):
            AutomatedEmailFixture.__init__(
                self, SeasonPassTicket,
                subject='Claim your {} badges with your MAGFest Season Pass'.format(event.name),
                ident='magprime_season_supporter_{}_invite'.format(event.slug),
                template='season_supporter_event_invite.txt',
                when=before(event.deadline),
                extra_data={'event': event})

    for _event in SeasonEvent.instances.values():
        SeasonSupporterEmailFixture(_event)


AutomatedEmailFixture(
    Attendee, 'MAGFest schedule, maps, and other FAQs', 'precon_faqs.html',
    filter=lambda a: not a.cannot_check_in_reason,
    ident='magprime_precon_faqs',
    when=days_before(7, c.EPOCH),
    sender='MAGFest <contact@magfest.org>')

AutomatedEmailFixture(
    Attendee, 'Thank you for your Super MAGFest Superstars Donation!',
    'superstar_intro.html',
    filter=lambda a: a.extra_donation >= c.SUPERSTAR_MINIMUM and a.active_receipt and not a.amount_unpaid,
    ident='superstar_intro',
    when=before(c.SUPERSTAR_DEADLINE),
    sender='MAGFest Superstar Program <superstars@magfest.org>'
)

AutomatedEmailFixture(
    Attendee, 'MAGFest food for guests', 'guest_food_restrictions.txt',
    lambda a: a.badge_type == c.GUEST_BADGE,
    sender='MAGFest Staff Suite <chefs@magfest.org>',
    ident='magprime_guest_food_restrictions')

AutomatedEmailFixture(
    Attendee, 'MAGFest hospitality suite information', 'food/guest_food_info.txt',
    lambda a: a.badge_type == c.GUEST_BADGE,
    sender='MAGFest Staff Suite <chefs@magfest.org>',
    ident='magprime_hospitality_suite_guest_food_info')

AutomatedEmailFixture(
    Attendee, 'Department Heads', 'food/department_heads.txt',
    lambda a: a.is_dept_head,
    ident='magprime_department_water_and_food_info',
   # when=days_before(7, c.UBER_TAKEDOWN),
    sender='MAGFest Staff Suite <chefs@magfest.org>')

AutomatedEmailFixture(
    Attendee, 'MAGFest Volunteer Food', 'volunteer_food_info.txt',
    lambda a: a.staffing,
    ident='magprime_volunteer_food_info',
    when=days_before(7, c.UBER_TAKEDOWN),
    sender='MAGFest Staff Suite <chefs@magfest.org>')

AutomatedEmailFixture(
    Attendee, 'Important MAGFest PC Gaming Room Information! *PLEASE READ*', 'lan_room.html',
    lambda a: c.LAN in a.interests_ints,
    ident='magprime_important_lan_room_info',
    sender='MAGFest LAN <lan@magfest.org>')

AutomatedEmailFixture(
    Attendee, 'Get Ready for MAGFest LAN!', 'lan_hype.html',
    lambda a: c.LAN in a.interests_ints,
    ident='magprime_lan_hype',
    needs_approval=True,
    sender='MAGFest LAN <lan@magfest.org>')

MarketplaceEmailFixture(
        'Your {} {} has been waitlisted'.format(c.EVENT_NAME, c.DEALER_APP_TERM.capitalize()),
        'dealers/waitlisted.txt',
        lambda g: g.status == c.WAITLISTED,
        # query=Group.status == c.WAITLISTED,
        needs_approval=True,
        ident='dealer_reg_waitlisted')

MarketplaceEmailFixture(
        'Your {} {} has been declined'.format(c.EVENT_NAME, c.DEALER_APP_TERM.capitalize()),
        'dealers/declined.txt',
        lambda g: g.status == c.DECLINED,
        # query=Group.status == c.DECLINED,
        needs_approval=True,
        ident='dealer_reg_declined')

"""
AutomatedEmailFixture(
    Attendee, 'MAGFest Tech Ops volunteering', 'techops.txt',
    lambda a: a.staffing and a.assigned_to(c.TECH_OPS),
    ident='magprime_techops_volunteer',
    sender='MAGFest TechOps <techops@magfest.org>')

AutomatedEmailFixture(
    Attendee, 'MAGFest Chipspace volunteering', 'chipspace.txt',
    lambda a: a.staffing and a.assigned_to(c.CHIPSPACE),
    ident='magprime_chipspace_volunteer',
    sender='MAGFest ChipSpace <chipspace@magfest.org>')

AutomatedEmailFixture(
    Attendee, 'MAGFest Chipspace shifts', 'chipspace_trusted.txt',
    lambda a: a.staffing and a.has_shifts_in(c.CHIPSPACE) and a.trusted_in(c.CHIPSPACE),
    ident='magprime_chipspace_trusted_volunteer',
    sender='MAGFest ChipSpace <chipspace@magfest.org>')

AutomatedEmailFixture(
    Attendee, 'MAGFest Chipspace', 'chipspace_untrusted.txt',
    lambda a: a.staffing and a.has_shifts_in(c.CHIPSPACE) and not a.trusted_in(c.CHIPSPACE),
    ident='magprime_chipspace_untrusted_volunteer',
    sender='MAGFest ChipSpace <chipspace@magfest.org>')

AutomatedEmailFixture(
    Attendee, 'Want to help run MAGFest poker tournaments?', 'poker.txt',
    lambda a: a.has_shifts_in(c.TABLETOP),
    ident='magprime_tabletop_volunteer_poker_inquiry',
    sender='MAGFest Tabletop <tabletop@magfest.org>')

StopsEmailFixture(
    'MAGFest Staff Support', 'staff_support.txt',
    lambda a: a.assigned_to(c.STAFF_SUPPORT) and not a.trusted_in(c.STAFF_SUPPORT),
    ident='magprime_staff_support_volunteer')
"""
StopsEmailFixture(
    'MAGFest Dept Checklist Introduction', 'dept_checklist_intro.txt',
    lambda a: a.is_checklist_admin and a.admin_account,
    extra_data={'checklist_items': DeptChecklistConf.instances.values()},
    ident='magprime_dept_checklist_intro')

if c.STAFF_EVENT_SHIRT_OPTS:
    StopsEmailFixture(
        'Last Chance to enter your MAGFest staff shirt preferences', 'second_shirt.html',
        lambda a: a.gets_staff_shirt and not a.shirt_info_marked,
        when=days_before(21, c.SHIRT_DEADLINE),
        ident='magprime_second_shirt')

AutomatedEmailFixture(
    Attendee, 'Last Chance for MAGFest ' + c.EVENT_YEAR + ' bonus swag!', 'attendee_swag_promo.html',
    lambda a: (
        a.can_spam
        and (a.paid == c.HAS_PAID or a.paid == c.NEED_NOT_PAY or (a.group and a.group.amount_paid))
        and days_after(3, a.registered)()),
    sender='MAGFest Merch Team <merch@magfest.org>',
    ident='magprime_bonus_swag_reminder_last_chance')

# Send to any attendee who will be receiving a t-shirt (staff, volunteers, anyone
# who kicked in at the shirt level or above). Should not be sent after the t-shirt
# size deadline.
AutomatedEmailFixture(
    Attendee, 'MAGFest ' + c.EVENT_YEAR + ' t-shirt size confirmation', 'confirm_shirt_size.html',
    lambda a: days_after(3, a.registered)() and a.gets_any_kind_of_shirt,
    when=before(c.SHIRT_DEADLINE),
    sender='MAGFest Merch Team <merch@magfest.org>',
    ident='magprime_shirt_size_confirmation')

