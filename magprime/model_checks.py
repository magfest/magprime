from magprime import *


@prereg_validation.Attendee
def child_badge_over_13(attendee):
    if attendee.is_new and attendee.badge_type == c.CHILD_BADGE and attendee.age_group_conf['val'] not in [c.UNDER_6, c.UNDER_13]:
        return "You cannot buy a Child badge if you will be 13 or older at the start of {}".format(c.EVENT_NAME)


@prereg_validation.Attendee
def attendee_badge_under_13(attendee):
    if attendee.is_new and attendee.badge_type == c.ATTENDEE_BADGE and attendee.age_group_conf['val'] in [c.UNDER_6, c.UNDER_13]:
        return "You cannot buy an Attendee badge if you will be under 13 at the start of {}".format(c.EVENT_NAME)


@validation.Attendee
def child_badge_over_18(attendee):
    if attendee.badge_type == c.CHILD_BADGE and attendee.age_group_conf['val'] in [c.UNDER_21, c.OVER_21]:
        # This message is confusing for attendees, so we only show it to admins
        if c.PAGE_PATH in ['/registration/change_badge']:
            return "Attendees who are 18 or over (or will be at the start of {}) cannot have Minor badges. Please update their date of birth instead.".format(c.EVENT_NAME)
