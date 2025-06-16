from .config import c
from uber.model_checks import prereg_validation, validation, ignore_unassigned_and_placeholders


@validation.PanelApplication
def magscouts(app):
    if c.NONE in app.granular_rating_ints and app.magscouts_opt_in == c.NO_CHOICE:
        return "Please choose whether to participate in the MAGScouts program."


@prereg_validation.Group
def license_if_permit(group):
    if group.has_permit and not group.license:
        return ('license', "Please provide your license number.")


@prereg_validation.Group
def prior_name_if_prior(group):
    if group.has_prior_name and not group.prior_name:
        return ('prior_name', "Please provide your prior table name.")


@prereg_validation.Attendee
def select_special_merch_size(attendee):
    if attendee.amount_extra >= c.SEASON_LEVEL and attendee.special_merch == c.NO_MERCH and len(c.SPECIAL_MERCH_OPTS) > 1:
        return "Please select a button-down shirt size."


@validation.GuestTravelPlans
def has_modes(guest_travel_plans):
    return


@validation.GuestTravelPlans
def has_modes_text(guest_travel_plans):
    return


@validation.GuestTravelPlans
def has_details(guest_travel_plans):
    return