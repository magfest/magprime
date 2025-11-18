from datetime import datetime, timedelta

import cherrypy
from collections import defaultdict
from sqlalchemy.orm import subqueryload

from uber.config import c
from uber.custom_tags import datetime_local_filter
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
    
    def superstars(self, session):
        counts = {}
        owe_money = {}
        superstars = session.valid_attendees().filter(Attendee.extra_donation >= c.SUPERSTAR_MINIMUM)

        valid_donations_list = c.SUPERSTAR_DONATION_OPTS[1:-1]
        last_index = len(valid_donations_list) - 1
        for index, opt in enumerate(valid_donations_list):
            amt, label = opt
            count_query = session.valid_attendees().filter(Attendee.extra_donation >= amt)
            if index != last_index:
                next_amt, next_label = valid_donations_list[index + 1]
                count_query = count_query.filter(Attendee.extra_donation < next_amt)
            counts[label] = count_query.count()

        for attendee in [a for a in superstars if a.amount_unpaid or not a.active_receipt]:
            owe_money[attendee.id] = attendee.amount_unpaid if attendee.active_receipt else attendee.default_cost
        
        return {
            'attendees': superstars,
            'counts': counts,
            'owe_money': owe_money,
            'total_count': superstars.count(),
        }
    
    @csv_file
    def superstars_csv(self, out, session):
        out.writerow(["Group Name", "Full Name", "Name on ID", "Badge Name", "Badge Type", "Ribbons", "Pre-ordered Merch",
                      "Donation", "Email", "ZIP/Postal Code", "Checked In"])
        for a in session.valid_attendees().filter(Attendee.extra_donation >= c.SUPERSTAR_MINIMUM):
            out.writerow([a.group_name, a.full_name, a.legal_name, a.badge_printed_name, a.badge_type_label,
                          ' / '.join(a.ribbon_labels), a.amount_extra_label, a.extra_donation, a.email, a.zip_code,
                          datetime_local_filter(a.checked_in)])
    
    @csv_file
    def donated_badge_attendees(self, out, session):
        out.writerow(["Full Name", "Legal Name", "Email", "Phone #", "Amount Paid", "Amount Unpaid", "Kick-In Level",
                      "Country", "Address1", "Address2", "City", "State/Region", "ZIP/Postal Code"])
        for a in session.query(Attendee).filter_by(donate_badge_cost=True).order_by('country').order_by('region'):
            out.writerow([a.full_name, a.legal_name, a.email, a.cellphone, a.amount_paid, a.amount_unpaid, a.amount_extra_label,
                          a.country, a.address1, a.address2, a.city, a.region, a.zip_code])
