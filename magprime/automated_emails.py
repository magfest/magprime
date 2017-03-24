from magprime import *

AutomatedEmail.queries[SeasonPassTicket] = lambda session: session.season_passes()


class SeasonSupporterEmail(AutomatedEmail):
    def __init__(self, event):
        AutomatedEmail.__init__(self, SeasonPassTicket,
                                subject='Claim your {} tickets with your MAGFest Season Pass'.format(event.name),
                                ident='magprime_season_supporter_{}_invite'.format(event.slug),
                                template='season_supporter_event_invite.txt',
                                when=before(event.deadline),
                                extra_data={'event': event})

for _event in SeasonEvent.instances.values():
    SeasonSupporterEmail(_event)


AutomatedEmail(Attendee, 'MAGFest schedule, maps, and other FAQs', 'precon_faqs.html',
               filter=lambda a: a.badge_status not in [c.INVALID_STATUS, c.DEFERRED_STATUS]
                            and a.paid != c.NOT_PAID
                            and (a.paid != c.PAID_BY_GROUP or a.group and not a.group.amount_unpaid),
               ident='magprime_precon_faqs',
               when=days_before(7, c.EPOCH))

AutomatedEmail(Attendee, 'MAGFest food for guests', 'guest_food_restrictions.txt',
               lambda a: a.badge_type == c.GUEST_BADGE, sender='MAGFest Staff Suite <chefs@magfest.org>',
               ident='magprime_guest_food_restrictions')
AutomatedEmail(Attendee, 'MAGFest hospitality suite information', 'guest_food_info.txt',
               lambda a: a.badge_type == c.GUEST_BADGE, sender='MAGFest Staff Suite <chefs@magfest.org>',
               ident='magprime_hospitality_suite_guest_food_info')

AutomatedEmail(Attendee, 'MAGFest Volunteer Food', 'volunteer_food_info.txt',
            lambda a: a.staffing,
            ident='magprime_volunteer_food_info',
            when=days_before(7, c.UBER_TAKEDOWN),
            sender='MAGFest Staff Suite <chefs@magfest.org>')

AutomatedEmail(Attendee, 'MAGFest Staff Suite Volunteering', 'food_interest.txt',
               lambda a: a.requested(c.FOOD_PREP) or a.assigned_to(c.FOOD_PREP),
               ident='magprime_staff_suite_volunteer_food_interest',
               sender='MAGFest Staff Suite <chefs@magfest.org>')

AutomatedEmail(Attendee, 'Important MAGFest PC Gaming Room Information! *PLEASE READ*', 'lan_room.html',
               lambda a: c.LAN in a.interests_ints,
               ident='magprime_important_lan_room_info',
               needs_approval=True,
               sender='MAGFest LAN <lan@magfest.org>')

AutomatedEmail(Attendee, 'MAGFest Tech Ops volunteering', 'techops.txt',
           lambda a: a.staffing and a.assigned_to(c.TECH_OPS),
           ident='magprime_techops_volunteer',
           sender='MAGFest TechOps <techops-heads@magfest.org>')

AutomatedEmail(Attendee, 'MAGFest Chipspace volunteering', 'chipspace.txt',
           lambda a: a.staffing and a.assigned_to(c.CHIPSPACE),
           ident='magprime_chipspace_volunteer',
           sender='MAGFest ChipSpace <chipspace@magfest.org>')

AutomatedEmail(Attendee, 'MAGFest Chipspace shifts', 'chipspace_trusted.txt',
           lambda a: a.staffing and a.has_shifts_in(c.CHIPSPACE) and a.trusted_in(c.CHIPSPACE),
           ident='magprime_chipspace_trusted_volunteer',
           sender='MAGFest ChipSpace <chipspace@magfest.org>')

AutomatedEmail(Attendee, 'MAGFest Chipspace', 'chipspace_untrusted.txt',
           lambda a: a.staffing and a.has_shifts_in(c.CHIPSPACE) and not a.trusted_in(c.CHIPSPACE),
           ident='magprime_chipspace_untrusted_volunteer',
           sender='MAGFest ChipSpace <chipspace@magfest.org>')

