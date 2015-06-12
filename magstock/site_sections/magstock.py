from uber.common import *


@all_renderable(c.PEOPLE)
class Root:
    def grouped(self, session):
        attendees = session.query(Attendee).all()

        names = {}
        for attendee in attendees:
            names.setdefault(attendee.last_name.lower(), set()).add(attendee)

        lookup = defaultdict(set)
        for xs in names.values():
            for attendee in xs:
                lookup[attendee] = xs

        for attendee in attendees:
            for word in attendee.coming_with.lower().replace(',', ' ').split():
                try:
                    combined = lookup[list(names[word])[0]] | lookup[attendee]
                    for attendee in combined:
                        lookup[attendee] = combined
                except:
                    pass

        return {'grouped': sorted({frozenset(group) for group in lookup.values()}, key=len, reverse=True)}

    def food_purchases(self, session):
        return {
            'attendees': session.query(Attendee)
                                .filter(or_(Attendee.purchased_food == True,
                                            Attendee.badge_type.in_([c.STAFF_BADGE, c.GUEST_BADGE])))
                                .order_by(Attendee.full_name).all()
        }
