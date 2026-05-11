import cherrypy

from uber.config import c
from uber.decorators import all_renderable, check_shutdown, requires_account
from uber.errors import HTTPRedirect
from uber.models import LotteryApplication


@all_renderable(public=True)
class Root:
    @requires_account()
    @check_shutdown
    def prelottery(self, session, id, message='', **params):
        if c.AFTER_HOTEL_LOTTERY_STAFF_DEADLINE and not c.HAS_HOTEL_LOTTERY_ADMIN_ACCESS:
            raise HTTPRedirect('../staffing/checklist?id={}&message={}', id, 'The prelottery selection deadline has passed')
        attendee = session.volunteer_from_id(id)

        if cherrypy.request.method == "POST":
            if params.get('prelottery'):
                attendee.hotel_eligible = False
                if attendee.lottery_application:
                    attendee.lottery_application.status = c.PARTIAL
                message = "You have been opted into the staff pre-lottery."
            elif params.get('crash_space'):
                attendee.hotel_eligible = True
                if not attendee.lottery_application:
                    attendee.lottery_application = LotteryApplication(attendee_id=attendee.id)
                attendee.lottery_application.status = c.DISQUALIFIED
                session.add(attendee.lottery_application)
                message = "You have been opted into staff crash space."
            raise HTTPRedirect('../staffing/checklist?id={}&message={}', id, message)

        return {
            'message':  message,
            'attendee': attendee
        }