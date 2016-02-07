from magprime import *

AutomatedEmail.extra_models[SeasonPassTicket] = lambda session: session.season_passes()


class SeasonSupporterEmail(AutomatedEmail):
    def __init__(self, event):
        AutomatedEmail.__init__(self, SeasonPassTicket,
                                subject='Claim your {} tickets with your MAGFest Season Pass'.format(event.name),
                                template='season_supporter_event_invite.txt',
                                filter=lambda a: before(event.deadline),
                                extra_data={'event': event})

for _event in SeasonEvent.instances.values():
    SeasonSupporterEmail(_event)


AutomatedEmail(Attendee, 'MAGFest schedule, maps, and other FAQs', 'precon_faqs.html', lambda a: days_before(7, c.EPOCH))

AutomatedEmail(Attendee, 'MAGFest food for guests', 'guest_food_restrictions.txt',
               lambda a: a.badge_type == c.GUEST_BADGE, sender='MAGFest Staff Suite <chefs@magfest.org>')
AutomatedEmail(Attendee, 'MAGFest hospitality suite information', 'guest_food_info.txt',
               lambda a: a.badge_type == c.GUEST_BADGE, sender='MAGFest Staff Suite <chefs@magfest.org>')

AutomatedEmail(Attendee, 'MAGFest Volunteer Food', 'volunteer_food_info.txt',
           lambda a: a.staffing and days_before(7, c.UBER_TAKEDOWN), sender='MAGFest Staff Suite <chefs@magfest.org>')

AutomatedEmail(Attendee, 'MAGFest Staff Suite Volunteering', 'food_interest.txt',
           lambda a: a.requested(c.FOOD_PREP) or a.assigned_to(c.FOOD_PREP), sender='MAGFest Staff Suite <chefs@magfest.org>')

AutomatedEmail(Attendee, 'Important MAGFest PC Gaming Room Information! *PLEASE READ*', 'lan_room.html',
               lambda a: c.LAN in a.interests_ints,
               needs_approval=True,
               sender='MAGFest LAN <lan@magfest.org>')

AutomatedEmail(Attendee, 'MAGFest Tech Ops volunteering', 'techops.txt',
           lambda a: a.staffing and a.assigned_to(c.TECH_OPS), sender='MAGFest TechOps <techops-heads@magfest.org>')

AutomatedEmail(Attendee, 'MAGFest Chipspace volunteering', 'chipspace.txt',
           lambda a: a.staffing and a.assigned_to(c.CHIPSPACE), sender='MAGFest ChipSpace <chipspace@magfest.org>')

AutomatedEmail(Attendee, 'MAGFest Chipspace shifts', 'chipspace_trusted.txt',
           lambda a: a.staffing and a.has_shifts_in(c.CHIPSPACE) and a.trusted_in(c.CHIPSPACE), sender='MAGFest ChipSpace <chipspace@magfest.org>')

AutomatedEmail(Attendee, 'MAGFest Chipspace', 'chipspace_untrusted.txt',
           lambda a: a.staffing and a.has_shifts_in(c.CHIPSPACE) and not a.trusted_in(c.CHIPSPACE), sender='MAGFest ChipSpace <chipspace@magfest.org>')

AutomatedEmail(Attendee, 'MAGFest Staff Suite rules', 'food_volunteers.txt',
           lambda a: a.staffing and a.has_shifts_in(c.FOOD_PREP) and not a.trusted_in(c.FOOD_PREP), sender='MAGFest Staff Suite <chefs@magfest.org>')

AutomatedEmail(Attendee, 'MAGFest message from Chef', 'food_trusted_staffers.txt',
           lambda a: a.staffing and a.has_shifts_in(c.FOOD_PREP) and a.trusted_in(c.FOOD_PREP), sender='MAGFest Staff Suite <chefs@magfest.org>')

AutomatedEmail(Attendee, 'Want to help run MAGFest poker tournaments?', 'poker.txt',
               lambda a: a.has_shifts_in(c.TABLETOP), sender='MAGFest Tabletop <tabletop@magfest.org>')

StopsEmail('MAGFest Staff Support', 'staff_support.txt',
           lambda a: a.assigned_to(c.STAFF_SUPPORT) and not a.trusted_in(c.STAFF_SUPPORT))

MarketplaceEmail('Your MAGFest Marketplace Application', 'marketplace_delay.txt',
                 lambda g: g.status == c.UNAPPROVED and g.registered < datetime(2015, 10, 29, tzinfo=c.EVENT_TIMEZONE))

MarketplaceEmail('Your MAGFest Marketplace Application has been waitlisted', 'marketplace_auto_waitlisted.txt',
                 lambda g: g.status == c.WAITLISTED and g.registered >= c.DEALER_REG_DEADLINE)

StopsEmail('MAGFest Dept Checklist Introduction', 'dept_checklist_intro.txt',
           lambda a: a.is_single_dept_head and a.admin_account)

AutomatedEmail(Attendee, 'Last Chance for MAGFest 2016 bonus swag!', 'attendee_swag_promo.html',
               lambda a: a.can_spam and
                         (a.paid == c.HAS_PAID or a.paid == c.NEED_NOT_PAY or (a.group and a.group.amount_paid)) and
                         days_after(3, a.registered) and
                         days_before(14, c.SUPPORTER_DEADLINE))

# Send to any attendee who will be receiving a t-shirt (staff, volunteers, anyone
# who kicked in at the shirt level or above).	Should not be sent after the t-shirt
# size deadline (a new deadline not yet recorded in uber).
AutomatedEmail(Attendee, 'MAGFest 2016 t-shirt size confirmation', 'confirm_shirt_size.html',
               lambda a: before(datetime(2016, 1, 16, tzinfo=c.EVENT_TIMEZONE)) and
                         days_after(3, a.registered) and
                         a.gets_shirt)
