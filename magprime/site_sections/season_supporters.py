from collections import defaultdict

from uber.config import c
from uber.decorators import all_renderable, unrestricted
from uber.errors import HTTPRedirect
from uber.utils import localized_now

from magprime.models import PrevSeasonSupporter, SeasonPassTicket
from magprime.utils import SeasonEvent


@all_renderable(c.PEOPLE)
class Root:
    def index(self, session):
        events = defaultdict(list)
        for spt in session.query(SeasonPassTicket).all():
            events[spt.slug].append(spt.fk)
        for attending in events.values():
            attending.sort(key=lambda a: (a.first_name, a.last_name))
        return {'events': dict(events)}

    def prev_supporters(self, session):
        return {'prev': session.query(PrevSeasonSupporter).order_by('last_name', 'first_name').all()}

    @unrestricted
    def event(self, session, id, slug, register=None):
        season_pass = session.season_pass(id)
        event = SeasonEvent.instances[slug]
        deadline_passed = localized_now() > event.deadline
        if register and not deadline_passed:
            session.add(SeasonPassTicket(fk_id=season_pass.id, slug=slug))
            raise HTTPRedirect('event?id={}&slug={}', id, slug)

        return {
            'event': event,
            'attendee': season_pass,
            'deadline_passed': deadline_passed,
            'registered': bool(session.query(SeasonPassTicket).filter_by(fk_id=id, slug=slug).count())
        }
