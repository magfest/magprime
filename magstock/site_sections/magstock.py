from uber.common import *


@all_renderable(c.PEOPLE)
class Root:
    def grouped(self, session, noise=None, site=None, camp=None):
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

        def match(a):
            return ((not site or a.site_type == int(site))
                and (not camp or a.camping_type == int(camp))
                and (not noise or a.noise_level == int(noise)))

        def any_match(group):
            return any(match(a) for a in group)

        return {
            'camp': camp,
            'site': site,
            'noise': noise,
            'grouped': sorted({frozenset(group) for group in lookup.values() if any_match(group)}, key=len, reverse=True)
        }

    def food_purchases(self, session):
        return {'attendees': session.food_purchasers().order_by(Attendee.full_name).all()}
