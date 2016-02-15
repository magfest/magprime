from magprime import *


@all_renderable(c.PEOPLE)
class Root:
    def index(self, session):
        from hotel import RoomAssignment
        return {
            'invalids': session.query(Attendee)
                               .options(subqueryload(Attendee.room_assignments).joinedload(RoomAssignment.room),
                                        subqueryload(Attendee.shifts).joinedload(Shift.job))
                               .filter_by(staffing=True,
                                          badge_status=c.INVALID_STATUS)
                               .order_by(Attendee.full_name).all()
        }

    def volunteer_food(self, session, message='', department=None, start=None, end=None):
        staffers = []
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
                for job in session.jobs().filter_by(location=department):
                    if hours.intersection(job.hours):
                        for shift in job.shifts:
                            staffers.append(shift.attendee)

        return {
            'message': message,
            'end': end,
            'start': start,
            'department': department,
            'staffers': sorted(staffers, key=lambda a: a.full_name)
        }
