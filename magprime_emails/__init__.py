from uber.common import *
from magprime_emails._version import __version__

config = parse_config(__file__)
django.conf.settings.TEMPLATE_DIRS.insert(0, join(config['module_root'], 'templates'))


AutomatedEmail(Attendee, 'MAGFest schedule, maps, and other FAQs', 'precon_faqs.html', lambda a: days_before(7, EPOCH),
               needs_approval=True)


# These definitely need to be reviewed
GuestEmail('MAGFest food for guests', 'guest_food_restrictions.txt')
GuestEmail('MAGFest hospitality suite information', 'guest_food_info.txt')


MarketplaceEmail('Delays with {EVENT_NAME} Dealer applications', 'dealer_deadline_change.txt',
                 lambda g: g.status == UNAPPROVED, needs_approval=True)


# we can just remove this next year
StopsEmail('(Corrected) Reminder to meet your {EVENT_NAME} hotel room requirements', 'hotel_hours_correction.txt',
           lambda a: days_before(1, datetime(2014, 12, 23, tzinfo=UTC)) and a.hotel_shifts_required and a.weighted_hours < 30,
           needs_approval=True)


# Turn these on after some review (they already went out to last year's staffers, whoops!)
if False:
    StopsEmail('MAGFest Tech Ops volunteering', 'techops.txt',
               lambda a: a.requested(TECH_OPS) and not a.assigned_to(TECH_OPS))

    StopsEmail('MAGFest Chipspace volunteering', 'chipspace.txt',
               lambda a: (a.requested(JAMSPACE) or a.assigned_to(JAMSPACE)) and not a.assigned_to(CHIPSPACE))

    StopsEmail('MAGFest Chipspace shifts', 'chipspace_trusted.txt',
               lambda a: a.assigned_to(CHIPSPACE) and a.trusted)

    StopsEmail('MAGFest Chipspace', 'chipspace_untrusted.txt',
               lambda a: a.has_shifts_in(CHIPSPACE) and not a.trusted)

    StopsEmail('MAGFest food prep volunteering', 'food_interest.txt',
               lambda a: a.requested(FOOD_PREP) and not a.assigned_depts)

    StopsEmail('MAGFest food prep rules', 'food_volunteers.txt',
               lambda a: a.has_shifts_in(FOOD_PREP) and not a.trusted)

    StopsEmail('MAGFest message from Chef', 'food_trusted_staffers.txt',
               lambda a: a.has_shifts_in(FOOD_PREP) and a.trusted)

    StopsEmail('MAGFest Volunteer Food', 'volunteer_food_info.txt',
               lambda a: days_before(7, UBER_TAKEDOWN))

    AutomatedEmail(Attendee, 'Want to help run MAGFest poker tournaments?', 'poker.txt',
                   lambda a: a.has_shifts_in(TABLETOP), sender='tabletop@magfest.org')
