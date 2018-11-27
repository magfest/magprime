from datetime import datetime, timedelta

import cherrypy
from sqlalchemy.orm import subqueryload

from uber.config import c
from uber.decorators import all_renderable, department_id_adapter
from uber.models import Attendee, Shift, RoomAssignment


@all_renderable(c.PEOPLE)
class Root:
    def index(self, session):
        return {
            'invalids': session.query(Attendee)
                               .options(subqueryload(Attendee.room_assignments).joinedload(RoomAssignment.room),
                                        subqueryload(Attendee.shifts).joinedload(Shift.job))
                               .filter_by(staffing=True,
                                          badge_status=c.INVALID_STATUS)
                               .order_by(Attendee.full_name).all()
        }

    @department_id_adapter
    def volunteer_food(self, session, message='', department_id=None, start=None, end=None):
        staffers = set()
        if cherrypy.request.method == 'POST':
            start = c.EVENT_TIMEZONE.localize(datetime.strptime(start, c.TIMESTAMP_FORMAT))
            end = c.EVENT_TIMEZONE.localize(datetime.strptime(end, c.TIMESTAMP_FORMAT))
            if end < start:
                message = 'Start must come before end {} {}'.format(start, end)
            else:
                hours = set()
                hour = start
                while hour < end:
                    hours.add(hour)
                    hour += timedelta(hours=1)
                for job in session.jobs().filter_by(department_id=department_id):
                    if hours.intersection(job.hours):
                        for shift in job.shifts:
                            if shift.attendee.badge_type == c.STAFF_BADGE or shift.attendee.weighted_hours > 12:
                                staffers.add(shift.attendee)

        return {
            'message': message,
            'end': end,
            'start': start,
            'department_id': department_id,
            'staffers': sorted(staffers, key=lambda a: a.full_name)
        }
def sweatpants_counts(self, session):
        counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        labels = ['size unknown'] + [label for val, label in c.SWEATPANTS_OPTS][1:]

        def sort(d):
            return sorted(d.items(), key=lambda tup: labels.index(tup[0]))

        def label(s):
            return 'size unknown' if s == c.SWEATPANTS[c.NO_SWEATPANTS] else s

        def status(got_merch):
            return 'picked_up' if got_merch else 'outstanding'

        sales_by_week = OrderedDict([(i, 0) for i in range(50)])

        for attendee in session.all_attendees():
            sweatpants_label = attendee.sweatpants_label or 'size unknown'
            counts['all_staff_sweatpantss'][label(sweatpants_label)][status(attendee.got_merch)] += attendee.num_staff_sweatpantss_owed
            counts['all_event_sweatpantss'][label(sweatpants_label)][status(attendee.got_merch)] += attendee.num_event_sweatpantss_owed
            if attendee.volunteer_event_sweatpants_eligible or attendee.replacement_staff_sweatpantss:
                counts['free_event_sweatpantss'][label(sweatpants_label)][status(attendee.got_merch)] += 1
            if attendee.paid_for_a_sweatpants:
                counts['paid_event_sweatpantss'][label(sweatpants_label)][status(attendee.got_merch)] += 1
                sales_by_week[(min(datetime.now(UTC), c.ESCHATON) - attendee.registered).days // 7] += 1

        for week in range(48, -1, -1):
            sales_by_week[week] += sales_by_week[week + 1]

        categories = [
            ('Free Event Sweatpants', sort(counts['free_event_sweatpantss'])),
            ('Paid Event Sweatpants', sort(counts['paid_event_sweatpantss'])),
            ('All Event Sweatpants', sort(counts['all_event_sweatpantss'])),
        ]
        if c.SWEATPANTS_PER_STAFFER > 0:
            categories.append(('Staff Sweatpants', sort(counts['all_staff_sweatpantss'])))

        return {
            'sales_by_week': sales_by_week,
            'categories': categories,
}
