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
        
    @csv_file
    def credits(self, out, session):
        out.writerow(["Name submitted for credits"])
        for attendee in session.all_attendees():
            if attendee.name_in_credits:
                out.writerow([attendee.name_in_credits])