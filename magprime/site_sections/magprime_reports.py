from datetime import datetime, timedelta

import cherrypy
from collections import defaultdict
from sqlalchemy.orm import subqueryload

from uber.config import c
from uber.decorators import all_renderable, csv_file, department_id_adapter
from uber.models import Attendee, Shift, RoomAssignment


@all_renderable()
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

    def special_merch_counts(self, session):
        counts = defaultdict(int)
        labels = ['Unknown'] + [label for val, label in c.SPECIAL_MERCH_OPTS if val != c.NO_MERCH]

        def label(s):
            return 'Unknown' if s == c.NO_MERCH else s

        # This is a little backwards, but we do it this way to catch anyone who has an option
        # that is no longer in our list of special merch options
        for attendee in session.query(Attendee).filter(Attendee.amount_extra >= c.SEASON_LEVEL):
            merch_label = attendee.special_merch_label or 'Unknown'
            counts[label(merch_label)] += 1

        return {
            'counts': counts,
        }
    
    @csv_file
    def donated_badge_attendees(self, out, session):
        out.writerow(["Full Name", "Legal Name", "Email", "Phone #", "Amount Paid", "Amount Unpaid", "Kick-In Level",
                      "Country", "Address1", "Address2", "City", "State/Region", "ZIP/Postal Code"])
        for a in session.query(Attendee).filter_by(donate_badge_cost=True).order_by('country').order_by('region'):
            out.writerow([a.full_name, a.legal_name, a.email, a.cellphone, a.amount_paid, a.amount_unpaid, a.amount_extra_label,
                          a.country, a.address1, a.address2, a.city, a.region, a.zip_code])
