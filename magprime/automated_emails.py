from uber.models import Attendee, AutomatedEmail, GuestGroup
from uber.automated_emails import StopsEmailFixture, AutomatedEmailFixture, MarketplaceEmailFixture, HotelLotteryEmailFixture
from uber.config import c
from uber.utils import before, days_after, days_before, DeptChecklistConf

from magprime.models import SeasonPassTicket
from magprime.utils import SeasonEvent


if c.HOTEL_LOTTERY_STAFF_START:
    HotelLotteryEmailFixture(
        f'{c.EVENT_NAME_AND_YEAR} Staff Pre-Lottery Award Notification',
        'hotel/prelim_notification.html',
        "lambda a: a.status == c.AWARDED and a.is_staff_entry",
        ident='hotel_lottery_prelim_staff'
    )

    HotelLotteryEmailFixture(
        f'{c.EVENT_NAME_AND_YEAR} Staff Pre-Lottery Booking Link',
        'hotel/award_notification.html',
        "lambda a: a.status == c.AWARDED and a.is_staff_entry and a.booking_url_ready",
        ident='hotel_lottery_awarded_staff'
    )

if c.HOTEL_LOTTERY_FORM_START:
    HotelLotteryEmailFixture(
        f'{c.EVENT_NAME_AND_YEAR} Hotel Lottery Notification',
        'hotel/award_notification.html',
        "lambda a: a.status == c.AWARDED and a.booking_url_ready and not a.is_staff_entry",
        ident='hotel_lottery_awarded'
    )

    HotelLotteryEmailFixture(
        f'{c.EVENT_NAME_AND_YEAR} Hotel Lottery Notification',
        'hotel/lottery_delay.html',
        "lambda a: a.status == c.AWARDED and not a.is_staff_entry",
        ident='hotel_lottery_awarded_late'
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
                when=[before(event.deadline)],
                extra_data={'event': event})

    for _event in SeasonEvent.instances.values():
        SeasonSupporterEmailFixture(_event)


AutomatedEmailFixture(
    Attendee, 'MAGFest schedule, map, and other FAQs', 'precon_faqs.html',
    "lambda a: not a.cannot_check_in_reason",
    'magprime_precon_faqs',
    when=[days_before(7, c.EPOCH)],
    sender='MAGFest <contact@magfest.org>')

AutomatedEmailFixture(
    Attendee, 'Thank you for your Super MAGFest Superstars Donation!',
    'superstar_intro.html',
    "lambda a: a.extra_donation >= c.SUPERSTAR_MINIMUM and a.active_receipt and not a.amount_unpaid",
    'superstar_intro',
    when=[before(c.SUPERSTAR_DEADLINE)],
    sender='MAGFest Superstar Program <superstars@magfest.org>'
)

AutomatedEmailFixture(
    Attendee,
    f'MAGFest {c.EVENT_YEAR} Superstar Donation Receipt',
    'superstar_receipt.html', None,
    'superstar_receipt',
    send_filter="lambda a: not a.amount_unpaid",
    sender='MAGFest Superstar Program <superstars@magfest.org>'
)

AutomatedEmailFixture(
    Attendee, 'MAGFest food for guests', 'guest_food_restrictions.txt',
    "lambda a: a.badge_type == c.GUEST_BADGE",
    sender='MAGFest Staff Suite <chefs@magfest.org>',
    ident='magprime_guest_food_restrictions')

AutomatedEmailFixture(
    Attendee, 'MAGFest hospitality suite information', 'food/guest_food_info.txt',
    "lambda a: a.badge_type == c.GUEST_BADGE",
    sender='MAGFest Staff Suite <chefs@magfest.org>',
    ident='magprime_hospitality_suite_guest_food_info')

AutomatedEmailFixture(
    Attendee, 'Department Heads', 'food/department_heads.txt',
    "lambda a: a.is_dept_head",
    'magprime_department_water_and_food_info',
    #when=[days_before(7, c.UBER_TAKEDOWN)],
    sender='MAGFest Staff Suite <chefs@magfest.org>')

AutomatedEmailFixture(
    Attendee, 'MAGFest Volunteer Food', 'volunteer_food_info.txt',
    "lambda a: a.staffing",
    'magprime_volunteer_food_info',
    when=[days_before(7, c.UBER_TAKEDOWN)],
    sender='MAGFest Staff Suite <chefs@magfest.org>')

AutomatedEmailFixture(
    Attendee, 'Important MAGFest PC Gaming Room Information! *PLEASE READ*', 'lan_room.html',
    "lambda a: c.LAN in a.interests_ints",
    'magprime_important_lan_room_info',
    sender='MAGFest LAN <lan@magfest.org>')

AutomatedEmailFixture(
    Attendee, 'Get Ready for MAGFest LAN!', 'lan_hype.html',
    "lambda a: c.LAN in a.interests_ints",
    'magprime_lan_hype',
    sender='MAGFest LAN <lan@magfest.org>')

StopsEmailFixture(
    f'{c.EVENT_NAME} ({c.EVENT_DATE}) shifts are live tomorrow!',
    'shifts/shifts_created.txt',
    "lambda a: a.badge_type != c.CONTRACTOR_BADGE and a.takes_shifts and a.registered_local <= c.SHIFTS_CREATED",
    'volunteer_shift_signup_notification',
    when=[before(c.PREREG_TAKEDOWN)])

StopsEmailFixture(
    'MAGFest Dept Checklist Introduction', 'dept_checklist_intro.txt',
    "lambda a: a.is_checklist_admin and a.admin_account",
    'magprime_dept_checklist_intro',
    extra_data={'checklist_items': DeptChecklistConf.instances.values()})

if c.STAFF_EVENT_SHIRT_OPTS:
    StopsEmailFixture(
        'Last Chance to enter your MAGFest staff shirt preferences', 'second_shirt.html',
        "lambda a: a.gets_staff_shirt and not a.shirt_info_marked",
        'magprime_second_shirt',
        when=[days_before(21, c.SHIRT_DEADLINE)])

AutomatedEmailFixture(
    Attendee, f'Last Chance for MAGFest {c.EVENT_YEAR} bonus swag!', 'attendee_swag_promo.html',
    "lambda a: a.can_spam and (a.paid == c.HAS_PAID or a.paid == c.NEED_NOT_PAY or \
        (a.group and a.group.amount_paid)) and days_after(3, a.registered)()",
    'magprime_bonus_swag_reminder_last_chance',
    sender='MAGFest Merch Team <merch@magfest.org>')

# Send to any attendee who will be receiving a t-shirt (staff, volunteers, anyone
# who kicked in at the shirt level or above). Should not be sent after the t-shirt
# size deadline.
AutomatedEmailFixture(
    Attendee, f'MAGFest {c.EVENT_YEAR} t-shirt size confirmation', 'confirm_shirt_size.html',
    "lambda a: days_after(3, a.registered)() and a.gets_any_kind_of_shirt",
    'magprime_shirt_size_confirmation',
    when=[before(c.SHIRT_DEADLINE)],
    sender='MAGFest Merch Team <merch@magfest.org>')


AutomatedEmailFixture(
    None, 'Panel Department Changed',
    'panel_changed_dept.txt', None,
    'panel_dept_changed_admin',
    sender="panels-heads@magfest.org"
)

AutomatedEmailFixture(
    None, 'Volunteer Invalidated',
    'invalidated_volunteer.txt', None,
    'invalidated_volunteer_admin',
    sender=c.STAFF_EMAIL
)