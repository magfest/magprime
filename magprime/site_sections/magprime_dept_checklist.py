from magprime import *


@all_renderable(c.PEOPLE)
class Root:
    def index(self, session, message=''):
        raise HTTPRedirect('../dept_checklist/?message={}', message)

    def treasury(self, session, submitted=None, csrf_token=None):
        attendee = session.admin_attendee()
        if submitted:
            try:
                [item] = [item for item in attendee.dept_checklist_items if item.slug == 'treasury']
            except:
                item = DeptChecklistItem(slug='treasury', attendee=attendee)
            check_csrf(csrf_token)  # since this form doesn't use our normal utility methods, we need to do this manually
            session.add(item)
            raise HTTPRedirect('../dept_checklist/index?message={}', 'Thanks for completing the Cash/MPoints form!')

        return {}
