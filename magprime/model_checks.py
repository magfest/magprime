from magprime import *


@prereg_validation.Attendee
def child_badge_over_13(attendee):
    if attendee.is_new and attendee.badge_type == c.CHILD_BADGE and attendee.age_group_conf['val'] not in [c.UNDER_6, c.UNDER_13]:
        return "You cannot buy a Child badge if you will be 13 or older at the start of {}".format(c.EVENT_NAME)


@prereg_validation.Attendee
def attendee_badge_under_13(attendee):
    if attendee.is_new and attendee.badge_type == c.ATTENDEE_BADGE and attendee.age_group_conf['val'] in [c.UNDER_6, c.UNDER_13]:
        return "You cannot buy an Attendee badge if you will be under 13 at the start of {}".format(c.EVENT_NAME)


@prereg_validation.Attendee
def group_leader_under_13(attendee):
    if attendee.badge_type == c.PSEUDO_GROUP_BADGE and attendee.age_group_conf['val'] in [c.UNDER_6, c.UNDER_13]:
        return "Children under 13 cannot be group leaders."


@prereg_validation.Attendee
def total_cost_over_paid(attendee):
    if attendee.total_cost < attendee.amount_paid:
        if attendee.orig_value_of('birthdate') < attendee.birthdate and attendee.age_group_conf['val'] in [c.UNDER_6, c.UNDER_13]:
            return 'The date of birth you entered incurs a discount; please email regsupport@magfest.org to change your badge and receive a refund'
        return 'You have already paid ${}, you cannot reduce your extras below that.'.format(attendee.amount_paid)


@validation.Attendee
def child_badge_over_18(attendee):
    if attendee.badge_type == c.CHILD_BADGE and attendee.age_group_conf['val'] in [c.UNDER_21, c.OVER_21]:
        # This message is confusing for attendees, so we only show it to admins
        if c.PAGE_PATH in ['/registration/form', '/registration/change_badge']:
            return "Attendees who are 18 or over (or will be at the start of {}) cannot have Minor badges.".format(c.EVENT_NAME)
