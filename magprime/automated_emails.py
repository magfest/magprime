from magprime import *

AutomatedEmail.extra_models['SeasonPass'] = lambda session: session.season_passes()


class SeasonSupporterEmail(AutomatedEmail):
    def __init__(self, event):
        AutomatedEmail.__init__(self, 'SeasonPass',
                                subject='Claim your {} tickets with your MAGFest Season Pass'.format(event.name),
                                template='season_supporter_event_invite.txt',
                                filter=lambda a: before(event.deadline),
                                extra_data={'event': event})

for _event in SeasonEvent.instances.values():
    SeasonSupporterEmail(_event)


AutomatedEmail(Attendee, 'MAGFest schedule, maps, and other FAQs', 'precon_faqs.html', lambda a: days_before(7, c.EPOCH))

GuestEmail('MAGFest food for guests', 'guest_food_restrictions.txt')
GuestEmail('MAGFest hospitality suite information', 'guest_food_info.txt')

StopsEmail('MAGFest Volunteer Food', 'volunteer_food_info.txt',
           lambda a: days_before(7, c.UBER_TAKEDOWN))

StopsEmail('MAGFest Staff Suite Volunteering', 'food_interest.txt',
           lambda a: a.requested(c.FOOD_PREP) and not a.assigned_depts)

AutomatedEmail(Attendee, 'Important MAGFest PC Gaming Room Information! *PLEASE READ*', 'lan_room.html',
               lambda a: LAN in a.interests_ints,
               needs_approval=True,
               sender='lan@magfest.org')

StopsEmail('MAGFest Tech Ops volunteering', 'techops.txt',
           lambda a: a.requested(c.TECH_OPS) and not a.assigned_to(c.TECH_OPS))

StopsEmail('MAGFest Chipspace volunteering', 'chipspace.txt',
           lambda a: (a.requested(c.JAMSPACE) or a.assigned_to(c.JAMSPACE)) and not a.assigned_to(c.CHIPSPACE))

StopsEmail('MAGFest Chipspace shifts', 'chipspace_trusted.txt',
           lambda a: a.assigned_to(c.CHIPSPACE) and a.trusted)

StopsEmail('MAGFest Chipspace', 'chipspace_untrusted.txt',
           lambda a: a.has_shifts_in(c.CHIPSPACE) and not a.trusted)

StopsEmail('MAGFest Staff Suite rules', 'food_volunteers.txt',
           lambda a: a.has_shifts_in(c.FOOD_PREP) and not a.trusted)

StopsEmail('MAGFest message from Chef', 'food_trusted_staffers.txt',
           lambda a: a.has_shifts_in(c.FOOD_PREP) and a.trusted)

AutomatedEmail(Attendee, 'Want to help run MAGFest poker tournaments?', 'poker.txt',
               lambda a: a.has_shifts_in(c.TABLETOP), sender='tabletop@magfest.org')

StopsEmail('MAGFest Staff Support', 'staff_support.txt',
           lambda a: a.assigned_to(c.STAFF_SUPPORT) and not a.trusted)