AutomatedEmail(Attendee, 'MAGFest Staff Suite rules', 'food_volunteers.txt',
           lambda a: a.staffing and a.has_shifts_in(c.FOOD_PREP) and not a.trusted_in(c.FOOD_PREP),
           ident='magprime_food_untrusted_volunteer',
           sender='MAGFest Staff Suite <chefs@magfest.org>')

AutomatedEmail(Attendee, 'MAGFest message from Chef', 'food_trusted_staffers.txt',
           lambda a: a.staffing and a.has_shifts_in(c.FOOD_PREP) and a.trusted_in(c.FOOD_PREP),
           ident='magprime_food_trusted_volunteer',
           sender='MAGFest Staff Suite <chefs@magfest.org>')

AutomatedEmail(Attendee, 'Want to help run MAGFest poker tournaments?', 'poker.txt',
               lambda a: a.has_shifts_in(c.TABLETOP),
               ident='magprime_tabletop_volunteer_poker_inquiry',
               sender='MAGFest Tabletop <tabletop@magfest.org>')

StopsEmail('MAGFest Staff Support', 'staff_support.txt',
           lambda a: a.assigned_to(c.STAFF_SUPPORT) and not a.trusted_in(c.STAFF_SUPPORT),
           ident='magprime_staff_support_volunteer')

# Left here in case the decision to remove is re-visited later. 20160809 RAE
# MarketplaceEmail('Your MAGFest Marketplace Application has been waitlisted', 'marketplace_auto_waitlisted.txt',
#                 lambda g: g.status == c.WAITLISTED and g.registered >= c.DEALER_REG_DEADLINE)

StopsEmail('MAGFest Dept Checklist Introduction', 'dept_checklist_intro.txt',
           lambda a: a.is_single_dept_head and a.admin_account,
           ident='magprime_dept_checklist_intro')

AutomatedEmail(Attendee, 'Last Chance for MAGFest ' + c.YEAR + ' bonus swag!', 'attendee_swag_promo.html',
               lambda a: a.can_spam and
                         (a.paid == c.HAS_PAID or a.paid == c.NEED_NOT_PAY or (a.group and a.group.amount_paid)) and
                         days_after(3, a.registered)(),
                         when=days_before(14, c.SUPPORTER_DEADLINE),
               ident='magprime_bonus_swag_reminder_last_chance')

# Send to any attendee who will be receiving a t-shirt (staff, volunteers, anyone
# who kicked in at the shirt level or above).	Should not be sent after the t-shirt
# size deadline.
AutomatedEmail(Attendee, 'MAGFest ' + c.YEAR + ' t-shirt size confirmation', 'confirm_shirt_size.html',
               lambda a: days_after(3, a.registered)() and
                         a.gets_shirt, when=before(c.SHIRT_DEADLINE),
               ident='magprime_shirt_size_confirmation')

AutomatedEmail(Attendee, 'MAGFest Dealer waitlist has been exhausted', 'dealer_waitlist_exhausted.txt',
               lambda a: 'automatically converted to unpaid discounted badge from a dealer application' in a.admin_notes,
               sender=c.MARKETPLACE_EMAIL, ident='magprime_marketplace_waitlist_exhausted')


@on_startup
def onsite_email_performance():
    """
    This is purely a performance tweak.  MAGFest has a large enough database
    that we don't want to iterate over all rows and instances every time the
    email task fires while we're in at-the-con mode, since we're more sensitive
    to performance while on-site.  Since we know that the only emails we care
    about sending while on-site are Attendee emails, we turn off all other
    database queries when in at-the-con mode so that we won't perform them.
    We then turn off all emails which aren't enabled to send during the con
    as a further optimization.
    """
    if c.AT_THE_CON:
        AutomatedEmail.queries = {Attendee: AutomatedEmail.queries[Attendee]}
        for ident, instance in list(AutomatedEmail.instances.items()):
            if not instance.allow_during_con:
                del AutomatedEmail.instances[ident]
