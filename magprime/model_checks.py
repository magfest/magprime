from .config import c
from uber.model_checks import prereg_validation, validation


@prereg_validation.Attendee
def read_covid_policy(attendee):
    if not attendee.agreed_to_covid_policies:
        return "Please read and agree to the COVID Policies for Super MAGFest 2022."


@prereg_validation.Attendee
def select_special_merch_size(attendee):
    if attendee.amount_extra >= c.SEASON_LEVEL and attendee.special_merch == c.NO_MERCH:
        return "Please select a button-down shirt size."


@prereg_validation.Attendee
def child_badge_over_13(attendee):
    if attendee.is_new and attendee.badge_type == c.CHILD_BADGE \
            and attendee.age_now_or_at_con and attendee.age_now_or_at_con >= 13:
        return "If you will be 13 or older at the start of {}, " \
            "please select an Attendee badge instead of a 12 and Under badge.".format(c.EVENT_NAME)


@validation.Attendee
def allowed_to_register(attendee):
    if not attendee.age_group_conf['can_register']:
        return 'Per our COVID policies, attendees {} years of age currently may not register. \
                Please email regsupport@magfest.org for more info.'.format(attendee.age_group_conf['desc'].lower())


@prereg_validation.Attendee
def attendee_badge_under_13(attendee):
    if attendee.is_new and attendee.badge_type == c.ATTENDEE_BADGE \
            and attendee.age_now_or_at_con and attendee.age_now_or_at_con < 13:
        return "If you will be 12 or younger at the start of {}, " \
            "please select the 12 and Under badge instead of an Attendee badge.".format(c.EVENT_NAME)

           
@validation.Attendee
def no_more_child_badges(attendee):
    if attendee.is_new and attendee.age_now_or_at_con and attendee.age_now_or_at_con < 18 \
            and not c.CHILD_BADGE_AVAILABLE:
        return "Unfortunately, we are sold out of badges for attendees under 18."