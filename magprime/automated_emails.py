from uber.models import Attendee
from uber.automated_emails import StopsEmailFixture, AutomatedEmailFixture
from uber.config import c
from uber.utils import before, days_after, days_before

from magprime.models import SeasonPassTicket
from magprime.utils import SeasonEvent


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
    filter=lambda a: (
        a.badge_status not in [c.INVALID_STATUS, c.DEFERRED_STATUS]
        and a.paid != c.NOT_PAID
        and (a.paid != c.PAID_BY_GROUP or a.group and not a.group.amount_unpaid)),
    ident='magprime_precon_faqs',
    when=days_before(7, c.EPOCH),
    sender='MAGFest <contact@magfest.org>')

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
    Attendee, 'MAGFest Staff Suite Volunteering', 'food/food_interest.txt',
    lambda a: a.requested(c.FOOD_PREP) or a.assigned_to(c.FOOD_PREP),
    ident='magprime_staff_suite_volunteer_food_interest',
    sender='MAGFest Staff Suite <chefs@magfest.org>')

AutomatedEmailFixture(
    Attendee, 'Important MAGFest PC Gaming Room Information! *PLEASE READ*', 'lan_room.html',
    lambda a: c.LAN in a.interests_ints,
    ident='magprime_important_lan_room_info',
    needs_approval=True,
    sender='MAGFest LAN <lan@magfest.org>')

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
    Attendee, 'MAGFest Staff Suite rules', 'food_volunteers.txt',
    lambda a: a.staffing and a.has_shifts_in(c.FOOD_PREP) and not a.trusted_in(c.FOOD_PREP),
    ident='magprime_food_untrusted_volunteer',
    sender='MAGFest Staff Suite <chefs@magfest.org>')

AutomatedEmailFixture(
    Attendee, 'MAGFest message from Chef', 'food_trusted_staffers.txt',
    lambda a: a.staffing and a.has_shifts_in(c.FOOD_PREP) and a.trusted_in(c.FOOD_PREP),
    ident='magprime_food_trusted_volunteer',
    sender='MAGFest Staff Suite <chefs@magfest.org>')

AutomatedEmailFixture(
    Attendee, 'Want to help run MAGFest poker tournaments?', 'poker.txt',
    lambda a: a.has_shifts_in(c.TABLETOP),
    ident='magprime_tabletop_volunteer_poker_inquiry',
    sender='MAGFest Tabletop <tabletop@magfest.org>')

StopsEmailFixture(
    'MAGFest Staff Support', 'staff_support.txt',
    lambda a: a.assigned_to(c.STAFF_SUPPORT) and not a.trusted_in(c.STAFF_SUPPORT),
    ident='magprime_staff_support_volunteer')

StopsEmailFixture(
    'MAGFest Dept Checklist Introduction', 'dept_checklist_intro.txt',
    lambda a: a.is_checklist_admin and a.admin_account,
    ident='magprime_dept_checklist_intro')

StopsEmailFixture(
    'Last Chance to enter your MAGFest staff shirt preferences', 'second_shirt.html',
    lambda a: not a.shirt_info_marked,
    when=days_before(21, c.SHIRT_DEADLINE),
    ident='magprime_second_shirt')

AutomatedEmailFixture(
    Attendee, 'Last Chance for MAGFest ' + c.EVENT_YEAR + ' bonus swag!', 'attendee_swag_promo.html',
    lambda a: (
        a.can_spam
        and (a.paid == c.HAS_PAID or a.paid == c.NEED_NOT_PAY or (a.group and a.group.amount_paid))
        and days_after(3, a.registered)()),
    when=days_before(14, c.SUPPORTER_DEADLINE),
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

AutomatedEmailFixture(
    Attendee, 'MAGFest ' + c.EVENT_YEAR + ' sweatpants size confirmation', 'confirm_sweatpants_size.html',
    lambda a: a.amount_extra >= c.SUPPORTER_LEVEL and (a.sweatpants == c.NO_SWEATPANTS or not a.sweatpants),
    when=before(c.SHIRT_DEADLINE),
    sender='MAGFest Merch Team <merch@magfest.org>',
    ident='magprime_sweatpants_size_confirmation')

AutomatedEmailFixture(
    Attendee, 'MAGFest Dealer waitlist has been exhausted', 'dealer_waitlist_exhausted.txt',
    lambda a: 'automatically converted to unpaid discounted badge from a dealer application' in a.admin_notes,
    sender=c.MARKETPLACE_EMAIL,
    ident='magprime_marketplace_waitlist_exhausted')
