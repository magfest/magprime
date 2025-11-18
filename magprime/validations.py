from wtforms import validators
from wtforms.validators import ValidationError, StopValidation

from .config import c
from uber.validations import TableInfo, BadgeExtras, PanelInfo, RoomLottery, DietaryRestrictions, JobInfo, JobTemplateInfo


TableInfo.field_validation.required_fields['prior_name'] = ("Please provide your prior table name.", 'has_prior_name')
TableInfo.field_validation.required_fields['license'] = ("Please provide your license number.", 'has_permit')


BadgeExtras.field_validation.validations['extra_donation']['minimum'] = validators.NumberRange(
    min=0, message="Superstar donation must be a number that is 0 or higher.")


PanelInfo.field_validation.required_fields['broadcast_title'] = ("Please provide a short title for digital displays.",
                                                                 'name', lambda x: len(x) > 40)
PanelInfo.field_validation.required_fields['broadcast_subtitle'] = "Please provide a one-line summary for digital displays."


@RoomLottery.field_validation('room_type_preference')
def atrium_gaylord_only(form, field):
    if not field.data or not form.hotel_preference or not form.hotel_preference.data:
        return
    
    if (c.HOTEL_LOTTERY_KING_ATRIUM in field.data or c.HOTEL_LOTTERY_DOUBLE_ATRIUM in field.data
            ) and c.HOTEL_LOTTERY_GAYLORD not in form.hotel_preference.data:
        raise ValidationError("Atrium rooms are only available at the Gaylord National Harbor.")


DietaryRestrictions.field_validation.required_fields = {
    'has_allergies': ("Please let us know if you have any allergies or dietary restrictions.",
                      'has_allergies', lambda x: x.raw_data == []),
    'standard': ("Please select one or more dietary restrictions, or 'Other'.",
                 'has_allergies'),
    'freeform': ("Please list each of your other allergies, separated by commas.",
                 'standard', lambda x: c.OTHER in x.data),
}


JobInfo.field_validation.required_fields['slots'] = "The minimum number of job slots is 1."
JobTemplateInfo.field_validation.required_fields['min_slots'] = "Please set a minimum of at least 1 job slot."