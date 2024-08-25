from .config import c
from uber.model_checks import prereg_validation, validation, ignore_unassigned_and_placeholders


@validation.PanelApplication
def magscouts(app):
    if c.NONE in app.granular_rating_ints and app.magscouts_opt_in == c.NO_CHOICE:
        return "Please choose whether to participate in the MAGScouts program."


@prereg_validation.Group
def license_if_permit(group):
    if group.has_permit and not group.license:
        return "Please provide your license number."


@prereg_validation.Attendee
def select_special_merch_size(attendee):
    if attendee.amount_extra >= c.SEASON_LEVEL and attendee.special_merch == c.NO_MERCH and len(c.SPECIAL_MERCH_OPTS) > 1:
        return "Please select a button-down shirt size."


@validation.Attendee
@ignore_unassigned_and_placeholders
def address(attendee):
    if c.COLLECT_FULL_ADDRESS or attendee.donate_badge_cost:
        if not attendee.address1:
            return 'Please enter a street address.'
        if not attendee.city:
            return 'Please enter a city.'
        if not attendee.region and attendee.country in ['United States', 'Canada']:
            return 'Please enter a state, province, or region.'
        if not attendee.country:
            return 'Please enter a country.'


@validation.GuestTravelPlans
def has_modes(guest_travel_plans):
    return


@validation.GuestTravelPlans
def has_modes_text(guest_travel_plans):
    return


@validation.GuestTravelPlans
def has_details(guest_travel_plans):
    return